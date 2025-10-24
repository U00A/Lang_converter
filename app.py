"""
FastAPI application for the AI Code Converter.
"""
import asyncio
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config.settings import settings
from config.logging import configure_logging, get_logger
from models.schemas import (
    ConversionRequest, ConversionResponse, BatchConversionRequest, 
    BatchConversionResponse, FileUploadRequest, SystemStatus, 
    ErrorResponse, ApplicationConfig, LanguageInfo, AIProviderConfig,
    ConversionHistory
)
from services.converter import conversion_service
from services.ai_providers import provider_manager
from services.code_analyzer import code_analyzer
from services.cache_service import cache_service


# Configure logging
configure_logging()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AI Code Converter application", version="1.0.0")
    
    # Initialize services
    try:
        # Initialize cache service
        await cache_service.initialize()
        logger.info("Cache service initialized")
        
        # Check AI providers
        provider_status = await provider_manager.get_provider_status()
        available_providers = [name for name, status in provider_status.items() if status["available"]]
        logger.info("Available AI providers", providers=available_providers)
        
        if not available_providers:
            logger.warning("No AI providers available. Only fallback conversion will work.")
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Code Converter application")
    # Close cache connection
    await cache_service.close()


# Create FastAPI app
app = FastAPI(
    title="AI Code Converter",
    description="Advanced AI-powered code conversion between multiple programming languages",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
if os.path.exists("templates"):
    templates = Jinja2Templates(directory="templates")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An internal error occurred",
            details={"error_type": type(exc).__name__}
        ).dict()
    )


# Dependency for rate limiting (simplified)
async def rate_limit_check(request: Request):
    """Simple rate limiting check."""
    # In production, use Redis or similar for distributed rate limiting
    client_ip = request.client.host
    # For now, just log the request
    logger.info("API request", client_ip=client_ip, path=request.url.path)
    return True


# API Routes

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main application page."""
    if os.path.exists("templates/index.html"):
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("""
        <html>
            <head><title>AI Code Converter</title></head>
            <body>
                <h1>AI Code Converter API</h1>
                <p>Welcome to the AI Code Converter API!</p>
                <p><a href="/docs">View API Documentation</a></p>
                <p><a href="/health">Check System Health</a></p>
            </body>
        </html>
        """)


@app.get("/health", response_model=SystemStatus)
async def health_check():
    """Health check endpoint."""
    try:
        provider_status = await provider_manager.get_provider_status()
        available_providers = [name for name, status in provider_status.items() if status["available"]]
        
        stats = await conversion_service.get_statistics()
        
        return SystemStatus(
            status="healthy",
            version="1.0.0",
            uptime=time.time(),  # Simplified uptime
            active_conversions=stats["active_conversions"],
            total_conversions=stats["total_conversions"],
            available_providers=available_providers,
            system_load=0.0  # Placeholder
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/config", response_model=ApplicationConfig)
async def get_config():
    """Get application configuration."""
    try:
        # Language information
        languages = [
            LanguageInfo(
                name="Python",
                extensions=[".py", ".pyw"],
                syntax_highlighter="python",
                popular_frameworks=["Django", "Flask", "FastAPI", "Pandas"],
                package_managers=["pip", "conda", "poetry"]
            ),
            LanguageInfo(
                name="JavaScript",
                extensions=[".js", ".mjs"],
                syntax_highlighter="javascript",
                popular_frameworks=["React", "Vue", "Angular", "Node.js"],
                package_managers=["npm", "yarn", "pnpm"]
            ),
            LanguageInfo(
                name="TypeScript",
                extensions=[".ts", ".tsx"],
                syntax_highlighter="typescript",
                popular_frameworks=["React", "Angular", "Vue", "Nest.js"],
                package_managers=["npm", "yarn", "pnpm"]
            ),
            LanguageInfo(
                name="Java",
                extensions=[".java"],
                syntax_highlighter="java",
                popular_frameworks=["Spring", "Spring Boot", "Hibernate"],
                package_managers=["Maven", "Gradle"]
            ),
            # Add more languages as needed
        ]
        
        # AI provider configurations
        provider_status = await provider_manager.get_provider_status()
        ai_providers = []
        for name, status in provider_status.items():
            ai_providers.append(AIProviderConfig(
                name=name,
                enabled=status["enabled"],
                priority=status["priority"],
                max_tokens=2000,  # Default
                timeout=30,
                rate_limit=60
            ))
        
        return ApplicationConfig(
            supported_languages=languages,
            conversion_types=settings.conversion_types,
            style_guides=settings.style_guides,
            ai_providers=ai_providers,
            limits={
                "max_file_size_mb": settings.max_file_size_mb,
                "max_concurrent_conversions": settings.max_concurrent_conversions,
                "conversion_timeout_seconds": settings.conversion_timeout_seconds
            },
            features={
                "batch_conversion": True,
                "file_upload": True,
                "code_analysis": True,
                "syntax_highlighting": True,
                "export_options": True
            }
        )
    except Exception as e:
        logger.error("Failed to get config", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get configuration")


@app.post("/convert", response_model=ConversionResponse)
async def convert_code(
    request: ConversionRequest,
    background_tasks: BackgroundTasks,
    _: bool = Depends(rate_limit_check)
):
    """Convert code between programming languages."""
    try:
        logger.info("Code conversion requested", 
                   source_lang=request.source_language.value,
                   target_lang=request.target_language.value,
                   code_length=len(request.source_code))
        
        # Validate request
        if len(request.source_code) > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Code too large")
        
        # Perform conversion
        result = await conversion_service.convert_code(request)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Conversion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.post("/convert/batch", response_model=BatchConversionResponse)
async def convert_batch(
    request: BatchConversionRequest,
    _: bool = Depends(rate_limit_check)
):
    """Convert multiple code snippets in batch."""
    try:
        if len(request.conversions) > 10:
            raise HTTPException(status_code=400, detail="Too many conversions in batch (max 10)")
        
        logger.info("Batch conversion requested", count=len(request.conversions))
        
        result = await conversion_service.convert_batch(request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Batch conversion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Batch conversion failed: {str(e)}")


@app.post("/convert/file", response_model=ConversionResponse)
async def convert_file(
    file: UploadFile = File(...),
    target_language: str = "python",
    conversion_type: str = "direct",
    style_guide: str = "default",
    auto_detect_language: bool = True,
    _: bool = Depends(rate_limit_check)
):
    """Convert code from uploaded file."""
    try:
        # Validate file size
        if file.size and file.size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Create file upload request
        from models.schemas import LanguageEnum, ConversionTypeEnum, StyleGuideEnum
        
        file_request = FileUploadRequest(
            filename=file.filename,
            content=content_str,
            auto_detect_language=auto_detect_language,
            target_language=LanguageEnum(target_language),
            conversion_type=ConversionTypeEnum(conversion_type),
            style_guide=StyleGuideEnum(style_guide)
        )
        
        logger.info("File conversion requested", 
                   filename=file.filename,
                   target_lang=target_language,
                   file_size=len(content_str))
        
        result = await conversion_service.convert_file(file_request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File conversion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"File conversion failed: {str(e)}")


@app.get("/conversion/{conversion_id}", response_model=ConversionResponse)
async def get_conversion_status(conversion_id: str):
    """Get status of a conversion job."""
    try:
        result = await conversion_service.get_conversion_status(conversion_id)
        if not result:
            raise HTTPException(status_code=404, detail="Conversion not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get conversion status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get conversion status")


@app.delete("/conversion/{conversion_id}")
async def cancel_conversion(conversion_id: str):
    """Cancel an active conversion."""
    try:
        success = await conversion_service.cancel_conversion(conversion_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversion not found or already completed")
        return {"message": "Conversion cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel conversion", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel conversion")


@app.get("/conversion/{conversion_id}/export")
async def export_conversion(conversion_id: str, format: str = "file"):
    """Export conversion result."""
    try:
        file_path = await conversion_service.export_conversion(conversion_id, format)
        if not file_path:
            raise HTTPException(status_code=404, detail="Conversion not found or no result available")
        
        return FileResponse(
            file_path,
            media_type='application/octet-stream',
            filename=os.path.basename(file_path)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export conversion", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to export conversion")


@app.get("/history", response_model=ConversionHistory)
async def get_conversion_history(limit: int = 50):
    """Get conversion history."""
    try:
        conversions = await conversion_service.get_conversion_history(limit)
        stats = await conversion_service.get_statistics()
        
        return ConversionHistory(
            conversions=conversions,
            total_count=stats["total_conversions"],
            success_rate=stats["success_rate"]
        )
    except Exception as e:
        logger.error("Failed to get conversion history", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get conversion history")


@app.get("/statistics")
async def get_statistics():
    """Get conversion statistics."""
    try:
        stats = await conversion_service.get_statistics()
        return stats
    except Exception as e:
        logger.error("Failed to get statistics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@app.get("/providers/status")
async def get_provider_status():
    """Get AI provider status."""
    try:
        status = await provider_manager.get_provider_status()
        return status
    except Exception as e:
        logger.error("Failed to get provider status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get provider status")


@app.post("/analyze")
async def analyze_code(
    code: str,
    language: str,
    _: bool = Depends(rate_limit_check)
):
    """Analyze code for complexity, security, and performance issues."""
    try:
        if len(code) > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Code too large")
        
        analysis = await code_analyzer.analyze_code(code, language)
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Code analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")


@app.post("/detect-language")
async def detect_language(code: str, filename: Optional[str] = None):
    """Auto-detect programming language from code."""
    try:
        detected_language = code_analyzer.detect_language(code, filename)
        return {
            "detected_language": detected_language,
            "confidence": "high" if detected_language else "low"
        }
    except Exception as e:
        logger.error("Language detection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Language detection failed")


# Cache management endpoints
@app.post("/cache/clear")
async def clear_cache():
    """Clear all cached data."""
    try:
        await cache_service.clear_all()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error("Failed to clear cache", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        stats = await cache_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error("Failed to get cache stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get cache stats")


@app.post("/cache/invalidate/{cache_type}")
async def invalidate_cache(cache_type: str):
    """Invalidate specific cache type (conversions, analysis, providers)."""
    try:
        if cache_type == "conversions":
            await cache_service.invalidate_conversions()
        elif cache_type == "analysis":
            await cache_service.invalidate_analysis()
        elif cache_type == "providers":
            await cache_service.invalidate_providers()
        else:
            raise HTTPException(status_code=400, detail="Invalid cache type")
        
        return {"message": f"{cache_type} cache invalidated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to invalidate cache", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to invalidate cache")


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        log_level="info" if settings.debug else "warning"
    )