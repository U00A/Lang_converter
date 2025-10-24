# AI Code Converter - Windows PowerShell Setup Script
# This script sets up the development environment for the AI Code Converter on Windows

param(
    [switch]$Dev,
    [switch]$Test,
    [switch]$Health,
    [switch]$NoVenv,
    [switch]$Help
)

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check Python version
function Test-Python {
    Write-Status "Checking Python installation..."
    
    $pythonCmd = $null
    if (Test-Command "python") {
        $pythonCmd = "python"
    }
    elseif (Test-Command "python3") {
        $pythonCmd = "python3"
    }
    else {
        Write-Error "Python is not installed. Please install Python 3.8+ first."
        exit 1
    }
    
    # Check Python version
    $versionOutput = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $pythonVersion = [version]$versionOutput
    $requiredVersion = [version]"3.8"
    
    if ($pythonVersion -ge $requiredVersion) {
        Write-Success "Python $versionOutput found"
        return $pythonCmd
    }
    else {
        Write-Error "Python $versionOutput found, but Python 3.8+ is required"
        exit 1
    }
}

# Function to check pip
function Test-Pip {
    Write-Status "Checking pip installation..."
    
    if (Test-Command "pip") {
        Write-Success "pip found"
        return "pip"
    }
    elseif (Test-Command "pip3") {
        Write-Success "pip3 found"
        return "pip3"
    }
    else {
        Write-Error "pip is not installed. Please install pip first."
        exit 1
    }
}

# Function to create virtual environment
function New-VirtualEnvironment {
    param([string]$PythonCmd)
    
    Write-Status "Creating virtual environment..."
    
    if (Test-Path "venv") {
        Write-Warning "Virtual environment already exists. Skipping creation."
        return
    }
    
    & $PythonCmd -m venv venv
    Write-Success "Virtual environment created"
}

# Function to activate virtual environment
function Enable-VirtualEnvironment {
    Write-Status "Activating virtual environment..."
    
    $activateScript = "venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        Write-Success "Virtual environment activated"
    }
    else {
        Write-Error "Could not find virtual environment activation script"
        exit 1
    }
}

# Function to upgrade pip
function Update-Pip {
    Write-Status "Upgrading pip..."
    pip install --upgrade pip
    Write-Success "pip upgraded"
}

# Function to install dependencies
function Install-Dependencies {
    Write-Status "Installing Python dependencies..."
    
    if (-not (Test-Path "requirements.txt")) {
        Write-Error "requirements.txt not found"
        exit 1
    }
    
    pip install -r requirements.txt
    Write-Success "Dependencies installed"
}

# Function to install development dependencies
function Install-DevDependencies {
    Write-Status "Installing development dependencies..."
    
    $devPackages = @(
        "pytest-xdist",
        "pytest-mock", 
        "pytest-benchmark",
        "coverage",
        "bandit",
        "safety",
        "pre-commit"
    )
    
    pip install $devPackages
    Write-Success "Development dependencies installed"
}

# Function to setup pre-commit hooks
function Set-PreCommitHooks {
    Write-Status "Setting up pre-commit hooks..."
    
    if (Test-Command "pre-commit") {
        pre-commit install
        Write-Success "Pre-commit hooks installed"
    }
    else {
        Write-Warning "pre-commit not available, skipping hooks setup"
    }
}

# Function to create environment file
function New-EnvironmentFile {
    Write-Status "Creating environment file..."
    
    if (Test-Path ".env") {
        Write-Warning ".env file already exists. Skipping creation."
        return
    }
    
    $envContent = @"
# AI Code Converter - Development Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]

# AI Provider API Keys (Optional - app works without them)
# OPENAI_API_KEY=your-openai-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
# GOOGLE_API_KEY=your-google-api-key

# Database (Optional - uses SQLite by default)
# DATABASE_URL=sqlite:///./app.db
# REDIS_URL=redis://localhost:6379/0

# File Upload Limits
MAX_FILE_SIZE_MB=10
MAX_CONCURRENT_CONVERSIONS=5
CONVERSION_TIMEOUT_SECONDS=300

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Development Settings
CORS_ENABLED=true
STATIC_FILES_ENABLED=true
TEMPLATES_AUTO_RELOAD=true
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Success "Environment file created"
}

# Function to run tests
function Invoke-Tests {
    Write-Status "Running tests..."
    
    if (Test-Path "tests") {
        python -m pytest tests/ -v --tb=short
        Write-Success "Tests completed"
    }
    else {
        Write-Warning "No tests directory found, skipping tests"
    }
}

# Function to check application health
function Test-ApplicationHealth {
    Write-Status "Checking application health..."
    
    # Start the application in background
    $job = Start-Job -ScriptBlock { python app.py }
    
    # Wait a moment for the app to start
    Start-Sleep -Seconds 5
    
    # Check health endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "Application is healthy"
        }
        else {
            Write-Warning "Health check failed, but application might still be starting"
        }
    }
    catch {
        Write-Warning "Health check failed: $($_.Exception.Message)"
    }
    
    # Stop the application
    Stop-Job $job -Force
    Remove-Job $job -Force
}

# Function to display usage information
function Show-Usage {
    Write-Host "AI Code Converter Setup Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  -Dev          Install development dependencies" -ForegroundColor Gray
    Write-Host "  -Test         Run tests after setup" -ForegroundColor Gray
    Write-Host "  -Health       Check application health after setup" -ForegroundColor Gray
    Write-Host "  -NoVenv       Skip virtual environment creation" -ForegroundColor Gray
    Write-Host "  -Help         Show this help message" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\setup.ps1                    # Basic setup" -ForegroundColor Gray
    Write-Host "  .\setup.ps1 -Dev -Test         # Development setup with tests" -ForegroundColor Gray
    Write-Host "  .\setup.ps1 -NoVenv            # Setup without virtual environment" -ForegroundColor Gray
}

# Main setup function
function Main {
    if ($Help) {
        Show-Usage
        exit 0
    }
    
    Write-Host "🚀 AI Code Converter Setup Script" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check prerequisites
    $pythonCmd = Test-Python
    $pipCmd = Test-Pip
    
    # Setup virtual environment
    if (-not $NoVenv) {
        New-VirtualEnvironment -PythonCmd $pythonCmd
        Enable-VirtualEnvironment
        Update-Pip
    }
    
    # Install dependencies
    Install-Dependencies
    
    if ($Dev) {
        Install-DevDependencies
        Set-PreCommitHooks
    }
    
    # Create environment file
    New-EnvironmentFile
    
    # Run tests if requested
    if ($Test) {
        Invoke-Tests
    }
    
    # Check health if requested
    if ($Health) {
        Test-ApplicationHealth
    }
    
    Write-Host ""
    Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Activate the virtual environment:" -ForegroundColor Gray
    if (-not $NoVenv) {
        Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "2. (Optional) Add your AI provider API keys to .env file" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Start the development server:" -ForegroundColor Gray
    Write-Host "   python app.py" -ForegroundColor Yellow
    Write-Host "   # or" -ForegroundColor Gray
    Write-Host "   python deploy.py local" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "4. Open your browser and go to:" -ForegroundColor Gray
    Write-Host "   http://localhost:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "5. View API documentation at:" -ForegroundColor Gray
    Write-Host "   http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host ""
    
    if ($Dev) {
        Write-Host "Development tools installed:" -ForegroundColor White
        Write-Host "- pytest: Run tests with 'pytest'" -ForegroundColor Gray
        Write-Host "- pre-commit: Git hooks for code quality" -ForegroundColor Gray
        Write-Host "- coverage: Code coverage reports" -ForegroundColor Gray
        Write-Host "- bandit: Security linting" -ForegroundColor Gray
        Write-Host "- safety: Dependency vulnerability scanning" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Success "Ready to start coding! 🎯"
}

# Run main function
Main