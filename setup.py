"""
DEDAN Mine - Setup Configuration
Production-ready setup with safe changelog reading
"""

import os
from setuptools import setup, find_packages

def get_version():
    """Safely get version from CHANGELOG.txt"""
    import os
    from pathlib import Path
    
    # Try multiple possible locations for CHANGELOG.txt
    changelog_paths = [
        'CHANGELOG.txt',
        './CHANGELOG.txt',
        Path(__file__).parent / 'CHANGELOG.txt',
        Path(__file__).parent / 'backend' / 'CHANGELOG.txt'
    ]
    
    for changelog_path in changelog_paths:
        try:
            if isinstance(changelog_path, str):
                changelog_path = Path(changelog_path)
            
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('v'):
                        return first_line.split(' - ')[0]
        except (FileNotFoundError, OSError, Exception):
            continue
    
    # If no changelog found, use default version
    return "1.0.0"

def get_long_description():
    """Safely get long description from README"""
    from pathlib import Path
    
    # Try multiple possible locations for README.md
    readme_paths = [
        'README.md',
        './README.md',
        Path(__file__).parent / 'README.md'
    ]
    
    for readme_path in readme_paths:
        try:
            if isinstance(readme_path, str):
                readme_path = Path(readme_path)
            
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except (FileNotFoundError, OSError, Exception):
            continue
    
    # If no README found, use default description
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
        # REMOVED: web3 (build issues)
        # REMOVED: eth-account (build issues)
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
