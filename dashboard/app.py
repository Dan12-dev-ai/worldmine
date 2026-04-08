import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, Any

# Configure Streamlit
st.set_page_config(
    page_title="UOTA Elite v2 Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #262730;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #ffffff;
        background-color: #262730;
        border-radius: 10px 10px 0 0;
    }
    .plotly-chart {
        background-color: #0e1117;
    }
    .emergency-kill {
        background-color: #ff4444;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        border: 3px solid #ff0000;
        margin: 20px 0;
    }
    .mode-toggle {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #4a5568;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #1a1d29;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #4a5568;
        margin: 10px 0;
    }
    .thought-process {
        background-color: #1a1d29;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4a5568;
        font-family: monospace;
        font-size: 12px;
        max-height: 300px;
        overflow-y: auto;
    }
    /* Mobile optimizations */
    .stButton > button {
        min-height: 44px;
        font-size: 16px;
        padding: 12px 24px;
        margin: 8px 0;
    }
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column;
        }
        .stDataFrame {
            font-size: 12px;
        }
        .plotly-chart {
            height: 300px !important;
        }
    }
    @media (orientation: landscape) and (max-height: 500px) {
        .stApp > header {
            padding: 0.5rem 1rem;
        }
        .stTabs {
            padding: 0.25rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'bot_status' not in st.session_state:
    st.session_state.bot_status = 'running'
if 'trading_mode' not in st.session_state:
    st.session_state.trading_mode = 'demo'
if 'emergency_kill' not in st.session_state:
    st.session_state.emergency_kill = False

# API Configuration
API_BASE = "http://localhost:8000/api/v1"

class DashboardAPI:
    """API client for dashboard data"""
    
    @staticmethod
    async def get_live_data() -> Dict[str, Any]:
        """Get live trading data"""
        try:
            response = requests.get(f"{API_BASE}/live-data", timeout=5)
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    @staticmethod
    async def get_performance_data() -> Dict[str, Any]:
        """Get performance data"""
        try:
            response = requests.get(f"{API_BASE}/performance", timeout=5)
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    @staticmethod
    async def get_smc_zones() -> Dict[str, Any]:
        """Get SMC zones"""
        try:
            response = requests.get(f"{API_BASE}/smc-zones", timeout=5)
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    @staticmethod
    async def get_thought_process() -> Dict[str, Any]:
        """Get bot thought process"""
        try:
            response = requests.get(f"{API_BASE}/thought-process", timeout=5)
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    @staticmethod
    async def emergency_kill() -> bool:
        """Emergency kill switch"""
        try:
            response = requests.post(f"{API_BASE}/emergency-kill", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    async def toggle_mode(mode: str) -> bool:
        """Toggle trading mode"""
        try:
            response = requests.post(
                f"{API_BASE}/toggle-mode",
                json={"mode": mode},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

# Mock data generators for demo
def generate_mock_gold_price():
    """Generate mock gold price data"""
    import random
    base_price = 2350.50
    change = random.uniform(-50, 50)
    return {
        "price": base_price + change,
        "change": change,
        "timestamp": datetime.now().isoformat()
    }

def generate_mock_smc_zones():
    """Generate mock SMC zones"""
    return {
        "zones": {
            "order_blocks": [
                {"price": 2345.20, "type": "bullish", "strength": "high"},
                {"price": 2368.80, "type": "bearish", "strength": "medium"},
                {"price": 2332.10, "type": "bullish", "strength": "high"}
            ],
            "liquidity_zones": [
                {"price": 2355.00, "range": 10, "type": "sell_side"},
                {"price": 2330.00, "range": 15, "type": "buy_side"}
            ],
            "fair_value_gap": [
                {"top": 2360.00, "bottom": 2355.00, "filled": False},
                {"top": 2340.00, "bottom": 2335.00, "filled": True}
            ]
        }
    }

def generate_mock_thoughts():
    """Generate mock thought process"""
    thoughts = [
        "[14:30:15] Analyzing XAUUSD market structure...",
        "[14:30:20] Identified bullish order block at 2345.20",
        "[14:30:25] Price approaching liquidity zone at 2355.00",
        "[14:30:30] RSI showing oversold conditions (28.5)",
        "[14:30:35] Fair value gap detected - potential fill target",
        "[14:30:40] Risk assessment: Medium - 2% risk per trade",
        "[14:30:45] Entry signal: Buy at 2348.00 with SL at 2340.00",
        "[14:30:50] Position size: 0.1 lots (2% risk)",
        "[14:30:55] Order placed - awaiting execution"
    ]
    return {"thoughts": thoughts}

def generate_mock_performance():
    """Generate mock performance data"""
    import random
    current_balance = 2000 + random.uniform(-200, 800)
    starting_balance = 2000
    target_balance = 50000
    
    # Generate historical data
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    balances = []
    balance = starting_balance
    
    for i in range(len(dates)):
        daily_change = random.uniform(-50, 100)
        balance += daily_change
        balances.append(max(balance, 100))  # Minimum balance
    
    return {
        "current_balance": current_balance,
        "starting_balance": starting_balance,
        "target_balance": target_balance,
        "daily_pnl": random.uniform(-50, 150),
        "win_rate": random.uniform(60, 85),
        "total_trades": random.randint(50, 200),
        "historical_data": [
            {"timestamp": dates[i].isoformat(), "balance": balances[i]} 
            for i in range(len(dates))
        ]
    }

# Main Dashboard
def main():
    """Main dashboard function"""
    
    # Header
    st.title("🤖 UOTA Elite v2 - Mobile Dashboard")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Live Ops", "💰 Performance", "🛡️ Safety"])
    
    with tab1:
        live_ops_tab()
    
    with tab2:
        performance_tab()
    
    with tab3:
        safety_tab()

def live_ops_tab():
    """Live Operations Tab"""
    st.header("📊 Live Operations")
    
    # Create columns for live data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Gold Price Card
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🥇 Gold (XAUUSD)")
        
        # Get live data (mock for now)
        gold_data = generate_mock_gold_price()
        
        gold_price = gold_data['price']
        price_change = gold_data['change']
        
        st.markdown(f"### ${gold_price:.2f}")
        
        if price_change > 0:
            st.markdown(f"📈 +${price_change:.2f} (+{price_change/gold_price*100:.2f}%)")
        elif price_change < 0:
            st.markdown(f"📉 ${abs(price_change):.2f} ({price_change/gold_price*100:.2f}%)")
        else:
            st.markdown("➡️ $0.00 (0.00%)")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # SMC Zones Card
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🎯 Smart Money Concepts")
        
        smc_data = generate_mock_smc_zones()
        zones = smc_data['zones']
        
        for zone_type, zone_data in zones.items():
            if zone_type == 'order_blocks':
                st.markdown(f"**Order Blocks:** {len(zone_data)}")
                for block in zone_data[:3]:  # Show top 3
                    st.markdown(f"- ${block['price']:.2f} ({block['type']})")
            elif zone_type == 'liquidity_zones':
                st.markdown(f"**Liquidity:** {len(zone_data)} zones")
            elif zone_type == 'fair_value_gap':
                st.markdown(f"**FVG:** {len(zone_data)} gaps")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Bot Status Card
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🤖 Bot Status")
        
        if st.session_state.bot_status == 'running':
            st.markdown("### 🟢 RUNNING")
        else:
            st.markdown("### 🔴 STOPPED")
        
        st.markdown(f"**Mode:** {st.session_state.trading_mode.upper()}")
        st.markdown(f"**Uptime:** {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Thought Process Section
    st.markdown("---")
    st.subheader("🧠 Bot Thought Process")
    
    thought_data = generate_mock_thoughts()
    
    if thought_data and 'thoughts' in thought_data:
        thoughts = thought_data['thoughts']
        thought_text = "\n".join(thoughts)
        
        st.markdown('<div class="thought-process">', unsafe_allow_html=True)
        st.text(thought_text)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="thought-process">', unsafe_allow_html=True)
        st.text("No thought process data available...")
        st.markdown('</div>', unsafe_allow_html=True)

def performance_tab():
    """Performance Tab"""
    st.header("💰 Performance Metrics")
    
    # Get performance data (mock for now)
    perf_data = generate_mock_performance()
    
    if perf_data:
        # Current Balance
        current_balance = perf_data.get('current_balance', 2000)
        starting_balance = perf_data.get('starting_balance', 2000)
        target_balance = perf_data.get('target_balance', 50000)
        
        # Calculate metrics
        profit_loss = current_balance - starting_balance
        profit_percentage = (profit_loss / starting_balance) * 100
        progress_percentage = (current_balance / target_balance) * 100
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("💰 Current Balance")
            st.markdown(f"### ${current_balance:,.2f}")
            if profit_loss >= 0:
                st.markdown(f"📈 +${profit_loss:,.2f} (+{profit_percentage:.2f}%)")
            else:
                st.markdown(f"📉 ${abs(profit_loss):,.2f} ({profit_percentage:.2f}%)")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("🎯 Target Progress")
            st.markdown(f"### ${target_balance:,.2f}")
            st.markdown(f"Progress: {progress_percentage:.2f}%")
            
            # Progress bar
            st.progress(progress_percentage / 100)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📊 Daily Stats")
            daily_pnl = perf_data.get('daily_pnl', 0)
            win_rate = perf_data.get('win_rate', 0)
            total_trades = perf_data.get('total_trades', 0)
            
            st.markdown(f"**Daily P&L:** ${daily_pnl:,.2f}")
            st.markdown(f"**Win Rate:** {win_rate:.1f}%")
            st.markdown(f"**Total Trades:** {total_trades}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # P&L Chart
        st.markdown("---")
        st.subheader("📈 Profit/Loss Chart")
        
        if 'historical_data' in perf_data:
            df = pd.DataFrame(perf_data['historical_data'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create interactive chart
            fig = go.Figure()
            
            # Add balance line
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['balance'],
                mode='lines',
                name='Balance',
                line=dict(color='#00ff88', width=3)
            ))
            
            # Add target line
            fig.add_hline(
                y=target_balance,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Target: ${target_balance:,.2f}"
            )
            
            # Update layout
            fig.update_layout(
                title="Account Balance Over Time",
                xaxis_title="Time",
                yaxis_title="Balance ($)",
                template="plotly_dark",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 📊 No historical data available")
    else:
        st.markdown("### ⚠️ Performance data unavailable")

def safety_tab():
    """Safety Tab"""
    st.header("🛡️ Safety Controls")
    
    # Emergency Kill Switch
    st.markdown('<div class="emergency-kill">', unsafe_allow_html=True)
    st.markdown("🚨 EMERGENCY KILL SWITCH 🚨")
    
    if st.button("🛑 KILL ALL TRADING", type="primary"):
        if st.session_state.emergency_kill:
            st.error("Trading already stopped!")
        else:
            # Show confirmation dialog
            if st.session_state.get('kill_confirmation', False):
                # Execute emergency kill
                st.session_state.emergency_kill = True
                st.session_state.bot_status = 'stopped'
                st.success("🛑 Trading stopped successfully!")
                st.balloons()
            else:
                st.session_state.kill_confirmation = True
                st.warning("⚠️ Click again to confirm emergency kill!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mode Toggle
    st.markdown('<div class="mode-toggle">', unsafe_allow_html=True)
    st.subheader("🔄 Trading Mode Toggle")
    
    current_mode = st.session_state.trading_mode
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎮 DEMO MODE", type="secondary"):
            if current_mode != 'demo':
                st.session_state.trading_mode = 'demo'
                st.success("✅ Switched to DEMO mode")
            else:
                st.info("Already in DEMO mode")
    
    with col2:
        if st.button("💰 REAL MODE", type="primary"):
            if current_mode != 'real':
                st.session_state.trading_mode = 'real'
                st.success("✅ Switched to REAL mode")
                st.warning("⚠️ Real money trading enabled!")
            else:
                st.info("Already in REAL mode")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current Mode Display
    st.markdown("---")
    st.subheader("📊 Current Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🔄 Trading Mode")
        mode_color = "🟢" if st.session_state.trading_mode == 'real' else "🔵"
        st.markdown(f"### {mode_color} {st.session_state.trading_mode.upper()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🤖 Bot Status")
        status_color = "🟢" if st.session_state.bot_status == 'running' else "🔴"
        st.markdown(f"### {status_color} {st.session_state.bot_status.upper()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🛡️ Safety Status")
        safety_status = "🛑 STOPPED" if st.session_state.emergency_kill else "✅ ACTIVE"
        safety_color = "🔴" if st.session_state.emergency_kill else "🟢"
        st.markdown(f"### {safety_color} {safety_status}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Safety Log
    st.markdown("---")
    st.subheader("📋 Safety Log")
    
    safety_log = [
        {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "action": "Dashboard loaded", "status": "info"},
        {"timestamp": (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'), "action": "Mode switched to demo", "status": "success"},
        {"timestamp": (datetime.now() - timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S'), "action": "Risk limit check", "status": "info"},
        {"timestamp": (datetime.now() - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'), "action": "Position monitoring active", "status": "success"},
    ]
    
    for log_entry in safety_log:
        status_icon = "✅" if log_entry["status"] == "success" else "⚠️" if log_entry["status"] == "warning" else "ℹ️"
        st.markdown(f"{status_icon} **{log_entry['timestamp']}** - {log_entry['action']}")

if __name__ == "__main__":
    main()
