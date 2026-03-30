import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Newspaper, 
  Clock, 
  ExternalLink,
  ChevronRight,
  AlertTriangle,
  BarChart3,
  Package
} from 'lucide-react';
import { Button } from './ui/button';

interface MarketNews {
  id: string;
  title: string;
  content: string;
  category: 'Economic' | 'Supply' | 'Mini';
  analysis?: string;
  analysis_am?: string;
  source_url?: string;
  price_trend?: {
    direction: 'up' | 'down' | 'stable';
    percentage: number;
    commodity: string;
  };
  priority: number;
  created_at: string;
}

interface NewsHubProps {
  className?: string;
}

const NewsHub: React.FC<NewsHubProps> = ({ className = '' }) => {
  const { t, i18n } = useTranslation();
  const [news, setNews] = useState<MarketNews[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<'All' | 'Economic' | 'Supply' | 'Mini'>('All');
  const [tickerIndex, setTickerIndex] = useState(0);

  const categories = [
    { id: 'All', label: t('news.all'), icon: Newspaper },
    { id: 'Economic', label: t('news.economic'), icon: BarChart3 },
    { id: 'Supply', label: t('news.supply'), icon: Package },
    { id: 'Mini', label: t('news.mini'), icon: Clock }
  ];

  useEffect(() => {
    fetchMarketNews();
    const interval = setInterval(fetchMarketNews, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [selectedCategory]);

  useEffect(() => {
    const tickerInterval = setInterval(() => {
      if (news.length > 0) {
        setTickerIndex((prev) => (prev + 1) % news.length);
      }
    }, 4000);
    return () => clearInterval(tickerInterval);
  }, [news]);

  const fetchMarketNews = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/market-news');
      const data = await response.json();
      
      const filteredNews = selectedCategory === 'All' 
        ? data 
        : data.filter((item: MarketNews) => item.category === selectedCategory);
      
      setNews(filteredNews.sort((a: MarketNews, b: MarketNews) => 
        b.priority - a.priority || new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ));
    } catch (error) {
      console.error('Failed to fetch market news:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriceTrendIcon = (trend: MarketNews['price_trend']) => {
    if (!trend) return null;
    
    switch (trend.direction) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriceTrendColor = (trend: MarketNews['price_trend']) => {
    if (!trend) return 'text-gray-500';
    
    switch (trend.direction) {
      case 'up':
        return 'text-green-500';
      case 'down':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getCategoryColor = (category: MarketNews['category']) => {
    switch (category) {
      case 'Economic':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'Supply':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'Mini':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)}h ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)}d ago`;
    }
  };

  if (loading && news.length === 0) {
    return (
      <div className={`glass-morphism rounded-2xl p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-neon-cyan"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* News Ticker */}
      {news.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-morphism rounded-xl p-4 overflow-hidden"
        >
          <div className="flex items-center space-x-3">
            <Newspaper className="w-5 h-5 text-neon-cyan" />
            <span className="text-sm font-medium text-neon-cyan">Breaking:</span>
            <div className="flex-1 overflow-hidden">
              <AnimatePresence mode="wait">
                <motion.div
                  key={tickerIndex}
                  initial={{ opacity: 0, x: 100 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  className="flex items-center space-x-2"
                >
                  <span className="text-sm text-white truncate">
                    {news[tickerIndex]?.title}
                  </span>
                  {news[tickerIndex]?.price_trend && (
                    <div className="flex items-center space-x-1">
                      {getPriceTrendIcon(news[tickerIndex].price_trend)}
                      <span className={`text-xs font-medium ${getPriceTrendColor(news[tickerIndex].price_trend)}`}>
                        {news[tickerIndex].price_trend.percentage > 0 ? '+' : ''}{news[tickerIndex].price_trend.percentage}%
                      </span>
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </motion.div>
      )}

      {/* Category Filter */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        {categories.map((category) => {
          const Icon = category.icon;
          return (
            <Button
              key={category.id}
              variant={selectedCategory === category.id ? 'default' : 'ghost'}
              onClick={() => setSelectedCategory(category.id as any)}
              className="flex items-center space-x-2 whitespace-nowrap"
            >
              <Icon className="w-4 h-4" />
              <span>{category.label}</span>
            </Button>
          );
        })}
      </div>

      {/* News Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {news.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.1 }}
              className="glass-morphism rounded-xl p-6 hover:border-neon-cyan/50 transition-all duration-300 group"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getCategoryColor(item.category)}`}>
                    {item.category}
                  </span>
                  {item.priority >= 4 && (
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                  )}
                </div>
                <span className="text-xs text-gray-500">
                  {formatTimeAgo(item.created_at)}
                </span>
              </div>

              {/* Title */}
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-neon-cyan transition-colors">
                {item.title}
              </h3>

              {/* Price Trend */}
              {item.price_trend && (
                <div className="flex items-center space-x-2 mb-3 p-2 bg-white/5 rounded-lg">
                  {getPriceTrendIcon(item.price_trend)}
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-300">{item.price_trend.commodity}</span>
                      <span className={`text-sm font-medium ${getPriceTrendColor(item.price_trend)}`}>
                        {item.price_trend.percentage > 0 ? '+' : ''}{item.price_trend.percentage}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Analysis */}
              <div className="mb-4">
                <p className="text-sm text-gray-300 leading-relaxed">
                  {i18n.language === 'am' && item.analysis_am ? item.analysis_am : item.analysis || item.content}
                </p>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <Clock className="w-3 h-3" />
                  <span>{formatTimeAgo(item.created_at)}</span>
                </div>
                {item.source_url && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(item.source_url, '_blank')}
                    className="text-neon-cyan hover:text-neon-cyan/80"
                  >
                    <ExternalLink className="w-3 h-3" />
                  </Button>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Load More */}
      {news.length === 0 && !loading && (
        <div className="text-center py-12">
          <Newspaper className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">No market news available</p>
        </div>
      )}
    </div>
  );
};

export default NewsHub;
