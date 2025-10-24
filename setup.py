"""
Setup script for AI Code Converter.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-code-converter",
    version="1.0.0",
    author="AI Code Converter Team",
    author_email="team@codeconverter.ai",
    description="Advanced AI-powered code conversion between multiple programming languages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-code-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "sentry-sdk[fastapi]>=1.38.0",
            "structlog>=23.2.0",
        ],
        "deployment": [
            "gunicorn>=21.0.0",
            "uvicorn[standard]>=0.24.0",
            "docker>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "code-converter=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "static/*", "config/*.yml"],
    },
    keywords=[
        "code-conversion",
        "ai",
        "programming-languages",
        "fastapi",
        "machine-learning",
        "developer-tools",
        "code-translation",
        "openai",
        "anthropic",
        "huggingface",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/ai-code-converter/issues",
        "Source": "https://github.com/your-username/ai-code-converter",
        "Documentation": "https://ai-code-converter.readthedocs.io/",
        "Funding": "https://github.com/sponsors/your-username",
    },
)