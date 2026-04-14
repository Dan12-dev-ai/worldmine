/**
 * DEDAN Mine - Spatial Liquid Glass UI (v4.5.0)
 * 2026 Global Fintech Standards with Invisible Security & Planetary Trust
 * Spatial Glassmorphism with 25px background blur and dynamic mesh gradients
 * shadcn/ui components with Bento Box layouts for high information density
 * Responsive from 320px mobile to 4K ultra-wide with Tailwind CSS container queries
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence, useAnimation, useScroll, useTransform } from 'framer-motion';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import {
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
    Globe,
    Lock,
    Unlock,
    Sparkles,
    Flame,
    Brain,
    Fingerprint,
    Smartphone,
    Monitor,
    Tablet,
    ChevronDown,
    ChevronUp,
    Menu,
    X,
    Search,
    Bell,
    User,
    Home,
    BarChart3,
    CreditCard,
    ArrowRight,
    ArrowLeft,
    RefreshCw,
    Download,
    Upload,
    Filter,
    Calendar,
    Clock,
    MapPin,
    Phone,
    Mail,
  } from 'lucide-react';

// Responsive breakpoint hook
const useBreakpoint = () => {
    const [breakpoint, setBreakpoint] = useState('desktop');
    
    useEffect(() => {
        const updateBreakpoint = () => {
            const width = window.innerWidth;
            if (width < 640) setBreakpoint('mobile');
            else if (width < 768) setBreakpoint('sm');
            else if (width < 1024) setBreakpoint('md');
            else if (width < 1280) setBreakpoint('lg');
            else if (width < 1536) setBreakpoint('xl');
            else if (width < 1920) setBreakpoint('2xl');
            else setBreakpoint('4k');
        };
        
        updateBreakpoint();
        window.addEventListener('resize', updateBreakpoint);
        return () => window.removeEventListener('resize', updateBreakpoint);
    }, []);
    
    return breakpoint;
};

// Security Pulse Component
const SecurityPulse = ({ isActive, quantumVerified }) => {
    const [pulseIntensity, setPulseIntensity] = useState(0.3);
    
    useEffect(() => {
        if (isActive && quantumVerified) {
            const interval = setInterval(() => {
                setPulseIntensity(prev => {
                    const next = prev + 0.1;
                    return next > 1 ? 0.3 : next;
                });
            }, 1000);
            return () => clearInterval(interval);
        }
    }, [isActive, quantumVerified]);
    
    return (
        <div className="absolute inset-0 rounded-2xl pointer-events-none">
            <div 
                className="absolute inset-0 rounded-2xl border-2 transition-all duration-1000"
                style={{
                    borderColor: quantumVerified 
                        ? `rgba(34, 197, 94, ${pulseIntensity})` 
                        : `rgba(239, 68, 68, ${pulseIntensity})`,
                    boxShadow: quantumVerified
                        ? `0 0 ${20 * pulseIntensity}px rgba(34, 197, 94, 0.3)`
                        : `0 0 ${20 * pulseIntensity}px rgba(239, 68, 68, 0.3)`,
                    borderWidth: quantumVerified ? '3px' : '2px'
                }}
            />
            {quantumVerified && (
                <div className="absolute top-2 right-2 flex items-center space-x-1 px-2 py-1 bg-green-500/20 backdrop-blur-sm rounded-full">
                    <Shield className="w-3 h-3 text-green-400" />
                    <span className="text-xs text-green-400 font-medium">NIST-2026 PQC</span>
                </div>
            )}
        </div>
    );
};

// Bento Box Component
const BentoBox = ({ 
    children, 
    size = 'medium', 
    className = '', 
    glassIntensity = 25,
    withSecurityPulse = false,
    quantumVerified = true 
}) => {
    const [isHovered, setIsHovered] = useState(false);
    const [isPressed, setIsPressed] = useState(false);
    
    const sizeClasses = {
        small: 'col-span-1 row-span-1',
        medium: 'col-span-1 row-span-2',
        large: 'col-span-2 row-span-2',
        wide: 'col-span-3 row-span-1',
        tall: 'col-span-1 row-span-3'
    };
    
    return (
        <motion.div
            className={`
                relative overflow-hidden rounded-2xl cursor-pointer transition-all duration-300
                ${sizeClasses[size] || sizeClasses.medium}
                ${className}
            `}
            style={{
                background: `linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.1), 
                    rgba(255, 255, 255, 0.05))`,
                backdropFilter: `blur(${glassIntensity}px)`,
                WebkitBackdropFilter: `blur(${glassIntensity}px)`,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: isHovered 
                    ? '0 20px 40px rgba(0, 0, 0, 0.3)' 
                    : '0 8px 32px rgba(0, 0, 0, 0.1)',
            }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
            onTapStart={() => setIsPressed(true)}
            onTap={() => setIsPressed(false)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
        >
            {/* Dynamic Mesh Gradient Background */}
            <div className="absolute inset-0 opacity-30">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20 animate-pulse" />
                <div className="absolute inset-0 bg-gradient-to-tr from-green-500/10 via-yellow-500/10 to-red-500/10 animate-pulse" style={{ animationDelay: '1s' }} />
            </div>
            
            {/* Content */}
            <div className="relative z-10 p-6 h-full flex flex-col">
                {children}
            </div>
            
            {/* Security Pulse */}
            {withSecurityPulse && (
                <SecurityPulse isActive={isHovered} quantumVerified={quantumVerified} />
            )}
            
            {/* Glass Effect Overlay */}
            <div 
                className="absolute inset-0 pointer-events-none rounded-2xl"
                style={{
                    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
                    backdropFilter: 'blur(10px)',
                    WebkitBackdropFilter: 'blur(10px)',
                }}
            />
        </motion.div>
    );
};

// Mobile Thumb Zone Component
const MobileThumbZone = ({ children, isVisible }) => {
    const breakpoint = useBreakpoint();
    const isMobile = breakpoint === 'mobile' || breakpoint === 'sm';
    
    if (!isMobile || !isVisible) return null;
    
    return (
        <motion.div
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            exit={{ y: 100 }}
            className="fixed bottom-0 left-0 right-0 bg-black/80 backdrop-blur-xl border-t border-white/10 z-50"
        >
            <div className="p-4 pb-safe">
                {children}
            </div>
        </motion.div>
    );
};

// Agentic Chat Overlay
const AgenticChatOverlay = ({ isOpen, onClose, onCommand }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    
    const handleSend = useCallback(() => {
        if (!input.trim()) return;
        
        const userMessage = { role: 'user', content: input, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        
        setIsTyping(true);
        setInput('');
        
        // Simulate AI response
        setTimeout(() => {
            const aiResponse = { 
                role: 'assistant', 
                content: `Processing: "${input}". I'll help you with that request.`,
                timestamp: new Date() 
            };
            setMessages(prev => [...prev, aiResponse]);
            setIsTyping(false);
            onCommand(input);
        }, 1000);
    }, [input, onCommand]);
    
    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end justify-center p-4"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ y: 100 }}
                        animate={{ y: 0 }}
                        exit={{ y: 100 }}
                        className="bg-black/90 backdrop-blur-xl rounded-t-2xl w-full max-w-md max-h-[70vh] overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-white/10">
                            <div className="flex items-center space-x-2">
                                <Brain className="w-5 h-5 text-blue-400" />
                                <span className="text-white font-medium">DEDAN Companion</span>
                            </div>
                            <button
                                onClick={onClose}
                                className="text-white/50 hover:text-white transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        
                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-96">
                            {messages.map((message, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] p-3 rounded-2xl ${
                                            message.role === 'user'
                                                ? 'bg-blue-500 text-white'
                                                : 'bg-white/10 text-white'
                                        }`}
                                    >
                                        <p className="text-sm">{message.content}</p>
                                        <p className="text-xs opacity-70 mt-1">
                                            {message.timestamp.toLocaleTimeString()}
                                        </p>
                                    </div>
                                </motion.div>
                            ))}
                            
                            {isTyping && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex justify-start"
                                >
                                    <div className="bg-white/10 text-white p-3 rounded-2xl">
                                        <div className="flex space-x-1">
                                            <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" />
                                            <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                            <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </div>
                        
                        {/* Input */}
                        <div className="p-4 border-t border-white/10">
                            <div className="flex space-x-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Ask DEDAN anything..."
                                    className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-2 text-white placeholder-white/50 focus:outline-none focus:border-white/40"
                                />
                                <button
                                    onClick={handleSend}
                                    className="bg-blue-500 hover:bg-blue-600 text-white rounded-xl px-4 py-2 transition-colors"
                                >
                                    <ArrowRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

// Main Spatial Liquid Glass UI Component
const SpatialLiquidGlassUI = () => {
    const breakpoint = useBreakpoint();
    const [selectedBento, setSelectedBento] = useState(null);
    const [showChat, setShowChat] = useState(false);
    const [quantumVerified, setQuantumVerified] = useState(true);
    const [securityPulseActive, setSecurityPulseActive] = useState(false);
    const [showMobileActions, setShowMobileActions] = useState(false);
    const [marketData, setMarketData] = useState({});
    const [walletData, setWalletData] = useState({});
    
    // Mock data updates
    useEffect(() => {
        const interval = setInterval(() => {
            setMarketData({
                price: 1850 + Math.random() * 100,
                change: (Math.random() - 0.5) * 5,
                volume: 2.3 + Math.random() * 0.5,
                activeTrades: 150 + Math.floor(Math.random() * 50)
            });
            
            setWalletData({
                totalBalance: 50000 + Math.random() * 10000,
                todayChange: (Math.random() - 0.5) * 2000,
                activeTransactions: Math.floor(Math.random() * 10)
            });
        }, 2000);
        
        return () => clearInterval(interval);
    }, []);
    
    // Responsive grid configuration
    const gridConfig = useMemo(() => {
        switch (breakpoint) {
            case 'mobile':
                return {
                    grid: 'grid-cols-2 gap-3',
                    bentoSizes: {
                        price: 'small',
                        wallet: 'small',
                        trading: 'wide',
                        security: 'small',
                        chart: 'large'
                    }
                };
            case 'sm':
                return {
                    grid: 'grid-cols-3 gap-4',
                    bentoSizes: {
                        price: 'medium',
                        wallet: 'small',
                        trading: 'large',
                        security: 'small',
                        chart: 'large'
                    }
                };
            case 'md':
                return {
                    grid: 'grid-cols-4 gap-4',
                    bentoSizes: {
                        price: 'medium',
                        wallet: 'small',
                        trading: 'large',
                        security: 'small',
                        chart: 'large'
                    }
                };
            case 'lg':
                return {
                    grid: 'grid-cols-5 gap-4',
                    bentoSizes: {
                        price: 'medium',
                        wallet: 'small',
                        trading: 'large',
                        security: 'small',
                        chart: 'large'
                    }
                };
            case 'xl':
                return {
                    grid: 'grid-cols-6 gap-4',
                    bentoSizes: {
                        price: 'medium',
                        wallet: 'small',
                        trading: 'large',
                        security: 'small',
                        chart: 'large'
                    }
                };
            case '2xl':
            case '4k':
                return {
                    grid: 'grid-cols-8 gap-6',
                    bentoSizes: {
                        price: 'large',
                        wallet: 'medium',
                        trading: 'large',
                        security: 'medium',
                        chart: 'large'
                    }
                };
            default:
                return {
                    grid: 'grid-cols-4 gap-4',
                    bentoSizes: {
                        price: 'medium',
                        wallet: 'small',
                        trading: 'large',
                        security: 'small',
                        chart: 'large'
                    }
                };
        }
    }, [breakpoint]);
    
    const handleCommand = useCallback((command) => {
        console.log('Command received:', command);
        // Handle AI commands here
    }, []);
    
    const handleBiometricScan = useCallback(() => {
        setSecurityPulseActive(true);
        // Simulate biometric scan
        setTimeout(() => {
            setSecurityPulseActive(false);
            setQuantumVerified(true);
        }, 2000);
    }, []);
    
    return (
        <div className="min-h-screen bg-black text-white overflow-hidden">
            {/* Dynamic Mesh Gradient Background */}
            <div className="fixed inset-0">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 animate-pulse" />
                <div className="absolute inset-0 bg-gradient-to-tr from-green-900/10 via-yellow-900/10 to-red-900/10 animate-pulse" style={{ animationDelay: '2s' }} />
                <div className="absolute inset-0 bg-gradient-to-bl from-indigo-900/15 via-cyan-900/15 to-orange-900/15 animate-pulse" style={{ animationDelay: '4s' }} />
            </div>
            
            {/* Header */}
            <header className="relative z-10 p-4 lg:p-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <Sparkles className="w-6 h-6 lg:w-8 lg:h-8 text-blue-400" />
                            <h1 className="text-xl lg:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                                DEDAN Mine
                            </h1>
                        </div>
                        <div className="hidden lg:flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${
                                quantumVerified ? 'bg-green-400' : 'bg-red-400'
                            }`} />
                            <span className="text-sm text-white/70">
                                {quantumVerified ? 'Quantum Verified' : 'Verification Required'}
                            </span>
                        </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 lg:space-x-4">
                        {/* Mobile Menu */}
                        <button className="lg:hidden p-2">
                            <Menu className="w-5 h-5" />
                        </button>
                        
                        {/* Desktop Actions */}
                        <div className="hidden lg:flex items-center space-x-4">
                            <button className="p-2 rounded-lg bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all">
                                <Search className="w-4 h-4" />
                            </button>
                            <button className="p-2 rounded-lg bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all">
                                <Bell className="w-4 h-4" />
                            </button>
                            <button className="p-2 rounded-lg bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all">
                                <User className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => setShowChat(true)}
                                className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all flex items-center space-x-2"
                            >
                                <Brain className="w-4 h-4" />
                                <span className="hidden xl:inline">Ask DEDAN</span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>
            
            {/* Main Content */}
            <main className="relative z-10 p-4 lg:p-6">
                <div className={`grid ${gridConfig.grid} max-w-screen-2xl 4xl:max-w-screen-3xl mx-auto`}>
                    {/* Price Bento */}
                    <BentoBox 
                        size={gridConfig.bentoSizes.price} 
                        withSecurityPulse={true}
                        quantumVerified={quantumVerified}
                        onClick={() => setSelectedBento('price')}
                    >
                        <div className="flex flex-col h-full">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                    <DollarSign className="w-5 h-5 text-green-400" />
                                    <h3 className="text-lg font-semibold">Current Price</h3>
                                </div>
                                <TrendingUp className="w-4 h-4 text-green-400" />
                            </div>
                            <div className="flex-1 flex flex-col justify-center">
                                <div className="text-2xl lg:text-3xl font-bold">
                                    ${marketData.price?.toFixed(2) || '0.00'}
                                </div>
                                <div className={`text-sm mt-1 ${
                                    (marketData.change || 0) > 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {(marketData.change || 0) > 0 ? '+' : ''}{(marketData.change || 0).toFixed(2)}%
                                </div>
                            </div>
                            <div className="text-xs text-white/50 mt-2">
                                Volume: {(marketData.volume || 0).toFixed(1)}B
                            </div>
                        </div>
                    </BentoBox>
                    
                    {/* Wallet Bento */}
                    <BentoBox 
                        size={gridConfig.bentoSizes.wallet}
                        onClick={() => setSelectedBento('wallet')}
                    >
                        <div className="flex flex-col h-full">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                    <Wallet className="w-5 h-5 text-blue-400" />
                                    <h3 className="text-lg font-semibold">Wallet</h3>
                                </div>
                                <Shield className="w-4 h-4 text-green-400" />
                            </div>
                            <div className="flex-1 flex flex-col justify-center">
                                <div className="text-xl lg:text-2xl font-bold">
                                    ${(walletData.totalBalance || 0).toLocaleString()}
                                </div>
                                <div className={`text-sm mt-1 ${
                                    (walletData.todayChange || 0) > 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {(walletData.todayChange || 0) > 0 ? '+' : ''}${(walletData.todayChange || 0).toFixed(2)}
                                </div>
                            </div>
                            <div className="text-xs text-white/50 mt-2">
                                {walletData.activeTransactions || 0} active
                            </div>
                        </div>
                    </BentoBox>
                    
                    {/* Trading Bento */}
                    <BentoBox 
                        size={gridConfig.bentoSizes.trading}
                        withSecurityPulse={securityPulseActive}
                        quantumVerified={quantumVerified}
                        onClick={() => setSelectedBento('trading')}
                    >
                        <div className="flex flex-col h-full">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                    <Activity className="w-5 h-5 text-purple-400" />
                                    <h3 className="text-lg font-semibold">Trading</h3>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                                    <span className="text-xs text-green-400">Live</span>
                                </div>
                            </div>
                            <div className="flex-1">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="text-2xl font-bold">
                                            {marketData.activeTrades || 0}
                                        </div>
                                        <div className="text-xs text-white/50">Active Trades</div>
                                    </div>
                                    <div>
                                        <div className="text-2xl font-bold">
                                            98.5%
                                        </div>
                                        <div className="text-xs text-white/50">Success Rate</div>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-4 flex space-x-2">
                                <button className="flex-1 px-3 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors text-sm">
                                    Buy
                                </button>
                                <button className="flex-1 px-3 py-2 bg-red-500 hover:bg-red-600 rounded-lg transition-colors text-sm">
                                    Sell
                                </button>
                            </div>
                        </div>
                    </BentoBox>
                    
                    {/* Security Bento */}
                    <BentoBox 
                        size={gridConfig.bentoSizes.security}
                        onClick={handleBiometricScan}
                    >
                        <div className="flex flex-col h-full items-center justify-center">
                            <div className="mb-4">
                                <Fingerprint className="w-8 h-8 text-blue-400" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">Security</h3>
                            <div className="text-xs text-white/50 text-center">
                                {quantumVerified ? 'Verified' : 'Tap to verify'}
                            </div>
                        </div>
                    </BentoBox>
                    
                    {/* Chart Bento */}
                    <BentoBox 
                        size={gridConfig.bentoSizes.chart}
                        onClick={() => setSelectedBento('chart')}
                    >
                        <div className="flex flex-col h-full">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                    <BarChart3 className="w-5 h-5 text-yellow-400" />
                                    <h3 className="text-lg font-semibold">Analytics</h3>
                                </div>
                                <RefreshCw className="w-4 h-4 text-white/50" />
                            </div>
                            <div className="flex-1 flex items-center justify-center">
                                <div className="w-full h-32 bg-white/5 rounded-lg flex items-center justify-center">
                                    <div className="text-white/50 text-center">
                                        <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                                        <p className="text-xs">Real-time Chart</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </BentoBox>
                </div>
            </main>
            
            {/* Mobile Thumb Zone */}
            <MobileThumbZone isVisible={showMobileActions}>
                <div className="grid grid-cols-4 gap-2">
                    <button className="flex flex-col items-center justify-center p-3 bg-green-500/20 rounded-xl">
                        <ArrowUpRight className="w-5 h-5 text-green-400 mb-1" />
                        <span className="text-xs text-green-400">Buy</span>
                    </button>
                    <button className="flex flex-col items-center justify-center p-3 bg-red-500/20 rounded-xl">
                        <ArrowDownRight className="w-5 h-5 text-red-400 mb-1" />
                        <span className="text-xs text-red-400">Sell</span>
                    </button>
                    <button className="flex flex-col items-center justify-center p-3 bg-blue-500/20 rounded-xl">
                        <Wallet className="w-5 h-5 text-blue-400 mb-1" />
                        <span className="text-xs text-blue-400">Wallet</span>
                    </button>
                    <button className="flex flex-col items-center justify-center p-3 bg-purple-500/20 rounded-xl">
                        <Brain className="w-5 h-5 text-purple-400 mb-1" />
                        <span className="text-xs text-purple-400">Ask</span>
                    </button>
                </div>
            </MobileThumbZone>
            
            {/* Agentic Chat Overlay */}
            <AgenticChatOverlay 
                isOpen={showChat} 
                onClose={() => setShowChat(false)} 
                onCommand={handleCommand}
            />
        </div>
    );
};

export default SpatialLiquidGlassUI;
