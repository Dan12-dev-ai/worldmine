# DEDAN Mine Backend

## World's Most Advanced AI-Powered Global Mining Marketplace

### 🚀 Features

#### Core Marketplace (Competitor Strengths)
- ✅ **Simple Auctions & Buy-It-Now**: Easy listing creation and bidding
- ✅ **Professional Verification**: Multi-tier verification system
- ✅ **Trust Signals**: Watchlists, feedback, reputation scoring
- ✅ **Bulk Trading**: Volume handling and tiered pricing
- ✅ **Clean UI**: Curated browsing experience

#### Future-Ready Technology
- 🤖 **Autonomous AI Trading Agents**: Self-learning with reinforcement learning
- 📹 **Live Video Negotiations**: Real-time video + live auctions
- 🌍 **Mine-to-Market Traceability**: IoT sensors + GPS + satellite monitoring
- 🌱 **ESG & Carbon Credits**: Automatic scoring and carbon tracking
- ⚖️ **ECX Compliance**: Ethiopian gem export forms + anti-smuggling
- 🔐 **Quantum-Resistant Security**: Zero-Trust + Homomorphic encryption
- 🧠 **Federated Learning**: Privacy-preserving AI training

### 📁 Project Structure

```
backend/
├── 📄 app.py                    # Main FastAPI application
├── 📄 models.py                  # SQLAlchemy database models
├── 📄 database.py                # Database configuration
├── 📄 requirements.txt           # Python dependencies
├── 📁 services/                  # Core business logic
│   ├── 📁 marketplace/           # Listings, auctions, trading
│   ├── 📁 ai-agents/            # Autonomous trading agents
│   ├── 📁 video-negotiation/     # Live video & auctions
│   ├── 📁 traceability/          # IoT & GPS tracking
│   ├── 📁 esg/                  # ESG scoring & carbon credits
│   ├── 📁 compliance/            # ECX legal compliance
│   ├── 📁 security/              # Quantum encryption
│   ├── 📁 ai/                    # Explainable AI
│   └── 📁 federated-learning/     # Privacy-preserving ML
├── 📁 tests/                     # Test suite
└── 📄 README.md                 # This file
```

### 🛠️ Installation

#### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (for frontend)

#### Setup
```bash
# Clone repository
git clone https://github.com/Dan12-dev-ai/worldmine.git
cd worldmine/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python -c "from database import init_db; init_db()"

# Start development server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 🔧 Configuration

#### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dedanmine

# AI Services
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_AI_API_KEY=your_google_ai_key

# Security
SECRET_KEY=your_secret_key
QUANTUM_KEY_PATH=/path/to/quantum/keys

# External Services
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
TAVILY_API_KEY=your_tavily_key

# Monitoring
REDIS_URL=redis://localhost:6379
PROMETHEUS_PORT=9090
```

### 📊 Database Schema

#### Core Tables
- **users**: User accounts and profiles
- **listings**: Marketplace listings with future features
- **auctions**: Auction management
- **bids**: Bidding system
- **buy_it_now_transactions**: Fixed-price transactions

#### Advanced Features
- **ai_agents**: Autonomous trading agents
- **agent_actions**: AI agent decision logs
- **video_sessions**: Live video negotiations
- **traceability_records**: Mine-to-market tracking
- **esg_metrics**: ESG scoring and carbon credits
- **compliance_records**: ECX legal compliance
- **trust_signals**: Reputation and trust building

### 🔌 API Endpoints

#### Core Marketplace
```http
POST /api/v1/listings/create          # Create listing
GET  /api/v1/listings/browse           # Browse listings
GET  /api/v1/listings/{id}            # Get listing details
POST /api/v1/auctions/{id}/bid        # Place bid
POST /api/v1/listings/{id}/buy-now    # Buy-It-Now
```

#### AI Agents
```http
POST /api/v1/ai-agents/create         # Create AI agent
GET  /api/v1/ai-agents/{id}/analyze    # Market analysis
POST /api/v1/ai-agents/{id}/bid       # Autonomous bid
```

#### Video Negotiations
```http
POST /api/v1/video/schedule            # Schedule video session
POST /api/v1/video/join/{id}          # Join session
POST /api/v1/video/message             # Send message
```

#### Traceability
```http
POST /api/v1/traceability/register-sensors  # Register IoT sensors
POST /api/v1/traceability/record-sensors    # Record sensor data
GET  /api/v1/traceability/report/{id}       # Get traceability report
```

#### ESG & Compliance
```http
POST /api/v1/esg/calculate-score      # Calculate ESG score
GET  /api/v1/esg/dashboard/{id}       # ESG dashboard
POST /api/v1/compliance/generate-export-form  # ECX export form
POST /api/v1/compliance/anti-smuggling-check   # Anti-smuggling
```

### 🔐 Security Features

#### Quantum-Resistant Cryptography
- **CRYSTALS-Kyber**: Post-quantum key exchange
- **Dilithium**: Quantum-resistant digital signatures
- **NTRU**: Alternative quantum algorithm

#### Zero-Trust Architecture
- **Continuous Authentication**: Behavioral analysis
- **Device Trust Scoring**: Dynamic risk assessment
- **Microsegmentation**: Network isolation

#### Homomorphic Encryption
- **Encrypted Search**: Privacy-preserving queries
- **Private Matching**: Secure data comparison
- **Secure Computation**: Encrypted data processing

### 🌱 ESG Integration

#### Environmental Scoring
- **Carbon Footprint**: CO2 emissions tracking
- **Water Usage**: Resource consumption monitoring
- **Energy Source**: Renewable energy verification
- **Biodiversity Impact**: Environmental protection

#### Social Impact
- **Local Jobs Created**: Community employment
- **Training Programs**: Skill development
- **Fair Labor**: Ethical workplace practices
- **Community Investment**: Local development

#### Carbon Credits
- **Automatic Calculation**: Based on environmental metrics
- **Trading System**: Buy/sell credits
- **Blockchain Verification**: Immutable records

### ⚖️ ECX Compliance

#### Ethiopian Gem Export
- **Automatic Forms**: ECX-compliant export documentation
- **Anti-Smuggling**: AI-powered risk detection
- **Origin Verification**: GPS + satellite confirmation
- **Legal Compliance**: Ethiopian mining regulations

#### Supported Gem Types
- **Ethiopian Opal**: Wollo, Mezezo, etc.
- **Ethiopian Emerald**: Green, blue-green varieties
- **Ethiopian Sapphire**: Blue, fancy colors
- **Ethiopian Ruby**: Red to pink-red stones

### 🤖 AI Agents

#### Autonomous Trading
- **Market Analysis**: Real-time price prediction
- **Strategy Execution**: Automated bidding/buying
- **Risk Management**: Portfolio optimization
- **Learning**: Reinforcement learning improvement

#### Federated Learning
- **Privacy-Preserving**: Local model training
- **Secure Aggregation**: Encrypted model updates
- **Explainable AI**: Transparent decision making
- **Continuous Improvement**: Global model enhancement

### 📹 Video Negotiations

#### Live Video Features
- **Real-time Streaming**: WebRTC-based video
- **Screen Sharing**: Document presentation
- **Live Chat**: Text + audio + video messages
- **Recording**: Session archiving

#### Live Auctions
- **Real-time Bidding**: Live auction interface
- **Auto-Extension**: Last-minute bid protection
- **Multi-participant**: Group negotiations
- **Transcription**: Automatic speech-to-text

### 🌍 Traceability

#### IoT Integration
- **Sensor Network**: Temperature, humidity, vibration
- **GPS Tracking**: Real-time location monitoring
- **Satellite Verification**: Orbital imagery analysis
- **Blockchain Records**: Immutable tracking

#### Mine-to-Market
- **Extraction Data**: Mine location + method
- **Processing History**: Cutting + treatment records
- **Transport Tracking**: Logistics monitoring
- **Authenticity**: AI-powered verification

### 📈 Monitoring & Analytics

#### Performance Metrics
- **Response Times**: API performance tracking
- **User Analytics**: Behavior analysis
- **Transaction Metrics**: Trading volume + success rates
- **AI Performance**: Agent effectiveness

#### Health Checks
- **Service Health**: Component status monitoring
- **Database Health**: Connection + query performance
- **Resource Usage**: CPU + memory + storage
- **Error Tracking**: Comprehensive error logging

### 🧪 Testing

#### Test Suite
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_marketplace.py

# Run with coverage
pytest --cov=services tests/

# Run performance tests
pytest tests/performance/
```

#### Test Categories
- **Unit Tests**: Individual function testing
- **Integration Tests**: Service interaction testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability assessment

### 🚀 Deployment

#### Production Deployment
```bash
# Build Docker image
docker build -t dedan-mine-backend .

# Deploy to Kubernetes
kubectl apply -f k8s/

# Monitor deployment
kubectl logs -f deployment/dedan-mine-backend
```

#### Environment Configuration
- **Development**: Local development with hot reload
- **Staging**: Production-like testing environment
- **Production**: Full deployment with monitoring
- **Edge**: Low-bandwidth optimization for emerging markets

### 📚 Documentation

#### API Documentation
- **Swagger UI**: `/docs` - Interactive API explorer
- **ReDoc**: `/redoc` - Alternative API docs
- **OpenAPI**: `/openapi.json` - API specification

#### Architecture Docs
- **System Design**: High-level architecture overview
- **Database Schema**: Complete ERD documentation
- **Security Model**: Threat analysis and mitigation
- **Performance**: Optimization strategies and benchmarks

### 🤝 Contributing

#### Development Workflow
1. Fork repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request
6. Code review and merge

#### Code Quality
- **Linting**: `flake8` for code style
- **Type Checking**: `mypy` for static analysis
- **Security**: `bandit` for vulnerability scanning
- **Testing**: Minimum 80% code coverage

### 📞 Support

#### Contact
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: support@dedan-mine.com
- **Documentation**: docs.dedan-mine.com

---

## 🏆 License

DEDAN Mine is licensed under the MIT License. See LICENSE file for details.

## 🌍 Global Impact

DEDAN Mine is committed to:
- **Financial Inclusion**: Empowering small miners globally
- **Environmental Sustainability**: Promoting responsible mining
- **Technological Innovation**: Leading the industry in AI adoption
- **Economic Development**: Supporting local communities
- **Transparency**: Building trust through traceability

*Together, we're building the future of global mining.* 💎🌍
