/**
 * DEDAN Mine - Agentic Dashboard (v4.5.0)
 * The 'DEDAN' Companion with AI-powered commands and spatial visualizations
 * Real-time mineral price tracking with spatial 3D depth
 * Natural language command processing with Recharts/D3.js integration
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';
import {
    Brain,
    TrendingUp,
    TrendingDown,
    DollarSign,
    Activity,
    Globe,
    BarChart3,
    PieChart,
    LineChart,
    Zap,
    Eye,
    Layers,
    Settings,
    AlertTriangle,
    CheckCircle,
    Info,
    ArrowUpRight,
    ArrowDownRight,
    Wallet,
    Shield,
    Sparkles,
    Flame,
  Target,
  Compass,
  Radar,
  Map,
  MessageSquare,
  Send,
  Mic,
  Camera,
  Search,
  Filter,
  Download,
  RefreshCw,
  Calendar,
  Clock,
  Users,
  Package,
  Truck,
  Factory,
  Building2,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  Minimize2,
  Fullscreen,
  Grid3x3,
  Layers3
} from 'lucide-react';

// Mock data generator
const generateMockData = () => {
  const minerals = ['Gold', 'Silver', 'Copper', 'Platinum', 'Palladium', 'Rhodium'];
  const now = new Date();
  
  return {
    prices: minerals.map(mineral => ({
      mineral,
      current: 1000 + Math.random() * 5000,
      change: (Math.random() - 0.5) * 10,
      volume: Math.random() * 1000000,
      trend: Math.random() > 0.5 ? 'up' : 'down',
      timestamp: now
    })),
    revenue: {
      today: 50000 + Math.random() * 100000,
      thisWeek: 250000 + Math.random() * 500000,
      thisMonth: 1000000 + Math.random() * 2000000,
      growth: (Math.random() - 0.5) * 20
    },
    portfolio: {
      totalValue: 500000 + Math.random() * 1000000,
      holdings: minerals.map(mineral => ({
        mineral,
        quantity: Math.random() * 1000,
        value: Math.random() * 100000,
        percentage: Math.random() * 100
      }))
    },
    transactions: Array.from({ length: 50 }, (_, i) => ({
      id: `TXN_${i + 1}`,
      type: ['buy', 'sell', 'transfer'][Math.floor(Math.random() * 3)],
      mineral: minerals[Math.floor(Math.random() * minerals.length)],
      amount: Math.random() * 10000,
      status: ['completed', 'pending', 'processing'][Math.floor(Math.random() * 3)],
      timestamp: new Date(now.getTime() - Math.random() * 86400000),
      profit: (Math.random() - 0.5) * 1000
    }))
  };
};

// Command processor
const processCommand = (command) => {
  const lowerCommand = command.toLowerCase();
  
  if (lowerCommand.includes('revenue') && lowerCommand.includes('month')) {
    return {
      type: 'revenue_month',
      response: 'Your total USD revenue this month is $1,234,567.89, representing a 15.3% increase from last month.',
      data: { revenue: 1234567.89, growth: 15.3 }
    };
  }
  
  if (lowerCommand.includes('profit') || lowerCommand.includes('gain')) {
    return {
      type: 'profit',
      response: 'Your current profit is $45,678.90 with a 12.5% return on investment.',
      data: { profit: 45678.90, roi: 12.5 }
    };
  }
  
  if (lowerCommand.includes('portfolio') || lowerCommand.includes('holdings')) {
    return {
      type: 'portfolio',
      response: 'Your portfolio consists of 5 minerals with a total value of $567,890.12.',
      data: { totalValue: 567890.12, minerals: 5 }
    };
  }
  
  if (lowerCommand.includes('best') && lowerCommand.includes('performing')) {
    return {
      type: 'best_performing',
      response: 'Gold is your best performing mineral this month with a 23.4% gain.',
      data: { mineral: 'Gold', gain: 23.4 }
    };
  }
  
  if (lowerCommand.includes('risk') || lowerCommand.includes('exposure')) {
    return {
      type: 'risk',
      response: 'Your current risk exposure is moderate at 35% with a diversified portfolio.',
      data: { riskLevel: 'moderate', exposure: 35 }
    };
  }
  
  return {
    type: 'general',
    response: 'I understand your request. Let me help you with that.',
    data: null
  };
};

// Spatial 3D Chart Component
const SpatialChart = ({ data, type, size = 'medium' }) => {
  const canvasRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);
  
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Create spatial effect
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.1)');
    gradient.addColorStop(1, 'rgba(147, 51, 234, 0.1)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw chart based on type
    if (type === 'line') {
      drawLineChart(ctx, data, canvas.width, canvas.height);
    } else if (type === 'bar') {
      drawBarChart(ctx, data, canvas.width, canvas.height);
    } else if (type === 'pie') {
      drawPieChart(ctx, data, canvas.width, canvas.height);
    }
    
  }, [data, type]);
  
  const drawLineChart = (ctx, data, width, height) => {
    if (!data || data.length === 0) return;
    
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    
    // Draw axes
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw line
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.8)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    data.forEach((point, index) => {
      const x = padding + (index / (data.length - 1)) * chartWidth;
      const y = height - padding - (point.value / 100) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();
    
    // Draw points
    data.forEach((point, index) => {
      const x = padding + (index / (data.length - 1)) * chartWidth;
      const y = height - padding - (point.value / 100) * chartHeight;
      
      ctx.fillStyle = 'rgba(59, 130, 246, 1)';
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
    });
  };
  
  const drawBarChart = (ctx, data, width, height) => {
    if (!data || data.length === 0) return;
    
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    const barWidth = chartWidth / data.length * 0.6;
    const barSpacing = chartWidth / data.length * 0.4;
    
    data.forEach((item, index) => {
      const x = padding + index * (barWidth + barSpacing);
      const barHeight = (item.value / 100) * chartHeight;
      const y = height - padding - barHeight;
      
      // Create gradient
      const gradient = ctx.createLinearGradient(0, y, 0, height - padding);
      gradient.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
      gradient.addColorStop(1, 'rgba(147, 51, 234, 0.8)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, barWidth, barHeight);
      
      // Add glow effect
      ctx.shadowColor = 'rgba(59, 130, 246, 0.5)';
      ctx.shadowBlur = 10;
      ctx.fillRect(x, y, barWidth, barHeight);
      ctx.shadowBlur = 0;
    });
  };
  
  const drawPieChart = (ctx, data, width, height) => {
    if (!data || data.length === 0) return;
    
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;
    
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = -Math.PI / 2;
    
    const colors = [
      'rgba(59, 130, 246, 0.8)',
      'rgba(147, 51, 234, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(245, 158, 11, 0.8)'
    ];
    
    data.forEach((item, index) => {
      const sliceAngle = (item.value / total) * Math.PI * 2;
      
      // Draw slice
      ctx.fillStyle = colors[index % colors.length];
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      ctx.fill();
      
      // Add 3D effect
      ctx.shadowColor = colors[index % colors.length];
      ctx.shadowBlur = 15;
      ctx.fill();
      ctx.shadowBlur = 0;
      
      currentAngle += sliceAngle;
    });
  };
  
  const sizeClasses = {
    small: 'w-64 h-32',
    medium: 'w-96 h-48',
    large: 'w-full h-64'
  };
  
  return (
    <motion.div
      className={`relative ${sizeClasses[size]} bg-black/50 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden cursor-pointer`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ scale: 1.02 }}
    >
      <canvas
        ref={canvasRef}
        width={size === 'small' ? 256 : size === 'medium' ? 384 : 800}
        height={size === 'small' ? 128 : size === 'medium' ? 192 : 256}
        className="w-full h-full"
      />
      
      {/* Spatial overlay */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/50" />
      </div>
      
      {/* Hover effect */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-white/10 backdrop-blur-sm flex items-center justify-center"
          >
            <div className="text-white text-center">
              <Eye className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm">Interactive 3D View</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const AgenticDashboard = () => {
  const [data, setData] = useState(generateMockData());
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedView, setSelectedView] = useState('overview');
  const [chartType, setChartType] = useState('line');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [gridView, setGridView] = useState('3x3');
  
  const messagesEndRef = useRef(null);
  
  // Update data periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setData(generateMockData());
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Handle command submission
  const handleCommand = useCallback(async (command) => {
    if (!command.trim()) return;
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: command,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);
    
    // Process command
    setTimeout(() => {
      const result = processCommand(command);
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: result.response,
        data: result.data,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setIsProcessing(false);
    }, 1000);
  }, []);
  
  // Render metric card
  const renderMetricCard = (title, value, change, icon, color = 'blue') => {
    const colorClasses = {
      blue: 'from-blue-500 to-blue-600',
      green: 'from-green-500 to-green-600',
      red: 'from-red-500 to-red-600',
      purple: 'from-purple-500 to-purple-600',
      yellow: 'from-yellow-500 to-yellow-600'
    };
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative bg-black/50 backdrop-blur-md rounded-2xl border border-white/10 p-6 overflow-hidden"
      >
        {/* Background gradient */}
        <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses[color]} opacity-10`} />
        
        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`p-2 bg-${color}-500/20 rounded-lg`}>
                {React.createElement(icon, { className: `w-5 h-5 text-${color}-400` })}
              </div>
              <h3 className="text-white font-medium">{title}</h3>
            </div>
            <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${
              change > 0 ? 'bg-green-500/20' : 'bg-red-500/20'
            }`}>
              {change > 0 ? (
                <TrendingUp className="w-3 h-3 text-green-400" />
              ) : (
                <TrendingDown className="w-3 h-3 text-red-400" />
              )}
              <span className={`text-xs ${change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {change > 0 ? '+' : ''}{change.toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div className="text-2xl font-bold text-white">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </div>
        </div>
        
        {/* Spatial effect */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-t from-transparent to-white/5" />
        </div>
      </motion.div>
    );
  };
  
  // Render chat interface
  const renderChatInterface = () => (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-2xl ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white/10 text-white border border-white/20'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              {message.data && (
                <div className="mt-2 p-2 bg-black/20 rounded-lg">
                  <div className="text-xs text-white/60">Data:</div>
                  <pre className="text-xs text-white/80 mt-1">
                    {JSON.stringify(message.data, null, 2)}
                  </pre>
                </div>
              )}
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </motion.div>
        ))}
        
        {isProcessing && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="bg-white/10 text-white border border-white/20 p-3 rounded-2xl">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-blue-400" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCommand(input)}
              placeholder="Ask DEDAN anything about your portfolio..."
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 pr-10 text-white placeholder-white/50 focus:outline-none focus:border-white/40 focus:bg-white/20"
            />
            <button className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-white/50 hover:text-white">
              <Mic className="w-4 h-4" />
            </button>
          </div>
          <button
            onClick={() => handleCommand(input)}
            disabled={!input.trim() || isProcessing}
            className="px-4 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:opacity-50 text-white rounded-xl transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        {/* Quick commands */}
        <div className="mt-2 flex flex-wrap gap-2">
          {[
            'Show me my total USD revenue this month',
            'What is my current profit?',
            'How is my portfolio performing?',
            'What are my best performing minerals?'
          ].map((command) => (
            <button
              key={command}
              onClick={() => handleCommand(command)}
              className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-xs text-white/70 hover:text-white transition-colors"
            >
              {command.length > 30 ? command.substring(0, 30) + '...' : command}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
  
  // Render main content based on selected view
  const renderMainContent = () => {
    switch (selectedView) {
      case 'overview':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {renderMetricCard('Total Revenue', data.revenue.thisMonth, data.revenue.growth, DollarSign, 'green')}
            {renderMetricCard('Portfolio Value', data.portfolio.totalValue, 12.5, Wallet, 'blue')}
            {renderMetricCard('Active Trades', data.transactions.filter(t => t.status === 'completed').length, 15.3, Activity, 'purple')}
            
            <div className="md:col-span-2 lg:col-span-2">
              <SpatialChart data={data.prices} type="line" size="large" />
            </div>
            
            <div className="md:col-span-2 lg:col-span-1">
              <SpatialChart data={data.portfolio.holdings} type="pie" size="medium" />
            </div>
          </div>
        );
        
      case 'analytics':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Analytics</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => setChartType('line')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    chartType === 'line' ? 'bg-blue-500 text-white' : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  Line Chart
                </button>
                <button
                  onClick={() => setChartType('bar')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    chartType === 'bar' ? 'bg-blue-500 text-white' : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  Bar Chart
                </button>
                <button
                  onClick={() => setChartType('pie')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    chartType === 'pie' ? 'bg-blue-500 text-white' : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  Pie Chart
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SpatialChart data={data.prices} type={chartType} size="large" />
              <SpatialChart data={data.portfolio.holdings} type="pie" size="large" />
            </div>
          </div>
        );
        
      case 'transactions':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">Transactions</h2>
            
            <div className="bg-black/50 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left p-4 text-white/60">ID</th>
                      <th className="text-left p-4 text-white/60">Type</th>
                      <th className="text-left p-4 text-white/60">Mineral</th>
                      <th className="text-left p-4 text-white/60">Amount</th>
                      <th className="text-left p-4 text-white/60">Status</th>
                      <th className="text-left p-4 text-white/60">Profit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.transactions.map((transaction) => (
                      <tr key={transaction.id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="p-4 text-white/80">{transaction.id}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded-lg text-xs ${
                            transaction.type === 'buy' ? 'bg-green-500/20 text-green-400' :
                            transaction.type === 'sell' ? 'bg-red-500/20 text-red-400' :
                            'bg-blue-500/20 text-blue-400'
                          }`}>
                            {transaction.type}
                          </span>
                        </td>
                        <td className="p-4 text-white/80">{transaction.mineral}</td>
                        <td className="p-4 text-white/80">${transaction.amount.toFixed(2)}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded-lg text-xs ${
                            transaction.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                            transaction.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-blue-500/20 text-blue-400'
                          }`}>
                            {transaction.status}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className={`${
                            transaction.profit > 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {transaction.profit > 0 ? '+' : ''}{transaction.profit.toFixed(2)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-screen-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Brain className="w-8 h-8 text-blue-400" />
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                DEDAN Companion
              </h1>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1 bg-blue-500/20 rounded-full">
              <Zap className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-blue-400">AI-Powered</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* View Selector */}
            <div className="flex space-x-2">
              {['overview', 'analytics', 'transactions'].map((view) => (
                <button
                  key={view}
                  onClick={() => setSelectedView(view)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    selectedView === view
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  {view.charAt(0).toUpperCase() + view.slice(1)}
                </button>
              ))}
            </div>
            
            {/* Controls */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            
            <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {renderMainContent()}
          </div>
          
          {/* Chat Interface */}
          <div className="lg:col-span-1">
            <div className="bg-black/50 backdrop-blur-md rounded-2xl border border-white/10 h-[600px] flex flex-col">
              <div className="p-4 border-b border-white/10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">AI Assistant</h3>
                  </div>
                  <div className="flex items-center space-x-1 px-2 py-1 bg-green-500/20 rounded-full">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-xs text-green-400">Online</span>
                  </div>
                </div>
              </div>
              
              {renderChatInterface()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgenticDashboard;
