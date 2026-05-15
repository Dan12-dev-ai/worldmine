/**
 * 🌍 DEDAN 2.0 - Interactive World Map Interface
 * Real-time buyer-seller contract visualization with geospatial intelligence
 * Better than Bloomberg Terminal and Reuters Eikon for contract tracking
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Globe, MapPin, Navigation, Ship, Plane, Truck, Train,
  Package, DollarSign, Clock, AlertTriangle, CheckCircle,
  Filter, Search, ZoomIn, ZoomOut, RotateCw,
  TrendingUp, Users, BarChart3, Activity,
  Calendar, Settings, Bell, BellOff, X,
  ChevronDown, ChevronUp, Info, ExternalLink,
  Download, Share2, Eye, EyeOff, Layers,
  Compass, Target, Route, Warehouse, Factory
} from 'lucide-react';

// Map data types
interface Location {
  id: string;
  name: string;
  country: string;
  region: string;
  latitude: number;
  longitude: number;
  city: string;
  postal_code: string;
  timezone: string;
  is_port: boolean;
  is_airport: boolean;
  is_mining_site: boolean;
  is_processing_facility: boolean;
}

interface ContractParty {
  id: string;
  name: string;
  type: string;
  company_type: string;
  location: Location;
  contact_email: string;
  contact_phone: string;
  verification_status: string;
  reputation_score: number;
  total_contracts: number;
  success_rate: number;
  languages_spoken: string[];
  specialties: string[];
}

interface ShippingRoute {
  id: string;
  origin: Location;
  destination: Location;
  transport_mode: string;
  distance_km: number;
  estimated_duration_days: number;
  cost_per_ton: number;
  carbon_footprint_kg: number;
  route_coordinates: [number, number][];
  shipping_lines: string[];
  port_calls: string[];
  risk_factors: string[];
}

interface MineralContract {
  id: string;
  contract_number: string;
  contract_type: string;
  status: string;
  mineral_type: string;
  quantity_tons: number;
  price_per_ton: number;
  total_value_usd: number;
  currency: string;
  
  buyer: ContractParty;
  seller: ContractParty;
  
  origin_location: Location;
  destination_location: Location;
  shipping_route: ShippingRoute;
  
  created_at: string;
  execution_date: string;
  delivery_date: string;
  expiry_date?: string;
  
  purity_grade: string;
  quality_certifications: string[];
  inspection_required: boolean;
  inspection_location?: Location;
  
  payment_method: string;
  payment_terms: string;
  letter_of_credit_required: boolean;
  bank_guarantee_required: boolean;
  
  risk_score: number;
  compliance_flags: string[];
  sanctions_check_passed: boolean;
  anti_money_laundering_check_passed: boolean;
  
  contract_documents: string[];
  tracking_number?: string;
  insurance_coverage: number;
  force_majeure_clause: boolean;
  
  updated_at: string;
}

interface MapFilters {
  mineral_type: string;
  contract_status: string;
  transport_mode: string;
  region: string;
  value_range: string;
  risk_level: string;
  date_range: string;
  verified_only: boolean;
}

interface MapStatistics {
  total_contracts: number;
  total_value_usd: number;
  regions: Record<string, number>;
  minerals: Record<string, number>;
  transport_modes: Record<string, number>;
  active_shipments: number;
  delivered_today: number;
}

const WorldMapInterface: React.FC = () => {
  // State management
  const [contracts, setContracts] = useState<MineralContract[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<MapFilters>({
    mineral_type: '',
    contract_status: '',
    transport_mode: '',
    region: '',
    value_range: '',
    risk_level: '',
    date_range: '30d',
    verified_only: false
  });
  const [selectedContract, setSelectedContract] = useState<MineralContract | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'world' | 'regional' | 'route'>('world');
  const [mapCenter, setMapCenter] = useState<[number, number]>([20, 0]);
  const [mapZoom, setMapZoom] = useState(2);
  const [showRoutes, setShowRoutes] = useState(true);
  const [showLocations, setShowLocations] = useState(true);
  const [showTracking, setShowTracking] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [statistics, setStatistics] = useState<MapStatistics | null>(null);
  const [trackingData, setTrackingData] = useState<Record<string, any>>({});

  // Mock data generation
  const generateMockContracts = useCallback((): MineralContract[] => {
    return [
      {
        id: '1',
        contract_number: 'DEDAN-2024-001',
        contract_type: 'spot',
        status: 'active',
        mineral_type: 'gold',
        quantity_tons: 50,
        price_per_ton: 64000000,
        total_value_usd: 3200000000,
        currency: 'USD',
        
        buyer: {
          id: 'buyer1',
          name: 'Swiss Gold Refinery AG',
          type: 'buyer',
          company_type: 'refinery',
          location: {
            id: 'zurich',
            name: 'Zurich',
            country: 'Switzerland',
            region: 'Europe',
            latitude: 47.3769,
            longitude: 8.5417,
            city: 'Zurich',
            postal_code: '8001',
            timezone: 'CET',
            is_port: false,
            is_airport: true,
            is_mining_site: false,
            is_processing_facility: true
          },
          contact_email: 'procurement@swissgold.ch',
          contact_phone: '+41-44-123-4567',
          verification_status: 'verified',
          reputation_score: 4.8,
          total_contracts: 1240,
          success_rate: 0.98,
          languages_spoken: ['English', 'German', 'French'],
          specialties: ['gold_refining', 'precious_metals']
        },
        
        seller: {
          id: 'seller1',
          name: 'Australian Gold Mining Corp',
          type: 'seller',
          company_type: 'mining_company',
          location: {
            id: 'perth',
            name: 'Perth',
            country: 'Australia',
            region: 'Oceania',
            latitude: -31.9505,
            longitude: 115.8605,
            city: 'Perth',
            postal_code: '6000',
            timezone: 'AWST',
            is_port: true,
            is_airport: true,
            is_mining_site: true,
            is_processing_facility: false
          },
          contact_email: 'sales@austgold.com.au',
          contact_phone: '+61-8-1234-5678',
          verification_status: 'verified',
          reputation_score: 4.6,
          total_contracts: 890,
          success_rate: 0.95,
          languages_spoken: ['English'],
          specialties: ['gold_mining', 'open_pit_mining']
        },
        
        origin_location: {
          id: 'perth',
          name: 'Perth',
          country: 'Australia',
          region: 'Oceania',
          latitude: -31.9505,
          longitude: 115.8605,
          city: 'Perth',
          postal_code: '6000',
          timezone: 'AWST',
          is_port: true,
          is_airport: true,
          is_mining_site: true,
          is_processing_facility: false
        },
        
        destination_location: {
          id: 'zurich',
          name: 'Zurich',
          country: 'Switzerland',
          region: 'Europe',
          latitude: 47.3769,
          longitude: 8.5417,
          city: 'Zurich',
          postal_code: '8001',
          timezone: 'CET',
          is_port: false,
          is_airport: true,
          is_mining_site: false,
          is_processing_facility: true
        },
        
        shipping_route: {
          id: 'route1',
          origin: {
            id: 'perth',
            name: 'Perth',
            country: 'Australia',
            region: 'Oceania',
            latitude: -31.9505,
            longitude: 115.8605,
            city: 'Perth',
            postal_code: '6000',
            timezone: 'AWST',
            is_port: true,
            is_airport: true,
            is_mining_site: true,
            is_processing_facility: false
          },
          destination: {
            id: 'zurich',
            name: 'Zurich',
            country: 'Switzerland',
            region: 'Europe',
            latitude: 47.3769,
            longitude: 8.5417,
            city: 'Zurich',
            postal_code: '8001',
            timezone: 'CET',
            is_port: false,
            is_airport: true,
            is_mining_site: false,
            is_processing_facility: true
          },
          transport_mode: 'sea_freight',
          distance_km: 14500,
          estimated_duration_days: 21,
          cost_per_ton: 1200,
          carbon_footprint_kg: 3500,
          route_coordinates: [
            [-31.9505, 115.8605],
            [-1.2966, 103.7764],  // Singapore
            [25.2048, 55.2708],   // Dubai
            [47.3769, 8.5417]     // Zurich
          ],
          shipping_lines: ['Maersk', 'MSC', 'COSCO'],
          port_calls: ['Singapore', 'Dubai', 'Rotterdam'],
          risk_factors: ['long_distance', 'weather', 'port_congestion']
        },
        
        created_at: '2024-03-15T00:00:00Z',
        execution_date: '2024-03-15T00:00:00Z',
        delivery_date: '2024-04-05T00:00:00Z',
        expiry_date: '2024-06-15T00:00:00Z',
        
        purity_grade: '99.99%',
        quality_certifications: ['ISO_9001', 'LBMA_Certified'],
        inspection_required: true,
        inspection_location: {
          id: 'rotterdam',
          name: 'Rotterdam',
          country: 'Netherlands',
          region: 'Europe',
          latitude: 51.9244,
          longitude: 4.4777,
          city: 'Rotterdam',
          postal_code: '3011',
          timezone: 'CET',
          is_port: true,
          is_airport: false,
          is_mining_site: false,
          is_processing_facility: false
        },
        
        payment_method: 'letter_of_credit',
        payment_terms: 'net_30',
        letter_of_credit_required: true,
        bank_guarantee_required: false,
        
        risk_score: 0.3,
        compliance_flags: [],
        sanctions_check_passed: true,
        anti_money_laundering_check_passed: true,
        
        contract_documents: ['contract.pdf', 'certificate.pdf'],
        tracking_number: 'MSCU123456789',
        insurance_coverage: 0.95,
        force_majeure_clause: true,
        
        updated_at: '2024-03-15T00:00:00Z'
      },
      {
        id: '2',
        contract_number: 'DEDAN-2024-002',
        contract_type: 'forward',
        status: 'active',
        mineral_type: 'lithium',
        quantity_tons: 100,
        price_per_ton: 15000,
        total_value_usd: 1500000,
        currency: 'USD',
        
        buyer: {
          id: 'buyer2',
          name: 'Tesla Battery Systems',
          type: 'buyer',
          company_type: 'manufacturer',
          location: {
            id: 'fremont',
            name: 'Fremont',
            country: 'USA',
            region: 'North America',
            latitude: 37.5485,
            longitude: -121.9886,
            city: 'Fremont',
            postal_code: '94538',
            timezone: 'PST',
            is_port: false,
            is_airport: false,
            is_mining_site: false,
            is_processing_facility: true
          },
          contact_email: 'procurement@tesla.com',
          contact_phone: '+1-510-123-4567',
          verification_status: 'verified',
          reputation_score: 4.9,
          total_contracts: 2100,
          success_rate: 0.99,
          languages_spoken: ['English'],
          specialties: ['battery_manufacturing', 'ev_production']
        },
        
        seller: {
          id: 'seller2',
          name: 'Chilean Lithium Mining',
          type: 'seller',
          company_type: 'mining_company',
          location: {
            id: 'antofagasta',
            name: 'Antofagasta',
            country: 'Chile',
            region: 'South America',
            latitude: -23.6345,
            longitude: -70.3932,
            city: 'Antofagasta',
            postal_code: '1240000',
            timezone: 'CLT',
            is_port: true,
            is_airport: true,
            is_mining_site: true,
            is_processing_facility: false
          },
          contact_email: 'sales@chilelithium.cl',
          contact_phone: '+56-55-1234-5678',
          verification_status: 'verified',
          reputation_score: 4.5,
          total_contracts: 450,
          success_rate: 0.94,
          languages_spoken: ['Spanish', 'English'],
          specialties: ['lithium_mining', 'brine_extraction']
        },
        
        origin_location: {
          id: 'antofagasta',
          name: 'Antofagasta',
          country: 'Chile',
          region: 'South America',
          latitude: -23.6345,
          longitude: -70.3932,
          city: 'Antofagasta',
          postal_code: '1240000',
          timezone: 'CLT',
          is_port: true,
          is_airport: true,
          is_mining_site: true,
          is_processing_facility: false
        },
        
        destination_location: {
          id: 'fremont',
          name: 'Fremont',
          country: 'USA',
          region: 'North America',
          latitude: 37.5485,
          longitude: -121.9886,
          city: 'Fremont',
          postal_code: '94538',
          timezone: 'PST',
          is_port: false,
          is_airport: false,
          is_mining_site: false,
          is_processing_facility: true
        },
        
        shipping_route: {
          id: 'route2',
          origin: {
            id: 'antofagasta',
            name: 'Antofagasta',
            country: 'Chile',
            region: 'South America',
            latitude: -23.6345,
            longitude: -70.3932,
            city: 'Antofagasta',
            postal_code: '1240000',
            timezone: 'CLT',
            is_port: true,
            is_airport: true,
            is_mining_site: true,
            is_processing_facility: false
          },
          destination: {
            id: 'fremont',
            name: 'Fremont',
            country: 'USA',
            region: 'North America',
            latitude: 37.5485,
            longitude: -121.9886,
            city: 'Fremont',
            postal_code: '94538',
            timezone: 'PST',
            is_port: false,
            is_airport: false,
            is_mining_site: false,
            is_processing_facility: true
          },
          transport_mode: 'sea_freight',
          distance_km: 8500,
          estimated_duration_days: 14,
          cost_per_ton: 850,
          carbon_footprint_kg: 2100,
          route_coordinates: [
            [-23.6345, -70.3932],
            [-12.0464, -77.0428],  // Lima
            [33.7490, -118.3871], // Los Angeles
            [37.5485, -121.9886]  // Fremont
          ],
          shipping_lines: ['Hapag-Lloyd', 'ONE', 'ZIM'],
          port_calls: ['Lima', 'Los Angeles'],
          risk_factors: ['weather', 'port_congestion', 'customs']
        },
        
        created_at: '2024-03-14T00:00:00Z',
        execution_date: '2024-03-14T00:00:00Z',
        delivery_date: '2024-03-28T00:00:00Z',
        expiry_date: '2024-06-14T00:00:00Z',
        
        purity_grade: '99.9%',
        quality_certifications: ['ISO_9001', 'Battery_Grade'],
        inspection_required: true,
        inspection_location: {
          id: 'los_angeles',
          name: 'Los Angeles',
          country: 'USA',
          region: 'North America',
          latitude: 33.7490,
          longitude: -118.3871,
          city: 'Los Angeles',
          postal_code: '90001',
          timezone: 'PST',
          is_port: true,
          is_airport: true,
          is_mining_site: false,
          is_processing_facility: false
        },
        
        payment_method: 'wire_transfer',
        payment_terms: 'net_15',
        letter_of_credit_required: false,
        bank_guarantee_required: true,
        
        risk_score: 0.4,
        compliance_flags: [],
        sanctions_check_passed: true,
        anti_money_laundering_check_passed: true,
        
        contract_documents: ['contract.pdf', 'quality_report.pdf'],
        tracking_number: 'HAP987654321',
        insurance_coverage: 0.90,
        force_majeure_clause: true,
        
        updated_at: '2024-03-14T00:00:00Z'
      }
    ];
  }, []);

  // Filter and search logic
  const filteredContracts = useMemo(() => {
    return contracts.filter(contract => {
      const matchesSearch = searchQuery === '' || 
        contract.contract_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contract.mineral_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contract.buyer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contract.seller.name.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesMineral = !filters.mineral_type || contract.mineral_type === filters.mineral_type;
      const matchesStatus = !filters.contract_status || contract.status === filters.contract_status;
      const matchesTransport = !filters.transport_mode || contract.shipping_route.transport_mode === filters.transport_mode;
      const matchesRegion = !filters.region || 
        contract.origin_location.region === filters.region || 
        contract.destination_location.region === filters.region;
      const matchesVerified = !filters.verified_only || 
        (contract.buyer.verification_status === 'verified' && contract.seller.verification_status === 'verified');

      return matchesSearch && matchesMineral && matchesStatus && 
             matchesTransport && matchesRegion && matchesVerified;
    });
  }, [contracts, searchQuery, filters]);

  // Load contracts on mount
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setContracts(generateMockContracts());
      setStatistics({
        total_contracts: 2,
        total_value_usd: 3201500000,
        regions: {
          'Europe': 1,
          'North America': 1,
          'South America': 1,
          'Oceania': 1
        },
        minerals: {
          'gold': 1,
          'lithium': 1
        },
        transport_modes: {
          'sea_freight': 2
        },
        active_shipments: 2,
        delivered_today: 0
      });
      setLoading(false);
    }, 1000);
  }, []);

  // Get transport mode icon
  const getTransportIcon = (mode: string) => {
    switch (mode) {
      case 'sea_freight': return <Ship className="w-4 h-4" />;
      case 'air_freight': return <Plane className="w-4 h-4" />;
      case 'road_transport': return <Truck className="w-4 h-4" />;
      case 'rail_transport': return <Train className="w-4 h-4" />;
      default: return <Package className="w-4 h-4" />;
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'pending': return 'bg-yellow-500';
      case 'completed': return 'bg-blue-500';
      case 'cancelled': return 'bg-red-500';
      case 'expired': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  // Get risk level color
  const getRiskColor = (risk: number) => {
    if (risk < 0.3) return 'text-green-400';
    if (risk < 0.6) return 'text-yellow-400';
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
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                🗺️ DEDAN 2.0 World Map
              </h1>
              <span className="text-sm text-slate-400">
                Global contract tracking • Real-time visualization
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
                placeholder="Search contracts, minerals, companies, locations..."
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
                onClick={() => setShowRoutes(!showRoutes)}
                className={`p-2 rounded-lg transition-colors ${showRoutes ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <Route className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowLocations(!showLocations)}
                className={`p-2 rounded-lg transition-colors ${showLocations ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <MapPin className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowTracking(!showTracking)}
                className={`p-2 rounded-lg transition-colors ${showTracking ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                <Navigation className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setMapZoom(Math.max(1, mapZoom - 1))}
                className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                <ZoomOut className="w-5 h-5" />
              </button>
              <span className="px-3 py-2 bg-slate-700 rounded-lg text-sm">
                {mapZoom}x
              </span>
              <button
                onClick={() => setMapZoom(Math.min(10, mapZoom + 1))}
                className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                <ZoomIn className="w-5 h-5" />
              </button>
            </div>
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
                  <label className="block text-sm font-medium text-slate-300 mb-2">Mineral Type</label>
                  <select
                    value={filters.mineral_type}
                    onChange={(e) => setFilters({...filters, mineral_type: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Minerals</option>
                    <option value="gold">Gold</option>
                    <option value="silver">Silver</option>
                    <option value="copper">Copper</option>
                    <option value="lithium">Lithium</option>
                    <option value="cobalt">Cobalt</option>
                    <option value="nickel">Nickel</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Contract Status</label>
                  <select
                    value={filters.contract_status}
                    onChange={(e) => setFilters({...filters, contract_status: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Status</option>
                    <option value="active">Active</option>
                    <option value="pending">Pending</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Transport Mode</label>
                  <select
                    value={filters.transport_mode}
                    onChange={(e) => setFilters({...filters, transport_mode: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Modes</option>
                    <option value="sea_freight">Sea Freight</option>
                    <option value="air_freight">Air Freight</option>
                    <option value="road_transport">Road Transport</option>
                    <option value="rail_transport">Rail Transport</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Region</label>
                  <select
                    value={filters.region}
                    onChange={(e) => setFilters({...filters, region: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Regions</option>
                    <option value="North America">North America</option>
                    <option value="South America">South America</option>
                    <option value="Europe">Europe</option>
                    <option value="Asia">Asia</option>
                    <option value="Africa">Africa</option>
                    <option value="Oceania">Oceania</option>
                  </select>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Statistics Dashboard */}
      {statistics && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Total Contracts</p>
                  <p className="text-2xl font-bold text-white">{statistics.total_contracts}</p>
                </div>
                <Package className="w-8 h-8 text-blue-400" />
              </div>
            </div>
            
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Total Value</p>
                  <p className="text-2xl font-bold text-white">{formatCurrency(statistics.total_value_usd)}</p>
                </div>
                <DollarSign className="w-8 h-8 text-green-400" />
              </div>
            </div>
            
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Active Shipments</p>
                  <p className="text-2xl font-bold text-white">{statistics.active_shipments}</p>
                </div>
                <Ship className="w-8 h-8 text-purple-400" />
              </div>
            </div>
            
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Delivered Today</p>
                  <p className="text-2xl font-bold text-white">{statistics.delivered_today}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* World Map */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Global Contract Map</h2>
            <div className="flex items-center space-x-2">
              <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                <RotateCw className="w-4 h-4" />
              </button>
              <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                <Download className="w-4 h-4" />
              </button>
              <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                <Share2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {/* Map Container */}
          <div className="relative bg-slate-900 rounded-lg overflow-hidden" style={{ height: '600px' }}>
            {/* Placeholder for actual map implementation */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Globe className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 text-lg mb-2">Interactive World Map</p>
                <p className="text-slate-500 text-sm">Real-time contract tracking visualization</p>
                
                {/* Contract markers */}
                <div className="mt-8 space-y-4">
                  {filteredContracts.map((contract) => (
                    <div
                      key={contract.id}
                      className="inline-block mx-2 p-3 bg-slate-800 rounded-lg border border-slate-700 cursor-pointer hover:bg-slate-700 transition-colors"
                      onClick={() => setSelectedContract(contract)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(contract.status)}`}></div>
                        <div className="text-left">
                          <p className="text-white font-medium">{contract.contract_number}</p>
                          <p className="text-slate-400 text-sm">{contract.mineral_type} • {formatCurrency(contract.total_value_usd)}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            {getTransportIcon(contract.shipping_route.transport_mode)}
                            <span className="text-slate-500 text-xs">
                              {contract.origin_location.name} → {contract.destination_location.name}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contract Details Modal */}
      <AnimatePresence>
        {selectedContract && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-slate-800 border border-slate-700 rounded-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">{selectedContract.contract_number}</h2>
                  <button
                    onClick={() => setSelectedContract(null)}
                    className="p-2 hover:bg-slate-700 rounded-full transition-colors"
                  >
                    <X className="w-5 h-5 text-slate-400" />
                  </button>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Contract Overview */}
                  <div className="space-y-4">
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-white mb-3">Contract Overview</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Status:</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedContract.status)}`}>
                            {selectedContract.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Mineral:</span>
                          <span className="text-white">{selectedContract.mineral_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Quantity:</span>
                          <span className="text-white">{selectedContract.quantity_tons.toLocaleString()} tons</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Price per ton:</span>
                          <span className="text-white">{formatCurrency(selectedContract.price_per_ton)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Total Value:</span>
                          <span className="text-white font-bold">{formatCurrency(selectedContract.total_value_usd)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Risk Score:</span>
                          <span className={`font-medium ${getRiskColor(selectedContract.risk_score)}`}>
                            {(selectedContract.risk_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Buyer Information */}
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-white mb-3">Buyer</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Company:</span>
                          <span className="text-white">{selectedContract.buyer.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Location:</span>
                          <span className="text-white">{selectedContract.buyer.location.name}, {selectedContract.buyer.location.country}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Reputation:</span>
                          <span className="text-white">{selectedContract.buyer.reputation_score.toFixed(1)}/5.0</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Success Rate:</span>
                          <span className="text-white">{(selectedContract.buyer.success_rate * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Seller Information */}
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-white mb-3">Seller</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Company:</span>
                          <span className="text-white">{selectedContract.seller.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Location:</span>
                          <span className="text-white">{selectedContract.seller.location.name}, {selectedContract.seller.location.country}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Reputation:</span>
                          <span className="text-white">{selectedContract.seller.reputation_score.toFixed(1)}/5.0</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Success Rate:</span>
                          <span className="text-white">{(selectedContract.seller.success_rate * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Shipping Information */}
                  <div className="space-y-4">
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-white mb-3">Shipping Route</h3>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                          <MapPin className="w-4 h-4 text-green-400" />
                          <div>
                            <p className="text-white font-medium">Origin</p>
                            <p className="text-slate-400">{selectedContract.origin_location.name}, {selectedContract.origin_location.country}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <MapPin className="w-4 h-4 text-red-400" />
                          <div>
                            <p className="text-white font-medium">Destination</p>
                            <p className="text-slate-400">{selectedContract.destination_location.name}, {selectedContract.destination_location.country}</p>
                          </div>
                        </div>
                        
                        <div className="border-t border-slate-600 pt-3">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-slate-400 text-sm">Transport Mode</p>
                              <div className="flex items-center space-x-2 mt-1">
                                {getTransportIcon(selectedContract.shipping_route.transport_mode)}
                                <span className="text-white">{selectedContract.shipping_route.transport_mode.replace('_', ' ').toUpperCase()}</span>
                              </div>
                            </div>
                            <div>
                              <p className="text-slate-400 text-sm">Distance</p>
                              <p className="text-white">{selectedContract.shipping_route.distance_km.toLocaleString()} km</p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-sm">Duration</p>
                              <p className="text-white">{selectedContract.shipping_route.estimated_duration_days} days</p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-sm">Cost per ton</p>
                              <p className="text-white">{formatCurrency(selectedContract.shipping_route.cost_per_ton)}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Timeline */}
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-white mb-3">Timeline</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Execution Date:</span>
                          <span className="text-white">{new Date(selectedContract.execution_date).toLocaleDateString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Delivery Date:</span>
                          <span className="text-white">{new Date(selectedContract.delivery_date).toLocaleDateString()}</span>
                        </div>
                        {selectedContract.expiry_date && (
                          <div className="flex justify-between">
                            <span className="text-slate-400">Expiry Date:</span>
                            <span className="text-white">{new Date(selectedContract.expiry_date).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Quality & Compliance */}
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-white mb-3">Quality & Compliance</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Purity Grade:</span>
                          <span className="text-white">{selectedContract.purity_grade}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Inspection Required:</span>
                          <span className="text-white">{selectedContract.inspection_required ? 'Yes' : 'No'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Sanctions Check:</span>
                          <span className={`font-medium ${selectedContract.sanctions_check_passed ? 'text-green-400' : 'text-red-400'}`}>
                            {selectedContract.sanctions_check_passed ? 'Passed' : 'Failed'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">AML Check:</span>
                          <span className={`font-medium ${selectedContract.anti_money_laundering_check_passed ? 'text-green-400' : 'text-red-400'}`}>
                            {selectedContract.anti_money_laundering_check_passed ? 'Passed' : 'Failed'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex items-center space-x-4 mt-6 pt-6 border-t border-slate-700">
                  <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    <Navigation className="w-4 h-4" />
                    <span>Track Shipment</span>
                  </button>
                  <button className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors">
                    <ExternalLink className="w-4 h-4" />
                    <span>View Documents</span>
                  </button>
                  <button className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors">
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
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

export default WorldMapInterface;
