"""
DEDAN Mine - Setup Configuration
Production-ready setup with safe changelog reading
"""

import os
from setuptools import setup, find_packages

def get_version():
    """Safely get version from CHANGELOG.txt"""
    try:
        with open('CHANGELOG.txt', 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('v'):
                return first_line.split(' - ')[0]
    except FileNotFoundError:
        print("CHANGELOG.txt not found, using default version")
    except Exception as e:
        print(f"Error reading CHANGELOG.txt: {e}")
    
    return "v1.0.0"

def get_long_description():
    """Safely get long description from README"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "DEDAN Mine - World's most advanced AI-powered mining transaction marketplace"
    except Exception as e:
        print(f"Error reading README.md: {e}")
        return "DEDAN Mine - World's most advanced AI-powered mining transaction marketplace"

setup(
    name="dedan-mine",
    version=get_version(),
    description="World's most advanced AI-powered mining transaction marketplace",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="DEDAN Mine Team",
    author_email="contact@dedanmine.io",
    url="https://github.com/Dan12-dev-ai/worldmine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "google-generativeai",
        "anthropic",
        "langchain",
        "langchain-openai",
        "langgraph",
        "tavily-python",
        "supabase",
        "python-dotenv",
        "pydantic-settings",
        "sqlalchemy",
        "psycopg2-binary",
        "redis",
        "numpy",
        "opencv-python",
        "pillow",
        "websockets",
        "python-multipart",
        "asyncpg",
        "aioredis",
        "aiohttp",
        "sentry-sdk[fastapi]",
        "aiofiles",
        "cryptography",
        "pyjwt",
        "passlib",
        "bcrypt",
        "email-validator",
        "python-jose",
        "alembic",
        "httpx",
        "requests",
        "beautifulsoup4",
        "selenium",
        "celery",
        "kombu",
        "flower",
        "prometheus-client",
        "elasticsearch",
        "kafka-python",
        "pika",
        "web3",
        "eth-account",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "black",
        "flake8",
        "mypy",
        "webauthn",
        "py-webauthn",
        "liboqs-python",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
        "production": [
            "sentry-sdk[fastapi]",
            "prometheus-client",
            "elasticsearch",
        ],
    },
    entry_points={
        "console_scripts": [
            "dedan-mine=backend.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
)
