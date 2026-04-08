/**
 * DEDAN Mine - Global Resource Map (Three.js)
 * High-performance 3D visualization with real-time commodity price fluctuations
 * Spatial UX with hyper-personalization for international institutional buyers
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Globe,
  TrendingUp,
  TrendingDown,
  Activity,
  MapPin,
  DollarSign,
  BarChart3,
  Settings,
  Eye,
  Layers,
  Zap,
  Shield,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';

const GlobalResourceMap = () => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const frameRef = useRef(null);
  
  const [userRegion, setUserRegion] = useState('US');
  const [selectedMineral, setSelectedMineral] = useState('gold');
  const [priceData, setPriceData] = useState({});
  const [complianceBadges, setComplianceBadges] = useState([]);
  const [unitSystem, setUnitSystem] = useState('metric');
  const [currency, setCurrency] = useState('USD');
  const [showPriceFluctuations, setShowPriceFluctuations] = useState(true);
  const [loading, setLoading] = useState(true);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [tradeDisclaimers, setTradeDisclaimers] = useState([]);
  
  // Regional configurations
  const regionalConfigs = useMemo(() => ({
    US: {
      currency: 'USD',
      unitSystem: 'imperial',
      disclaimers: [
        'Commodity trading involves substantial risk of loss',
        'Prices subject to market volatility and regulatory changes',
        'SEC regulations apply to institutional trading'
      ],
      complianceBadges: ['SEC Compliant', 'CFTC Registered', 'FINRA Member'],
      priceFormat: (price) => `$${price.toLocaleString()}`,
      weightUnit: 'ounces',
      weightConversion: 31.1035
    },
    EU: {
      currency: 'EUR',
      unitSystem: 'metric',
      disclaimers: [
        'MiFID II regulations apply to all trading activities',
        'ESMA guidelines for commodity derivatives',
        'GDPR compliance for all data processing'
      ],
      complianceBadges: ['MiFID II Compliant', 'ESMA Registered', 'GDPR Compliant'],
      priceFormat: (price) => `EUR ${price.toLocaleString()}`,
      weightUnit: 'grams',
      weightConversion: 1000
    },
    ASIA: {
      currency: 'USD',
      unitSystem: 'metric',
      disclaimers: [
        'Local regulations and exchange rules apply',
        'Currency conversion risks may apply',
        'Regional market hours affect pricing'
      ],
      complianceBadges: ['MAS Regulated', 'HKMA Licensed', 'FSA Authorized'],
      priceFormat: (price) => `$${price.toLocaleString()}`,
      weightUnit: 'kilograms',
      weightConversion: 1
    }
  }), []);
  
  // Mineral data
  const mineralData = useMemo(() => ({
    gold: {
      name: 'Gold',
      color: 0xFFD700,
      price: 1850.00,
      change: 2.5,
      volatility: 0.8,
      regions: ['US', 'EU', 'ASIA'],
      major_producers: ['China', 'Australia', 'Russia', 'US', 'Canada'],
      icon: 'Au'
    },
    silver: {
      name: 'Silver',
      color: 0xC0C0C0,
      price: 24.50,
      change: -1.2,
      volatility: 1.2,
      regions: ['US', 'EU', 'ASIA'],
      major_producers: ['Mexico', 'Peru', 'China', 'Russia'],
      icon: 'Ag'
    },
    copper: {
      name: 'Copper',
      color: 0xB87333,
      price: 4.25,
      change: 3.8,
      volatility: 1.5,
      regions: ['US', 'EU', 'ASIA'],
      major_producers: ['Chile', 'Peru', 'China', 'Congo'],
      icon: 'Cu'
    },
    lithium: {
      name: 'Lithium',
      color: 0xFF6B6B,
      price: 15000.00,
      change: 8.2,
      volatility: 2.1,
      regions: ['ASIA', 'EU', 'US'],
      major_producers: ['Australia', 'Chile', 'China', 'Argentina'],
      icon: 'Li'
    },
    cobalt: {
      name: 'Cobalt',
      color: 0x0047AB,
      price: 35000.00,
      change: -3.5,
      volatility: 2.8,
      regions: ['ASIA', 'EU', 'US'],
      major_producers: ['Congo', 'China', 'Russia', 'Australia'],
      icon: 'Co'
    }
  }), []);
  
  // Mining locations
  const miningLocations = useMemo(() => [
    {
      id: 'nevada_gold',
      name: 'Nevada Gold Mines',
      coordinates: { lat: 39.0, lon: -117.0 },
      mineral: 'gold',
      production: 175000,  // ounces per year
      country: 'US',
      region: 'US',
      compliance: 'RMI Certified',
      satellite_verified: true
    },
    {
      id: 'peru_copper',
      name: 'Peru Copper Belt',
      coordinates: { lat: -12.0, lon: -75.0 },
      mineral: 'copper',
      production: 2200000,  // tonnes per year
      country: 'Peru',
      region: 'ASIA',
      compliance: 'ISO 20400',
      satellite_verified: true
    },
    {
      id: 'australia_lithium',
      name: 'Western Australia Lithium',
      coordinates: { lat: -30.0, lon: 121.0 },
      mineral: 'lithium',
      production: 45000,  // tonnes per year
      country: 'Australia',
      region: 'ASIA',
      compliance: 'OECD Compliant',
      satellite_verified: true
    },
    {
      id: 'congo_cobalt',
      name: 'DRC Cobalt Belt',
      coordinates: { lat: -10.0, lon: 25.0 },
      mineral: 'cobalt',
      production: 120000,  // tonnes per year
      country: 'DRC',
      region: 'ASIA',
      compliance: 'Due Diligence Required',
      satellite_verified: false
    }
  ], []);
  
  // Detect user region
  useEffect(() => {
    const detectUserRegion = async () => {
      try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        
        let detectedRegion = 'US';
        if (data.continent_code === 'EU') {
          detectedRegion = 'EU';
        } else if (['CN', 'JP', 'KR', 'SG', 'AU', 'IN'].includes(data.country_code)) {
          detectedRegion = 'ASIA';
        }
        
        setUserRegion(detectedRegion);
        setCurrency(regionalConfigs[detectedRegion].currency);
        setUnitSystem(regionalConfigs[detectedRegion].unitSystem);
        setTradeDisclaimers(regionalConfigs[detectedRegion].disclaimers);
        setComplianceBadges(regionalConfigs[detectedRegion].complianceBadges);
        
      } catch (error) {
        console.error('Region detection failed:', error);
        // Default to US
        setUserRegion('US');
        setTradeDisclaimers(regionalConfigs.US.disclaimers);
        setComplianceBadges(regionalConfigs.US.complianceBadges);
      }
    };
    
    detectUserRegion();
  }, [regionalConfigs]);
  
  // Initialize Three.js scene
  useEffect(() => {
    if (!mountRef.current) return;
    
    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    sceneRef.current = scene;
    
    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 0, 3);
    cameraRef.current = camera;
    
    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;
    
    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5;
    controlsRef.current = controls;
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 3, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);
    
    const pointLight = new THREE.PointLight(0x4a90e2, 1, 100);
    pointLight.position.set(0, 0, 0);
    scene.add(pointLight);
    
    // Create globe
    createGlobe(scene);
    
    // Create mineral indicators
    createMineralIndicators(scene);
    
    // Create price fluctuation visualization
    if (showPriceFluctuations) {
      createPriceVisualization(scene);
    }
    
    // Handle resize
    const handleResize = () => {
      if (!mountRef.current) return;
      
      camera.aspect = mountRef.current.clientWidth / mountRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Animation loop
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      
      controls.update();
      
      // Update price fluctuations
      if (showPriceFluctuations) {
        updatePriceFluctuations(scene);
      }
      
      renderer.render(scene, camera);
    };
    
    animate();
    
    setLoading(false);
    
    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
      window.removeEventListener('resize', handleResize);
      
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      
      renderer.dispose();
    };
  }, [showPriceFluctuations, selectedMineral]);
  
  const createGlobe = (scene) => {
    // Globe geometry
    const globeGeometry = new THREE.SphereGeometry(1, 64, 64);
    
    // Create earth texture (mock)
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Create gradient for earth
    const gradient = ctx.createLinearGradient(0, 0, 1024, 512);
    gradient.addColorStop(0, '#1e3c72');
    gradient.addColorStop(0.5, '#2a5298');
    gradient.addColorStop(1, '#1e3c72');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1024, 512);
    
    // Add continent patterns
    ctx.fillStyle = '#2d5016';
    for (let i = 0; i < 20; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 512;
      const size = Math.random() * 100 + 20;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fill();
    }
    
    const texture = new THREE.CanvasTexture(canvas);
    
    const globeMaterial = new THREE.MeshPhongMaterial({
      map: texture,
      transparent: true,
      opacity: 0.9,
      emissive: 0x112244,
      emissiveIntensity: 0.1
    });
    
    const globe = new THREE.Mesh(globeGeometry, globeMaterial);
    globe.userData.type = 'globe';
    scene.add(globe);
    
    // Add atmosphere
    const atmosphereGeometry = new THREE.SphereGeometry(1.1, 64, 64);
    const atmosphereMaterial = new THREE.MeshPhongMaterial({
      color: 0x4a90e2,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide
    });
    
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);
  };
  
  const createMineralIndicators = (scene) => {
    miningLocations.forEach(location => {
      const mineral = mineralData[location.mineral];
      
      // Convert coordinates to 3D position
      const phi = (90 - location.coordinates.lat) * (Math.PI / 180);
      const theta = (location.coordinates.lon + 180) * (Math.PI / 180);
      
      const x = 1.2 * Math.sin(phi) * Math.cos(theta);
      const y = 1.2 * Math.cos(phi);
      const z = 1.2 * Math.sin(phi) * Math.sin(theta);
      
      // Create indicator
      const indicatorGeometry = new THREE.SphereGeometry(0.05, 16, 16);
      const indicatorMaterial = new THREE.MeshPhongMaterial({
        color: mineral.color,
        emissive: mineral.color,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.8
      });
      
      const indicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial);
      indicator.position.set(x, y, z);
      indicator.userData = {
        type: 'mineral_indicator',
        location: location,
        mineral: mineral
      };
      
      scene.add(indicator);
      
      // Add pulsing animation
      const pulseGeometry = new THREE.RingGeometry(0.05, 0.1, 16);
      const pulseMaterial = new THREE.MeshBasicMaterial({
        color: mineral.color,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide
      });
      
      const pulse = new THREE.Mesh(pulseGeometry, pulseMaterial);
      pulse.position.copy(indicator.position);
      pulse.lookAt(0, 0, 0);
      pulse.userData = {
        type: 'pulse',
        target: indicator,
        scale: 1,
        growing: true
      };
      
      scene.add(pulse);
      
      // Add connection lines
      const lineGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        indicator.position
      ]);
      
      const lineMaterial = new THREE.LineBasicMaterial({
        color: mineral.color,
        transparent: true,
        opacity: 0.3
      });
      
      const line = new THREE.Line(lineGeometry, lineMaterial);
      line.userData = {
        type: 'connection',
        mineral: mineral
      };
      
      scene.add(line);
    });
  };
  
  const createPriceVisualization = (scene) => {
    // Create price fluctuation particles
    const particleCount = 1000;
    const particleGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
      // Random positions around globe
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;
      const radius = 1.5 + Math.random() * 0.5;
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.cos(phi);
      positions[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
      
      // Color based on price change
      const mineral = mineralData[selectedMineral];
      const color = new THREE.Color(mineral.color);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }
    
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
      size: 0.02,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending
    });
    
    const particles = new THREE.Points(particleGeometry, particleMaterial);
    particles.userData = {
      type: 'price_particles',
      time: 0
    };
    
    scene.add(particles);
  };
  
  const updatePriceFluctuations = (scene) => {
    scene.traverse((child) => {
      if (child.userData.type === 'price_particles') {
        child.userData.time += 0.01;
        
        const positions = child.geometry.attributes.position.array;
        for (let i = 0; i < positions.length; i += 3) {
          const offset = Math.sin(child.userData.time + i) * 0.01;
          positions[i + 1] += offset;
        }
        
        child.geometry.attributes.position.needsUpdate = true;
      }
      
      if (child.userData.type === 'pulse') {
        if (child.userData.growing) {
          child.userData.scale += 0.01;
          if (child.userData.scale > 2) {
            child.userData.growing = false;
          }
        } else {
          child.userData.scale -= 0.01;
          if (child.userData.scale < 1) {
            child.userData.growing = true;
          }
        }
        
        child.scale.setScalar(child.userData.scale);
        child.material.opacity = 0.3 / child.userData.scale;
      }
    });
  };
  
  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(() => {
      const newPriceData = {};
      
      Object.keys(mineralData).forEach(mineral => {
        const basePrice = mineralData[mineral].price;
        const volatility = mineralData[mineral].volatility;
        const change = (Math.random() - 0.5) * volatility * 0.1;
        
        newPriceData[mineral] = {
          price: basePrice * (1 + change),
          change: change * 100,
          timestamp: new Date().toISOString()
        };
      });
      
      setPriceData(newPriceData);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [mineralData]);
  
  const handleLocationClick = (location) => {
    setSelectedLocation(location);
  };
  
  const formatPrice = (mineral, price) => {
    const config = regionalConfigs[userRegion];
    return config.priceFormat(price);
  };
  
  const formatWeight = (weight, unit) => {
    const config = regionalConfigs[userRegion];
    const conversion = config.weightConversion;
    
    if (unit === 'ounces') {
      return `${(weight / conversion).toFixed(2)} ${config.weightUnit}`;
    } else if (unit === 'grams') {
      return `${(weight * conversion).toFixed(2)} ${config.weightUnit}`;
    } else {
      return `${weight.toFixed(2)} ${config.weightUnit}`;
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-4">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            Global Resource Map
          </h1>
          <p className="text-gray-300 text-lg">
            Real-time commodity price fluctuations & satellite-verified mining operations
          </p>
        </motion.div>
      </div>
      
      {/* Regional Configuration Bar */}
      <div className="max-w-7xl mx-auto mb-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="bg-slate-800 rounded-2xl p-4 border border-slate-700"
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Globe className="w-5 h-5 text-blue-400" />
                <span className="text-sm font-medium">Region:</span>
                <span className="text-sm font-bold text-blue-400">{userRegion}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-green-400" />
                <span className="text-sm font-medium">Currency:</span>
                <span className="text-sm font-bold text-green-400">{currency}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-purple-400" />
                <span className="text-sm font-medium">Units:</span>
                <span className="text-sm font-bold text-purple-400">{unitSystem}</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowPriceFluctuations(!showPriceFluctuations)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  showPriceFluctuations
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-gray-300'
                }`}
              >
                {showPriceFluctuations ? 'Hide' : 'Show'} Price Fluctuations
              </button>
            </div>
          </div>
        </motion.div>
      </div>
      
      {/* Compliance Badges */}
      <div className="max-w-7xl mx-auto mb-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-slate-800 rounded-2xl p-4 border border-slate-700"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-green-400" />
              <span className="text-sm font-medium">Compliance Badges:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {complianceBadges.map((badge, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-green-600 text-white rounded-full text-xs font-medium"
                >
                  {badge}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
      
      {/* Trade Disclaimers */}
      <div className="max-w-7xl mx-auto mb-6">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded-2xl p-4"
        >
          <div className="flex items-start space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-yellow-400 mb-2">Regional Trade Disclaimers:</h4>
              <ul className="text-xs text-gray-300 space-y-1">
                {tradeDisclaimers.map((disclaimer, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-yellow-400 mr-2">-</span>
                    {disclaimer}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 3D Globe */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
              style={{ height: '600px' }}
            >
              <div className="relative w-full h-full">
                {loading ? (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
                      <p className="text-gray-400">Loading Global Resource Map...</p>
                    </div>
                  </div>
                ) : (
                  <div ref={mountRef} className="w-full h-full" />
                )}
              </div>
            </motion.div>
          </div>
          
          {/* Control Panel */}
          <div className="space-y-6">
            {/* Mineral Selection */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
            >
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Layers className="w-5 h-5 mr-2 text-purple-400" />
                Mineral Selection
              </h3>
              <div className="space-y-2">
                {Object.keys(mineralData).map(mineral => (
                  <button
                    key={mineral}
                    onClick={() => setSelectedMineral(mineral)}
                    className={`w-full px-4 py-3 rounded-lg text-left transition-colors ${
                      selectedMineral === mineral
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: `#${mineralData[mineral].color.toString(16).padStart(6, '0')}` }}
                        />
                        <span className="font-medium">{mineralData[mineral].name}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold">
                          {formatPrice(mineral, priceData[mineral]?.price || mineralData[mineral].price)}
                        </div>
                        <div className={`text-xs flex items-center ${
                          (priceData[mineral]?.change || mineralData[mineral].change) > 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {(priceData[mineral]?.change || mineralData[mineral].change) > 0 ? (
                            <TrendingUp className="w-3 h-3 mr-1" />
                          ) : (
                            <TrendingDown className="w-3 h-3 mr-1" />
                          )}
                          {Math.abs(priceData[mineral]?.change || mineralData[mineral].change).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
            
            {/* Mining Locations */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
            >
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <MapPin className="w-5 h-5 mr-2 text-blue-400" />
                Mining Locations
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {miningLocations
                  .filter(location => location.mineral === selectedMineral)
                  .map(location => (
                    <button
                      key={location.id}
                      onClick={() => handleLocationClick(location)}
                      className={`w-full px-4 py-3 rounded-lg text-left transition-colors ${
                        selectedLocation?.id === location.id
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-sm">{location.name}</div>
                          <div className="text-xs opacity-75">{location.country}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-bold">
                            {formatWeight(location.production, 'ounces')}
                          </div>
                          <div className={`text-xs ${
                            location.satellite_verified ? 'text-green-400' : 'text-yellow-400'
                          }`}>
                            {location.satellite_verified ? 'Verified' : 'Pending'}
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
              </div>
            </motion.div>
            
            {/* Market Statistics */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-slate-800 rounded-2xl p-6 border border-slate-700"
            >
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-green-400" />
                Market Statistics
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Volatility</span>
                  <span className="text-sm font-bold">
                    {(mineralData[selectedMineral]?.volatility * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">24h Volume</span>
                  <span className="text-sm font-bold">$2.3B</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Market Cap</span>
                  <span className="text-sm font-bold">$12.7T</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Active Traders</span>
                  <span className="text-sm font-bold">847K</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
      
      {/* Location Detail Modal */}
      <AnimatePresence>
        {selectedLocation && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setSelectedLocation(null)}
          >
            <div
              className="bg-slate-800 rounded-2xl p-8 max-w-2xl mx-4 border border-slate-700"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold">{selectedLocation.name}</h3>
                <button
                  onClick={() => setSelectedLocation(null)}
                  className="text-gray-400 hover:text-white"
                >
                  ×
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-3 text-blue-400">Location Details</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Country:</span>
                      <span className="text-white">{selectedLocation.country}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Coordinates:</span>
                      <span className="text-white">
                        {selectedLocation.coordinates.lat.toFixed(2)}°, {selectedLocation.coordinates.lon.toFixed(2)}°
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Region:</span>
                      <span className="text-white">{selectedLocation.region}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold mb-3 text-green-400">Production</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Annual Production:</span>
                      <span className="text-white">
                        {formatWeight(selectedLocation.production, 'ounces')}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Mineral Type:</span>
                      <span className="text-white">{mineralData[selectedLocation.mineral].name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Compliance:</span>
                      <span className={`${
                        selectedLocation.satellite_verified ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {selectedLocation.satellite_verified ? 'Verified' : 'Pending'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <h4 className="text-lg font-semibold mb-3 text-purple-400">Compliance Status</h4>
                <div className="flex items-center space-x-2">
                  {selectedLocation.satellite_verified ? (
                    <>
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      <span className="text-green-400">Satellite Verified</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-5 h-5 text-yellow-400" />
                      <span className="text-yellow-400">Verification Required</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default GlobalResourceMap;
