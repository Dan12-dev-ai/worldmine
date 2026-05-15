/**
 * 🏪 DEDAN 2.0 - World-Class Mineral Marketplace Interface
 * Professional buyer-seller platform with escrow protection
 * High-quality listings, verified certifications, direct messaging
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Package, Shield, Star, MessageSquare, 
  Camera, FileText, Truck, Clock,
  Heart, Eye, DollarSign, Users,
  CheckCircle, AlertTriangle, Send,
  Filter, Search, ChevronDown,
  MapPin, Phone, Mail, Globe
} from 'lucide-react';

interface MineralListing {
  id: string;
  title: string;
  description: string;
  mineralType: string;
  weight: number;
  purity: number;
  price: number;
  currency: string;
  seller: {
    id: string;
    name: string;
    rating: number;
    totalTransactions: number;
    successRate: number;
    verified: boolean;
    location: string;
    responseTime: string;
  };
  certifications: {
    assayReport: string;
    originDocument: string;
    qualityCertificate: string;
    authenticityReport: string;
  };
  images: string[];
  videos: string[];
  location: {
    country: string;
    city: string;
    coordinates: { lat: number; lng: number };
  };
  shipping: {
    available: boolean;
    cost: number;
    estimatedDelivery: string;
    methods: string[];
  };
  inventory: {
    available: number;
    total: number;
    lowStockThreshold: number;
  };
  negotiable: boolean;
  bulkPricing: {
    minQuantity: number;
    discount: number;
  };
  createdAt: string;
  views: number;
  watchlist: boolean;
}

interface Message {
  id: string;
  senderId: string;
  senderName: string;
  content: string;
  timestamp: string;
  isEncrypted: boolean;
  read: boolean;
}

interface Offer {
  id: string;
  listingId: string;
  buyerId: string;
  amount: number;
  price: number;
  message: string;
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
  createdAt: string;
  expiresAt: string;
}

const MarketplaceInterface: React.FC = () => {
  // State management
  const [listings, setListings] = useState<MineralListing[]>([]);
  const [filteredListings, setFilteredListings] = useState<MineralListing[]>([]);
  const [selectedListing, setSelectedListing] = useState<MineralListing | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMineral, setSelectedMineral] = useState('all');
  const [priceRange, setPriceRange] = useState({ min: 0, max: 100000 });
  const [sortBy, setSortBy] = useState('newest');
  const [showFilters, setShowFilters] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [offers, setOffers] = useState<Offer[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'listings' | 'messages' | 'offers'>('listings');

  // Mock data generation
  const generateMockListings = (): MineralListing[] => {
    return [
      {
        id: '1',
        title: 'Premium Gold Bullion - 99.99% Purity',
        description: 'High-purity gold bullion bars, professionally refined and certified. Perfect for investment and industrial use. Each bar is individually weighed and certified by independent laboratories.',
        mineralType: 'gold',
        weight: 1000,
        purity: 99.99,
        price: 65000,
        currency: 'USD',
        seller: {
          id: 'seller_1',
          name: 'GoldMaster Trading Ltd',
          rating: 4.8,
          totalTransactions: 1247,
          successRate: 98.7,
          verified: true,
          location: 'Zurich, Switzerland',
          responseTime: '< 2 hours'
        },
        certifications: {
          assayReport: '/certificates/assay_1.pdf',
          originDocument: '/certificates/origin_1.pdf',
          qualityCertificate: '/certificates/quality_1.pdf',
          authenticityReport: '/certificates/authenticity_1.pdf'
        },
        images: [
          '/images/gold_bullion_1.jpg',
          '/images/gold_bullion_2.jpg',
          '/images/gold_bullion_3.jpg',
          '/images/gold_bullion_4.jpg'
        ],
        videos: ['/videos/gold_bullion_demo.mp4'],
        location: {
          country: 'Switzerland',
          city: 'Zurich',
          coordinates: { lat: 47.3769, lng: 8.5417 }
        },
        shipping: {
          available: true,
          cost: 250,
          estimatedDelivery: '3-5 business days',
          methods: ['DHL Express', 'FedEx', 'UPS Worldwide']
        },
        inventory: {
          available: 850,
          total: 1000,
          lowStockThreshold: 100
        },
        negotiable: true,
        bulkPricing: {
          minQuantity: 100,
          discount: 0.05
        },
        createdAt: '2024-03-15T10:30:00Z',
        views: 1547,
        watchlist: false
      },
      {
        id: '2',
        title: 'Industrial Grade Lithium Carbonate',
        description: 'High-purity lithium carbonate suitable for battery manufacturing and energy storage applications. Sourced from verified mining operations with complete traceability.',
        mineralType: 'lithium',
        weight: 5000,
        purity: 99.5,
        price: 12000,
        currency: 'USD',
        seller: {
          id: 'seller_2',
          name: 'LithiumTech Minerals',
          rating: 4.6,
          totalTransactions: 892,
          successRate: 96.2,
          verified: true,
          location: 'Santiago, Chile',
          responseTime: '< 4 hours'
        },
        certifications: {
          assayReport: '/certificates/assay_2.pdf',
          originDocument: '/certificates/origin_2.pdf',
          qualityCertificate: '/certificates/quality_2.pdf',
          authenticityReport: '/certificates/authenticity_2.pdf'
        },
        images: [
          '/images/lithium_1.jpg',
          '/images/lithium_2.jpg'
        ],
        videos: [],
        location: {
          country: 'Chile',
          city: 'Santiago',
          coordinates: { lat: -33.4489, lng: -70.6693 }
        },
        shipping: {
          available: true,
          cost: 450,
          estimatedDelivery: '5-7 business days',
          methods: ['DHL Express', 'Maersk Shipping', 'Local Pickup']
        },
        inventory: {
          available: 25000,
          total: 30000,
          lowStockThreshold: 5000
        },
        negotiable: false,
        bulkPricing: {
          minQuantity: 1000,
          discount: 0.08
        },
        createdAt: '2024-03-14T15:45:00Z',
        views: 892,
        watchlist: false
      }
    ];
  };

  const generateMockMessages = (): Message[] => {
    return [
      {
        id: '1',
        senderId: 'seller_1',
        senderName: 'GoldMaster Trading Ltd',
        content: 'Thank you for your interest in our gold bullion. We can offer a 2% discount for orders over 50 ounces. Would you like to discuss further?',
        timestamp: '2024-03-15T14:30:00Z',
        isEncrypted: true,
        read: false
      },
      {
        id: '2',
        senderId: 'buyer_1',
        senderName: 'You',
        content: 'I\'m interested in purchasing 100 ounces. Can you provide more details about the shipping options to the United States?',
        timestamp: '2024-03-15T13:15:00Z',
        isEncrypted: true,
        read: true
      }
    ];
  };

  // Initialize data
  useEffect(() => {
    setListings(generateMockListings());
    setMessages(generateMockMessages());
  }, []);

  // Filter listings
  useEffect(() => {
    let filtered = listings;

    // Filter by mineral type
    if (selectedMineral !== 'all') {
      filtered = filtered.filter(listing => listing.mineralType === selectedMineral);
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(listing => 
        listing.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        listing.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by price range
    filtered = filtered.filter(listing => 
      listing.price >= priceRange.min && listing.price <= priceRange.max
    );

    // Sort
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
        break;
      case 'price_low':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case 'price_high':
        filtered.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        filtered.sort((a, b) => b.seller.rating - a.seller.rating);
        break;
    }

    setFilteredListings(filtered);
  }, [listings, selectedMineral, searchQuery, priceRange, sortBy]);

  // Handle watchlist
  const toggleWatchlist = (listingId: string) => {
    setWatchlist(prev => 
      prev.includes(listingId) 
        ? prev.filter(id => id !== listingId)
        : [...prev, listingId]
    );
    
    setListings(prev => prev.map(listing => 
      listing.id === listingId 
        ? { ...listing, watchlist: !listing.watchlist }
        : listing
    ));
  };

  // Send message
  const sendMessage = () => {
    if (!newMessage.trim() || !selectedListing) return;

    const message: Message = {
      id: `msg_${Date.now()}`,
      senderId: 'buyer_1',
      senderName: 'You',
      content: newMessage,
      timestamp: new Date().toISOString(),
      isEncrypted: true,
      read: false
    };

    setMessages(prev => [...prev, message]);
    setNewMessage('');
  };

  // Make offer
  const makeOffer = (listing: MineralListing) => {
    const offer: Offer = {
      id: `offer_${Date.now()}`,
      listingId: listing.id,
      buyerId: 'buyer_1',
      amount: 100,
      price: listing.price * 0.95, // 5% discount
      message: 'I would like to make an offer for 100 units at 5% below your listed price.',
      status: 'pending',
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
    };

    setOffers(prev => [...prev, offer]);
  };

  const minerals = [
    { id: 'all', name: 'All Minerals', color: 'gray' },
    { id: 'gold', name: 'Gold', color: 'yellow' },
    { id: 'silver', name: 'Silver', color: 'gray' },
    { id: 'lithium', name: 'Lithium', color: 'purple' },
    { id: 'copper', name: 'Copper', color: 'orange' },
    { id: 'rare_earth', name: 'Rare Earth', color: 'green' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-6">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                DEDAN Marketplace
              </h1>
              <div className="flex space-x-1">
                <button
                  onClick={() => setActiveTab('listings')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'listings' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  Listings
                </button>
                <button
                  onClick={() => setActiveTab('messages')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'messages' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  Messages
                </button>
                <button
                  onClick={() => setActiveTab('offers')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'offers' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  Offers
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors">
                <Search className="w-5 h-5" />
              </button>
              <button className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors">
                <Filter className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search minerals, descriptions, or sellers..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-12 pr-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              {/* Mineral Filter */}
              <div>
                <select
                  value={selectedMineral}
                  onChange={(e) => setSelectedMineral(e.target.value)}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {minerals.map(mineral => (
                    <option key={mineral.id} value={mineral.id}>
                      {mineral.name}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Sort */}
              <div>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="newest">Newest First</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                  <option value="rating">Highest Rated</option>
                </select>
              </div>
            </div>
            
            {/* Price Range */}
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 pt-4 border-t border-slate-700"
              >
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-slate-400 text-sm mb-2">Min Price ($)</label>
                    <input
                      type="number"
                      value={priceRange.min}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, min: Number(e.target.value) }))}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 text-sm mb-2">Max Price ($)</label>
                    <input
                      type="number"
                      value={priceRange.max}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, max: Number(e.target.value) }))}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Content based on active tab */}
        {activeTab === 'listings' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {filteredListings.map((listing, index) => (
              <motion.div
                key={listing.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden backdrop-blur-sm"
              >
                {/* Images */}
                <div className="relative h-48 bg-slate-700">
                  <img 
                    src={listing.images[0]} 
                    alt={listing.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 right-2 flex space-x-2">
                    {listing.seller.verified && (
                      <div className="bg-green-500 rounded-full p-1">
                        <CheckCircle className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <button
                      onClick={() => toggleWatchlist(listing.id)}
                      className="bg-slate-800/80 rounded-full p-1 hover:bg-slate-700 transition-colors"
                    >
                      <Heart className={`w-4 h-4 ${listing.watchlist ? 'text-red-500 fill-current' : 'text-slate-400'}`} />
                    </button>
                  </div>
                </div>
                
                {/* Content */}
                <div className="p-6">
                  <h3 className="font-semibold text-lg mb-2">{listing.title}</h3>
                  <p className="text-slate-300 text-sm mb-4 line-clamp-2">{listing.description}</p>
                  
                  {/* Seller Info */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"></div>
                      <div>
                        <div className="font-medium text-white">{listing.seller.name}</div>
                        <div className="flex items-center space-x-2 text-sm text-slate-400">
                          <div className="flex items-center space-x-1">
                            <Star className="w-3 h-3 text-yellow-500 fill-current" />
                            <span>{listing.seller.rating}</span>
                          </div>
                          <span>•</span>
                          <span>{listing.seller.totalTransactions} transactions</span>
                          <span>•</span>
                          <span>{listing.seller.successRate}% success</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">${listing.price.toLocaleString()}</div>
                      <div className="text-sm text-slate-400">per {listing.mineralType}</div>
                    </div>
                  </div>
                  
                  {/* Certifications */}
                  <div className="mb-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <Shield className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-slate-400">Verified Certifications</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <button className="flex items-center space-x-1 text-blue-400 hover:text-blue-300">
                        <FileText className="w-3 h-3" />
                        <span>Assay Report</span>
                      </button>
                      <button className="flex items-center space-x-1 text-blue-400 hover:text-blue-300">
                        <FileText className="w-3 h-3" />
                        <span>Origin Document</span>
                      </button>
                      <button className="flex items-center space-x-1 text-blue-400 hover:text-blue-300">
                        <FileText className="w-3 h-3" />
                        <span>Quality Certificate</span>
                      </button>
                      <button className="flex items-center space-x-1 text-blue-400 hover:text-blue-300">
                        <FileText className="w-3 h-3" />
                        <span>Authenticity Report</span>
                      </button>
                    </div>
                  </div>
                  
                  {/* Inventory Alert */}
                  {listing.inventory.available < listing.inventory.lowStockThreshold && (
                    <div className="mb-4 p-2 bg-yellow-500/20 border border-yellow-500/50 rounded-lg">
                      <div className="flex items-center space-x-2 text-yellow-400 text-sm">
                        <AlertTriangle className="w-4 h-4" />
                        <span>Low Stock: Only {listing.inventory.available} units left</span>
                      </div>
                    </div>
                  )}
                  
                  {/* Action Buttons */}
                  <div className="flex space-x-3">
                    <button
                      onClick={() => setSelectedListing(listing)}
                      className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      View Details
                    </button>
                    {listing.negotiable && (
                      <button
                        onClick={() => makeOffer(listing)}
                        className="flex-1 bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                      >
                        Make Offer
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Messages Tab */}
        {activeTab === 'messages' && selectedListing && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Listing Preview */}
            <div className="lg:col-span-2">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h2 className="text-xl font-bold mb-4">{selectedListing.title}</h2>
                
                {/* Message Thread */}
                <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`flex ${message.senderId === 'buyer_1' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-xs lg:max-w-md ${
                        message.senderId === 'buyer_1' 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-slate-700 text-white'
                      } rounded-lg p-3`}
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="font-medium text-sm">{message.senderName}</span>
                          {message.isEncrypted && (
                            <Shield className="w-3 h-3 text-green-400" />
                          )}
                        </div>
                        <div className="text-sm">{message.content}</div>
                        <div className="text-xs opacity-70 mt-2">
                          {new Date(message.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                {/* Message Input */}
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={sendMessage}
                    className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-lg transition-colors"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Offers Tab */}
        {activeTab === 'offers' && (
          <div className="space-y-4">
            {offers.map((offer, index) => (
              <motion.div
                key={offer.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">Offer #{offer.id.slice(-4)}</h3>
                    <p className="text-slate-400 text-sm">
                      {new Date(offer.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    offer.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                    offer.status === 'accepted' ? 'bg-green-500/20 text-green-400' :
                    offer.status === 'rejected' ? 'bg-red-500/20 text-red-400' :
                    'bg-slate-700 text-slate-400'
                  }`}>
                    {offer.status.toUpperCase()}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-slate-400 text-sm mb-1">Amount</div>
                    <div className="text-lg font-semibold">{offer.amount} units</div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-sm mb-1">Price</div>
                    <div className="text-lg font-semibold">${offer.price.toLocaleString()}</div>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="text-slate-400 text-sm mb-1">Message</div>
                  <div className="text-slate-300">{offer.message}</div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="text-sm text-slate-400">
                    Expires: {new Date(offer.expiresAt).toLocaleDateString()}
                  </div>
                  {offer.status === 'pending' && (
                    <div className="flex space-x-2">
                      <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                        Accept
                      </button>
                      <button className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketplaceInterface;
