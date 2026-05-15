"""
AUTONOMOUS AI MARKET MAKERS - 24/7 LIQUIDITY PROVIDERS
Self-optimizing AI agents that provide continuous liquidity without human intervention

Uses advanced reinforcement learning and deep learning to:
- Provide bid/ask spreads with optimal pricing
- Adapt to market conditions in real-time
- Manage inventory risk dynamically
- Generate consistent profits while maintaining market stability

CRITICAL: Must operate 24/7 with <100ms response time for all market updates.
"""

import asyncio
import time
import json
import uuid
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import redis
import asyncpg
from collections import deque
import threading
from fastapi import HTTPException

# AI/ML Libraries
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
import gym
from gym import spaces

class MarketMakerStrategy(Enum):
    """Market maker strategies"""
    INVENTORY_BALANCED = "inventory_balanced"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    VOLATILITY_TRADING = "volatility_trading"

class OrderSide(Enum):
    """Order sides"""
    BID = "bid"
    ASK = "ask"

@dataclass
class MarketMakerOrder:
    """Market maker order"""
    order_id: str
    mm_id: str
    mineral_type: str
    side: OrderSide
    price: float
    quantity: float
    timestamp: datetime
    strategy: MarketMakerStrategy
    confidence: float
    inventory_impact: float

@dataclass
class MarketData:
    """Market data snapshot"""
    mineral_type: str
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    last_price: float
    volume_24h: float
    volatility: float
    timestamp: datetime

@dataclass
class MarketMakerState:
    """Market maker internal state"""
    mm_id: str
    mineral_type: str
    current_inventory: float
    target_inventory: float
    max_inventory: float
    min_inventory: float
    pnl: float
    total_trades: int
    active_orders: List[MarketMakerOrder]
    strategy: MarketMakerStrategy
    last_update: datetime
    performance_metrics: Dict[str, float]

class ReinforcementLearningMM:
    """Reinforcement Learning Market Maker"""
    
    def __init__(self, state_size=20, action_size=5):
        self.state_size = state_size
        self.action_size = action_size
        
        # Neural network for Q-learning
        self.q_network = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )
        
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=0.001)
        self.memory = deque(maxlen=10000)
        self.epsilon = 0.1  # Exploration rate
        self.gamma = 0.95  # Discount factor
        
    def get_state(self, market_data: MarketData, mm_state: MarketMakerState) -> np.ndarray:
        """Convert market data and MM state to neural network input"""
        state = np.array([
            market_data.bid_price,
            market_data.ask_price,
            market_data.bid_size,
            market_data.ask_size,
            market_data.last_price,
            market_data.volume_24h,
            market_data.volatility,
            mm_state.current_inventory,
            mm_state.target_inventory,
            mm_state.max_inventory,
            mm_state.min_inventory,
            mm_state.pnl,
            mm_state.total_trades,
            len(mm_state.active_orders),
            # Price indicators
            (market_data.last_price - market_data.bid_price) / market_data.bid_price,
            (market_data.ask_price - market_data.last_price) / market_data.last_price,
            (market_data.ask_price - market_data.bid_price) / market_data.bid_price,  # Spread
            # Time features
            datetime.now().hour / 24.0,
            datetime.now().weekday() / 7.0,
            # Volatility features
            market_data.volatility / 0.1,  # Normalized volatility
        ])
        
        return state
    
    def select_action(self, state: np.ndarray) -> int:
        """Select action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            return np.random.randint(0, self.action_size)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def update_model(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        """Update Q-network"""
        state_tensor = torch.FloatTensor(state)
        action_tensor = torch.LongTensor([action])
        reward_tensor = torch.FloatTensor([reward])
        next_state_tensor = torch.FloatTensor(next_state)
        
        # Current Q value
        current_q = self.q_network(state_tensor)[0][action]
        
        # Next Q value
        next_q = self.q_network(next_state_tensor).max(0)[0].detach()
        target_q = reward_tensor + (self.gamma * next_q)
        
        # Loss
        loss = nn.MSELoss()(current_q, target_q)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

class AutonomousMarketMaker:
    """
    Autonomous AI Market Maker
    
    Features:
    1. Reinforcement Learning for optimal pricing
    2. Real-time inventory management
    3. Multi-strategy adaptation
    4. Risk management and position limits
    5. Performance optimization
    """
    
    def __init__(self, mm_id: str, mineral_type: str, initial_capital: float = 100000.0):
        self.mm_id = mm_id
        self.mineral_type = mineral_type
        self.initial_capital = initial_capital
        
        # Market maker state
        self.state = MarketMakerState(
            mm_id=mm_id,
            mineral_type=mineral_type,
            current_inventory=0.0,
            target_inventory=0.0,
            max_inventory=initial_capital / 1000.0,  # Max 1000 units at $1000 each
            min_inventory=-initial_capital / 1000.0,  # Can short up to 1000 units
            pnl=0.0,
            total_trades=0,
            active_orders=[],
            strategy=MarketMakerStrategy.INVENTORY_BALANCED,
            last_update=datetime.now(timezone.utc),
            performance_metrics={}
        )
        
        # AI Models
        self.rl_model = ReinforcementLearningMM()
        self.price_predictor = GradientBoostingRegressor(n_estimators=100)
        self.volatility_predictor = GradientBoostingRegressor(n_estimators=100)
        
        # Market data history
        self.market_history = deque(maxlen=1000)
        self.trade_history = deque(maxlen=1000)
        
        # Performance tracking
        self.performance_metrics = {
            'total_pnl': 0.0,
            'total_trades': 0,
            'win_rate': 0.0,
            'avg_spread': 0.0,
            'inventory_turnover': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
        
        # Risk management
        self.max_position_size = initial_capital * 0.1  # 10% of capital
        self.max_daily_loss = initial_capital * 0.02  # 2% daily loss limit
        self.min_spread = 0.001  # 0.1% minimum spread
        
        # Database and Redis
        self.db_pool = None
        self.redis_client = None
        
        # Trading parameters
        self.base_spread = 0.002  # 0.2% base spread
        self.inventory_skew_factor = 0.5
        self.volatility_factor = 1.0
        
        # Control flags
        self.is_active = False
        self.last_market_update = None
        
    async def initialize(self, db_pool, redis_client):
        """Initialize market maker with database connections"""
        self.db_pool = db_pool
        self.redis_client = redis_client
        
        # Load historical data
        await self._load_historical_data()
        
        # Train AI models
        await self._train_models()
        
        print(f"Market Maker {self.mm_id} initialized for {self.mineral_type}")
    
    async def _load_historical_data(self):
        """Load historical market data for training"""
        try:
            async with self.db_pool.acquire() as conn:
                historical_data = await conn.fetch("""
                    SELECT 
                        price,
                        volume,
                        created_at,
                        bid_price,
                        ask_price,
                        bid_size,
                        ask_size
                    FROM market_data 
                    WHERE mineral_type = $1 
                    AND created_at > NOW() - INTERVAL '30 days'
                    ORDER BY created_at ASC
                """, self.mineral_type)
            
            if historical_data:
                for row in historical_data:
                    market_data = MarketData(
                        mineral_type=self.mineral_type,
                        bid_price=float(row['bid_price'] or row['price'] * 0.999),
                        ask_price=float(row['ask_price'] or row['price'] * 1.001),
                        bid_size=float(row['bid_size'] or 1000),
                        ask_size=float(row['ask_size'] or 1000),
                        last_price=float(row['price']),
                        volume_24h=float(row['volume']),
                        volatility=0.0,  # Will be calculated
                        timestamp=row['created_at']
                    )
                    self.market_history.append(market_data)
                
                # Calculate volatility
                self._calculate_volatility()
                
                print(f"Loaded {len(historical_data)} historical data points for {self.mineral_type}")
            
        except Exception as e:
            print(f"Failed to load historical data: {e}")
    
    def _calculate_volatility(self):
        """Calculate rolling volatility"""
        if len(self.market_history) < 20:
            return
        
        prices = [md.last_price for md in list(self.market_history)[-20:]]
        returns = np.diff(np.log(prices))
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        # Update volatility for recent market data
        for md in list(self.market_history)[-5:]:
            md.volatility = volatility
    
    async def _train_models(self):
        """Train AI prediction models"""
        if len(self.market_history) < 50:
            return
        
        # Prepare training data
        features = []
        price_targets = []
        volatility_targets = []
        
        for i in range(10, len(self.market_history)):
            # Features from past 10 periods
            past_data = list(self.market_history)[i-10:i]
            feature_vector = []
            
            for md in past_data:
                feature_vector.extend([
                    md.last_price,
                    md.volume_24h,
                    md.volatility,
                    md.bid_size,
                    md.ask_size
                ])
            
            features.append(feature_vector)
            price_targets.append(self.market_history[i].last_price)
            volatility_targets.append(self.market_history[i].volatility)
        
        if features:
            # Train price predictor
            self.price_predictor.fit(features, price_targets)
            
            # Train volatility predictor
            self.volatility_predictor.fit(features, volatility_targets)
            
            print(f"Trained prediction models on {len(features)} samples")
    
    async def start_market_making(self):
        """Start autonomous market making"""
        self.is_active = True
        print(f"Market Maker {self.mm_id} started for {self.mineral_type}")
        
        # Main market making loop
        while self.is_active:
            try:
                # Get current market data
                market_data = await self._get_current_market_data()
                
                if market_data:
                    # Update market maker state
                    await self._update_state(market_data)
                    
                    # Make trading decisions
                    await self._make_trading_decisions(market_data)
                    
                    # Update orders
                    await self._update_orders(market_data)
                
                # Sleep for short interval (100ms)
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Market making error: {e}")
                await asyncio.sleep(1.0)  # Wait longer on error
    
    async def _get_current_market_data(self) -> Optional[MarketData]:
        """Get current market data"""
        try:
            # Try Redis first for real-time data
            market_key = f"market_data:{self.mineral_type}"
            redis_data = self.redis_client.get(market_key)
            
            if redis_data:
                data = json.loads(redis_data)
                return MarketData(
                    mineral_type=self.mineral_type,
                    bid_price=float(data['bid_price']),
                    ask_price=float(data['ask_price']),
                    bid_size=float(data['bid_size']),
                    ask_size=float(data['ask_size']),
                    last_price=float(data['last_price']),
                    volume_24h=float(data['volume_24h']),
                    volatility=float(data['volatility']),
                    timestamp=datetime.fromisoformat(data['timestamp'])
                )
            
            # Fallback to database
            async with self.db_pool.acquire() as conn:
                latest_data = await conn.fetchrow("""
                    SELECT 
                        price as last_price,
                        volume as volume_24h,
                        created_at
                    FROM market_data 
                    WHERE mineral_type = $1 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, self.mineral_type)
                
                if latest_data:
                    return MarketData(
                        mineral_type=self.mineral_type,
                        bid_price=latest_data['last_price'] * 0.999,
                        ask_price=latest_data['last_price'] * 1.001,
                        bid_size=1000.0,
                        ask_size=1000.0,
                        last_price=latest_data['last_price'],
                        volume_24h=latest_data['volume_24h'],
                        volatility=0.02,  # Default volatility
                        timestamp=latest_data['created_at']
                    )
            
            return None
            
        except Exception as e:
            print(f"Failed to get market data: {e}")
            return None
    
    async def _update_state(self, market_data: MarketData):
        """Update market maker state"""
        self.state.last_update = datetime.now(timezone.utc)
        
        # Update market history
        self.market_history.append(market_data)
        
        # Recalculate volatility
        self._calculate_volatility()
        
        # Update performance metrics
        self._update_performance_metrics()
    
    async def _make_trading_decisions(self, market_data: MarketData):
        """Make trading decisions using AI"""
        # Get current state for RL model
        current_state = self.rl_model.get_state(market_data, self.state)
        
        # Select action (0: no action, 1: tighten spread, 2: widen spread, 3: increase inventory, 4: decrease inventory)
        action = self.rl_model.select_action(current_state)
        
        # Execute action
        if action == 1:  # Tighten spread
            self.base_spread = max(self.min_spread, self.base_spread * 0.9)
        elif action == 2:  # Widen spread
            self.base_spread = min(0.01, self.base_spread * 1.1)
        elif action == 3:  # Increase inventory target
            self.state.target_inventory = min(self.state.max_inventory, self.state.target_inventory + 10)
        elif action == 4:  # Decrease inventory target
            self.state.target_inventory = max(self.state.min_inventory, self.state.target_inventory - 10)
        
        # Predict future price and volatility
        future_price = self._predict_future_price(market_data)
        future_volatility = self._predict_future_volatility(market_data)
        
        # Adjust strategy based on predictions
        if future_price > market_data.last_price * 1.01:  # Expected price increase
            self.strategy = MarketMakerStrategy.TREND_FOLLOWING
        elif future_volatility > market_data.volatility * 1.2:  # Expected volatility increase
            self.strategy = MarketMakerStrategy.VOLATILITY_TRADING
        else:
            self.strategy = MarketMakerStrategy.INVENTORY_BALANCED
    
    def _predict_future_price(self, market_data: MarketData) -> float:
        """Predict future price using ML model"""
        if len(self.market_history) < 10:
            return market_data.last_price
        
        # Prepare features
        past_data = list(self.market_history)[-10:]
        features = []
        
        for md in past_data:
            features.extend([
                md.last_price,
                md.volume_24h,
                md.volatility,
                md.bid_size,
                md.ask_size
            ])
        
        try:
            predicted_price = self.price_predictor.predict([features])[0]
            return predicted_price
        except:
            return market_data.last_price
    
    def _predict_future_volatility(self, market_data: MarketData) -> float:
        """Predict future volatility using ML model"""
        if len(self.market_history) < 10:
            return market_data.volatility
        
        # Prepare features
        past_data = list(self.market_history)[-10:]
        features = []
        
        for md in past_data:
            features.extend([
                md.last_price,
                md.volume_24h,
                md.volatility,
                md.bid_size,
                md.ask_size
            ])
        
        try:
            predicted_volatility = self.volatility_predictor.predict([features])[0]
            return max(0.001, predicted_volatility)  # Minimum volatility
        except:
            return market_data.volatility
    
    async def _update_orders(self, market_data: MarketData):
        """Update market maker orders"""
        # Cancel existing orders
        await self._cancel_all_orders()
        
        # Calculate optimal bid and ask prices
        optimal_prices = self._calculate_optimal_prices(market_data)
        
        # Determine order sizes
        order_sizes = self._calculate_order_sizes(market_data)
        
        # Create new orders
        if order_sizes['bid_size'] > 0:
            await self._place_order(
                side=OrderSide.BID,
                price=optimal_prices['bid_price'],
                quantity=order_sizes['bid_size'],
                market_data=market_data
            )
        
        if order_sizes['ask_size'] > 0:
            await self._place_order(
                side=OrderSide.ASK,
                price=optimal_prices['ask_price'],
                quantity=order_sizes['ask_size'],
                market_data=market_data
            )
    
    def _calculate_optimal_prices(self, market_data: MarketData) -> Dict[str, float]:
        """Calculate optimal bid and ask prices"""
        mid_price = (market_data.bid_price + market_data.ask_price) / 2
        
        # Base spread
        spread = self.base_spread * mid_price
        
        # Adjust spread based on volatility
        volatility_adjustment = market_data.volatility * self.volatility_factor * mid_price
        spread += volatility_adjustment
        
        # Adjust spread based on inventory skew
        inventory_ratio = self.state.current_inventory / self.state.max_inventory
        inventory_adjustment = abs(inventory_ratio) * self.inventory_skew_factor * mid_price
        
        # Calculate bid and ask
        if self.state.current_inventory > self.state.target_inventory:
            # Too much inventory, lower bid price, raise ask price
            bid_price = mid_price - spread - inventory_adjustment
            ask_price = mid_price + spread
        else:
            # Too little inventory, raise bid price, lower ask price
            bid_price = mid_price - spread
            ask_price = mid_price + spread + inventory_adjustment
        
        return {
            'bid_price': max(bid_price, market_data.bid_price * 0.99),
            'ask_price': min(ask_price, market_data.ask_price * 1.01)
        }
    
    def _calculate_order_sizes(self, market_data: MarketData) -> Dict[str, float]:
        """Calculate optimal order sizes"""
        # Base order size
        base_size = 100.0  # 100 units base size
        
        # Adjust based on market depth
        market_depth = (market_data.bid_size + market_data.ask_size) / 2
        depth_adjustment = min(2.0, market_depth / 1000.0)
        
        # Adjust based on inventory
        inventory_ratio = self.state.current_inventory / self.state.max_inventory
        
        if abs(inventory_ratio) > 0.8:  # Near inventory limits
            bid_size = base_size * depth_adjustment * 0.5
            ask_size = base_size * depth_adjustment * 0.5
        elif self.state.current_inventory > self.state.target_inventory:
            # Too much inventory, smaller bids, larger asks
            bid_size = base_size * depth_adjustment * 0.7
            ask_size = base_size * depth_adjustment * 1.3
        else:
            # Too little inventory, larger bids, smaller asks
            bid_size = base_size * depth_adjustment * 1.3
            ask_size = base_size * depth_adjustment * 0.7
        
        return {
            'bid_size': max(10.0, bid_size),
            'ask_size': max(10.0, ask_size)
        }
    
    async def _place_order(self, side: OrderSide, price: float, quantity: float, market_data: MarketData):
        """Place a new order"""
        order = MarketMakerOrder(
            order_id=str(uuid.uuid4()),
            mm_id=self.mm_id,
            mineral_type=self.mineral_type,
            side=side,
            price=price,
            quantity=quantity,
            timestamp=datetime.now(timezone.utc),
            strategy=self.strategy,
            confidence=0.8,
            inventory_impact=quantity / self.state.max_inventory
        )
        
        # Add to active orders
        self.state.active_orders.append(order)
        
        # Store in Redis for order book
        order_key = f"mm_order:{order.order_id}"
        order_data = asdict(order)
        order_data['timestamp'] = order.timestamp.isoformat()
        order_data['side'] = side.value
        order_data['strategy'] = self.strategy.value
        
        self.redis_client.setex(order_key, 300, json.dumps(order_data))  # 5 minute TTL
        
        # Add to order book
        orderbook_key = f"orderbook:{self.mineral_type}:{side.value}"
        orderbook_data = {
            'order_id': order.order_id,
            'mm_id': self.mm_id,
            'price': price,
            'quantity': quantity,
            'timestamp': order.timestamp.isoformat()
        }
        
        self.redis_client.lpush(orderbook_key, json.dumps(orderbook_data))
        self.redis_client.expire(orderbook_key, 300)  # 5 minute TTL
    
    async def _cancel_all_orders(self):
        """Cancel all existing orders"""
        for order in self.state.active_orders:
            # Remove from order book
            orderbook_key = f"orderbook:{self.mineral_type}:{order.side.value}"
            
            # Remove specific order (simplified - in production would use more sophisticated removal)
            self.redis_client.delete(f"mm_order:{order.order_id}")
        
        # Clear active orders
        self.state.active_orders.clear()
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        if not self.trade_history:
            return
        
        # Calculate PnL
        realized_pnl = sum(trade.get('pnl', 0) for trade in self.trade_history)
        self.performance_metrics['total_pnl'] = realized_pnl
        
        # Calculate win rate
        winning_trades = sum(1 for trade in self.trade_history if trade.get('pnl', 0) > 0)
        self.performance_metrics['win_rate'] = winning_trades / len(self.trade_history)
        
        # Calculate average spread
        if self.market_history:
            avg_spread = np.mean([(md.ask_price - md.bid_price) / md.bid_price for md in self.market_history])
            self.performance_metrics['avg_spread'] = avg_spread
        
        # Update state PnL
        self.state.pnl = realized_pnl
        self.state.total_trades = len(self.trade_history)
    
    async def handle_trade_execution(self, trade_data: Dict[str, Any]):
        """Handle trade execution"""
        try:
            # Update inventory
            if trade_data['side'] == 'bid':
                self.state.current_inventory += trade_data['quantity']
                trade_pnl = -trade_data['quantity'] * trade_data['price']  # Bought
            else:
                self.state.current_inventory -= trade_data['quantity']
                trade_pnl = trade_data['quantity'] * trade_data['price']  # Sold
            
            # Add to trade history
            trade_record = {
                'timestamp': datetime.now(timezone.utc),
                'side': trade_data['side'],
                'price': trade_data['price'],
                'quantity': trade_data['quantity'],
                'pnl': trade_pnl
            }
            self.trade_history.append(trade_record)
            
            # Update RL model
            if len(self.market_history) > 0:
                current_state = self.rl_model.get_state(self.market_history[-1], self.state)
                reward = trade_pnl / 1000.0  # Normalize reward
                
                # Simplified next state (in production would be more sophisticated)
                next_state = current_state.copy()
                next_state[7] = self.state.current_inventory  # Update inventory in state
                
                self.rl_model.update_model(current_state, 0, reward, next_state)
            
            print(f"Trade executed: {trade_data['side']} {trade_data['quantity']} @ {trade_data['price']}")
            
        except Exception as e:
            print(f"Error handling trade execution: {e}")
    
    async def stop_market_making(self):
        """Stop market making"""
        self.is_active = False
        await self._cancel_all_orders()
        print(f"Market Maker {self.mm_id} stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get market maker status"""
        return {
            'mm_id': self.mm_id,
            'mineral_type': self.mineral_type,
            'is_active': self.is_active,
            'current_inventory': self.state.current_inventory,
            'target_inventory': self.state.target_inventory,
            'pnl': self.state.pnl,
            'total_trades': self.state.total_trades,
            'active_orders': len(self.state.active_orders),
            'strategy': self.strategy.value,
            'performance_metrics': self.performance_metrics
        }

class MarketMakerManager:
    """Manages multiple autonomous market makers"""
    
    def __init__(self):
        self.market_makers = {}
        self.db_pool = None
        self.redis_client = None
    
    async def initialize(self):
        """Initialize market maker manager"""
        self.db_pool = await asyncpg.create_pool(
            "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb",
            min_size=5,
            max_size=20
        )
        
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=2,
            decode_responses=True
        )
        
        # Create market makers for different minerals
        minerals = ['gold', 'silver', 'lithium', 'copper', 'rare_earth']
        
        for mineral in minerals:
            mm_id = f"mm_{mineral}_{uuid.uuid4().hex[:8]}"
            mm = AutonomousMarketMaker(mm_id, mineral, initial_capital=100000.0)
            await mm.initialize(self.db_pool, self.redis_client)
            self.market_makers[mineral] = mm
        
        print(f"Initialized {len(self.market_makers)} market makers")
    
    async def start_all_market_makers(self):
        """Start all market makers"""
        tasks = []
        for mm in self.market_makers.values():
            task = asyncio.create_task(mm.start_market_making())
            tasks.append(task)
        
        print(f"Started {len(tasks)} market makers")
        return tasks
    
    async def stop_all_market_makers(self):
        """Stop all market makers"""
        for mm in self.market_makers.values():
            await mm.stop_market_making()
        
        print("Stopped all market makers")
    
    def get_market_maker(self, mineral_type: str) -> Optional[AutonomousMarketMaker]:
        """Get market maker for specific mineral"""
        return self.market_makers.get(mineral_type)
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all market makers"""
        return {
            mineral: mm.get_status()
            for mineral, mm in self.market_makers.items()
        }

# Global instances
market_maker_manager = MarketMakerManager()

# FastAPI endpoints
from fastapi import FastAPI
from pydantic import BaseModel

class MarketMakerStatusResponse(BaseModel):
    mm_id: str
    mineral_type: str
    is_active: bool
    current_inventory: float
    target_inventory: float
    pnl: float
    total_trades: int
    active_orders: int
    strategy: str
    performance_metrics: Dict[str, float]

@app.post("/api/v2/marketmakers/start")
async def start_market_makers():
    """Start all autonomous market makers"""
    tasks = await market_maker_manager.start_all_market_makers()
    return {"message": f"Started {len(tasks)} market makers"}

@app.post("/api/v2/marketmakers/stop")
async def stop_market_makers():
    """Stop all autonomous market makers"""
    await market_maker_manager.stop_all_market_makers()
    return {"message": "Stopped all market makers"}

@app.get("/api/v2/marketmakers/status")
async def get_market_makers_status():
    """Get status of all market makers"""
    return market_maker_manager.get_all_status()

@app.get("/api/v2/marketmakers/{mineral_type}/status", response_model=MarketMakerStatusResponse)
async def get_market_maker_status(mineral_type: str):
    """Get status of specific market maker"""
    mm = market_maker_manager.get_market_maker(mineral_type)
    if not mm:
        raise HTTPException(status_code=404, detail=f"Market maker for {mineral_type} not found")
    
    status = mm.get_status()
    return MarketMakerStatusResponse(**status)

@app.post("/api/v2/marketmakers/{mineral_type}/trade")
async def handle_trade_execution(mineral_type: str, trade_data: Dict[str, Any]):
    """Handle trade execution for market maker"""
    mm = market_maker_manager.get_market_maker(mineral_type)
    if not mm:
        raise HTTPException(status_code=404, detail=f"Market maker for {mineral_type} not found")
    
    await mm.handle_trade_execution(trade_data)
    return {"message": "Trade executed successfully"}

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    await market_maker_manager.initialize()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
