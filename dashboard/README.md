# 📱 UOTA Elite v2 - Mobile Monitoring Dashboard

## 🚀 Quick Start

### 📱 **Deploy Dashboard**
```bash
# Navigate to dashboard directory
cd dashboard

# Deploy with Docker
docker-compose -f docker-compose.dashboard.yml up -d

# Check dashboard
curl http://localhost:8501

# Setup Ngrok for mobile access
ngrok http 8501
```

### 🎯 **Access URLs**
- **Local**: `http://localhost:8501`
- **Ngrok**: `https://your-domain.ngrok-free.app`
- **Mobile**: Open Ngrok URL on your phone

## 📊 **Dashboard Features**

### 🎯 **Live Ops Tab**
- **Real-time Gold Price**: Current XAUUSD with change indicators
- **SMC Zones**: Order blocks, liquidity zones, fair value gaps
- **Bot Status**: Running/stopped status with current mode
- **Thought Process**: Real-time AI decision-making logs

### 💰 **Performance Tab**
- **Balance Display**: Current $2,000 balance with P&L
- **Progress Tracking**: Visual progress toward $50,000 goal
- **P&L Chart**: Interactive profit/loss chart
- **Daily Stats**: Win rate, daily P&L, total trades

### 🛡️ **Safety Tab**
- **Emergency Kill**: Large red button to stop all trading
- **Mode Toggle**: Switch between Demo/Real trading modes
- **Status Display**: Current mode and bot status
- **Safety Log**: Historical safety actions and events

## 📱 **Mobile Features**

### 🎯 **Touch-Optimized Interface**
- **Large Buttons**: Minimum 44px height for touch
- **Responsive Design**: Adapts to all screen sizes
- **Landscape Mode**: Optimized for horizontal viewing
- **Dark Mode**: Easy on the eyes in low light

### 🚀 **Performance Optimizations**
- **Fast Loading**: Lightweight components
- **Efficient Updates**: Only refresh necessary data
- **Battery Friendly**: Minimal resource usage

## 🔧 **Configuration**

### 📋 **Environment Variables**
```bash
# API Configuration
API_BASE=http://localhost:8000/api/v1

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 🛠️ **API Integration**
The dashboard expects these API endpoints:
- `GET /api/v1/live-data` - Live trading data
- `GET /api/v1/performance` - Performance metrics
- `GET /api/v1/smc-zones` - SMC zones data
- `GET /api/v1/thought-process` - Bot thought process
- `POST /api/v1/emergency-kill` - Emergency kill switch
- `POST /api/v1/toggle-mode` - Mode toggle

## 🌐 **Mobile Access Setup**

### 📱 **Ngrok Configuration**
```bash
# Install Ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Start Ngrok tunnel
ngrok http 8501 --domain=your-custom-domain.ngrok-free.app

# Or use authtoken for persistent tunnel
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
ngrok http 8501
```

## 🔧 **Troubleshooting**

### 🐛 **Common Issues**
1. **Dashboard not loading**: Check Docker logs
2. **API connection errors**: Verify bot API is running
3. **Ngrok not working**: Check Ngrok status and domain
4. **Mobile display issues**: Refresh browser cache

### 📋 **Health Checks**
```bash
# Check dashboard health
curl http://localhost:8501/_stcore/health

# Check Docker logs
docker-compose -f docker-compose.dashboard.yml logs

# Restart dashboard
docker-compose -f docker-compose.dashboard.yml restart
```

## 🎉 **Your Mobile Dashboard is Ready!**

**Features:**
- 📱 **Mobile-First Design**: Optimized for phones and tablets
- 🎯 **Real-Time Data**: Live gold prices and SMC zones
- 💰 **Performance Tracking**: P&L charts and progress to $50K
- 🛡️ **Safety Controls**: Emergency kill and mode toggle
- 🌐 **Remote Access**: Ngrok tunnel for mobile monitoring
- 🔄 **Auto-Restart**: Always available monitoring

**Access Methods:**
- **Desktop**: `http://localhost:8501`
- **Mobile**: Ngrok URL on your phone
- **Tablet**: Responsive design adapts to screen size

**🎉 Monitor your UOTA Elite v2 bot from anywhere!** 📱🚀📊
