/**
 * 🌍 DEDAN 2.0 - Daily Mineral News Interface
 * Real-time mineral market news with AI-powered analysis
 * Better than Bloomberg, Reuters, and MarketWatch for mineral intelligence
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, TrendingDown, AlertTriangle, Globe, Clock,
  Calendar, Filter, Search, Eye, MessageSquare, Share2,
  Bookmark, ExternalLink, Zap, BarChart3, Newspaper,
  ChevronDown, ChevronUp, X, RefreshCw, Info,
  Star, Users, MapPin, Award, Target, Activity,
  DollarSign, Package, Ship, Factory, Building,
  Briefcase, FileText, Settings, Bell, BellOff,
  List
} from 'lucide-react';

// News data types
interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  content: string;
  url: string;
  source: string;
  category: string;
  author: string;
  published_at: string;
  sentiment: string;
  impact_level: string;
  mentioned_minerals: string[];
  mentioned_companies: string[];
  mentioned_countries: string[];
  price_impact: Record<string, number>;
  ai_analysis: string;
  relevance_score: number;
  verification_status: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

interface NewsFilters {
  category: string;
  sentiment: string;
  impact_level: string;
  source: string;
  minerals: string[];
  time_range: string;
  verified_only: boolean;
}

interface NewsStatistics {
  total_articles: number;
  category_distribution: Record<string, number>;
  impact_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  recent_articles_24h: number;
  last_updated: string;
}

const MineralNewsInterface: React.FC = () => {
  // State management
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<NewsFilters>({
    category: '',
    sentiment: '',
    impact_level: '',
    source: '',
    minerals: [],
    time_range: '24h',
    verified_only: false
  });
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'cards' | 'list' | 'compact'>('cards');
  const [sortBy, setSortBy] = useState<'relevance' | 'time' | 'impact' | 'sentiment'>('relevance');
  const [bookmarkedArticles, setBookmarkedArticles] = useState<string[]>([]);
  const [notifications, setNotifications] = useState(true);
  const [statistics, setStatistics] = useState<NewsStatistics | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);

  // Mock data generation
  const generateMockNews = useCallback((): NewsArticle[] => {
    return [
      {
        id: '1',
        title: 'Major Gold Discovery in Chile Could Impact Global Supply',
        summary: 'Chilean mining company announces significant gold deposit discovery, potentially affecting global gold prices and supply chains.',
        content: 'Chilean state mining company Codelco announced today the discovery of a major gold deposit in the Atacama Desert region. The discovery, estimated to contain over 10 million ounces of gold, could significantly impact global gold supply and pricing dynamics. Mining experts suggest this discovery could help offset declining production from established mines and provide new investment opportunities in the region.',
        url: 'https://example.com/gold-discovery-chile',
        source: 'mining_com',
        category: 'discoveries',
        author: 'Mining Reporter',
        published_at: '2024-03-15T10:30:00Z',
        sentiment: 'positive',
        impact_level: 'high',
        mentioned_minerals: ['gold'],
        mentioned_companies: ['codelco'],
        mentioned_countries: ['chile'],
        price_impact: { 'gold': -5.2 },
        ai_analysis: 'This discovery could lead to a short-term price decline for gold due to increased future supply expectations. However, the actual impact will depend on extraction timeline and production costs. Investors should monitor the development timeline and potential regulatory approvals.',
        relevance_score: 8.5,
        verification_status: 'verified',
        tags: ['gold', 'discovery', 'chile', 'supply', 'codelco'],
        created_at: '2024-03-15T10:30:00Z',
        updated_at: '2024-03-15T10:30:00Z'
      },
      {
        id: '2',
        title: 'Lithium Prices Surge as EV Demand Accelerates',
        summary: 'Global lithium carbonate prices jump 15% this week as electric vehicle manufacturers scramble to secure long-term supply contracts.',
        content: 'Lithium carbonate prices have surged by 15% this week, reaching record highs as electric vehicle manufacturers intensify efforts to secure long-term supply contracts. The price increase reflects growing demand from the EV sector and supply constraints from major producers. Industry analysts predict continued upward pressure on lithium prices throughout 2024.',
        url: 'https://example.com/lithium-prices-surge',
        source: 'reuters',
        category: 'market_updates',
        author: 'Commodities Correspondent',
        published_at: '2024-03-15T09:15:00Z',
        sentiment: 'positive',
        impact_level: 'critical',
        mentioned_minerals: ['lithium'],
        mentioned_companies: ['tesla', 'byd', 'albemarle'],
        mentioned_countries: ['china', 'australia', 'chile'],
        price_impact: { 'lithium': 15.0 },
        ai_analysis: 'The lithium price surge reflects fundamental supply-demand imbalances in the EV battery market. With EV adoption accelerating globally, lithium demand is expected to outpace supply growth through 2025. This creates significant opportunities for lithium producers and potential challenges for battery manufacturers.',
        relevance_score: 9.2,
        verification_status: 'verified',
        tags: ['lithium', 'ev', 'prices', 'demand', 'supply'],
        created_at: '2024-03-15T09:15:00Z',
        updated_at: '2024-03-15T09:15:00Z'
      },
      {
        id: '3',
        title: 'New EU Regulations Impact Rare Earth Mining Operations',
        summary: 'European Union introduces stricter environmental regulations for rare earth mining, potentially affecting global supply chains.',
        content: 'The European Union has introduced new environmental regulations that will significantly impact rare earth mining operations. The new rules require mining companies to meet stricter environmental standards and implement comprehensive sustainability measures. Industry experts warn that these regulations could lead to supply disruptions and increased costs for rare earth elements critical to technology and defense applications.',
        url: 'https://example.com/eu-rare-earth-regulations',
        source: 'financial_times',
        category: 'regulatory',
        author: 'Policy Analyst',
        published_at: '2024-03-15T08:45:00Z',
        sentiment: 'negative',
        impact_level: 'high',
        mentioned_minerals: ['rare_earth'],
        mentioned_companies: ['lynas', 'mp materials'],
        mentioned_countries: ['european_union', 'china', 'australia'],
        price_impact: { 'rare_earth': 8.5 },
        ai_analysis: 'The new EU regulations represent a significant shift in rare earth mining policy. While environmentally beneficial, these rules could create supply bottlenecks and increase production costs. Companies with existing sustainable mining practices may gain competitive advantages.',
        relevance_score: 7.8,
        verification_status: 'verified',
        tags: ['rare_earth', 'regulations', 'european_union', 'environment', 'sustainability'],
        created_at: '2024-03-15T08:45:00Z',
        updated_at: '2024-03-15T08:45:00Z'
      },
      {
        id: '4',
        title: 'Copper Production Decline in Peru Amid Labor Strikes',
        summary: 'Major copper mines in Peru face production disruptions as workers strike for better wages and working conditions.',
        content: 'Peru\'s copper mining sector is facing significant production disruptions as workers at major mines launch strikes demanding better wages and improved working conditions. The strikes have already reduced daily copper output by an estimated 30%, affecting global copper supply. Mining companies are negotiating with union representatives, but no immediate resolution is expected.',
        url: 'https://example.com/peru-copper-strikes',
        source: 'bloomberg',
        category: 'mining_operations',
        author: 'Mining Correspondent',
        published_at: '2024-03-15T07:20:00Z',
        sentiment: 'negative',
        impact_level: 'medium',
        mentioned_minerals: ['copper'],
        mentioned_companies: ['freeport-mcmoran', 'southern copper'],
        mentioned_countries: ['peru'],
        price_impact: { 'copper': 4.2 },
        ai_analysis: 'The labor strikes in Peru highlight the ongoing challenges in copper mining operations. With Peru being a major copper producer, these disruptions could support copper prices in the short term. Investors should monitor the duration of strikes and potential spillover effects to other mining regions.',
        relevance_score: 6.9,
        verification_status: 'verified',
        tags: ['copper', 'peru', 'strikes', 'labor', 'production'],
        created_at: '2024-03-15T07:20:00Z',
        updated_at: '2024-03-15T07:20:00Z'
      },
      {
        id: '5',
        title: 'Breakthrough Technology Enables Deep-Sea Mineral Extraction',
        summary: 'New deep-sea mining technology promises to unlock vast mineral resources from ocean floors with minimal environmental impact.',
        content: 'A breakthrough in deep-sea mining technology could unlock vast mineral resources from ocean floors while minimizing environmental impact. The new system uses advanced robotics and AI to extract minerals from deep-sea nodules with unprecedented precision. Environmental groups have cautiously welcomed the technology, which promises to reduce the ecological footprint of deep-sea mining operations.',
        url: 'https://example.com/deep-sea-mining-technology',
        source: 'technology_today',
        category: 'technology',
        author: 'Tech Reporter',
        published_at: '2024-03-15T06:00:00Z',
        sentiment: 'positive',
        impact_level: 'high',
        mentioned_minerals: ['manganese', 'nickel', 'cobalt', 'copper'],
        mentioned_companies: ['deep_sea_resources', 'ocean_minerals'],
        mentioned_countries: ['international_waters'],
        price_impact: { 'manganese': -3.5, 'nickel': -2.8, 'cobalt': -4.1, 'copper': -1.9 },
        ai_analysis: 'This technological breakthrough could fundamentally change the mining industry by providing access to previously untapped resources. However, regulatory and environmental challenges remain. The technology\'s commercial viability and scalability will be key factors in its market impact.',
        relevance_score: 8.1,
        verification_status: 'pending',
        tags: ['technology', 'deep_sea', 'innovation', 'environment', 'manganese', 'nickel', 'cobalt'],
        created_at: '2024-03-15T06:00:00Z',
        updated_at: '2024-03-15T06:00:00Z'
      }
    ];
  }, []);

  // Filter and search logic
  const filteredArticles = useMemo(() => {
    return articles.filter(article => {
      const matchesSearch = searchQuery === '' || 
        article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        article.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
        article.content.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = !filters.category || article.category === filters.category;
      const matchesSentiment = !filters.sentiment || article.sentiment === filters.sentiment;
      const matchesImpact = !filters.impact_level || article.impact_level === filters.impact_level;
      const matchesSource = !filters.source || article.source === filters.source;
      const matchesMinerals = filters.minerals.length === 0 || 
        filters.minerals.some(mineral => article.mentioned_minerals.includes(mineral));
      const matchesTime = (() => {
        const now = new Date();
        const articleTime = new Date(article.published_at);
        const diffInHours = Math.floor((now.getTime() - articleTime.getTime()) / (1000 * 60 * 60));
        
        switch (filters.time_range) {
          case '1h': return diffInHours < 1;
          case '24h': return diffInHours < 24;
          case '7d': return diffInHours < 168; // 7 days
          case '30d': return diffInHours < 720; // 30 days
          default: return true;
        }
      })();
      const matchesVerified = !filters.verified_only || article.verification_status === 'verified';

      return matchesSearch && matchesCategory && matchesSentiment && 
             matchesImpact && matchesSource && matchesMinerals && 
             matchesTime && matchesVerified;
    });
  }, [articles, searchQuery, filters]);

  // Sort logic
  const sortedArticles = useMemo(() => {
    const sorted = [...filteredArticles];
    
    switch (sortBy) {
      case 'relevance':
        return sorted.sort((a, b) => b.relevance_score - a.relevance_score);
      case 'time':
        return sorted.sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime());
      case 'impact':
        const impactOrder = { 'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'informational': 1 };
        return sorted.sort((a, b) => impactOrder[b.impact_level as keyof typeof impactOrder] - impactOrder[a.impact_level as keyof typeof impactOrder]);
      case 'sentiment':
        const sentimentOrder = { 'very_positive': 5, 'positive': 4, 'neutral': 3, 'negative': 2, 'very_negative': 1 };
        return sorted.sort((a, b) => sentimentOrder[b.sentiment as keyof typeof sentimentOrder] - sentimentOrder[a.sentiment as keyof typeof sentimentOrder]);
      default:
        return sorted;
    }
  }, [filteredArticles, sortBy]);

  // Load articles on mount
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setArticles(generateMockNews());
      setTotalResults(generateMockNews().length);
      setLoading(false);
    }, 1000);
  }, []);

  // Toggle bookmark
  const toggleBookmark = (articleId: string) => {
    setBookmarkedArticles(prev => 
      prev.includes(articleId) 
        ? prev.filter(id => id !== articleId)
        : [...prev, articleId]
    );
  };

  // Get sentiment color
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'very_positive': return 'text-green-500';
      case 'positive': return 'text-green-400';
      case 'neutral': return 'text-gray-400';
      case 'negative': return 'text-red-400';
      case 'very_negative': return 'text-red-500';
      default: return 'text-gray-400';
    }
  };

  // Get impact color
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      case 'informational': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  // Format time ago
  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                📰 DEDAN 2.0 Mineral News
              </h1>
              <span className="text-sm text-slate-400">
                Real-time market intelligence • AI-powered analysis
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setNotifications(!notifications)}
                className="relative p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                {notifications ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
              </button>
              
              <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Search and Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
          {/* Search Bar */}
          <div className="flex space-x-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search mineral news, companies, countries..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800"
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
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode('cards')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'cards' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <Globe className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <FileText className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('compact')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'compact' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800"
            >
              <option value="relevance">Most Relevant</option>
              <option value="time">Latest First</option>
              <option value="impact">Highest Impact</option>
              <option value="sentiment">Sentiment</option>
            </select>
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
                  <label className="block text-sm font-medium text-slate-300 mb-2">Category</label>
                  <select
                    value={filters.category}
                    onChange={(e) => setFilters({...filters, category: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Categories</option>
                    <option value="market_updates">Market Updates</option>
                    <option value="discoveries">Discoveries</option>
                    <option value="regulatory">Regulatory</option>
                    <option value="technology">Technology</option>
                    <option value="sustainability">Sustainability</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Sentiment</label>
                  <select
                    value={filters.sentiment}
                    onChange={(e) => setFilters({...filters, sentiment: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Sentiments</option>
                    <option value="very_positive">Very Positive</option>
                    <option value="positive">Positive</option>
                    <option value="neutral">Neutral</option>
                    <option value="negative">Negative</option>
                    <option value="very_negative">Very Negative</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Impact Level</label>
                  <select
                    value={filters.impact_level}
                    onChange={(e) => setFilters({...filters, impact_level: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Impact Levels</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Time Range</label>
                  <select
                    value={filters.time_range}
                    onChange={(e) => setFilters({...filters, time_range: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="1h">Last Hour</option>
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last Week</option>
                    <option value="30d">Last Month</option>
                  </select>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* News Articles */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="space-y-6">
            {sortedArticles.map((article) => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm hover:bg-slate-800/70 transition-colors cursor-pointer"
                onClick={() => setSelectedArticle(article)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(article.impact_level)}`}>
                        {article.impact_level.toUpperCase()}
                      </span>
                      <span className="text-xs text-slate-400">
                        {formatTimeAgo(article.published_at)}
                      </span>
                      <span className="text-xs text-slate-400">
                        {article.source}
                      </span>
                      {article.verification_status === 'verified' && (
                        <span className="text-xs text-green-400 flex items-center">
                          <Award className="w-3 h-3 mr-1" />
                          Verified
                        </span>
                      )}
                    </div>
                    
                    <h3 className="text-xl font-semibold text-white mb-2">
                      {article.title}
                    </h3>
                    
                    <p className="text-slate-300 mb-3">
                      {article.summary}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-sm">
                      <span className={`flex items-center ${getSentimentColor(article.sentiment)}`}>
                        {article.sentiment === 'positive' || article.sentiment === 'very_positive' ? (
                          <TrendingUp className="w-4 h-4 mr-1" />
                        ) : article.sentiment === 'negative' || article.sentiment === 'very_negative' ? (
                          <TrendingDown className="w-4 h-4 mr-1" />
                        ) : (
                          <Activity className="w-4 h-4 mr-1" />
                        )}
                        {article.sentiment}
                      </span>
                      
                      {article.mentioned_minerals.length > 0 && (
                        <span className="text-slate-400">
                          <Package className="w-4 h-4 inline mr-1" />
                          {article.mentioned_minerals.join(', ')}
                        </span>
                      )}
                      
                      {article.mentioned_countries.length > 0 && (
                        <span className="text-slate-400">
                          <MapPin className="w-4 h-4 inline mr-1" />
                          {article.mentioned_countries.join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleBookmark(article.id);
                      }}
                      className="p-2 hover:bg-slate-700 rounded-full transition-colors"
                    >
                      <Bookmark className={`w-4 h-4 ${bookmarkedArticles.includes(article.id) ? 'text-blue-500 fill-current' : 'text-slate-400'}`} />
                    </button>
                    <button className="p-2 hover:bg-slate-700 rounded-full transition-colors">
                      <Share2 className="w-4 h-4 text-slate-400" />
                    </button>
                    <button className="p-2 hover:bg-slate-700 rounded-full transition-colors">
                      <ExternalLink className="w-4 h-4 text-slate-400" />
                    </button>
                  </div>
                </div>
                
                {/* Price Impact */}
                {Object.keys(article.price_impact).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-700/50">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Price Impact</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(article.price_impact).map(([mineral, impact]) => (
                        <span
                          key={mineral}
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            impact > 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {mineral}: {impact > 0 ? '+' : ''}{impact.toFixed(1)}%
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Article Detail Modal */}
      <AnimatePresence>
        {selectedArticle && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-slate-800 border border-slate-700 rounded-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">{selectedArticle.title}</h2>
                  <button
                    onClick={() => setSelectedArticle(null)}
                    className="p-2 hover:bg-slate-700 rounded-full transition-colors"
                  >
                    <X className="w-5 h-5 text-slate-400" />
                  </button>
                </div>
                
                <div className="space-y-6">
                  {/* Article Meta */}
                  <div className="flex items-center space-x-4 text-sm text-slate-400">
                    <span>{selectedArticle.source}</span>
                    <span>•</span>
                    <span>{formatTimeAgo(selectedArticle.published_at)}</span>
                    <span>•</span>
                    <span>By {selectedArticle.author}</span>
                  </div>
                  
                  {/* Impact and Sentiment */}
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getImpactColor(selectedArticle.impact_level)}`}>
                      {selectedArticle.impact_level.toUpperCase()} IMPACT
                    </span>
                    <span className={`text-sm font-medium ${getSentimentColor(selectedArticle.sentiment)}`}>
                      {selectedArticle.sentiment.toUpperCase()}
                    </span>
                  </div>
                  
                  {/* Content */}
                  <div className="prose prose-invert max-w-none">
                    <p className="text-slate-300 leading-relaxed">
                      {selectedArticle.content}
                    </p>
                  </div>
                  
                  {/* AI Analysis */}
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-2">AI Analysis</h3>
                    <p className="text-slate-300">{selectedArticle.ai_analysis}</p>
                  </div>
                  
                  {/* Mentions */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {selectedArticle.mentioned_minerals.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-slate-300 mb-2">Minerals</h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedArticle.mentioned_minerals.map(mineral => (
                            <span key={mineral} className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs">
                              {mineral}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {selectedArticle.mentioned_companies.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-slate-300 mb-2">Companies</h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedArticle.mentioned_companies.map(company => (
                            <span key={company} className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs">
                              {company}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {selectedArticle.mentioned_countries.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-slate-300 mb-2">Countries</h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedArticle.mentioned_countries.map(country => (
                            <span key={country} className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs">
                              {country}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Tags */}
                  <div>
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedArticle.tags.map(tag => (
                        <span key={tag} className="px-2 py-1 bg-slate-600 text-slate-300 rounded-full text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center space-x-4 pt-4 border-t border-slate-700">
                    <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <ExternalLink className="w-4 h-4" />
                      <span>Read Full Article</span>
                    </button>
                    <button className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors">
                      <Share2 className="w-4 h-4" />
                      <span>Share</span>
                    </button>
                    <button
                      onClick={() => toggleBookmark(selectedArticle.id)}
                      className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
                    >
                      <Bookmark className={`w-4 h-4 ${bookmarkedArticles.includes(selectedArticle.id) ? 'text-blue-500 fill-current' : ''}`} />
                      <span>{bookmarkedArticles.includes(selectedArticle.id) ? 'Bookmarked' : 'Bookmark'}</span>
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MineralNewsInterface;
