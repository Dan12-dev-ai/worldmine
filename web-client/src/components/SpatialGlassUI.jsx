/**
 * DEDAN Mine - Spatial Glassmorphism UI (v3.0.0)
 * 2026 Trend: Frosted-glass backgrounds with 25px blur and dynamic gradients
 * Bento Grid layout with self-healing components
 * Infinite Globe with live Trade Liquidity Veins
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { useTranslation } from 'react-i18next';
import {
  Globe,
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  Shield,
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
  Satellite,
  BarChart3,
  Users,
  Lock,
  Unlock,
  Sparkles,
  Flame
} from 'lucide-react';

const SpatialGlassUI = () => {
  const { t, i18n } = useTranslation();
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const frameRef = useRef(null);
  
  const [marketSentiment, setMarketSentiment] = useState('bullish');
  const [selectedBento, setSelectedBento] = useState(null);
  const [glassBlur, setGlassBlur] = useState(25);
  const [gradientShift, setGradientShift] = useState(0);
  const [liquidityVeins, setLiquidityVeins] = useState([]);
  const [bentoData, setBentoData] = useState({});
  const [loading, setLoading] = useState(true);
  const [userLanguage, setUserLanguage] = useState('en');
  
  // Market sentiment colors
  const sentimentColors = useMemo(() => ({
    bullish: {
      primary: 'rgba(34, 197, 94, 0.8)',
      secondary: 'rgba(16, 185, 129, 0.6)',
      accent: 'rgba(5, 150, 105, 0.4)',
      glow: 'rgba(34, 197, 94, 0.3)'
    },
    bearish: {
      primary: 'rgba(239, 68, 68, 0.8)',
      secondary: 'rgba(220, 38, 38, 0.6)',
      accent: 'rgba(185, 28, 28, 0.4)',
      glow: 'rgba(239, 68, 68, 0.3)'
    },
    neutral: {
      primary: 'rgba(59, 130, 246, 0.8)',
      secondary: 'rgba(37, 99, 235, 0.6)',
      accent: 'rgba(29, 78, 216, 0.4)',
      glow: 'rgba(59, 130, 246, 0.3)'
    }
  }), []);
  
  // Bento grid configuration
  const bentoGrid = useMemo(() => [
    {
      id: 'price',
      title: t('bento.price.title'),
      icon: <DollarSign className="w-6 h-6" />,
      size: 'large',
      position: { row: 0, col: 0, rowSpan: 2, colSpan: 2 },
      component: 'PriceDashboard',
      selfHealing: true,
      updateInterval: 1000
    },
    {
      id: 'wallet',
      title: t('bento.wallet.title'),
      icon: <Wallet className="w-6 h-6" />,
      size: 'medium',
      position: { row: 0, col: 2, rowSpan: 1, colSpan: 1 },
      component: 'WalletDashboard',
      selfHealing: true,
      updateInterval: 2000
    },
    {
      id: 'satellite',
      title: t('bento.satellite.title'),
      icon: <Satellite className="w-6 h-6" />,
      size: 'medium',
      position: { row: 1, col: 2, rowSpan: 1, colSpan: 1 },
      component: 'SatelliteFeed',
      selfHealing: true,
      updateInterval: 5000
    },
    {
      id: 'liquidity',
      title: t('bento.liquidity.title'),
      icon: <Activity className="w-6 h-6" />,
      size: 'large',
      position: { row: 2, col: 0, rowSpan: 2, colSpan: 2 },
      component: 'LiquidityVeins',
      selfHealing: true,
      updateInterval: 3000
    },
    {
      id: 'trading',
      title: t('bento.trading.title'),
      icon: <BarChart3 className="w-6 h-6" />,
      size: 'medium',
      position: { row: 2, col: 2, rowSpan: 1, colSpan: 1 },
      component: 'TradingDashboard',
      selfHealing: true,
      updateInterval: 1500
    },
    {
      id: 'security',
      title: t('bento.security.title'),
      icon: <Shield className="w-6 h-6" />,
      size: 'medium',
      position: { row: 3, col: 2, rowSpan: 1, colSpan: 1 },
      component: 'SecurityStatus',
      selfHealing: true,
      updateInterval: 10000
    }
  ], [t]);
  
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
    
    // Create globe
    createGlobe(scene);
    
    // Create liquidity veins
    createLiquidityVeins(scene);
    
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
      
      // Update liquidity veins
      updateLiquidityVeins(scene);
      
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
  }, []);
  
  // Market sentiment effect
  useEffect(() => {
    const interval = setInterval(() => {
      setGradientShift(prev => (prev + 1) % 360);
    }, 50);
    
    return () => clearInterval(interval);
  }, []);
  
  // Bento data updates
  useEffect(() => {
    const updateBentoData = () => {
      const newData = {};
      
      bentoGrid.forEach(bento => {
        // Mock data updates based on component type
        switch (bento.component) {
          case 'PriceDashboard':
            newData[bento.id] = {
              price: 1850.00 + Math.random() * 100,
              change: (Math.random() - 0.5) * 5,
              volume: 2.3 + Math.random() * 0.5
            };
            break;
          case 'WalletDashboard':
            newData[bento.id] = {
              balance: 10000 + Math.random() * 5000,
              pending: Math.random() * 1000,
              transactions: Math.floor(Math.random() * 100)
            };
            break;
          case 'SatelliteFeed':
            newData[bento.id] = {
              activeSatellites: 12,
              coverage: 95 + Math.random() * 5,
              lastUpdate: new Date().toISOString()
            };
            break;
          case 'LiquidityVeins':
            newData[bento.id] = {
              totalLiquidity: 50000000 + Math.random() * 10000000,
              activeVeins: 8,
              flowRate: 1000000 + Math.random() * 500000
            };
            break;
          case 'TradingDashboard':
            newData[bento.id] = {
              activeTrades: 150 + Math.random() * 50,
              successRate: 85 + Math.random() * 10,
              avgPrice: 1850 + Math.random() * 100
            };
            break;
          case 'SecurityStatus':
            newData[bento.id] = {
              securityLevel: 'high',
              threatsBlocked: Math.floor(Math.random() * 100),
              lastScan: new Date().toISOString()
            };
            break;
        }
      });
      
      setBentoData(newData);
    };
    
    updateBentoData();
    const interval = setInterval(updateBentoData, 1000);
    
    return () => clearInterval(interval);
  }, [bentoGrid]);
  
  const createGlobe = (scene) => {
    // Globe geometry
    const globeGeometry = new THREE.SphereGeometry(1, 64, 64);
    
    // Create earth texture with dynamic colors
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Create gradient based on market sentiment
    const gradient = ctx.createLinearGradient(0, 0, 1024, 512);
    const colors = sentimentColors[marketSentiment];
    
    gradient.addColorStop(0, colors.primary);
    gradient.addColorStop(0.5, colors.secondary);
    gradient.addColorStop(1, colors.accent);
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1024, 512);
    
    // Add continent patterns
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
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
      emissive: new THREE.Color(colors.glow),
      emissiveIntensity: 0.2
    });
    
    const globe = new THREE.Mesh(globeGeometry, globeMaterial);
    globe.userData.type = 'globe';
    scene.add(globe);
    
    // Add atmosphere
    const atmosphereGeometry = new THREE.SphereGeometry(1.1, 64, 64);
    const atmosphereMaterial = new THREE.MeshPhongMaterial({
      color: new THREE.Color(colors.primary),
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide
    });
    
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);
  };
  
  const createLiquidityVeins = (scene) => {
    const veins = [];
    const veinData = [
      { start: { lat: 9, lon: 40 }, end: { lat: 51, lon: -0.1 }, color: 0x00ff00 }, // Ethiopia to London
      { start: { lat: 9, lon: 40 }, end: { lat: 40.7, lon: -74 }, color: 0x0000ff }, // Ethiopia to New York
      { start: { lat: 9, lon: 40 }, end: { lat: 35.6, lon: 139.6 }, color: 0xff0000 }, // Ethiopia to Tokyo
      { start: { lat: 9, lon: 40 }, end: { lat: -33.8, lon: 151.2 }, color: 0xffff00 }, // Ethiopia to Sydney
      { start: { lat: 9, lon: 40 }, end: { lat: 1.3, lon: 103.8 }, color: 0xff00ff }, // Ethiopia to Singapore
      { start: { lat: 9, lon: 40 }, end: { lat: 48.8, lon: 2.3 }, color: 0x00ffff }, // Ethiopia to Paris
      { start: { lat: 9, lon: 40 }, end: { lat: 52.5, lon: 13.3 }, color: 0xffa500 }, // Ethiopia to Berlin
      { start: { lat: 9, lon: 40 }, end: { lat: 25.2, lon: 55.2 }, color: 0x800080 }, // Ethiopia to Dubai
    ];
    
    veinData.forEach((vein, index) => {
      const points = [];
      const startLat = vein.start.lat * Math.PI / 180;
      const startLon = vein.start.lon * Math.PI / 180;
      const endLat = vein.end.lat * Math.PI / 180;
      const endLon = vein.end.lon * Math.PI / 180;
      
      // Create curved path
      const segments = 50;
      for (let i = 0; i <= segments; i++) {
        const t = i / segments;
        
        // Spherical interpolation
        const lat = startLat + (endLat - startLat) * t;
        const lon = startLon + (endLon - startLon) * t;
        
        // Add curve
        const curveHeight = Math.sin(t * Math.PI) * 0.2;
        const radius = 1.2 + curveHeight;
        
        const x = radius * Math.sin(lat) * Math.cos(lon);
        const y = radius * Math.cos(lat);
        const z = radius * Math.sin(lat) * Math.sin(lon);
        
        points.push(new THREE.Vector3(x, y, z));
      }
      
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const material = new THREE.LineBasicMaterial({
        color: vein.color,
        transparent: true,
        opacity: 0.8,
        linewidth: 2
      });
      
      const line = new THREE.Line(geometry, material);
      line.userData = {
        type: 'liquidity_vein',
        veinIndex: index,
        flowPhase: 0,
        color: vein.color
      };
      
      scene.add(line);
      veins.push(line);
    });
    
    setLiquidityVeins(veins);
  };
  
  const updateLiquidityVeins = (scene) => {
    scene.traverse((child) => {
      if (child.userData.type === 'liquidity_vein') {
        child.userData.flowPhase += 0.02;
        
        // Create flowing effect
        const material = child.material;
        material.opacity = 0.5 + Math.sin(child.userData.flowPhase) * 0.3;
        
        // Pulse effect based on market sentiment
        const pulseIntensity = marketSentiment === 'bullish' ? 1.2 : marketSentiment === 'bearish' ? 0.8 : 1.0;
        material.linewidth = 2 * pulseIntensity;
      }
    });
  };
  
  const renderBentoComponent = (bento) => {
    const data = bentoData[bento.id] || {};
    
    switch (bento.component) {
      case 'PriceDashboard':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">${data.price?.toFixed(2) || '0.00'}</span>
              <div className={`flex items-center space-x-1 ${
                data.change > 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {data.change > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                <span className="text-sm">{Math.abs(data.change || 0).toFixed(2)}%</span>
              </div>
            </div>
            <div className="text-sm opacity-75">
              Volume: ${(data.volume || 0).toFixed(1)}B
            </div>
          </div>
        );
      
      case 'WalletDashboard':
        return (
          <div className="space-y-4">
            <div className="text-2xl font-bold">${(data.balance || 0).toFixed(2)}</div>
            <div className="text-sm opacity-75">
              Pending: ${(data.pending || 0).toFixed(2)}
            </div>
            <div className="text-sm opacity-75">
              Transactions: {data.transactions || 0}
            </div>
          </div>
        );
      
      case 'SatelliteFeed':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Satellite className="w-4 h-4 text-blue-400" />
              <span className="text-sm">{data.activeSatellites || 0} Active</span>
            </div>
            <div className="text-sm opacity-75">
              Coverage: {data.coverage?.toFixed(1) || 0}%
            </div>
            <div className="text-xs opacity-50">
              {new Date(data.lastUpdate).toLocaleTimeString()}
            </div>
          </div>
        );
      
      case 'LiquidityVeins':
        return (
          <div className="space-y-4">
            <div className="text-2xl font-bold">
              ${(data.totalLiquidity || 0).toLocaleString()}
            </div>
            <div className="text-sm opacity-75">
              {data.activeVeins || 0} Active Veins
            </div>
            <div className="text-sm opacity-75">
              Flow Rate: ${(data.flowRate || 0).toLocaleString()}/s
            </div>
          </div>
        );
      
      case 'TradingDashboard':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-green-400" />
              <span className="text-sm">{data.activeTrades || 0} Active</span>
            </div>
            <div className="text-sm opacity-75">
              Success Rate: {data.successRate?.toFixed(1) || 0}%
            </div>
            <div className="text-sm opacity-75">
              Avg Price: ${data.avgPrice?.toFixed(2) || '0.00'}
            </div>
          </div>
        );
      
      case 'SecurityStatus':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-green-400" />
              <span className="text-sm capitalize">{data.securityLevel || 'Unknown'}</span>
            </div>
            <div className="text-sm opacity-75">
              Threats Blocked: {data.threatsBlocked || 0}
            </div>
            <div className="text-xs opacity-50">
              Last Scan: {new Date(data.lastScan).toLocaleTimeString()}
            </div>
          </div>
        );
      
      default:
        return <div className="text-center opacity-50">Component Loading...</div>;
    }
  };
  
  const getBentoSize = (size) => {
    switch (size) {
      case 'large':
        return 'col-span-2 row-span-2';
      case 'medium':
        return 'col-span-1 row-span-1';
      case 'small':
        return 'col-span-1 row-span-1';
      default:
        return 'col-span-1 row-span-1';
    }
  };
  
  const getGlassStyles = () => {
    const colors = sentimentColors[marketSentiment];
    
    return {
      background: `linear-gradient(${gradientShift}deg, ${colors.primary}, ${colors.secondary}, ${colors.accent})`,
      backdropFilter: `blur(${glassBlur}px)`,
      WebkitBackdropFilter: `blur(${glassBlur}px)`,
      border: `1px solid rgba(255, 255, 255, 0.1)`,
      boxShadow: `0 8px 32px 0 ${colors.glow}`,
    };
  };
  
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* Dynamic gradient background */}
      <div 
        className="fixed inset-0 transition-all duration-1000"
        style={{
          background: `linear-gradient(${gradientShift}deg, 
            rgba(34, 197, 94, 0.1), 
            rgba(59, 130, 246, 0.1), 
            rgba(239, 68, 68, 0.1))`,
          filter: `blur(${glassBlur / 2}px)`
        }}
      />
      
      {/* Header */}
      <div className="relative z-10 p-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-8 h-8 text-blue-400" />
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                DEDAN Mine
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                marketSentiment === 'bullish' ? 'bg-green-400' :
                marketSentiment === 'bearish' ? 'bg-red-400' : 'bg-blue-400'
              }`} />
              <span className="text-sm capitalize">{marketSentiment}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setGlassBlur(glassBlur === 25 ? 15 : 25)}
              className="px-3 py-1 rounded-lg bg-white bg-opacity-10 backdrop-blur-sm hover:bg-opacity-20 transition-all"
            >
              <Eye className="w-4 h-4" />
            </button>
            
            <select
              value={userLanguage}
              onChange={(e) => setUserLanguage(e.target.value)}
              className="px-3 py-1 rounded-lg bg-white bg-opacity-10 backdrop-blur-sm hover:bg-opacity-20 transition-all"
            >
              <option value="en">English</option>
              <option value="am">Amharic</option>
              <option value="ar">Arabic</option>
              <option value="zh">Mandarin</option>
            </select>
            
            <button className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all">
              <Lock className="w-4 h-4 mr-2" />
              Secure
            </button>
          </div>
        </motion.div>
      </div>
      
      {/* Main Content */}
      <div className="relative z-10 p-6">
        <div className="grid grid-cols-3 gap-4 max-w-7xl mx-auto">
          {/* Bento Grid */}
          {bentoGrid.map((bento, index) => (
            <motion.div
              key={bento.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`relative ${getBentoSize(bento.size)} p-6 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-105`}
              style={getGlassStyles()}
              onClick={() => setSelectedBento(bento)}
            >
              {/* Self-healing indicator */}
              {bento.selfHealing && (
                <div className="absolute top-2 right-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                </div>
              )}
              
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <div className="text-white opacity-80">
                    {bento.icon}
                  </div>
                  <h3 className="text-lg font-semibold">{bento.title}</h3>
                </div>
                <Settings className="w-4 h-4 opacity-50 hover:opacity-100 transition-opacity" />
              </div>
              
              {/* Content */}
              <div className="relative z-10">
                {renderBentoComponent(bento)}
              </div>
              
              {/* Glass effect overlay */}
              <div 
                className="absolute inset-0 rounded-2xl pointer-events-none"
                style={{
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
                  backdropFilter: 'blur(10px)',
                  WebkitBackdropFilter: 'blur(10px)',
                }}
              />
            </motion.div>
          ))}
          
          {/* Infinite Globe */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="col-span-3 row-span-2 relative rounded-2xl overflow-hidden"
            style={getGlassStyles()}
          >
            <div className="absolute inset-0">
              <div ref={mountRef} className="w-full h-full" />
            </div>
            
            {/* Globe overlay */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-2">Global Liquidity Veins</h2>
                <p className="text-sm opacity-75">Live trade flows from Ethiopia to the world</p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* Bento Detail Modal */}
      <AnimatePresence>
        {selectedBento && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setSelectedBento(null)}
          >
            <motion.div
              className="bg-slate-900 rounded-2xl p-8 max-w-2xl mx-4 border border-slate-700"
              style={getGlassStyles()}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold">{selectedBento.title}</h3>
                <button
                  onClick={() => setSelectedBento(null)}
                  className="text-gray-400 hover:text-white"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                {renderBentoComponent(selectedBento)}
              </div>
              
              <div className="mt-6 flex items-center justify-between">
                <div className="text-sm opacity-50">
                  Self-healing: {selectedBento.selfHealing ? 'Enabled' : 'Disabled'}
                </div>
                <div className="text-sm opacity-50">
                  Update interval: {selectedBento.updateInterval}ms
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SpatialGlassUI;
