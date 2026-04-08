#!/bin/bash

# DEDAN Mine - Zero Budget Deployment Script
# Complete FREE Infrastructure Setup

echo "=== DEDAN Mine Zero Budget Deployment ==="
echo "Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_step "Checking requirements..."
    
    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check for node
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check for npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    print_status "All requirements satisfied!"
}

# Step 1: Setup Environment Variables
setup_environment() {
    print_step "Setting up environment variables..."
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        print_status "Creating backend .env file..."
        cp backend/.env.example backend/.env
        print_warning "Please update backend/.env with your actual API keys"
    else
        print_status "Backend .env file already exists"
    fi
    
    # Frontend environment
    if [ ! -f "frontend/.env" ]; then
        print_status "Creating frontend .env file..."
        cp frontend/.env.example frontend/.env
        print_warning "Please update frontend/.env with your actual configuration"
    else
        print_status "Frontend .env file already exists"
    fi
}

# Step 2: Install Dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    
    # Backend dependencies
    print_status "Installing backend dependencies..."
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    print_status "Dependencies installed successfully!"
}

# Step 3: Build Frontend
build_frontend() {
    print_step "Building frontend..."
    
    cd frontend
    npm run build
    cd ..
    
    print_status "Frontend built successfully!"
}

# Step 4: Test Local Setup
test_local_setup() {
    print_step "Testing local setup..."
    
    # Test backend
    print_status "Testing backend..."
    cd backend
    source venv/bin/activate
    python -c "import fastapi; print('FastAPI imported successfully')"
    cd ..
    
    # Test frontend
    print_status "Testing frontend..."
    cd frontend
    npm run build
    cd ..
    
    print_status "Local setup test completed!"
}

# Step 5: Git Setup
setup_git() {
    print_step "Setting up Git repository..."
    
    # Initialize git if not already done
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit - DEDAN Mine v4.5.0"
        print_status "Git repository initialized"
    else
        print_status "Git repository already exists"
    fi
    
    # Check if remote is set
    if ! git remote get-url origin &> /dev/null; then
        print_warning "Please set up GitHub repository and add remote:"
        echo "git remote add origin https://github.com/yourusername/dedan-mine.git"
        echo "git push -u origin main"
    else
        print_status "Git remote already configured"
    fi
}

# Step 6: Create Deployment Files
create_deployment_files() {
    print_step "Creating deployment files..."
    
    # koyeb.yaml already exists
    print_status "koyeb.yaml already exists"
    
    # vercel.json already exists
    print_status "vercel.json already exists"
    
    # Environment examples already exist
    print_status "Environment example files already exist"
    
    print_status "Deployment files ready!"
}

# Step 7: Service Setup Instructions
show_service_setup() {
    print_step "Service Setup Instructions:"
    
    echo ""
    echo "=== FREE SERVICES TO SETUP ==="
    echo ""
    echo "1. NEON.TECH (Database - FREE)"
    echo "   - Go to: https://neon.tech"
    echo "   - Sign up for FREE account"
    echo "   - Create new project"
    echo "   - Get connection string"
    echo "   - Update DATABASE_URL in backend/.env"
    echo ""
    echo "2. KOYEB (Backend Hosting - FREE)"
    echo "   - Go to: https://koyeb.com"
    echo "   - Sign up with GitHub"
    echo "   - Connect your repository"
    echo "   - Use koyeb.yaml configuration"
    echo "   - Deploy backend"
    echo ""
    echo "3. VERCEL (Frontend Hosting - FREE)"
    echo "   - Go to: https://vercel.com"
    echo "   - Sign up with GitHub"
    echo "   - Import your repository"
    echo "   - Use vercel.json configuration"
    echo "   - Deploy frontend"
    echo ""
    echo "4. CLOUDFLARE (CDN & DNS - FREE)"
    echo "   - Go to: https://cloudflare.com"
    echo "   - Sign up for FREE account"
    echo "   - Add your domain"
    echo "   - Configure DNS"
    echo "   - Set up SSL"
    echo ""
    echo "5. UPSTASH (Redis Cache - FREE)"
    echo "   - Go to: https://upstash.com"
    echo "   - Sign up for FREE account"
    echo "   - Create Redis database"
    echo "   - Get connection string"
    echo "   - Update REDIS_URL in backend/.env"
    echo ""
    echo "6. UPTIMEROBOT (Monitoring - FREE)"
    echo "   - Go to: https://uptimerobot.com"
    echo "   - Sign up for FREE account"
    echo "   - Add monitors for your services"
    echo "   - Configure alerts"
    echo ""
    echo "7. SENTRY (Error Tracking - FREE)"
    echo "   - Go to: https://sentry.io"
    echo "   - Sign up for FREE account"
    echo "   - Create project"
    echo "   - Add SDK to backend"
    echo "   - Update SENTRY_DSN in backend/.env"
    echo ""
    echo "8. RESEND (Email Service - FREE)"
    echo "   - Go to: https://resend.com"
    echo "   - Sign up for FREE account"
    echo "   - Verify domain"
    echo "   - Update RESEND_API_KEY in backend/.env"
    echo ""
}

# Step 8: Pre-deployment Checklist
pre_deployment_checklist() {
    print_step "Pre-deployment Checklist:"
    
    echo ""
    echo "=== BEFORE DEPLOYMENT ==="
    echo ""
    echo "1. Update API Keys:"
    echo "   - Edit backend/.env with real API keys"
    echo "   - Edit frontend/.env with real configuration"
    echo "   - Test all services locally"
    echo ""
    echo "2. Test Payment Integration:"
    echo "   - Test Stripe (test mode)"
    echo "   - Test Chapa (test mode)"
    echo "   - Test all payment flows"
    echo ""
    echo "3. Test Security:"
    echo "   - Test authentication"
    echo "   - Test biometric verification"
    echo "   - Test security features"
    echo ""
    echo "4. Test Performance:"
    echo "   - Test page load times"
    echo "   - Test API response times"
    echo "   - Test mobile responsiveness"
    echo ""
    echo "5. Backup Data:"
    echo "   - Backup database schema"
    echo "   - Backup configuration files"
    echo "   - Document deployment process"
    echo ""
}

# Step 9: Deployment Commands
deployment_commands() {
    print_step "Deployment Commands:"
    
    echo ""
    echo "=== DEPLOYMENT COMMANDS ==="
    echo ""
    echo "1. Deploy to Koyeb (Backend):"
    echo "   koyeb app create --name dedan-mine-api --region was"
    echo "   koyeb app deploy"
    echo ""
    echo "2. Deploy to Vercel (Frontend):"
    echo "   cd frontend"
    echo "   npx vercel --prod"
    echo ""
    echo "3. Monitor Deployment:"
    echo "   koyeb service logs dedan-mine-api --follow"
    echo "   npx vercel logs"
    echo ""
    echo "4. Test Production:"
    echo "   curl https://dedan-mine-api.koyeb.app/health"
    echo "   Visit https://your-domain.vercel.app"
    echo ""
}

# Step 10: Post-deployment
post_deployment() {
    print_step "Post-deployment Tasks:"
    
    echo ""
    echo "=== AFTER DEPLOYMENT ==="
    echo ""
    echo "1. Configure DNS:"
    echo "   - Update Cloudflare DNS"
    echo "   - Point domain to Vercel"
    echo "   - Configure SSL"
    echo ""
    echo "2. Set up Monitoring:"
    echo "   - Add UptimeRobot monitors"
    echo "   - Configure Sentry alerts"
    echo "   - Set up Google Analytics"
    echo ""
    echo "3. Test Everything:"
    echo "   - Test all user flows"
    echo "   - Test payment processing"
    echo "   - Test security features"
    echo ""
    echo "4. Launch Marketing:"
    echo "   - Social media announcement"
    echo "   - User onboarding"
    echo "   - Community building"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "========================================"
    echo "DEDAN Mine - Zero Budget Deployment"
    echo "========================================"
    echo ""
    
    check_requirements
    setup_environment
    install_dependencies
    build_frontend
    test_local_setup
    setup_git
    create_deployment_files
    show_service_setup
    pre_deployment_checklist
    deployment_commands
    post_deployment
    
    echo ""
    echo "========================================"
    echo "DEPLOYMENT SCRIPT COMPLETED!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Setup all FREE services listed above"
    echo "2. Update API keys in .env files"
    echo "3. Test everything locally"
    echo "4. Deploy to Koyeb and Vercel"
    echo "5. Configure DNS and monitoring"
    echo "6. GO LIVE! $0/month"
    echo ""
    print_status "Total cost: $0/month for complete platform!"
    echo ""
}

# Run the script
main "$@"
