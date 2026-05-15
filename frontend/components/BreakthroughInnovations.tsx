/**
 * 🌍 DEDAN 2.0 - Breakthrough Innovations Interface
 * Revolutionary features to beat all competitors in mineral trading
 * Quantum computing, AI agents, blockchain, and advanced analytics
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, Brain, Cpu, Atom, Shield, TrendingUp,
  Activity, BarChart3, PieChart, LineChart,
  Globe, Network, Lock, Eye, Target,
  Rocket, Sparkles, Gauge, AlertTriangle,
  CheckCircle, X, RefreshCw, Settings,
  Bell, BellOff, Filter, Search,
  ChevronDown, ChevronUp, Info, ExternalLink,
  Download, Share2, Play, Pause,
  SkipForward, FastForward, Database,
  Cloud, Server, Terminal, Code,
  Microscope, Telescope, Satellite,
  Compass, Navigation, MapPin,
  DollarSign, Package, Truck,
  Factory, Warehouse, Ship
} from 'lucide-react';

// Innovation data types
interface QuantumPrediction {
  id: string;
  innovation_type: string;
  model_type: string;
  input_data: Record<string, any>;
  prediction: Record<string, any>;
  confidence_score: number;
  quantum_advantage: number;
  classical_comparison: Record<string, any>;
  execution_time_ms: number;
  created_at: string;
}

interface ArbitrageOpportunity {
  id: string;
  mineral_type: string;
  exchange_1: string;
  exchange_2: string;
  price_1: number;
  price_2: number;
  spread_percentage: number;
  volume_1: number;
  volume_2: number;
  transaction_cost: number;
  net_profit_potential: number;
  risk_score: number;
  time_window_seconds: number;
  created_at: string;
}

interface AutonomousNegotiation {
  id: string;
  contract_id: string;
  negotiation_type: string;
  participants: string[];
  current_round: number;
  max_rounds: number;
  proposals: Record<string, any>[];
  optimal_terms: Record<string, any>;
  success_probability: number;
  ai_strategy: string;
  created_at: string;
}

interface BlockchainVerification {
  id: string;
  contract_id: string;
  blockchain_type: string;
  transaction_hash: string;
  verification_status: string;
  smart_contract_address: string;
  gas_used: number;
  confirmation_count: number;
  carbon_offset: number;
  created_at: string;
}

interface InnovationStatistics {
  quantum_predictions_total: number;
  arbitrage_opportunities_total: number;
  average_quantum_advantage: number;
  recent_quantum_predictions_24h: number;
  recent_arbitrage_opportunities_24h: number;
  active_innovations: number;
  innovation_types: string[];
  model_types: string[];
  last_updated: string;
}

interface InnovationFilters {
  innovation_type: string;
  model_type: string;
  status: string;
  time_range: string;
  confidence_min: number;
  quantum_advantage_min: number;
}

const BreakthroughInnovations: React.FC = () => {
  // State management
  const [quantumPredictions, setQuantumPredictions] = useState<QuantumPrediction[]>([]);
  const [arbitrageOpportunities, setArbitrageOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [autonomousNegotiations, setAutonomousNegotiations] = useState<AutonomousNegotiation[]>([]);
  const [blockchainVerifications, setBlockchainVerifications] = useState<BlockchainVerification[]>([]);
  const [statistics, setStatistics] = useState<InnovationStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<InnovationFilters>({
    innovation_type: '',
    model_type: '',
    status: '',
    time_range: '24h',
    confidence_min: 0,
    quantum_advantage_min: 0
  });
  const [selectedInnovation, setSelectedInnovation] = useState<QuantumPrediction | ArbitrageOpportunity | AutonomousNegotiation | BlockchainVerification | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'dashboard' | 'quantum' | 'arbitrage' | 'negotiation' | 'blockchain'>('dashboard');
  const [isEngineRunning, setIsEngineRunning] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [realTimeData, setRealTimeData] = useState<Record<string, any>>({});

  // Mock data generation
  const generateMockQuantumPredictions = useCallback((): QuantumPrediction[] => {
    return [
      {
        id: '1',
        innovation_type: 'quantum_price_prediction',
        model_type: 'quantum_neural_network',
        input_data: {
          mineral_type: 'gold',
          current_price: 64000,
          volume_24h: 1200,
          rsi: 65,
          macd: 150,
          sentiment_score: 0.7,
          supply_index: 0.4,
          demand_index: 0.8,
          geopolitical_risk: 0.2,
          currency_correlation: 0.3
        },
        prediction: {
          predicted_price: 65800,
          quantum_probabilities: {'00000000': 0.15, '00000001': 0.12, '00000010': 0.08},
          confidence_interval: {
            lower_bound: 0.92,
            upper_bound: 1.08,
            confidence_level: 0.85
          },
          market_volatility: 0.23
        },
        confidence_score: 0.85,
        quantum_advantage: 0.23,
        classical_comparison: {
          predicted_price: 64500,
          confidence_score: 0.72
        },
        execution_time_ms: 145,
        created_at: '2024-03-15T10:30:00Z'
      },
      {
        id: '2',
        innovation_type: 'quantum_price_prediction',
        model_type: 'quantum_neural_network',
        input_data: {
          mineral_type: 'lithium',
          current_price: 15000,
          volume_24h: 2500,
          rsi: 58,
          macd: 75,
          sentiment_score: 0.8,
          supply_index: 0.3,
          demand_index: 0.9,
          geopolitical_risk: 0.15,
          currency_correlation: 0.25
        },
        prediction: {
          predicted_price: 15850,
          quantum_probabilities: {'10000000': 0.18, '01000000': 0.14, '00100000': 0.09},
          confidence_interval: {
            lower_bound: 0.94,
            upper_bound: 1.12,
            confidence_level: 0.88
          },
          market_volatility: 0.19
        },
        confidence_score: 0.88,
        quantum_advantage: 0.31,
        classical_comparison: {
          predicted_price: 15200,
          confidence_score: 0.69
        },
        execution_time_ms: 132,
        created_at: '2024-03-15T10:25:00Z'
      }
    ];
  }, []);

  const generateMockArbitrageOpportunities = useCallback((): ArbitrageOpportunity[] => {
    return [
      {
        id: '1',
        mineral_type: 'gold',
        exchange_1: 'kraken',
        exchange_2: 'binance',
        price_1: 63950,
        price_2: 64120,
        spread_percentage: 0.27,
        volume_1: 850,
        volume_2: 1200,
        transaction_cost: 12.5,
        net_profit_potential: 2450,
        risk_score: 0.15,
        time_window_seconds: 30,
        created_at: '2024-03-15T10:35:00Z'
      },
      {
        id: '2',
        mineral_type: 'lithium',
        exchange_1: 'coinbase',
        exchange_2: 'kraken',
        price_1: 14980,
        price_2: 15120,
        spread_percentage: 0.93,
        volume_1: 600,
        volume_2: 450,
        transaction_cost: 8.75,
        net_profit_potential: 1275,
        risk_score: 0.22,
        time_window_seconds: 45,
        created_at: '2024-03-15T10:32:00Z'
      }
    ];
  }, []);

  const generateMockAutonomousNegotiations = useCallback((): AutonomousNegotiation[] => {
    return [
      {
        id: '1',
        contract_id: 'DEDAN-2024-001',
        negotiation_type: 'price',
        participants: ['Swiss Gold Refinery AG', 'Australian Gold Mining Corp'],
        current_round: 7,
        max_rounds: 10,
        proposals: [
          {
            round: 1,
            price_per_ton: 63500,
            payment_terms: 'net_30',
            delivery_days: 35,
            confidence: 0.6
          },
          {
            round: 7,
            price_per_ton: 64200,
            payment_terms: 'net_15',
            delivery_days: 28,
            confidence: 0.85
          }
        ],
        optimal_terms: {
          price_per_ton: 64200,
          payment_terms: 'net_15',
          delivery_days: 28,
          purity_grade: '99.99%'
        },
        success_probability: 0.87,
        ai_strategy: 'multi_objective_optimization',
        created_at: '2024-03-15T09:15:00Z'
      }
    ];
  }, []);

  const generateMockBlockchainVerifications = useCallback((): BlockchainVerification[] => {
    return [
      {
        id: '1',
        contract_id: 'DEDAN-2024-001',
        blockchain_type: 'ethereum',
        transaction_hash: '0x7f9a8b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1',
        verification_status: 'verified',
        smart_contract_address: '0x1234567890123456789012345678901234567890',
        gas_used: 125000,
        confirmation_count: 12,
        carbon_offset: 0.65,
        created_at: '2024-03-15T08:45:00Z'
      }
    ];
  }, []);

  const generateMockStatistics = useCallback((): InnovationStatistics => {
    return {
      quantum_predictions_total: 1247,
      arbitrage_opportunities_total: 89,
      average_quantum_advantage: 0.28,
      recent_quantum_predictions_24h: 156,
      recent_arbitrage_opportunities_24h: 23,
      active_innovations: 8,
      innovation_types: [
        'quantum_price_prediction',
        'ai_market_making',
        'blockchain_verification',
        'real_time_arbitrage',
        'predictive_maintenance',
        'supply_chain_optimization',
        'risk_quantum_modeling',
        'autonomous_negotiation'
      ],
      model_types: [
        'quantum_neural_network',
        'transformer_gpt',
        'random_forest',
        'gradient_boosting',
        'lstm_network',
        'reinforcement_learning',
        'ensemble_model'
      ],
      last_updated: '2024-03-15T10:45:00Z'
    };
  }, []);

  // Filter logic
  const filteredQuantumPredictions = useMemo(() => {
    return quantumPredictions.filter(pred => {
      const matchesSearch = searchQuery === '' || 
        pred.innovation_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pred.model_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pred.input_data.mineral_type?.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesType = !filters.innovation_type || pred.innovation_type === filters.innovation_type;
      const matchesModel = !filters.model_type || pred.model_type === filters.model_type;
      const matchesConfidence = pred.confidence_score >= filters.confidence_min;
      const matchesQuantumAdvantage = pred.quantum_advantage >= filters.quantum_advantage_min;

      return matchesSearch && matchesType && matchesModel && matchesConfidence && matchesQuantumAdvantage;
    });
  }, [quantumPredictions, searchQuery, filters]);

  const filteredArbitrageOpportunities = useMemo(() => {
    return arbitrageOpportunities.filter(opp => {
      const matchesSearch = searchQuery === '' || 
        opp.mineral_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.exchange_1.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.exchange_2.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesType = !filters.innovation_type || filters.innovation_type === 'real_time_arbitrage';
      const matchesProfit = opp.net_profit_potential > 0;

      return matchesSearch && matchesType && matchesProfit;
    });
  }, [arbitrageOpportunities, searchQuery, filters]);

  // Load data on mount
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setQuantumPredictions(generateMockQuantumPredictions());
      setArbitrageOpportunities(generateMockArbitrageOpportunities());
      setAutonomousNegotiations(generateMockAutonomousNegotiations());
      setBlockchainVerifications(generateMockBlockchainVerifications());
      setStatistics(generateMockStatistics());
      setLoading(false);
    }, 1000);
  }, []);

  // Real-time data simulation
  useEffect(() => {
    if (!isEngineRunning) return;

    const interval = setInterval(() => {
      setRealTimeData(prev => ({
        ...prev,
        timestamp: new Date().toISOString(),
        quantum_processing: Math.random() > 0.7,
        arbitrage_scanning: Math.random() > 0.8,
        blockchain_mining: Math.random() > 0.9,
        ai_training: Math.random() > 0.6
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [isEngineRunning]);

  // Get innovation icon
  const getInnovationIcon = (type: string) => {
    switch (type) {
      case 'quantum_price_prediction': return <Atom className="w-5 h-5" />;
      case 'real_time_arbitrage': return <TrendingUp className="w-5 h-5" />;
      case 'autonomous_negotiation': return <Brain className="w-5 h-5" />;
      case 'blockchain_verification': return <Shield className="w-5 h-5" />;
      case 'ai_market_making': return <Cpu className="w-5 h-5" />;
      default: return <Zap className="w-5 h-5" />;
    }
  };

  // Get confidence color
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                🚀 DEDAN 2.0 Breakthrough Innovations
              </h1>
              <span className="text-sm text-slate-400">
                Quantum AI • Blockchain • Revolutionary Trading
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsEngineRunning(!isEngineRunning)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isEngineRunning ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'
                }`}
              >
                {isEngineRunning ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                <span>{isEngineRunning ? 'Engine Running' : 'Engine Stopped'}</span>
              </button>
              
              <button
                onClick={() => setNotifications(!notifications)}
                className="relative p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                {notifications ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
                {realTimeData.quantum_processing && (
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                )}
              </button>
              
              <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-1 backdrop-blur-sm">
          <div className="flex space-x-1">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 className="w-4 h-4" /> },
              { id: 'quantum', label: 'Quantum AI', icon: <Atom className="w-4 h-4" /> },
              { id: 'arbitrage', label: 'Arbitrage', icon: <TrendingUp className="w-4 h-4" /> },
              { id: 'negotiation', label: 'Negotiation', icon: <Brain className="w-4 h-4" /> },
              { id: 'blockchain', label: 'Blockchain', icon: <Shield className="w-4 h-4" /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setViewMode(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  viewMode === tab.id ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex space-x-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search innovations, models, minerals..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-slate-800"
              />
            </div>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
            >
              <Filter className="w-5 h-5" />
              <span>Filters</span>
              <ChevronDown className={`w-4 h-4 transform transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            
            <button className="flex items-center space-x-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors">
              <RefreshCw className="w-5 h-5" />
              <span>Refresh</span>
            </button>
          </div>

          {/* Filters Panel */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-6"
              >
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Innovation Type</label>
                  <select
                    value={filters.innovation_type}
                    onChange={(e) => setFilters({...filters, innovation_type: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">All Types</option>
                    <option value="quantum_price_prediction">Quantum Price Prediction</option>
                    <option value="real_time_arbitrage">Real-Time Arbitrage</option>
                    <option value="autonomous_negotiation">Autonomous Negotiation</option>
                    <option value="blockchain_verification">Blockchain Verification</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Model Type</label>
                  <select
                    value={filters.model_type}
                    onChange={(e) => setFilters({...filters, model_type: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">All Models</option>
                    <option value="quantum_neural_network">Quantum Neural Network</option>
                    <option value="transformer_gpt">Transformer GPT</option>
                    <option value="reinforcement_learning">Reinforcement Learning</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Min Confidence</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={filters.confidence_min}
                    onChange={(e) => setFilters({...filters, confidence_min: Number(e.target.value)})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Min Quantum Advantage</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={filters.quantum_advantage_min}
                    onChange={(e) => setFilters({...filters, quantum_advantage_min: Number(e.target.value)})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Statistics Dashboard */}
      {viewMode === 'dashboard' && statistics && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 border border-purple-500/30 rounded-xl p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-300">Quantum Predictions</p>
                  <p className="text-3xl font-bold text-white">{statistics.quantum_predictions_total}</p>
                  <p className="text-sm text-purple-400">+{statistics.recent_quantum_predictions_24h} in 24h</p>
                </div>
                <Atom className="w-10 h-10 text-purple-400" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-600/20 to-green-800/20 border border-green-500/30 rounded-xl p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-300">Arbitrage Opportunities</p>
                  <p className="text-3xl font-bold text-white">{statistics.arbitrage_opportunities_total}</p>
                  <p className="text-sm text-green-400">+{statistics.recent_arbitrage_opportunities_24h} in 24h</p>
                </div>
                <TrendingUp className="w-10 h-10 text-green-400" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 border border-blue-500/30 rounded-xl p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-300">Quantum Advantage</p>
                  <p className="text-3xl font-bold text-white">{(statistics.average_quantum_advantage * 100).toFixed(1)}%</p>
                  <p className="text-sm text-blue-400">Avg. improvement</p>
                </div>
                <Zap className="w-10 h-10 text-blue-400" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-orange-600/20 to-orange-800/20 border border-orange-500/30 rounded-xl p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-300">Active Innovations</p>
                  <p className="text-3xl font-bold text-white">{statistics.active_innovations}</p>
                  <p className="text-sm text-orange-400">Running now</p>
                </div>
                <Cpu className="w-10 h-10 text-orange-400" />
              </div>
            </div>
          </div>

          {/* Real-time Status */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
            <h3 className="text-xl font-semibold text-white mb-4">Real-time Engine Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${realTimeData.quantum_processing ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                <span className="text-slate-300">Quantum Processing</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${realTimeData.arbitrage_scanning ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                <span className="text-slate-300">Arbitrage Scanning</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${realTimeData.blockchain_mining ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                <span className="text-slate-300">Blockchain Mining</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${realTimeData.ai_training ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                <span className="text-slate-300">AI Training</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quantum Predictions */}
      {viewMode === 'quantum' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-6">Quantum Price Predictions</h2>
            
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {filteredQuantumPredictions.map((prediction) => (
                  <motion.div
                    key={prediction.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-slate-700/50 border border-slate-600/50 rounded-xl p-6 hover:bg-slate-700/70 transition-colors cursor-pointer"
                    onClick={() => setSelectedInnovation(prediction)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center space-x-3 mb-2">
                          <Atom className="w-5 h-5 text-purple-400" />
                          <span className="text-lg font-semibold text-white">
                            {prediction.input_data.mineral_type?.toUpperCase() || 'UNKNOWN'}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(prediction.confidence_score)}`}>
                            {(prediction.confidence_score * 100).toFixed(1)}% confidence
                          </span>
                        </div>
                        <p className="text-slate-300">
                          Predicted: {formatCurrency(prediction.prediction.predicted_price)} | 
                          Current: {formatCurrency(prediction.input_data.current_price)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-slate-400">Quantum Advantage</p>
                        <p className="text-xl font-bold text-purple-400">
                          +{(prediction.quantum_advantage * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Classical Comparison</p>
                        <p className="text-white">{formatCurrency(prediction.classical_comparison.predicted_price)}</p>
                        <p className="text-xs text-slate-500">
                          {(prediction.classical_comparison.confidence_score * 100).toFixed(1)}% confidence
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Market Volatility</p>
                        <p className="text-white">{(prediction.prediction.market_volatility * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Execution Time</p>
                        <p className="text-white">{prediction.execution_time_ms}ms</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Arbitrage Opportunities */}
      {viewMode === 'arbitrage' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-6">Real-Time Arbitrage Opportunities</h2>
            
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {filteredArbitrageOpportunities.map((opportunity) => (
                  <motion.div
                    key={opportunity.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-slate-700/50 border border-slate-600/50 rounded-xl p-6 hover:bg-slate-700/70 transition-colors cursor-pointer"
                    onClick={() => setSelectedInnovation(opportunity)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center space-x-3 mb-2">
                          <TrendingUp className="w-5 h-5 text-green-400" />
                          <span className="text-lg font-semibold text-white">
                            {opportunity.mineral_type.toUpperCase()}
                          </span>
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                            {opportunity.spread_percentage.toFixed(2)}% spread
                          </span>
                        </div>
                        <p className="text-slate-300">
                          Buy: {opportunity.exchange_1} @ {formatCurrency(opportunity.price_1)} | 
                          Sell: {opportunity.exchange_2} @ {formatCurrency(opportunity.price_2)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-slate-400">Net Profit</p>
                        <p className="text-xl font-bold text-green-400">
                          {formatCurrency(opportunity.net_profit_potential)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Volume 1</p>
                        <p className="text-white">{opportunity.volume_1.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Volume 2</p>
                        <p className="text-white">{opportunity.volume_2.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Transaction Cost</p>
                        <p className="text-white">{formatCurrency(opportunity.transaction_cost)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Risk Score</p>
                        <p className="text-white">{(opportunity.risk_score * 100).toFixed(1)}%</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Innovation Details Modal */}
      <AnimatePresence>
        {selectedInnovation && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-slate-800 border border-slate-700 rounded-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">Innovation Details</h2>
                  <button
                    onClick={() => setSelectedInnovation(null)}
                    className="p-2 hover:bg-slate-700 rounded-full transition-colors"
                  >
                    <X className="w-5 h-5 text-slate-400" />
                  </button>
                </div>
                
                <div className="space-y-6">
                  {/* Content based on innovation type */}
                  {'innovation_type' in selectedInnovation ? (
                    // Quantum Prediction Details
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-4">Quantum Price Prediction</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="text-md font-medium text-slate-300 mb-3">Prediction Results</h4>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-slate-400">Predicted Price:</span>
                              <span className="text-white font-bold">
                                {formatCurrency(selectedInnovation.prediction.predicted_price)}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Confidence:</span>
                              <span className={`font-medium ${getConfidenceColor(selectedInnovation.confidence_score)}`}>
                                {(selectedInnovation.confidence_score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Quantum Advantage:</span>
                              <span className="text-purple-400 font-medium">
                                +{(selectedInnovation.quantum_advantage * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>
                        <div>
                          <h4 className="text-md font-medium text-slate-300 mb-3">Technical Details</h4>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-slate-400">Model Type:</span>
                              <span className="text-white">{selectedInnovation.model_type}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Execution Time:</span>
                              <span className="text-white">{selectedInnovation.execution_time_ms}ms</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Created:</span>
                              <span className="text-white">
                                {new Date(selectedInnovation.created_at).toLocaleString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : 'mineral_type' in selectedInnovation ? (
                    // Arbitrage Opportunity Details
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-4">Arbitrage Opportunity</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="text-md font-medium text-slate-300 mb-3">Opportunity Details</h4>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-slate-400">Mineral:</span>
                              <span className="text-white font-bold">
                                {selectedInnovation.mineral_type.toUpperCase()}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Spread:</span>
                              <span className="text-green-400 font-medium">
                                {selectedInnovation.spread_percentage.toFixed(2)}%
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Net Profit:</span>
                              <span className="text-green-400 font-bold">
                                {formatCurrency(selectedInnovation.net_profit_potential)}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div>
                          <h4 className="text-md font-medium text-slate-300 mb-3">Exchange Details</h4>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-slate-400">Buy Exchange:</span>
                              <span className="text-white">{selectedInnovation.exchange_1}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Sell Exchange:</span>
                              <span className="text-white">{selectedInnovation.exchange_2}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Time Window:</span>
                              <span className="text-white">{selectedInnovation.time_window_seconds}s</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
                
                {/* Actions */}
                <div className="flex items-center space-x-4 mt-6 pt-6 border-t border-slate-700">
                  <button className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                    <Play className="w-4 h-4" />
                    <span>Execute</span>
                  </button>
                  <button className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors">
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
                  </button>
                  <button className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors">
                    <Download className="w-4 h-4" />
                    <span>Export</span>
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default BreakthroughInnovations;
