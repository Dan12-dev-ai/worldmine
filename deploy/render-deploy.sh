#!/bin/bash

# DEDAN Mine - Render Backend Deployment Script
# Deploys FastAPI backend with PostgreSQL database to Render

set -e

echo "🚀 DEDAN Mine - Render Backend Deployment"
echo "=================================="

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "📦 Installing Render CLI..."
    curl -s https://render.com/download/render.sh | bash
fi

# Check if we're in the backend directory
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Navigate to backend directory
cd backend

# Create render.yaml if it doesn't exist
if [ ! -f "render.yaml" ]; then
    echo "📄 Creating render.yaml configuration..."
    cat > render.yaml << 'EOF'
services:
  # Main Backend API
  - type: web
    name: dedan-mine-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0 --port \$PORT
    healthCheckPath: /health
    healthCheckTimeout: 30
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        value: \${DATABASE_URL}
      - key: REDIS_URL
        value: \${REDIS_URL}
      - key: CHAPA_PUBLIC_KEY
        value: \${CHAPA_PUBLIC_KEY}
      - key: CHAPA_SECRET_KEY
        value: \${CHAPA_SECRET_KEY}
      - key: PAYONEER_CLIENT_ID
        value: \${PAYONEER_CLIENT_ID}
      - key: PAYONEER_CLIENT_SECRET
        value: \${PAYONEER_CLIENT_SECRET}
      - key: PAYONEER_PARTNER_ID
        value: \${PAYONEER_PARTNER_ID}
      - key: GROQ_API_KEY
        value: \${GROQ_API_KEY}
      - key: BINANCE_API_KEY
        value: \${BINANCE_API_KEY}
      - key: BINANCE_SECRET_KEY
        value: \${BINANCE_SECRET_KEY}
      - key: SECRET_KEY
        value: \${SECRET_KEY}
      - key: ENCRYPTION_KEY
        value: \${ENCRYPTION_KEY}

  # Consumer Protection API
  - type: web
    name: dedan-mine-protection
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn api.consumer_protection_api:app --bind 0.0.0.0 --port \$PORT
    healthCheckPath: /health
    healthCheckTimeout: 30
    autoDeploy: true

  # Payout Orchestrator
  - type: web
    name: dedan-mine-payout
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn payout.api:app --bind 0.0.0.0 --port \$PORT
    healthCheckPath: /health
    healthCheckTimeout: 30
    autoDeploy: true

  # Mobile Dashboard
  - type: web
    name: dedan-mine-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run dashboard/app.py --server.port=\$PORT --server.address=0.0.0.0
    healthCheckPath: /_stcore/health
    healthCheckTimeout: 30
    autoDeploy: true

version: "1.0.0"
EOF
fi

# Login to Render (if not already logged in)
echo "🔐 Logging into Render..."
render login

# Deploy backend services
echo "🌍 Deploying backend services to Render..."
render deploy

# Check deployment status
if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully to Render!"
    echo "🌐 API endpoints will be available at: https://api.dedanmine.io"
else
    echo "❌ Render deployment failed"
    exit 1
fi

echo "🎉 Render deployment completed!"
echo "=================================="
