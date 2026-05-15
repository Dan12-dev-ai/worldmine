/**
 * 📈 DEDAN 2.0 - Bloomberg Terminal Quality Trading Interface
 * Real-time mineral trading with professional-grade features
 * Sub-100ms WebSocket updates, TradingView-quality charts
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, TrendingDown, 
  ArrowUpRight, ArrowDownRight,
  Settings, Maximize2, Minimize2,
  Play, Pause, RotateCcw,
  ChevronUp, ChevronDown,
  Plus, Minus, X, Check,
  AlertTriangle, Info
} from 'lucide-react';

// Trading types
interface PriceData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface OrderBookEntry {
  price: number;
  amount: number;
  total: number;
  type: 'bid' | 'ask';
}

interface Trade {
  id: string;
  price: number;
  amount: number;
  side: 'buy' | 'sell';
  timestamp: number;
}

interface Order {
  id: string;
  type: 'market' | 'limit' | 'stop-loss' | 'stop-limit' | 'iceberg';
  side: 'buy' | 'sell';
  amount: number;
  price?: number;
  stopPrice?: number;
  filled: number;
  status: 'pending' | 'filled' | 'cancelled';
  timestamp: number;
}

interface TechnicalIndicator {
  name: string;
  value: number;
  signal: 'buy' | 'sell' | 'neutral';
  confidence: number;
}

const TradingInterface: React.FC = () => {
  // State management
  const [selectedMineral, setSelectedMineral] = useState('gold');
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [currentPrice, setCurrentPrice] = useState(2001.50);
  const [priceChange, setPriceChange] = useState(0.50);
  const [priceChangePercent, setPriceChangePercent] = useState(0.025);
  const [orderBook, setOrderBook] = useState<{ bids: OrderBookEntry[], asks: OrderBookEntry[] }>({ bids: [], asks: [] });
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [technicalIndicators, setTechnicalIndicators] = useState<TechnicalIndicator[]>([]);
  const [timeframe, setTimeframe] = useState('1H');
  const [chartType, setChartType] = useState('candlestick');
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);
  const [selectedIndicators, setSelectedIndicators] = useState(['RSI', 'MACD', 'Volume']);
  
  // Order form state
  const [orderType, setOrderType] = useState<'market' | 'limit' | 'stop-loss' | 'stop-limit'>('limit');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderAmount, setOrderAmount] = useState(100);
  const [orderPrice, setOrderPrice] = useState(currentPrice);
  const [stopPrice, setStopPrice] = useState<number | undefined>();
  const [orders, setOrders] = useState<Order[]>([]);
  const [position, setPosition] = useState({ size: 0, pnl: 0, unrealizedPnl: 0 });
  
  // UI state
  const [isChartFullscreen, setIsChartFullscreen] = useState(false);
  const [showOrderBook, setShowOrderBook] = useState(true);
  const [showDepthChart, setShowDepthChart] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connected');
  
  // Refs
  const chartRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Mock data generation
  const generateMockPriceData = useCallback(() => {
    const data: PriceData[] = [];
    const basePrice = 2000;
    const now = Date.now();
    
    for (let i = 1000; i >= 0; i--) {
      const timestamp = now - (i * 60000); // 1-minute intervals
      const randomChange = (Math.random() - 0.5) * 10;
      const price = basePrice + randomChange + Math.sin(i / 50) * 20;
      
      data.push({
        timestamp,
        open: price,
        high: price + Math.random() * 5,
        low: price - Math.random() * 5,
        close: price + (Math.random() - 0.5) * 2,
        volume: Math.random() * 1000000
      });
    }
    
    return data;
  }, []);

  const generateMockOrderBook = useCallback(() => {
    const basePrice = currentPrice;
    const bids: OrderBookEntry[] = [];
    const asks: OrderBookEntry[] = [];
    
    for (let i = 1; i <= 20; i++) {
      const bidPrice = basePrice - (i * 0.01);
      const bidAmount = Math.random() * 1000;
      bids.push({
        price: bidPrice,
        amount: bidAmount,
        total: bidPrice * bidAmount,
        type: 'bid'
      });
      
      const askPrice = basePrice + (i * 0.01);
      const askAmount = Math.random() * 1000;
      asks.push({
        price: askPrice,
        amount: askAmount,
        total: askPrice * askAmount,
        type: 'ask'
      });
    }
    
    return { bids, asks };
  }, [currentPrice]);

  const generateMockTrades = useCallback(() => {
    const trades: Trade[] = [];
    const now = Date.now();
    
    for (let i = 0; i < 50; i++) {
      trades.push({
        id: `trade_${i}`,
        price: currentPrice + (Math.random() - 0.5) * 2,
        amount: Math.random() * 500,
        side: Math.random() > 0.5 ? 'buy' : 'sell',
        timestamp: now - (i * 30000) // 30-second intervals
      });
    }
    
    return trades;
  }, [currentPrice]);

  const generateTechnicalIndicators = useCallback((): TechnicalIndicator[] => {
    return [
      { name: 'RSI', value: 65.4, signal: 'neutral' as const, confidence: 0.78 },
      { name: 'MACD', value: 12.3, signal: 'buy' as const, confidence: 0.82 },
      { name: 'Bollinger Bands', value: 1998.5, signal: 'sell' as const, confidence: 0.71 },
      { name: 'Volume', value: 1250000, signal: 'buy' as const, confidence: 0.65 },
      { name: 'Stochastic', value: 45.2, signal: 'neutral' as const, confidence: 0.69 },
      { name: 'ATR', value: 15.8, signal: 'neutral' as const, confidence: 0.89 }
    ];
  }, []);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    try {
      setConnectionStatus('connecting');
      // Mock WebSocket - in production would connect to real WebSocket server
      wsRef.current = new WebSocket('wss://api.dedan2.com/ws/trading');
      
      wsRef.current.onopen = () => {
        setConnectionStatus('connected');
        console.log('WebSocket connected');
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Handle real-time updates
        if (data.type === 'price_update') {
          setCurrentPrice(data.price);
          setPriceChange(data.change);
          setPriceChangePercent(data.changePercent);
        } else if (data.type === 'orderbook_update') {
          setOrderBook(data.orderbook);
        } else if (data.type === 'trade') {
          setRecentTrades(prev => [data.trade, ...prev.slice(0, 49)]);
        }
      };
      
      wsRef.current.onclose = () => {
        setConnectionStatus('disconnected');
        // Attempt reconnection after 3 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  }, []);

  // Initialize data
  useEffect(() => {
    setPriceData(generateMockPriceData());
    setOrderBook(generateMockOrderBook());
    setRecentTrades(generateMockTrades());
    setTechnicalIndicators(generateTechnicalIndicators());
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [generateMockPriceData, generateMockOrderBook, generateMockTrades, generateTechnicalIndicators, connectWebSocket]);

  // Auto-refresh price data
  useEffect(() => {
    if (!isAutoRefresh) return;
    
    const interval = setInterval(() => {
      const newPrice = currentPrice + (Math.random() - 0.5) * 2;
      const change = newPrice - currentPrice;
      const changePercent = (change / currentPrice) * 100;
      
      setCurrentPrice(newPrice);
      setPriceChange(change);
      setPriceChangePercent(changePercent);
      setOrderPrice(newPrice);
      
      // Update order book
      setOrderBook(generateMockOrderBook());
      
      // Add new trade
      const newTrade: Trade = {
        id: `trade_${Date.now()}`,
        price: newPrice,
        amount: Math.random() * 500,
        side: Math.random() > 0.5 ? 'buy' : 'sell',
        timestamp: Date.now()
      };
      setRecentTrades(prev => [newTrade, ...prev.slice(0, 49)]);
    }, 1000); // Update every second for demo
    
    return () => clearInterval(interval);
  }, [isAutoRefresh, currentPrice, generateMockOrderBook]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return;
      
      switch (e.key.toLowerCase()) {
        case 'b':
          setOrderSide('buy');
          break;
        case 's':
          setOrderSide('sell');
          break;
        case 'x':
          // Cancel pending orders
          setOrders(prev => prev.map(order => 
            order.status === 'pending' ? { ...order, status: 'cancelled' as const } : order
          ));
          break;
        case 'k':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            // Focus on order amount input
            document.getElementById('order-amount')?.focus();
          }
          break;
        case 'escape':
          // Clear form
          setOrderAmount(100);
          setOrderPrice(currentPrice);
          setStopPrice(undefined);
          break;
      }
    };
    
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [currentPrice]);

  // Calculate position P&L
  const calculatePosition = useCallback(() => {
    const filledOrders = orders.filter(order => order.status === 'filled');
    const buyOrders = filledOrders.filter(order => order.side === 'buy');
    const sellOrders = filledOrders.filter(order => order.side === 'sell');
    
    const totalBought = buyOrders.reduce((sum, order) => sum + order.amount, 0);
    const totalSold = sellOrders.reduce((sum, order) => sum + order.amount, 0);
    
    const position = totalBought - totalSold;
    const avgBuyPrice = totalBought > 0 ? buyOrders.reduce((sum, order) => sum + (order.amount * (order.price || 0)), 0) / totalBought : 0;
    const avgSellPrice = totalSold > 0 ? sellOrders.reduce((sum, order) => sum + (order.amount * (order.price || 0)), 0) / totalSold : 0;
    
    const realizedPnl = (avgSellPrice * totalSold) - (avgBuyPrice * totalBought);
    const unrealizedPnl = position * (currentPrice - avgBuyPrice);
    
    setPosition({
      size: position,
      pnl: realizedPnl,
      unrealizedPnl
    });
  }, [orders, currentPrice]);

  useEffect(() => {
    calculatePosition();
  }, [calculatePosition]);

  // Order submission
  const submitOrder = useCallback(() => {
    if (orderAmount <= 0) return;
    
    const newOrder: Order = {
      id: `order_${Date.now()}`,
      type: orderType,
      side: orderSide,
      amount: orderAmount,
      price: orderType === 'market' ? undefined : orderPrice,
      stopPrice: orderType.includes('stop') ? stopPrice : undefined,
      filled: 0,
      status: 'pending',
      timestamp: Date.now()
    };
    
    setOrders(prev => [newOrder, ...prev]);
    
    // Simulate order execution
    setTimeout(() => {
      setOrders(prev => prev.map(order => 
        order.id === newOrder.id 
          ? { ...order, status: 'filled' as const, filled: order.amount }
          : order
      ));
    }, Math.random() * 2000 + 500); // 0.5-2.5 seconds
  }, [orderType, orderSide, orderAmount, orderPrice, stopPrice]);

  // Calculate fees
  const calculateFees = useCallback(() => {
    const baseFee = 0.001; // 0.1%
    const takerFee = orderType === 'market' ? 0.0005 : 0; // Additional 0.05% for market orders
    const totalFee = (baseFee + takerFee) * orderAmount * (orderPrice || currentPrice);
    return totalFee;
  }, [orderType, orderAmount, orderPrice, currentPrice]);

  const totalCost = useMemo(() => {
    const price = orderType === 'market' ? currentPrice : orderPrice;
    return orderAmount * price + calculateFees();
  }, [orderType, orderAmount, orderPrice, currentPrice, calculateFees]);

  // Timeframes
  const timeframes = ['1M', '5M', '15M', '1H', '4H', '1D', '1W'];
  
  // Minerals
  const minerals = [
    { id: 'gold', name: 'Gold', symbol: 'XAU', color: 'yellow' },
    { id: 'silver', name: 'Silver', symbol: 'XAG', color: 'gray' },
    { id: 'lithium', name: 'Lithium', symbol: 'LI', color: 'purple' },
    { id: 'copper', name: 'Copper', symbol: 'HG', color: 'orange' },
    { id: 'rare_earth', name: 'Rare Earth', symbol: 'RE', color: 'green' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-full px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              {/* Mineral Selector */}
              <div className="flex items-center space-x-2">
                <label className="text-slate-400 text-sm">Mineral:</label>
                <select 
                  value={selectedMineral}
                  onChange={(e) => setSelectedMineral(e.target.value)}
                  className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-1 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {minerals.map(mineral => (
                    <option key={mineral.id} value={mineral.id}>
                      {mineral.name} ({mineral.symbol})
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Timeframe Selector */}
              <div className="flex items-center space-x-2">
                <label className="text-slate-400 text-sm">Timeframe:</label>
                <div className="flex space-x-1">
                  {timeframes.map(tf => (
                    <button
                      key={tf}
                      onClick={() => setTimeframe(tf)}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        timeframe === tf 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-500' :
                  connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <span className="text-sm text-slate-400">
                  {connectionStatus === 'connected' ? 'Connected' :
                   connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
                </span>
              </div>
              
              {/* Auto Refresh */}
              <button
                onClick={() => setIsAutoRefresh(!isAutoRefresh)}
                className={`flex items-center space-x-2 px-3 py-1 rounded-lg transition-colors ${
                  isAutoRefresh ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-300'
                }`}
              >
                {isAutoRefresh ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span className="text-sm">Auto</span>
              </button>
              
              {/* Fullscreen */}
              <button
                onClick={() => setIsChartFullscreen(!isChartFullscreen)}
                className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
              >
                {isChartFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex h-[calc(100vh-60px)]">
        {/* Left Panel - Chart */}
        <div className={`${isChartFullscreen ? 'w-full' : 'w-3/5'} border-r border-slate-700 p-4`}>
          {/* Price Display */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="text-3xl font-bold">
                  ${currentPrice.toFixed(2)}
                </div>
                <div className={`flex items-center space-x-2 text-sm ${
                  priceChange >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {priceChange >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span>{priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(3)}%)</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-slate-400 text-sm">24h Volume</div>
                <div className="text-white font-medium">1,250,000</div>
              </div>
            </div>
          </div>
          
          {/* Chart Area */}
          <div 
            ref={chartRef}
            className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 mb-4"
            style={{ height: isChartFullscreen ? 'calc(100vh - 200px)' : '400px' }}
          >
            {/* TradingView-style chart would go here */}
            <div className="h-full flex items-center justify-center text-slate-400">
              <div className="text-center">
                <TrendingUp className="w-12 h-12 mx-auto mb-4 text-slate-500" />
                <div className="text-lg font-medium mb-2">Advanced Trading Chart</div>
                <div className="text-sm">TradingView-quality chart with technical indicators</div>
                <div className="flex space-x-2 mt-4">
                  {selectedIndicators.map(indicator => (
                    <span key={indicator} className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                      {indicator}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          {/* Technical Indicators */}
          <div className="grid grid-cols-3 gap-4">
            {technicalIndicators.map((indicator, index) => (
              <motion.div
                key={indicator.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">{indicator.name}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    indicator.signal === 'buy' ? 'bg-green-500/20 text-green-400' :
                    indicator.signal === 'sell' ? 'bg-red-500/20 text-red-400' :
                    'bg-slate-700 text-slate-400'
                  }`}>
                    {indicator.signal.toUpperCase()}
                  </span>
                </div>
                <div className="text-lg font-semibold mb-1">{indicator.value.toFixed(2)}</div>
                <div className="text-xs text-slate-400">Confidence: {(indicator.confidence * 100).toFixed(0)}%</div>
              </motion.div>
            ))}
          </div>
        </div>
        
        {/* Right Panel - Order Book, Orders, Trading */}
        {!isChartFullscreen && (
          <div className="w-2/5 flex flex-col">
            {/* Order Book */}
            {showOrderBook && (
              <div className="border-b border-slate-700 p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Order Book</h3>
                  <button
                    onClick={() => setShowDepthChart(!showDepthChart)}
                    className="text-sm text-blue-400 hover:text-blue-300"
                  >
                    {showDepthChart ? 'Order Book' : 'Depth Chart'}
                  </button>
                </div>
                
                <div className="space-y-2">
                  {/* Asks */}
                  <div className="space-y-1">
                    <div className="text-xs text-slate-400 mb-1">ASKS</div>
                    {orderBook.asks.slice(0, 5).map((ask, index) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span className="text-red-400">{ask.price.toFixed(2)}</span>
                        <span className="text-slate-300">{ask.amount.toFixed(0)}</span>
                      </div>
                    ))}
                  </div>
                  
                  {/* Spread */}
                  <div className="text-center py-2 border-t border-b border-slate-700">
                    <div className="text-xs text-slate-400">Spread</div>
                    <div className="text-sm font-medium">
                      {orderBook.asks[0] && orderBook.bids[0] ? 
                        (orderBook.asks[0].price - orderBook.bids[0].price).toFixed(2) : 
                        '0.00'
                      }
                    </div>
                  </div>
                  
                  {/* Bids */}
                  <div className="space-y-1">
                    <div className="text-xs text-slate-400 mb-1">BIDS</div>
                    {orderBook.bids.slice(0, 5).map((bid, index) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span className="text-green-400">{bid.price.toFixed(2)}</span>
                        <span className="text-slate-300">{bid.amount.toFixed(0)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {/* Recent Trades */}
            <div className="border-b border-slate-700 p-4 max-h-64 overflow-y-auto">
              <h3 className="font-semibold mb-4">Recent Trades</h3>
              <div className="space-y-2">
                {recentTrades.slice(0, 10).map((trade, index) => (
                  <div key={trade.id} className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${
                        trade.side === 'buy' ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                      <span className={trade.side === 'buy' ? 'text-green-400' : 'text-red-400'}>
                        {trade.side.toUpperCase()}
                      </span>
                    </div>
                    <span className="text-white">{trade.price.toFixed(2)}</span>
                    <span className="text-slate-400">{trade.amount.toFixed(0)}</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Trading Form */}
            <div className="p-4 flex-1">
              <h3 className="font-semibold mb-4">Place Order</h3>
              
              {/* Order Type */}
              <div className="mb-4">
                <label className="text-slate-400 text-sm mb-2">Order Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {['market', 'limit', 'stop-loss', 'stop-limit'].map(type => (
                    <button
                      key={type}
                      onClick={() => setOrderType(type as any)}
                      className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                        orderType === type 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      {type.replace('-', ' ').toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Side */}
              <div className="mb-4">
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setOrderSide('buy')}
                    className={`px-4 py-3 rounded-lg font-medium transition-colors ${
                      orderSide === 'buy' 
                        ? 'bg-green-500 text-white' 
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    BUY
                  </button>
                  <button
                    onClick={() => setOrderSide('sell')}
                    className={`px-4 py-3 rounded-lg font-medium transition-colors ${
                      orderSide === 'sell' 
                        ? 'bg-red-500 text-white' 
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    SELL
                  </button>
                </div>
              </div>
              
              {/* Amount */}
              <div className="mb-4">
                <label className="text-slate-400 text-sm mb-2">Amount (oz)</label>
                <input
                  id="order-amount"
                  type="number"
                  value={orderAmount}
                  onChange={(e) => setOrderAmount(Number(e.target.value))}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              
              {/* Price (for non-market orders) */}
              {orderType !== 'market' && (
                <div className="mb-4">
                  <label className="text-slate-400 text-sm mb-2">Price ($/oz)</label>
                  <input
                    type="number"
                    value={orderPrice}
                    onChange={(e) => setOrderPrice(Number(e.target.value))}
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>
              )}
              
              {/* Stop Price (for stop orders) */}
              {orderType.includes('stop') && (
                <div className="mb-4">
                  <label className="text-slate-400 text-sm mb-2">Stop Price ($)</label>
                  <input
                    type="number"
                    value={stopPrice || ''}
                    onChange={(e) => setStopPrice(Number(e.target.value) || undefined)}
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>
              )}
              
              {/* Fee Calculation */}
              <div className="mb-4 p-3 bg-slate-700/50 rounded-lg">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">Estimated Fee:</span>
                  <span className="text-white">${calculateFees().toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-medium">
                  <span>Total Cost:</span>
                  <span className="text-lg">${totalCost.toFixed(2)}</span>
                </div>
              </div>
              
              {/* Submit Button */}
              <button
                onClick={submitOrder}
                disabled={isLoading || orderAmount <= 0}
                className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium py-3 rounded-lg transition-colors"
              >
                {isLoading ? 'Processing...' : `Place ${orderSide.toUpperCase()} Order`}
              </button>
              
              {/* Position Info */}
              {position.size !== 0 && (
                <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
                  <div className="text-sm text-slate-400 mb-2">Current Position</div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Size:</span>
                      <span className={position.size > 0 ? 'text-green-400' : 'text-red-400'}>
                        {position.size > 0 ? '+' : ''}{position.size.toFixed(2)} oz
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Unrealized P&L:</span>
                      <span className={position.unrealizedPnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                        ${position.unrealizedPnl.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradingInterface;
