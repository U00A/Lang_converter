# AI Code Converter - Deployment Guide

This guide covers various deployment options for the AI Code Converter application, from local development to production cloud deployments.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployments](#cloud-deployments)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Python 3.8+ installed
- Git installed
- (Optional) Docker installed for containerized deployment

### Automated Setup

**Linux/macOS:**
```bash
# Clone the repository
git clone <repository-url>
cd ai-code-converter

# Run setup script
chmod +x setup.sh
./setup.sh --dev --test
```

**Windows:**
```powershell
# Clone the repository
git clone <repository-url>
cd ai-code-converter

# Run setup script
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1 -Dev -Test
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Start the application
python app.py
```

## Local Development

### Development Server

Start the development server with hot reload:

```bash
# Using the deployment script
python deploy.py local --env development

# Or directly with uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Development Features

- **Hot Reload**: Code changes automatically restart the server
- **Debug Mode**: Detailed error messages and stack traces
- **CORS Enabled**: Frontend development from different ports
- **Verbose Logging**: Detailed logs for debugging

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

## Docker Deployment

### Building the Image

```bash
# Build the Docker image
docker build -t ai-code-converter:latest .

# Or using the deployment script
python deploy.py docker --env production
```

### Running with Docker

```bash
# Run the container
docker run -d \
  --name ai-code-converter \
  -p 8000:8000 \
  --env-file .env \
  ai-code-converter:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The `docker-compose.yml` includes:
- **Web Application**: Main FastAPI app
- **Redis**: Caching and session storage
- **PostgreSQL**: Database (optional)
- **Nginx**: Reverse proxy and static files
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboard

## Cloud Deployments

### Heroku

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy to Heroku**
   ```bash
   # Login to Heroku
   heroku login
   
   # Create app
   heroku create your-app-name
   
   # Set environment variables
   heroku config:set ENVIRONMENT=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set OPENAI_API_KEY=your-openai-key
   
   # Deploy
   git push heroku main
   
   # Open the app
   heroku open
   ```

3. **Heroku Configuration**
   - **Procfile**: Already included
   - **Runtime**: Python 3.9 specified in `runtime.txt`
   - **Add-ons**: Consider Redis and PostgreSQL add-ons

### Railway

1. **Connect Repository**
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository
   - Railway will auto-detect the Python app

2. **Environment Variables**
   Set in Railway dashboard:
   ```
   ENVIRONMENT=production
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   ```

3. **Custom Start Command**
   ```
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

### Render

1. **Create Web Service**
   - Go to [Render](https://render.com)
   - Create new Web Service
   - Connect your repository

2. **Build & Start Commands**
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   ```
   ENVIRONMENT=production
   PYTHON_VERSION=3.9.16
   SECRET_KEY=your-secret-key
   ```

### AWS (Advanced)

#### Using AWS App Runner

1. **Create apprunner.yaml**
   ```yaml
   version: 1.0
   runtime: python3
   build:
     commands:
       build:
         - pip install -r requirements.txt
   run:
     runtime-version: 3.9
     command: uvicorn app:app --host 0.0.0.0 --port 8000
     network:
       port: 8000
       env: PORT
   ```

2. **Deploy via Console**
   - Go to AWS App Runner
   - Create service from source code
   - Connect your repository

#### Using ECS (Container)

1. **Push to ECR**
   ```bash
   # Build and tag
   docker build -t ai-code-converter .
   docker tag ai-code-converter:latest 123456789012.dkr.ecr.region.amazonaws.com/ai-code-converter:latest
   
   # Push to ECR
   aws ecr get-login-password --region region | docker login --username AWS --password-stdin 123456789012.dkr.ecr.region.amazonaws.com
   docker push 123456789012.dkr.ecr.region.amazonaws.com/ai-code-converter:latest
   ```

2. **Create ECS Service**
   - Use the provided `ecs-task-definition.json`
   - Configure load balancer and auto-scaling

### Google Cloud Platform

#### Using Cloud Run

1. **Deploy to Cloud Run**
   ```bash
   # Build and deploy
   gcloud run deploy ai-code-converter \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Set Environment Variables**
   ```bash
   gcloud run services update ai-code-converter \
     --set-env-vars ENVIRONMENT=production,SECRET_KEY=your-secret-key \
     --region us-central1
   ```

## Environment Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `SECRET_KEY` | Application secret key | - | Yes |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `OPENAI_API_KEY` | OpenAI API key | - | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | No |
| `GOOGLE_API_KEY` | Google API key | - | No |
| `DATABASE_URL` | Database connection URL | SQLite | No |
| `REDIS_URL` | Redis connection URL | - | No |
| `MAX_FILE_SIZE_MB` | Maximum upload size | `10` | No |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` | No |

### Production Environment

Create `.env.production`:

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Security
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_ORIGINS=["https://yourdomain.com"]

# AI Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port/0

# Performance
MAX_CONCURRENT_CONVERSIONS=10
CONVERSION_TIMEOUT_SECONDS=300

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true
```

### Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Secret Key**: Use a strong, random secret key
3. **CORS**: Restrict allowed origins in production
4. **HTTPS**: Always use HTTPS in production
5. **Rate Limiting**: Configure appropriate rate limits
6. **Input Validation**: All inputs are validated by Pydantic

## Monitoring & Maintenance

### Health Checks

The application provides several health check endpoints:

- **Basic Health**: `GET /health`
- **Detailed Status**: `GET /api/v1/status`
- **Provider Status**: `GET /providers/status`

### Logging

Logs are structured using `structlog`:

```python
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Logs include request IDs, user context, and performance metrics
```

### Metrics

Prometheus metrics are available at `/metrics`:

- Request count and duration
- Conversion success/failure rates
- AI provider response times
- System resource usage

### Monitoring Setup

1. **Prometheus Configuration**
   ```yaml
   scrape_configs:
     - job_name: 'ai-code-converter'
       static_configs:
         - targets: ['localhost:8000']
   ```

2. **Grafana Dashboard**
   - Import the provided dashboard JSON
   - Configure alerts for high error rates
   - Monitor conversion success rates

### Backup & Recovery

1. **Database Backups**
   ```bash
   # PostgreSQL
   pg_dump $DATABASE_URL > backup.sql
   
   # SQLite
   sqlite3 app.db ".backup backup.db"
   ```

2. **Configuration Backups**
   - Store environment files securely
   - Version control configuration changes
   - Document deployment procedures

## Troubleshooting

### Common Issues

#### Application Won't Start

1. **Check Python Version**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Check Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Environment Variables**
   ```bash
   python -c "from config.settings import settings; print(settings)"
   ```

#### Conversion Failures

1. **Check AI Provider Status**
   ```bash
   curl http://localhost:8000/providers/status
   ```

2. **Check API Keys**
   - Verify API keys are set correctly
   - Check API key permissions and quotas

3. **Check Logs**
   ```bash
   # View application logs
   docker logs ai-code-converter
   
   # Or check log files
   tail -f logs/app.log
   ```

#### Performance Issues

1. **Check System Resources**
   ```bash
   # CPU and memory usage
   htop
   
   # Disk space
   df -h
   ```

2. **Check Database Performance**
   ```sql
   -- PostgreSQL
   SELECT * FROM pg_stat_activity;
   
   -- Check slow queries
   SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC;
   ```

3. **Optimize Configuration**
   - Increase worker processes
   - Tune database connections
   - Configure caching

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG=true
export LOG_LEVEL=debug
python app.py
```

### Getting Help

1. **Check Documentation**: Review this guide and API docs
2. **Check Logs**: Application logs contain detailed error information
3. **Health Checks**: Use health endpoints to diagnose issues
4. **Community**: Check GitHub issues and discussions

## Performance Optimization

### Production Tuning

1. **Worker Processes**
   ```bash
   # Use multiple workers for better performance
   gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Database Optimization**
   - Use connection pooling
   - Configure appropriate timeouts
   - Index frequently queried columns

3. **Caching**
   - Enable Redis for session storage
   - Cache conversion results
   - Use CDN for static files

4. **Load Balancing**
   - Use nginx or cloud load balancer
   - Configure health checks
   - Implement graceful shutdowns

### Scaling Strategies

1. **Horizontal Scaling**
   - Deploy multiple instances
   - Use load balancer
   - Share state via Redis/database

2. **Vertical Scaling**
   - Increase CPU/memory
   - Optimize database queries
   - Profile application performance

3. **Auto-scaling**
   - Configure based on CPU/memory usage
   - Scale based on request queue length
   - Set appropriate min/max instances

---

This deployment guide covers the most common deployment scenarios. For specific requirements or advanced configurations, refer to the platform-specific documentation or contact support.