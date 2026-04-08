#!/bin/bash

# DEDAN Mine - Vercel Frontend Deployment Script
# Deploys React frontend to Vercel with production optimization

set -e

echo "🚀 DEDAN Mine - Vercel Frontend Deployment"
echo "=================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if we're in the frontend directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Build for production
echo "🔨 Building frontend for production..."
npm run build

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

# Deploy to Vercel
echo "🌍 Deploying to Vercel..."
vercel --prod

# Check deployment status
if [ $? -eq 0 ]; then
    echo "✅ Frontend deployed successfully to Vercel!"
    echo "🌐 Access your app at: https://dedanmine.io"
else
    echo "❌ Vercel deployment failed"
    exit 1
fi

echo "🎉 Vercel deployment completed!"
echo "=================================="
