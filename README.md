# 🤖 AI Code Converter

A comprehensive, production-ready web application that converts code between multiple programming languages using advanced AI models. Built with FastAPI, featuring a modern responsive frontend, and supporting 15+ programming languages with enterprise-grade features.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🔄 Core Conversion Capabilities
- **15+ Programming Languages**: Python, JavaScript, TypeScript, Java, C++, C#, Go, Ruby, PHP, Swift, Kotlin, Rust, Scala, R, MATLAB, SQL, Bash
- **Multiple Conversion Types**: Direct translation, idiomatic conversion, modern syntax upgrade, framework migration
- **Style Guide Support**: Google, Airbnb, PEP8, Black, Prettier, and more
- **Intelligent Fallback**: Multiple AI providers with automatic failover
- **Auto-Language Detection**: Smart detection from code content and file extensions

### 🧠 AI Integration
- **Multi-Provider Support**: OpenAI GPT-4o, Anthropic Claude, Google Gemini, HuggingFace
- **Free Alternatives**: Local HuggingFace models for offline processing
- **Smart Provider Selection**: Automatic selection based on availability, performance, and cost
- **Cost Optimization**: Efficient token usage, caching, and provider rotation
- **Confidence Scoring**: AI-generated confidence metrics for conversion quality

### 📊 Advanced Analysis
- **Code Complexity Analysis**: Cyclomatic complexity, maintainability index, lines of code
- **Security Scanning**: Vulnerability detection, hardcoded credentials, injection risks
- **Performance Analysis**: Bottleneck identification, optimization suggestions, algorithmic complexity
- **Dependency Mapping**: Automatic library detection, framework identification, migration suggestions

### 🎨 Modern UI/UX
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Dark/Light Theme**: System preference detection with manual toggle
- **Syntax Highlighting**: Real-time highlighting for all supported languages using Prism.js
- **Drag & Drop**: File upload with auto-language detection and validation
- **Split-Pane Layout**: Resizable side-by-side code comparison
- **Progressive Web App**: Offline capability and native app-like experience

### 🚀 Production Features
- **Batch Processing**: Convert multiple files simultaneously with parallel processing
- **Export Options**: Download as files, copy to clipboard, shareable links
- **Conversion History**: Persistent history with search, filtering, and favorites
- **Real-time Updates**: WebSocket integration for live conversion progress
- **Rate Limiting**: Configurable abuse prevention and quota management
- **Monitoring**: Comprehensive Prometheus metrics, health checks, and alerting
- **Caching**: Redis-based caching for improved performance
- **Background Jobs**: Celery integration for long-running conversions

## 🚀 Quick Start

### One-Command Setup

**Linux/macOS:**
```bash
git clone <repository-url> && cd ai-code-converter && chmod +x setup.sh && ./setup.sh --dev
```

**Windows PowerShell:**
```powershell
git clone <repository-url>; cd ai-code-converter; Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; .\setup.ps1 -Dev
```

### Manual Setup

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd ai-code-converter
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Optional: Add your AI provider API keys to .env
   ```

3. **Start the application**
   ```bash
   python app.py
   # or
   python deploy.py local
   ```

4. **Access the application**
   - 🌐 **Web Interface**: http://localhost:8000
   - 📚 **API Docs**: http://localhost:8000/docs
   - 💚 **Health Check**: http://localhost:8000/health

### Docker Quick Start

```bash
# Clone and start with Docker
git clone <repository-url>
cd ai-code-converter
docker-compose up -d

# Access at http://localhost:8000
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Python 3.11+**: Latest Python features
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM with async support
- **Redis**: Caching and session management
- **Celery**: Background task processing

### AI & Analysis
- **OpenAI API**: GPT-4o for high-quality conversions
- **Anthropic Claude**: Alternative AI provider
- **HuggingFace**: Local model support
- **Pygments**: Syntax highlighting
- **Radon**: Code complexity analysis

### Frontend
- **Modern HTML5**: Semantic markup
- **Tailwind CSS**: Utility-first styling
- **Vanilla JavaScript**: No framework dependencies
- **Prism.js**: Syntax highlighting
- **Responsive Design**: Mobile-first approach

### Infrastructure
- **Docker**: Containerized deployment
- **PostgreSQL**: Production database
- **Nginx**: Reverse proxy and load balancing
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend development)
- Docker & Docker Compose (for containerized deployment)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Converter
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access services**
   - Application: http://localhost:8000
   - Grafana: http://localhost:3000 (admin/admin123)
   - Prometheus: http://localhost:9090

## 📖 API Documentation

### Core Endpoints

#### Convert Code
```http
POST /convert
Content-Type: application/json

{
  "source_code": "def hello():\n    print('Hello, World!')",
  "source_language": "python",
  "target_language": "javascript",
  "conversion_type": "idiomatic",
  "style_guide": "airbnb",
  "include_comments": true
}
```

#### Batch Conversion
```http
POST /convert/batch
Content-Type: application/json

{
  "conversions": [
    {
      "source_code": "...",
      "source_language": "python",
      "target_language": "javascript"
    }
  ],
  "parallel_processing": true
}
```

#### File Upload
```http
POST /convert/file
Content-Type: multipart/form-data

file: <code-file>
target_language: javascript
auto_detect_language: true
```

#### Code Analysis
```http
POST /analyze
Content-Type: application/json

{
  "code": "def complex_function():\n    # code here",
  "language": "python"
}
```

### Response Format

```json
{
  "id": "conversion-uuid",
  "status": "completed",
  "request": { /* original request */ },
  "result": {
    "converted_code": "function hello() {\n    console.log('Hello, World!');\n}",
    "confidence_score": 95.0,
    "warnings": [],
    "suggestions": ["Consider using arrow functions"],
    "execution_time": 2.3,
    "tokens_used": 150
  },
  "analysis": {
    "complexity_score": 25.0,
    "maintainability_index": 85.0,
    "lines_of_code": 10,
    "dependencies": ["console"],
    "security_issues": [],
    "performance_issues": []
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite+aiosqlite:///./code_converter.db
REDIS_URL=redis://localhost:6379/0

# AI Providers (Optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
XAI_API_KEY=your-xai-key
HUGGINGFACE_API_KEY=your-hf-key

# Limits
MAX_FILE_SIZE_MB=10
MAX_CONCURRENT_CONVERSIONS=5
CONVERSION_TIMEOUT_SECONDS=300

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
```

### Supported Languages

| Language   | Extensions | Style Guides | Frameworks |
|------------|------------|--------------|------------|
| Python     | .py, .pyw  | PEP8, Black  | Django, Flask, FastAPI |
| JavaScript | .js, .mjs  | Airbnb, Standard, Prettier | React, Vue, Node.js |
| TypeScript | .ts, .tsx  | Prettier, ESLint | Angular, React |
| Java       | .java      | Google, Checkstyle | Spring, Spring Boot |
| C++        | .cpp, .cc  | Google, LLVM | - |
| C#         | .cs        | Microsoft    | .NET, ASP.NET |
| Go         | .go        | gofmt        | Gin, Echo |
| Ruby       | .rb        | RuboCop      | Rails, Sinatra |
| PHP        | .php       | PSR-12       | Laravel, Symfony |
| Swift      | .swift     | SwiftLint    | iOS, macOS |
| Kotlin     | .kt        | ktlint       | Android, Spring |
| Rust       | .rs        | rustfmt      | Actix, Rocket |

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# Coverage report
pytest --cov=. --cov-report=html
```

### Test Coverage
- Unit Tests: 85%+
- Integration Tests: 70%+
- End-to-End Tests: 60%+

## 📈 Monitoring & Analytics

### Metrics Collected
- Conversion success/failure rates
- Average conversion time by language pair
- AI provider performance and costs
- User engagement and retention
- System resource usage

### Health Checks
- `/health` - Basic health status
- `/health/detailed` - Comprehensive system status
- Database connectivity
- AI provider availability
- Cache system status

## 🔒 Security

### Security Features
- Input validation and sanitization
- Rate limiting and abuse prevention
- API key encryption and rotation
- CORS configuration
- Security headers
- Dependency vulnerability scanning

### Security Best Practices
- Regular security audits
- Automated dependency updates
- Secure coding guidelines
- Error handling without information leakage
- Logging and monitoring

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export ENVIRONMENT=production
   export DEBUG=false
   # Set all required API keys and database URLs
   ```

2. **Database Migration**
   ```bash
   alembic upgrade head
   ```

3. **Docker Production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Kubernetes Deployment**
   ```bash
   kubectl apply -f k8s/
   ```

### Scaling Considerations
- Horizontal scaling with load balancers
- Database read replicas
- Redis clustering
- CDN for static assets
- Auto-scaling based on metrics

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

### Code Style
- Python: Black, isort, flake8
- JavaScript: Prettier, ESLint
- Documentation: Clear docstrings and comments
- Type hints: Required for Python code

### Commit Convention
```
feat: add new conversion type
fix: resolve memory leak in batch processing
docs: update API documentation
test: add integration tests for file upload
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude
- HuggingFace for open-source models
- FastAPI team for the excellent framework
- All contributors and testers

---
