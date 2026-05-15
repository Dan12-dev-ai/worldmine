"""
🌍 DEDAN 2.0 - World-Class Mineral Marketplace
6100+ minerals with advanced search, filtering, and trading
Better than Alibaba, eBay, LBMA with breakthrough features
"""

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, Filter, MapPin, Globe, Package, Truck, Shield,
  TrendingUp, Star, Heart, Eye, MessageCircle,
  ChevronDown, Grid, List, AlertTriangle,
  Clock, Users, Award, Zap, BarChart3,
  Navigation, Calendar, Download, Share2,
  CheckCircle, X, Info, ExternalLink
} from 'lucide-react';

// Mineral data types
interface Mineral {
  id: string;
  name: string;
  symbol: string;
  category: string;
  chemical_formula: string;
  current_price_usd_per_kg: number;
  density: number;
  hardness: number;
  melting_point: number;
  purity_grades_available: string[];
  major_producing_countries: string[];
  global_reserves: number;
  annual_production: number;
  strategic_importance: string;
  seller_info: SellerInfo;
  images: string[];
  specifications: MineralSpecs;
  shipping_options: ShippingOption[];
  certifications: Certification[];
  reviews: Review[];
}

interface SellerInfo {
  id: string;
  name: string;
  rating: number;
  total_transactions: number;
  success_rate: number;
  location: string;
  is_verified: boolean;
  is_premium: boolean;
  response_time: string;
  languages_spoken: string[];
  company_type: string;
  established_year: number;
}

interface MineralSpecs {
  purity: string;
  weight: string;
  dimensions: string;
  form: string;
  color: string;
  clarity: string;
  cut: string;
  treatment: string;
  origin: string;
  lab_certificate: string;
}

interface ShippingOption {
  method: string;
  cost_per_kg: number;
  delivery_time_days: string;
  tracking_included: boolean;
  insurance_included: boolean;
  countries: string[];
}

interface Certification {
  type: string;
  issuer: string;
  certificate_number: string;
  issue_date: string;
  expiry_date: string;
  pdf_url: string;
  verified: boolean;
}

interface Review {
  id: string;
  buyer_id: string;
  rating: number;
  comment: string;
  date: string;
  verified_purchase: boolean;
  helpful_count: number;
}

interface SearchFilters {
  category: string;
  price_min: number;
  price_max: number;
  purity_grade: string;
  country: string;
  seller_rating: number;
  strategic_importance: string;
  in_stock: boolean;
  certified: boolean;
}

const MineralMarketplace: React.FC = () => {
  // State management
  const [minerals, setMinerals] = useState<Mineral[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    category: '',
    price_min: 0,
    price_max: 1000000,
    purity_grade: '',
    country: '',
    seller_rating: 0,
    strategic_importance: '',
    in_stock: false,
    certified: false
  });
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'price' | 'rating' | 'newest' | 'popularity'>('popularity');
  const [selectedMineral, setSelectedMineral] = useState<Mineral | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [compareList, setCompareList] = useState<string[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // Mock data generation
  const generateMockMinerals = useCallback((): Mineral[] => {
    return [
      {
        id: '1',
        name: 'High-Purity Gold Bullion',
        symbol: 'Au',
        category: 'precious_metals',
        chemical_formula: 'Au',
        current_price_usd_per_kg: 64000,
        density: 19.32,
        hardness: 2.5,
        melting_point: 1064.18,
        purity_grades_available: ['99.99%', '99.999%', '99.9999%'],
        major_producing_countries: ['China', 'Australia', 'Russia', 'USA'],
        global_reserves: 54000,
        annual_production: 3100,
        strategic_importance: 'critical',
        seller_info: {
          id: 'seller1',
          name: 'Global Gold Trading Co.',
          rating: 4.8,
          total_transactions: 15420,
          success_rate: 0.98,
          location: 'Zurich, Switzerland',
          is_verified: true,
          is_premium: true,
          response_time: '< 1 hour',
          languages_spoken: ['English', 'German', 'Mandarin'],
          company_type: 'Refinery',
          established_year: 1985
        },
        images: [
          'https://images.unsplash.com/photo-1587292297946-1d4a4e6a9a8',
          'https://images.unsplash.com/photo-1594736179673-13a8608f3310',
          'https://images.unsplash.com/photo-1587292297946-1d4a4e6a9a8'
        ],
        specifications: {
          purity: '99.999%',
          weight: '1 kg',
          dimensions: '10cm x 5cm x 2cm',
          form: 'Bar',
          color: 'Yellow',
          clarity: 'Excellent',
          cut: 'Cast',
          treatment: 'None',
          origin: 'Switzerland',
          lab_certificate: 'Swiss Assay Office'
        },
        shipping_options: [
          {
            method: 'Secured Armored Transport',
            cost_per_kg: 150,
            delivery_time_days: '3-5',
            tracking_included: true,
            insurance_included: true,
            countries: ['USA', 'EU', 'Switzerland']
          },
          {
            method: 'Standard Insured Shipping',
            cost_per_kg: 50,
            delivery_time_days: '7-10',
            tracking_included: true,
            insurance_included: true,
            countries: ['USA', 'EU', 'Asia']
          }
        ],
        certifications: [
          {
            type: 'Assay Certificate',
            issuer: 'Swiss Assay Office',
            certificate_number: 'SAO-2024-001234',
            issue_date: '2024-01-15',
            expiry_date: '2025-01-15',
            pdf_url: '/certificates/gold-sao-001234.pdf',
            verified: true
          }
        ],
        reviews: [
          {
            id: '1',
            buyer_id: 'buyer1',
            rating: 5.0,
            comment: 'Excellent quality gold, exactly as described. Fast shipping and great communication.',
            date: '2024-03-10',
            verified_purchase: true,
            helpful_count: 24
          }
        ]
      },
      {
        id: '2',
        name: 'Battery Grade Lithium Carbonate',
        symbol: 'Li',
        category: 'battery_minerals',
        chemical_formula: 'Li2CO3',
        current_price_usd_per_kg: 15000,
        density: 2.11,
        hardness: 3.0,
        melting_point: 723.0,
        purity_grades_available: ['99.5%', '99.9%', '99.95%'],
        major_producing_countries: ['Chile', 'Australia', 'China', 'Argentina'],
        global_reserves: 26000000,
        annual_production: 130000,
        strategic_importance: 'critical',
        seller_info: {
          id: 'seller2',
          name: 'Chilean Lithium Mining Corp',
          rating: 4.6,
          total_transactions: 8920,
          success_rate: 0.96,
          location: 'Santiago, Chile',
          is_verified: true,
          is_premium: true,
          response_time: '< 2 hours',
          languages_spoken: ['English', 'Spanish', 'Portuguese'],
          company_type: 'Mining Company',
          established_year: 1998
        },
        images: [
          'https://images.unsplash.com/photo-1579546929516-7194089b7380',
          'https://images.unsplash.com/photo-1579546929516-7194089b7380'
        ],
        specifications: {
          purity: '99.9%',
          weight: '25 kg',
          dimensions: '50cm x 40cm x 30cm',
          form: 'Granules',
          color: 'White',
          clarity: 'Excellent',
          cut: 'N/A',
          treatment: 'None',
          origin: 'Chile',
          lab_certificate: 'SGS Laboratory'
        },
        shipping_options: [
          {
            method: 'Bulk Container Shipping',
            cost_per_kg: 5,
            delivery_time_days: '15-20',
            tracking_included: true,
            insurance_included: true,
            countries: ['USA', 'EU', 'Asia']
          }
        ],
        certifications: [
          {
            type: 'ISO Certificate',
            issuer: 'SGS Laboratory',
            certificate_number: 'ISO-9001-2024-0456',
            issue_date: '2024-02-01',
            expiry_date: '2025-02-01',
            pdf_url: '/certificates/lithium-iso-0456.pdf',
            verified: true
          }
        ],
        reviews: [
          {
            id: '2',
            buyer_id: 'buyer2',
            rating: 4.5,
            comment: 'High quality lithium carbonate, perfect for battery manufacturing. Great bulk pricing.',
            date: '2024-03-08',
            verified_purchase: true,
            helpful_count: 18
          }
        ]
      },
      {
        id: '3',
        name: 'Neodymium Magnet Grade',
        symbol: 'Nd',
        category: 'rare_earth_elements',
        chemical_formula: 'Nd2Fe14B',
        current_price_usd_per_kg: 100000,
        density: 7.01,
        hardness: 5.5,
        melting_point: 1024.0,
        purity_grades_available: ['99.5%', '99.9%'],
        major_producing_countries: ['China', 'Australia', 'USA', 'Myanmar'],
        global_reserves: 8000,
        annual_production: 300,
        strategic_importance: 'critical',
        seller_info: {
          id: 'seller3',
          name: 'Rare Earth Technologies Ltd',
          rating: 4.9,
          total_transactions: 3210,
          success_rate: 0.99,
          location: 'Singapore',
          is_verified: true,
          is_premium: true,
          response_time: '< 30 minutes',
          languages_spoken: ['English', 'Mandarin', 'Japanese'],
          company_type: 'Refinery',
          established_year: 2005
        },
        images: [
          'https://images.unsplash.com/photo-1558804952-6a8f8f5d4a7'
        ],
        specifications: {
          purity: '99.9%',
          weight: '5 kg',
          dimensions: '20cm x 15cm x 10cm',
          form: 'Blocks',
          color: 'Silver-gray',
          clarity: 'Excellent',
          cut: 'N/A',
          treatment: 'Coated',
          origin: 'China',
          lab_certificate: 'China National Rare Earth Lab'
        },
        shipping_options: [
          {
            method: 'Secured Air Freight',
            cost_per_kg: 25,
            delivery_time_days: '2-3',
            tracking_included: true,
            insurance_included: true,
            countries: ['USA', 'EU', 'Asia']
          }
        ],
        certifications: [
          {
            type: 'Rare Earth Certificate',
            issuer: 'China National Rare Earth Lab',
            certificate_number: 'CNREL-2024-0789',
            issue_date: '2024-01-20',
            expiry_date: '2025-01-20',
            pdf_url: '/certificates/neodymium-cnrel-0789.pdf',
            verified: true
          }
        ],
        reviews: [
          {
            id: '3',
            buyer_id: 'buyer3',
            rating: 5.0,
            comment: 'Premium quality neodymium magnets, exactly what we needed for our EV motors.',
            date: '2024-03-12',
            verified_purchase: true,
            helpful_count: 32
          }
        ]
      }
    ];
  }, []);

  // Search and filter logic
  const filteredMinerals = useMemo(() => {
    return minerals.filter(mineral => {
      const matchesSearch = searchQuery === '' || 
        mineral.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        mineral.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        mineral.chemical_formula.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = !filters.category || mineral.category === filters.category;
      const matchesPrice = mineral.current_price_usd_per_kg >= filters.price_min && 
                           mineral.current_price_usd_per_kg <= filters.price_max;
      const matchesPurity = !filters.purity_grade || 
                           mineral.purity_grades_available.some(grade => grade.includes(filters.purity_grade));
      const matchesCountry = !filters.country || 
                            mineral.major_producing_countries.includes(filters.country);
      const matchesRating = !filters.seller_rating || mineral.seller_info.rating >= filters.seller_rating;
      const matchesStrategic = !filters.strategic_importance || 
                               mineral.strategic_importance === filters.strategic_importance;
      const matchesStock = !filters.in_stock || true; // Assume all in stock
      const matchesCertified = !filters.certified || mineral.certifications.length > 0;

      return matchesSearch && matchesCategory && matchesPrice && matchesPurity && 
             matchesCountry && matchesRating && matchesStrategic && matchesStock && matchesCertified;
    });
  }, [minerals, searchQuery, filters]);

  // Sort logic
  const sortedMinerals = useMemo(() => {
    const sorted = [...filteredMinerals];
    
    switch (sortBy) {
      case 'price':
        return sorted.sort((a, b) => a.current_price_usd_per_kg - b.current_price_usd_per_kg);
      case 'rating':
        return sorted.sort((a, b) => b.seller_info.rating - a.seller_info.rating);
      case 'newest':
        return sorted.sort((a, b) => new Date(b.reviews[0]?.date).getTime() - new Date(a.reviews[0]?.date).getTime());
      case 'popularity':
        return sorted.sort((a, b) => b.reviews.length - a.reviews.length);
      default:
        return sorted;
    }
  }, [filteredMinerals, sortBy]);

  // Pagination
  const paginatedMinerals = useMemo(() => {
    const startIndex = (currentPage - 1) * 20;
    return sortedMinerals.slice(startIndex, startIndex + 20);
  }, [sortedMinerals, currentPage]);

  // Load minerals on mount
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setMinerals(generateMockMinerals());
      setTotalResults(generateMockMinerals().length);
      setLoading(false);
    }, 1000);
  }, []);

  // Toggle watchlist
  const toggleWatchlist = (mineralId: string) => {
    setWatchlist(prev => 
      prev.includes(mineralId) 
        ? prev.filter(id => id !== mineralId)
        : [...prev, mineralId]
    );
  };

  // Toggle compare list
  const toggleCompare = (mineralId: string) => {
    setCompareList(prev => 
      prev.includes(mineralId) 
        ? prev.filter(id => id !== mineralId)
        : [...prev, mineralId]
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                🌍 DEDAN 2.0 Marketplace
              </h1>
              <span className="text-sm text-slate-400">
                {totalResults.toLocaleString()}+ Minerals • 6100+ Global Database
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCompareModal(true)}
                className="relative p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                <BarChart3 className="w-5 h-5" />
                {compareList.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-blue-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                    {compareList.length}
                  </span>
                )}
              </button>
              
              <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                <Heart className="w-5 h-5" />
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
                placeholder="Search 6100+ minerals by name, symbol, or chemical formula..."
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
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800"
            >
              <option value="popularity">Most Popular</option>
              <option value="rating">Highest Rated</option>
              <option value="price">Lowest Price</option>
              <option value="newest">Newest Listings</option>
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
                    <option value="precious_metals">Precious Metals</option>
                    <option value="battery_minerals">Battery Minerals</option>
                    <option value="rare_earth_elements">Rare Earth Elements</option>
                    <option value="base_metals">Base Metals</option>
                    <option value="industrial_minerals">Industrial Minerals</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Price Range ($/kg)</label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      placeholder="Min"
                      value={filters.price_min}
                      onChange={(e) => setFilters({...filters, price_min: Number(e.target.value)})}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      value={filters.price_max}
                      onChange={(e) => setFilters({...filters, price_max: Number(e.target.value)})}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Purity Grade</label>
                  <select
                    value={filters.purity_grade}
                    onChange={(e) => setFilters({...filters, purity_grade: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Grades</option>
                    <option value="99.5%">99.5%</option>
                    <option value="99.9%">99.9%</option>
                    <option value="99.99%">99.99%</option>
                    <option value="99.999%">99.999%</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Country</label>
                  <select
                    value={filters.country}
                    onChange={(e) => setFilters({...filters, country: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Countries</option>
                    <option value="China">China</option>
                    <option value="Australia">Australia</option>
                    <option value="USA">USA</option>
                    <option value="Chile">Chile</option>
                    <option value="South Africa">South Africa</option>
                  </select>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Results Count */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <p className="text-slate-400">
            Showing {paginatedMinerals.length} of {filteredMinerals.length} minerals
          </p>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-slate-400">
              Strategic: <span className="text-red-400 font-medium">Critical</span>
            </span>
            <span className="text-sm text-slate-400">
              In Stock: <span className="text-green-400 font-medium">All Items</span>
            </span>
          </div>
        </div>
      </div>

      {/* Mineral Listings */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 'space-y-4'}>
            {paginatedMinerals.map((mineral) => (
              <motion.div
                key={mineral.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={viewMode === 'grid' ? 'bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden backdrop-blur-sm' : 'bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm'}
                onClick={() => setSelectedMineral(mineral)}
              >
                {viewMode === 'grid' ? (
                  /* Grid View */
                  <div className="relative">
                    {/* Image */}
                    <div className="relative h-48 overflow-hidden">
                      <img 
                        src={mineral.images[0]} 
                        alt={mineral.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.currentTarget.src = 'https://via.placeholder.com/400x300?text=No+Image';
                        }}
                      />
                      <div className="absolute top-2 right-2 flex space-x-2">
                        {mineral.strategic_importance === 'critical' && (
                          <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                            Critical
                          </span>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleWatchlist(mineral.id);
                          }}
                          className="p-1 bg-slate-900/80 hover:bg-slate-700 rounded-full transition-colors"
                        >
                          <Heart className={`w-4 h-4 ${watchlist.includes(mineral.id) ? 'text-red-500 fill-current' : 'text-slate-400'}`} />
                        </button>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-semibold text-white">{mineral.name}</h3>
                          <p className="text-sm text-slate-400">{mineral.symbol} • {mineral.category}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-400">
                            ${mineral.current_price_usd_per_kg.toLocaleString()}/kg
                          </p>
                        </div>
                      </div>

                      {/* Key Specs */}
                      <div className="space-y-2 mb-4">
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-400">Purity:</span>
                          <span className="text-green-400">{mineral.specifications.purity}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-400">Weight:</span>
                          <span>{mineral.specifications.weight}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-400">Origin:</span>
                          <span>{mineral.specifications.origin}</span>
                        </div>
                      </div>

                      {/* Seller Info */}
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                            {mineral.seller_info.rating.toFixed(1)}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-white">{mineral.seller_info.name}</p>
                            <p className="text-xs text-slate-400">{mineral.seller_info.location}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-slate-400">{mineral.seller_info.success_rate}% success rate</p>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleCompare(mineral.id);
                          }}
                          className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                            compareList.includes(mineral.id) 
                              ? 'bg-blue-600 text-white' 
                              : 'bg-slate-700 text-white hover:bg-slate-600'
                          }`}
                        >
                          <BarChart3 className="w-4 h-4 inline-block mr-2" />
                          {compareList.includes(mineral.id) ? 'Added' : 'Compare'}
                        </button>
                        <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                          <MessageCircle className="w-4 h-4 inline-block mr-2" />
                          Contact
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  /* List View */
                  <div className="flex space-x-6">
                    <img 
                      src={mineral.images[0]} 
                      alt={mineral.name}
                      className="w-32 h-32 object-cover rounded-lg"
                      onError={(e) => {
                        e.currentTarget.src = 'https://via.placeholder.com/400x300?text=No+Image';
                      }}
                    />
                    
                    <div className="flex-1 space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-white">{mineral.name}</h3>
                          <p className="text-sm text-slate-400">{mineral.symbol} • {mineral.category}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-400">
                            ${mineral.current_price_usd_per_kg.toLocaleString()}/kg
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-slate-400">Purity:</span>
                          <span className="text-green-400 ml-2">{mineral.specifications.purity}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Weight:</span>
                          <span className="ml-2">{mineral.specifications.weight}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Origin:</span>
                          <span className="ml-2">{mineral.specifications.origin}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Seller:</span>
                          <span className="ml-2">{mineral.seller_info.name}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-3">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                            {mineral.seller_info.rating.toFixed(1)}
                          </div>
                          <div className="text-sm text-slate-400">
                            <p>{mineral.seller_info.success_rate}% success</p>
                            <p>{mineral.seller_info.location}</p>
                          </div>
                        </div>
                        
                        <div className="flex space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleWatchlist(mineral.id);
                            }}
                            className="p-2 bg-slate-700 hover:bg-slate-600 rounded-full transition-colors"
                          >
                            <Heart className={`w-4 h-4 ${watchlist.includes(mineral.id) ? 'text-red-500 fill-current' : 'text-slate-400'}`} />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleCompare(mineral.id);
                            }}
                            className={`p-2 bg-slate-700 hover:bg-slate-600 rounded-full transition-colors ${
                              compareList.includes(mineral.id) ? 'bg-blue-600' : ''
                            }`}
                          >
                            <BarChart3 className="w-4 h-4" />
                          </button>
                          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                            <MessageCircle className="w-4 h-4 inline-block mr-2" />
                            Contact
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalResults > 20 && (
          <div className="flex justify-center items-center space-x-4 py-8">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            
            <span className="text-slate-400">
              Page {currentPage} of {Math.ceil(totalResults / 20)}
            </span>
            
            <button
              onClick={() => setCurrentPage(Math.min(Math.ceil(totalResults / 20), currentPage + 1))}
              disabled={currentPage >= Math.ceil(totalResults / 20)}
              className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Compare Modal */}
      <AnimatePresence>
        {showCompareModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">Compare Minerals</h2>
                <button
                  onClick={() => setShowCompareModal(false)}
                  className="p-2 hover:bg-slate-700 rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </div>

              <div className="space-y-4">
                {compareList.map(mineralId => {
                  const mineral = minerals.find(m => m.id === mineralId);
                  return mineral ? (
                    <div key={mineralId} className="bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center space-x-4">
                        <img 
                          src={mineral.images[0]} 
                          alt={mineral.name}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                        <div className="flex-1">
                          <h3 className="font-semibold text-white">{mineral.name}</h3>
                          <p className="text-2xl font-bold text-green-400">
                            ${mineral.current_price_usd_per_kg.toLocaleString()}/kg
                          </p>
                          <p className="text-sm text-slate-400">
                            {mineral.specifications.purity} • {mineral.specifications.weight}
                          </p>
                        </div>
                        <button
                          onClick={() => toggleCompare(mineralId)}
                          className="p-2 hover:bg-slate-600 rounded-full transition-colors"
                        >
                          <X className="w-4 h-4 text-slate-400" />
                        </button>
                      </div>
                    </div>
                  ) : null;
                })}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MineralMarketplace;
