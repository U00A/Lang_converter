#!/usr/bin/env python3
"""
Deployment script for AI Code Converter.
Supports multiple deployment targets: local, docker, cloud platforms.
"""

import os
import sys
import subprocess
import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class DeploymentManager:
    """Manages deployment of the AI Code Converter application."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.config = self.load_deployment_config()
    
    def load_deployment_config(self) -> Dict:
        """Load deployment configuration."""
        config_file = self.project_root / "deployment" / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        
        # Default configuration
        return {
            "app_name": "ai-code-converter",
            "version": "1.0.0",
            "python_version": "3.9",
            "port": 8000,
            "workers": 4,
            "timeout": 120,
            "max_requests": 1000,
            "environments": {
                "development": {
                    "debug": True,
                    "reload": True,
                    "log_level": "debug"
                },
                "production": {
                    "debug": False,
                    "reload": False,
                    "log_level": "info"
                }
            }
        }
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            print("❌ Python 3.8+ is required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Check required files
        required_files = [
            "app.py",
            "requirements.txt",
            "config/settings.py",
            "services/__init__.py",
            "models/__init__.py"
        ]
        
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                print(f"❌ Missing required file: {file_path}")
                return False
        print("✅ All required files present")
        
        return True
    
    def install_dependencies(self, upgrade: bool = False) -> bool:
        """Install Python dependencies."""
        print("📦 Installing dependencies...")
        
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            if upgrade:
                cmd.append("--upgrade")
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
            
            print("✅ Dependencies installed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def setup_environment(self, env_name: str = "development") -> bool:
        """Setup environment variables."""
        print(f"🔧 Setting up {env_name} environment...")
        
        env_file = self.project_root / f".env.{env_name}"
        if not env_file.exists():
            # Create default environment file
            env_content = self.generate_env_content(env_name)
            with open(env_file, 'w') as f:
                f.write(env_content)
            print(f"✅ Created {env_file}")
        
        # Copy to .env for current use
        shutil.copy(env_file, self.project_root / ".env")
        print("✅ Environment configured")
        return True
    
    def generate_env_content(self, env_name: str) -> str:
        """Generate environment file content."""
        env_config = self.config["environments"].get(env_name, {})
        
        content = f"""# AI Code Converter - {env_name.title()} Environment
ENVIRONMENT={env_name}
DEBUG={str(env_config.get('debug', False)).lower()}
LOG_LEVEL={env_config.get('log_level', 'info')}

# Server Configuration
HOST=0.0.0.0
PORT={self.config.get('port', 8000)}
RELOAD={str(env_config.get('reload', False)).lower()}

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# AI Provider API Keys (Optional - app works without them)
# OPENAI_API_KEY=your-openai-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
# GOOGLE_API_KEY=your-google-api-key

# Database (Optional - uses SQLite by default)
# DATABASE_URL=postgresql://user:password@localhost/dbname
# REDIS_URL=redis://localhost:6379/0

# File Upload Limits
MAX_FILE_SIZE_MB=10
MAX_CONCURRENT_CONVERSIONS=5
CONVERSION_TIMEOUT_SECONDS=300

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Monitoring (Optional)
# SENTRY_DSN=your-sentry-dsn
# PROMETHEUS_ENABLED=true
"""
        return content
    
    def run_tests(self) -> bool:
        """Run application tests."""
        print("🧪 Running tests...")
        
        # Check if pytest is available
        try:
            result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️  pytest not available, skipping tests")
                return True
        except:
            print("⚠️  pytest not available, skipping tests")
            return True
        
        # Run tests
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/", "-v", "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}")
                return False
            
            print("✅ All tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def deploy_local(self, env_name: str = "development") -> bool:
        """Deploy application locally."""
        print("🚀 Deploying locally...")
        
        if not self.setup_environment(env_name):
            return False
        
        # Start the application
        try:
            env_config = self.config["environments"].get(env_name, {})
            cmd = [
                sys.executable, "-m", "uvicorn", "app:app",
                "--host", "0.0.0.0",
                "--port", str(self.config.get('port', 8000))
            ]
            
            if env_config.get('reload', False):
                cmd.append("--reload")
            
            if env_config.get('log_level'):
                cmd.extend(["--log-level", env_config['log_level']])
            
            print(f"Starting server with command: {' '.join(cmd)}")
            print(f"🌐 Application will be available at: http://localhost:{self.config.get('port', 8000)}")
            
            # Run the server
            subprocess.run(cmd, cwd=self.project_root)
            return True
            
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
            return True
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def build_docker(self) -> bool:
        """Build Docker image."""
        print("🐳 Building Docker image...")
        
        try:
            # Build the image
            cmd = [
                "docker", "build", 
                "-t", f"{self.config['app_name']}:{self.config['version']}",
                "-t", f"{self.config['app_name']}:latest",
                "."
            ]
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Docker build failed: {result.stderr}")
                return False
            
            print("✅ Docker image built successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error building Docker image: {e}")
            return False
    
    def deploy_docker(self, env_name: str = "production") -> bool:
        """Deploy using Docker."""
        print("🐳 Deploying with Docker...")
        
        if not self.build_docker():
            return False
        
        if not self.setup_environment(env_name):
            return False
        
        try:
            # Stop existing container
            subprocess.run(["docker", "stop", self.config['app_name']], 
                         capture_output=True)
            subprocess.run(["docker", "rm", self.config['app_name']], 
                         capture_output=True)
            
            # Run new container
            cmd = [
                "docker", "run", "-d",
                "--name", self.config['app_name'],
                "-p", f"{self.config['port']}:{self.config['port']}",
                "--env-file", ".env",
                f"{self.config['app_name']}:latest"
            ]
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to start Docker container: {result.stderr}")
                return False
            
            print(f"✅ Docker container started successfully")
            print(f"🌐 Application available at: http://localhost:{self.config['port']}")
            return True
            
        except Exception as e:
            print(f"❌ Error deploying with Docker: {e}")
            return False
    
    def deploy_cloud(self, platform: str) -> bool:
        """Deploy to cloud platform."""
        print(f"☁️  Deploying to {platform}...")
        
        if platform.lower() == "heroku":
            return self.deploy_heroku()
        elif platform.lower() == "railway":
            return self.deploy_railway()
        elif platform.lower() == "render":
            return self.deploy_render()
        else:
            print(f"❌ Unsupported platform: {platform}")
            return False
    
    def deploy_heroku(self) -> bool:
        """Deploy to Heroku."""
        print("🚂 Deploying to Heroku...")
        
        # Check if Heroku CLI is installed
        try:
            subprocess.run(["heroku", "--version"], capture_output=True, check=True)
        except:
            print("❌ Heroku CLI not found. Please install it first.")
            return False
        
        # Create Procfile if it doesn't exist
        procfile = self.project_root / "Procfile"
        if not procfile.exists():
            with open(procfile, 'w') as f:
                f.write(f"web: uvicorn app:app --host 0.0.0.0 --port $PORT\n")
            print("✅ Created Procfile")
        
        print("📝 Manual steps required:")
        print("1. heroku create your-app-name")
        print("2. git add .")
        print("3. git commit -m 'Deploy to Heroku'")
        print("4. git push heroku main")
        print("5. heroku config:set ENVIRONMENT=production")
        
        return True
    
    def deploy_railway(self) -> bool:
        """Deploy to Railway."""
        print("🚄 Deploying to Railway...")
        
        # Create railway.json if it doesn't exist
        railway_config = self.project_root / "railway.json"
        if not railway_config.exists():
            config = {
                "build": {
                    "builder": "NIXPACKS"
                },
                "deploy": {
                    "startCommand": f"uvicorn app:app --host 0.0.0.0 --port $PORT",
                    "healthcheckPath": "/health"
                }
            }
            with open(railway_config, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Created railway.json")
        
        print("📝 Manual steps required:")
        print("1. Connect your GitHub repository to Railway")
        print("2. Set environment variables in Railway dashboard")
        print("3. Deploy will happen automatically on git push")
        
        return True
    
    def deploy_render(self) -> bool:
        """Deploy to Render."""
        print("🎨 Deploying to Render...")
        
        # Create render.yaml if it doesn't exist
        render_config = self.project_root / "render.yaml"
        if not render_config.exists():
            config = {
                "services": [
                    {
                        "type": "web",
                        "name": self.config['app_name'],
                        "env": "python",
                        "buildCommand": "pip install -r requirements.txt",
                        "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
                        "healthCheckPath": "/health",
                        "envVars": [
                            {"key": "ENVIRONMENT", "value": "production"},
                            {"key": "PYTHON_VERSION", "value": "3.9.16"}
                        ]
                    }
                ]
            }
            with open(render_config, 'w') as f:
                import yaml
                yaml.dump(config, f, default_flow_style=False)
            print("✅ Created render.yaml")
        
        print("📝 Manual steps required:")
        print("1. Connect your GitHub repository to Render")
        print("2. Create a new Web Service")
        print("3. Set environment variables in Render dashboard")
        
        return True
    
    def health_check(self, url: str = None) -> bool:
        """Perform health check on deployed application."""
        if not url:
            url = f"http://localhost:{self.config['port']}/health"
        
        print(f"🏥 Performing health check: {url}")
        
        try:
            import requests
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False


def main():
    """Main deployment script."""
    parser = argparse.ArgumentParser(description="AI Code Converter Deployment Script")
    parser.add_argument("action", choices=[
        "install", "test", "local", "docker", "cloud", "health"
    ], help="Deployment action")
    parser.add_argument("--env", default="development", 
                       choices=["development", "production"],
                       help="Environment name")
    parser.add_argument("--platform", choices=["heroku", "railway", "render"],
                       help="Cloud platform for deployment")
    parser.add_argument("--upgrade", action="store_true",
                       help="Upgrade dependencies")
    parser.add_argument("--url", help="URL for health check")
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    deployer = DeploymentManager()
    
    # Check prerequisites for most actions
    if args.action != "health" and not deployer.check_prerequisites():
        sys.exit(1)
    
    success = False
    
    if args.action == "install":
        success = deployer.install_dependencies(upgrade=args.upgrade)
    
    elif args.action == "test":
        success = deployer.install_dependencies() and deployer.run_tests()
    
    elif args.action == "local":
        success = (deployer.install_dependencies() and 
                  deployer.deploy_local(args.env))
    
    elif args.action == "docker":
        success = (deployer.install_dependencies() and 
                  deployer.deploy_docker(args.env))
    
    elif args.action == "cloud":
        if not args.platform:
            print("❌ --platform is required for cloud deployment")
            sys.exit(1)
        success = deployer.deploy_cloud(args.platform)
    
    elif args.action == "health":
        success = deployer.health_check(args.url)
    
    if success:
        print("🎉 Deployment completed successfully!")
        sys.exit(0)
    else:
        print("💥 Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()