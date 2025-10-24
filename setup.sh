#!/bin/bash

# AI Code Converter - Setup Script
# This script sets up the development environment for the AI Code Converter

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    print_status "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python $PYTHON_VERSION found, but Python 3.8+ is required"
        exit 1
    fi
}

# Function to check pip
check_pip() {
    print_status "Checking pip installation..."
    
    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        print_error "pip is not installed. Please install pip first."
        exit 1
    fi
    
    print_success "pip found"
}

# Function to create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
        return
    fi
    
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_success "Virtual environment activated (Windows)"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Function to upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Function to install development dependencies
install_dev_dependencies() {
    print_status "Installing development dependencies..."
    
    # Install additional development tools
    pip install \
        pytest-xdist \
        pytest-mock \
        pytest-benchmark \
        coverage \
        bandit \
        safety \
        pre-commit
    
    print_success "Development dependencies installed"
}

# Function to setup pre-commit hooks
setup_precommit() {
    print_status "Setting up pre-commit hooks..."
    
    if command_exists pre-commit; then
        pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_warning "pre-commit not available, skipping hooks setup"
    fi
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment file..."
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists. Skipping creation."
        return
    fi
    
    cat > .env << EOF
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
EOF
    
    print_success "Environment file created"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if [ -d "tests" ]; then
        python -m pytest tests/ -v --tb=short
        print_success "Tests completed"
    else
        print_warning "No tests directory found, skipping tests"
    fi
}

# Function to check application health
check_health() {
    print_status "Checking application health..."
    
    # Start the application in background
    python app.py &
    APP_PID=$!
    
    # Wait a moment for the app to start
    sleep 5
    
    # Check health endpoint
    if command_exists curl; then
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Application is healthy"
        else
            print_warning "Health check failed, but application might still be starting"
        fi
    else
        print_warning "curl not available, skipping health check"
    fi
    
    # Stop the application
    kill $APP_PID 2>/dev/null || true
}

# Function to display usage information
show_usage() {
    echo "AI Code Converter Setup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev          Install development dependencies"
    echo "  --test         Run tests after setup"
    echo "  --health       Check application health after setup"
    echo "  --no-venv      Skip virtual environment creation"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Basic setup"
    echo "  $0 --dev --test       # Development setup with tests"
    echo "  $0 --no-venv          # Setup without virtual environment"
}

# Main setup function
main() {
    echo "🚀 AI Code Converter Setup Script"
    echo "=================================="
    echo ""
    
    # Parse command line arguments
    INSTALL_DEV=false
    RUN_TESTS=false
    CHECK_HEALTH=false
    USE_VENV=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                INSTALL_DEV=true
                shift
                ;;
            --test)
                RUN_TESTS=true
                shift
                ;;
            --health)
                CHECK_HEALTH=true
                shift
                ;;
            --no-venv)
                USE_VENV=false
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    check_python
    check_pip
    
    # Setup virtual environment
    if [ "$USE_VENV" = true ]; then
        create_venv
        activate_venv
        upgrade_pip
    fi
    
    # Install dependencies
    install_dependencies
    
    if [ "$INSTALL_DEV" = true ]; then
        install_dev_dependencies
        setup_precommit
    fi
    
    # Create environment file
    create_env_file
    
    # Run tests if requested
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    # Check health if requested
    if [ "$CHECK_HEALTH" = true ]; then
        check_health
    fi
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    if [ "$USE_VENV" = true ]; then
        echo "   source venv/bin/activate  # Linux/Mac"
        echo "   venv\\Scripts\\activate     # Windows"
    fi
    echo ""
    echo "2. (Optional) Add your AI provider API keys to .env file"
    echo ""
    echo "3. Start the development server:"
    echo "   python app.py"
    echo "   # or"
    echo "   python deploy.py local"
    echo ""
    echo "4. Open your browser and go to:"
    echo "   http://localhost:8000"
    echo ""
    echo "5. View API documentation at:"
    echo "   http://localhost:8000/docs"
    echo ""
    
    if [ "$INSTALL_DEV" = true ]; then
        echo "Development tools installed:"
        echo "- pytest: Run tests with 'pytest'"
        echo "- pre-commit: Git hooks for code quality"
        echo "- coverage: Code coverage reports"
        echo "- bandit: Security linting"
        echo "- safety: Dependency vulnerability scanning"
        echo ""
    fi
    
    print_success "Ready to start coding! 🎯"
}

# Run main function
main "$@"