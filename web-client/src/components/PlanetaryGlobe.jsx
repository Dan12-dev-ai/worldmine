/**
 * Planetary Globe - 3D Digital Twin of Ethiopian Mining Operations
 * Interactive globe showing live provenance from Ethiopia to global markets
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Globe, 
  Activity, 
  Zap, 
  Shield, 
  TrendingUp,
  MapPin,
  Navigation,
  Eye,
  Layers,
  Database,
  Cpu,
  Wifi
} from 'lucide-react';

const PlanetaryGlobe = () => {
  const [globeData, setGlobeData] = useState(null);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [showProvenance, setShowProvenance] = useState(true);
  const [showHeatMap, setShowHeatMap] = useState(true);
  const [showConnections, setShowConnections] = useState(true);
  const [isRotating, setIsRotating] = useState(true);
  const [ndviValue, setNdviValue] = useState(0.5);
  const [loading, setLoading] = useState(true);
  const globeRef = useRef(null);

  // Ethiopian mining locations
  const ethiopianMines = [
    {
      id: 'tigray-gold',
      name: 'Tigray Gold Mine',
      location: { lat: 14.0, lon: 38.7 },
      minerals: ['gold', 'silver', 'copper'],
      capacity: '500 tons/year',
      status: 'active',
      nbeCompliant: true,
      carbonFootprint: 0.02
    },
    {
      id: 'oromia-potash',
      name: 'Oromia Potash Mine',
      location: { lat: 9.6, lon: 42.4 },
      minerals: ['potash', 'salt', 'soda ash'],
      capacity: '1,000,000 tons/year',
      status: 'active',
      nbeCompliant: true,
      carbonFootprint: 0.15
    },
    {
      id: 'sidamo-tantalum',
      name: 'Sidamo Tantalum Mine',
      location: { lat: 6.8, lon: 37.8 },
      minerals: ['tantalum', 'rare earth'],
      capacity: '200 tons/year',
      status: 'active',
      nbeCompliant: true,
      carbonFootprint: 0.05
    },
    {
      id: 'benishangul-coal',
      name: 'Benishangul-Gumuz Coal Mine',
      location: { lat: 11.1, lon: 40.5 },
      minerals: ['coal', 'limestone', 'gypsum'],
      capacity: '2,000,000 tons/year',
      status: 'active',
      nbeCompliant: true,
      carbonFootprint: 0.25
    }
  ];

  // Global hub destinations
  const globalHubs = [
    {
      id: 'dubai',
      name: 'Dubai Gold Hub',
      location: { lat: 25.3, lon: 55.3 },
      type: 'global_hub',
      status: 'active'
    },
    {
      id: 'singapore',
      name: 'Singapore Trading Hub',
      location: { lat: 1.3, lon: 103.8 },
      type: 'global_hub',
      status: 'active'
    },
    {
      id: 'rotterdam',
      name: 'Rotterdam Port',
      location: { lat: 51.9, lon: 4.5 },
      type: 'global_hub',
      status: 'active'
    },
    {
      id: 'new-york',
      name: 'New York Harbor',
      location: { lat: 40.7, lon: -74.0 },
      type: 'global_hub',
      status: 'active'
    },
    {
      id: 'london',
      name: 'London Bullion Market',
      location: { lat: 51.5, lon: -0.1 },
      type: 'global_hub',
      status: 'active'
    },
    {
      id: 'shanghai',
      name: 'Shanghai Metals Exchange',
      location: { lat: 31.2, lon: 121.5 },
      type: 'global_hub',
      status: 'active'
    },
    {
      id: 'tokyo',
      name: 'Tokyo Commodities Exchange',
      location: { lat: 35.7, lon: 139.7 },
      type: 'global_hub',
      status: 'active'
    }
  ];

  // Provenance trails (mock data)
  const provenanceTrails = [
    {
      id: 'trail-001',
      from: 'tigray-gold',
      to: 'dubai',
      mineral: 'gold',
      quantity: 150,
      status: 'completed',
      timestamp: '2024-04-08T10:30:00Z',
      nbeCompliant: true
    },
    {
      id: 'trail-002',
      from: 'oromia-potash',
      to: 'singapore',
      mineral: 'potash',
      quantity: 50000,
      status: 'in_transit',
      timestamp: '2024-04-08T08:15:00Z',
      nbeCompliant: true
    },
    {
      id: 'trail-003',
      from: 'sidamo-tantalum',
      to: 'rotterdam',
      mineral: 'tantalum',
      quantity: 75,
      status: 'completed',
      timestamp: '2024-04-08T06:45:00Z',
      nbeCompliant: true
    }
  ];

  useEffect(() => {
    // Initialize Three.js globe
    initializeGlobe();
    
    // Fetch live data
    fetchLiveProvenanceData();
    
    return () => {
      if (globeRef.current) {
        // Cleanup Three.js resources
        globeRef.current.dispose();
      }
    };
  }, []);

  const initializeGlobe = () => {
    // Mock Three.js initialization
    // In production, integrate with actual Three.js library
    setLoading(false);
  };

  const fetchLiveProvenanceData = async () => {
    try {
      const response = await fetch('/api/v1/planetary/provenance');
      const data = await response.json();
      setGlobeData(data);
    } catch (error) {
      console.error('Error fetching provenance data:', error);
    }
  };

  const handlePointClick = (point) => {
    setSelectedPoint(point);
  };

  const toggleRotation = () => {
    setIsRotating(!isRotating);
  };

  const handleNdviChange = (value) => {
    setNdviValue(value);
  };

  const getPointColor = (point) => {
    if (point.status === 'active') {
      return '#10b981'; // Green
    } else if (point.status === 'in_transit') {
      return '#f59e0b'; // Orange
    } else {
      return '#6b7280'; // Gray
    }
  };

  const getTrailColor = (trail) => {
    if (trail.status === 'completed') {
      return '#10b981'; // Green
    } else if (trail.status === 'in_transit') {
      return '#f59e0b'; // Orange
    } else {
      return '#6b7280'; // Gray
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-4">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            Planetary Digital Twin
          </h1>
          <p className="text-gray-300 text-lg">
            Live Ethiopian Mining Provenance - Global Supply Chain Visualization
          </p>
        </motion.div>
      </div>

      {/* Control Panel */}
      <div className="max-w-7xl mx-auto mb-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Globe Controls */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <Globe className="w-5 h-5 mr-2 text-blue-400" />
                Globe Controls
              </h3>
              <div className="space-y-2">
                <button
                  onClick={toggleRotation}
                  className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
                    isRotating
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                  }`}
                >
                  {isRotating ? 'Pause Rotation' : 'Start Rotation'}
                </button>
                <div className="text-sm text-gray-400">
                  Status: {isRotating ? 'Rotating' : 'Paused'}
                </div>
              </div>
            </div>

            {/* NDVI Toggle */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-green-400" />
                NDVI Vegetation
              </h3>
              <div className="space-y-2">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={ndviValue}
                  onChange={(e) => handleNdviChange(parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="text-sm text-gray-400">
                  NDVI: {ndviValue.toFixed(2)}
                </div>
                <div className="text-xs text-gray-500">
                  {ndviValue > 0.6 ? 'High Vegetation' : ndviValue > 0.3 ? 'Moderate Vegetation' : 'Low Vegetation'}
                </div>
              </div>
            </div>

            {/* Layer Controls */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <Layers className="w-5 h-5 mr-2 text-purple-400" />
                Display Layers
              </h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showProvenance}
                    onChange={(e) => setShowProvenance(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Provenance Trails</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showHeatMap}
                    onChange={(e) => setShowHeatMap(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Carbon Heat Map</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showConnections}
                    onChange={(e) => setShowConnections(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Global Connections</span>
                </label>
              </div>
            </div>

            {/* System Status */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <Cpu className="w-5 h-5 mr-2 text-orange-400" />
                System Status
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Satellite Network</span>
                  <span className="text-sm text-green-400">Online</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">API Status</span>
                  <span className="text-sm text-green-400">Connected</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Data Freshness</span>
                  <span className="text-sm text-blue-400">5 min</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">NBE Compliance</span>
                  <span className="text-sm text-green-400">100%</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* 3D Globe Container */}
      <div className="max-w-7xl mx-auto mb-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
          style={{ height: '600px' }}
        >
          <div className="relative w-full h-full">
            {/* Mock 3D Globe */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Globe className="w-16 h-16 mx-auto mb-4 text-blue-400 animate-pulse" />
                <h3 className="text-xl font-semibold mb-2">3D Digital Twin Globe</h3>
                <p className="text-gray-400 mb-4">
                  Interactive visualization of Ethiopian mining operations and global supply chains
                </p>
                <div className="flex items-center justify-center space-x-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">{ethiopianMines.length}</div>
                    <div className="text-sm text-gray-400">Active Mines</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">{globalHubs.length}</div>
                    <div className="text-sm text-gray-400">Global Hubs</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">{provenanceTrails.length}</div>
                    <div className="text-sm text-gray-400">Provenance Trails</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Globe would be rendered here with Three.js */}
            <div ref={globeRef} className="absolute inset-0" />
          </div>
        </motion.div>
      </div>

      {/* Bento Box Dashboard */}
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {/* The Vault */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
          >
            <div className="flex items-center mb-4">
              <Shield className="w-6 h-6 mr-3 text-green-400" />
              <h3 className="text-xl font-bold">The Vault</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">PQC Key Health</span>
                <span className="text-green-400 font-semibold">Optimal</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Wallet Balance</span>
                <span className="text-blue-400 font-semibold">$2,000,000</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Active Transactions</span>
                <span className="text-purple-400 font-semibold">247</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Security Level</span>
                <span className="text-green-400 font-semibold">Quantum</span>
              </div>
            </div>
          </motion.div>

          {/* The Field */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
          >
            <div className="flex items-center mb-4">
              <Eye className="w-6 h-6 mr-3 text-blue-400" />
              <h3 className="text-xl font-bold">The Field</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Satellite Feed</span>
                <span className="text-green-400 font-semibold">Live</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">NDVI Index</span>
                <span className="text-green-400 font-semibold">{ndviValue.toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Active Drones</span>
                <span className="text-blue-400 font-semibold">12</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Coverage Area</span>
                <span className="text-purple-400 font-semibold">98.5%</span>
              </div>
            </div>
          </motion.div>

          {/* The Nexus */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
          >
            <div className="flex items-center mb-4">
              <Zap className="w-6 h-6 mr-3 text-purple-400" />
              <h3 className="text-xl font-bold">The Nexus</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">AI Market Intel</span>
                <span className="text-green-400 font-semibold">Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Prediction Accuracy</span>
                <span className="text-blue-400 font-semibold">94.2%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Risk Score</span>
                <span className="text-green-400 font-semibold">Low</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Opportunities</span>
                <span className="text-purple-400 font-semibold">8</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Provenance Details */}
      <AnimatePresence>
        {selectedPoint && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <div className="bg-slate-800 rounded-2xl p-8 max-w-2xl mx-4 border border-slate-700">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold">{selectedPoint.name}</h3>
                <button
                  onClick={() => setSelectedPoint(null)}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-3 text-blue-400">Location</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Latitude:</span>
                      <span className="text-white">{selectedPoint.location.lat}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Longitude:</span>
                      <span className="text-white">{selectedPoint.location.lon}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold mb-3 text-green-400">Operations</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Status:</span>
                      <span className="text-green-400">{selectedPoint.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Capacity:</span>
                      <span className="text-white">{selectedPoint.capacity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">NBE Compliant:</span>
                      <span className="text-green-400">Yes</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <h4 className="text-lg font-semibold mb-3 text-purple-400">Minerals</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedPoint.minerals.map((mineral, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm"
                    >
                      {mineral}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PlanetaryGlobe;
