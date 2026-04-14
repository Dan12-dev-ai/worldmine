/**
 * DEDAN Mine - Mobile Thumb Zone Component (v4.5.0)
 * One-Handed Command Interface for Mobile Devices
 * Critical action buttons in the bottom 30% of screen
 * Optimistic UI updates for instant user feedback
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowUp,
    ArrowDown,
    Wallet,
    Brain,
    TrendingUp,
    CreditCard,
    ArrowRight,
    ArrowLeft,
    Plus,
    Minus,
    SwapHorizontal,
    ShoppingCart,
    PieChart,
    Bell,
    User,
    Home,
    BarChart3,
    Settings,
    Shield,
    Zap,
    Lock,
    Unlock,
    Eye,
    EyeOff,
    ChevronUp,
    ChevronDown,
    X
} from 'lucide-react';

const MobileThumbZone = ({
    isVisible,
    actions = ['buy', 'sell', 'wallet', 'ai'],
    optimisticUI = true,
    onAction,
    balance,
    currentPrice,
    notifications = 0,
    userVerified = false
}) => {
    const [activeAction, setActiveAction] = useState(null);
    const [processingActions, setProcessingActions] = useState(new Set());
    const [showQuickActions, setShowQuickActions] = useState(false);
    const [biometricPrompt, setBiometricPrompt] = useState(false);
    const [hapticFeedback, setHapticFeedback] = useState(false);
    
    // Default action configurations
    const defaultActions = {
        buy: {
            icon: ArrowUp,
            label: 'Buy',
            color: 'green',
            bgGradient: 'from-green-500 to-emerald-600',
            requiresAuth: false,
            haptic: 'light'
        },
        sell: {
            icon: ArrowDown,
            label: 'Sell',
            color: 'red',
            bgGradient: 'from-red-500 to-pink-600',
            requiresAuth: false,
            haptic: 'light'
        },
        wallet: {
            icon: Wallet,
            label: 'Wallet',
            color: 'blue',
            bgGradient: 'from-blue-500 to-indigo-600',
            requiresAuth: false,
            haptic: 'medium'
        },
        ai: {
            icon: Brain,
            label: 'Ask AI',
            color: 'purple',
            bgGradient: 'from-purple-500 to-pink-600',
            requiresAuth: false,
            haptic: 'light'
        },
        trade: {
            icon: SwapHorizontal,
            label: 'Trade',
            color: 'yellow',
            bgGradient: 'from-yellow-500 to-orange-600',
            requiresAuth: true,
            haptic: 'heavy'
        },
        portfolio: {
            icon: PieChart,
            label: 'Portfolio',
            color: 'indigo',
            bgGradient: 'from-indigo-500 to-purple-600',
            requiresAuth: false,
            haptic: 'medium'
        }
    };
    
    // Enhanced actions with additional options
    const enhancedActions = {
        ...defaultActions,
        quickBuy: {
            icon: Plus,
            label: 'Quick Buy',
            color: 'green',
            bgGradient: 'from-green-600 to-emerald-700',
            requiresAuth: false,
            haptic: 'light'
        },
        quickSell: {
            icon: Minus,
            label: 'Quick Sell',
            color: 'red',
            bgGradient: 'from-red-600 to-pink-700',
            requiresAuth: false,
            haptic: 'light'
        },
        notifications: {
            icon: Bell,
            label: 'Alerts',
            color: 'yellow',
            bgGradient: 'from-yellow-500 to-orange-600',
            requiresAuth: false,
            haptic: 'light'
        },
        profile: {
            icon: User,
            label: 'Profile',
            color: 'blue',
            bgGradient: 'from-blue-500 to-indigo-600',
            requiresAuth: false,
            haptic: 'medium'
        }
    };
    
    // Trigger haptic feedback
    const triggerHaptic = useCallback((intensity = 'light') => {
        if ('vibrate' in navigator) {
            const patterns = {
                light: [10],
                medium: [50],
                heavy: [100, 50, 100]
            };
            navigator.vibrate(patterns[intensity] || patterns.light);
        }
        setHapticFeedback(true);
        setTimeout(() => setHapticFeedback(false), 100);
    }, []);
    
    // Handle action press
    const handleActionPress = useCallback(async (actionKey) => {
        const action = enhancedActions[actionKey];
        
        if (!action) return;
        
        // Trigger haptic feedback
        triggerHaptic(action.haptic);
        
        // Check if authentication required
        if (action.requiresAuth && !userVerified) {
            setBiometricPrompt(true);
            return;
        }
        
        // Set active action for visual feedback
        setActiveAction(actionKey);
        
        // Add to processing set
        setProcessingActions(prev => new Set(prev).add(actionKey));
        
        // Optimistic UI update
        if (optimisticUI) {
            onAction(actionKey, { optimistic: true });
        }
        
        // Simulate processing
        setTimeout(() => {
            setProcessingActions(prev => {
                const newSet = new Set(prev);
                newSet.delete(actionKey);
                return newSet;
            });
            setActiveAction(null);
            
            // Real callback
            if (!optimisticUI) {
                onAction(actionKey, { optimistic: false });
            }
        }, 1500);
    }, [actionKey, userVerified, optimisticUI, onAction, triggerHaptic]);
    
    // Handle biometric verification
    const handleBiometricVerification = useCallback(async () => {
        triggerHaptic('heavy');
        
        // Simulate biometric verification
        setTimeout(() => {
            setBiometricPrompt(false);
            // Retry the action that required auth
            if (activeAction) {
                handleActionPress(activeAction);
            }
        }, 2000);
    }, [activeAction, handleActionPress, triggerHaptic]);
    
    // Get action configuration
    const getActionConfig = useCallback((actionKey) => {
        return enhancedActions[actionKey] || defaultActions[actionKey];
    }, []);
    
    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ y: 100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 100, opacity: 0 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    className="fixed bottom-0 left-0 right-0 z-50"
                >
                    {/* Main Action Bar */}
                    <div className="bg-black/95 backdrop-blur-xl border-t border-white/10">
                        {/* Safe Area Padding */}
                        <div className="pb-safe">
                            {/* Quick Actions Header */}
                            <AnimatePresence>
                                {showQuickActions && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="border-b border-white/10"
                                    >
                                        <div className="p-4">
                                            <div className="flex items-center justify-between mb-3">
                                                <span className="text-white/60 text-sm">Quick Actions</span>
                                                <button
                                                    onClick={() => setShowQuickActions(false)}
                                                    className="text-white/60 hover:text-white"
                                                >
                                                    <X className="w-4 h-4" />
                                                </button>
                                            </div>
                                            <div className="grid grid-cols-4 gap-3">
                                                {Object.entries(enhancedActions)
                                                    .filter(([key]) => !actions.includes(key))
                                                    .slice(0, 4)
                                                    .map(([key, action]) => (
                                                        <button
                                                            key={key}
                                                            onClick={() => handleActionPress(key)}
                                                            className={`flex flex-col items-center justify-center p-3 rounded-xl ${action.color}/10 hover:${action.color}/20 transition-all`}
                                                        >
                                                            <action.icon className={`w-5 h-5 text-${action.color}-400`} />
                                                            <span className="text-xs text-white/60 mt-1">{action.label}</span>
                                                        </button>
                                                    ))}
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                            
                            {/* Main Actions */}
                            <div className="p-4">
                                {/* Balance Display */}
                                {(balance !== undefined || currentPrice !== undefined) && (
                                    <div className="mb-4 p-3 bg-white/5 rounded-xl">
                                        <div className="flex items-center justify-between">
                                            {balance !== undefined && (
                                                <div>
                                                    <p className="text-xs text-white/60">Balance</p>
                                                    <p className="text-sm font-medium text-white">
                                                        ${balance.toLocaleString()}
                                                    </p>
                                                </div>
                                            )}
                                            {currentPrice !== undefined && (
                                                <div className="text-right">
                                                    <p className="text-xs text-white/60">Current</p>
                                                    <p className="text-sm font-medium text-white">
                                                        ${currentPrice.toFixed(2)}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                                
                                {/* Action Buttons */}
                                <div className="grid grid-cols-4 gap-3">
                                    {actions.map((actionKey) => {
                                        const action = getActionConfig(actionKey);
                                        const isActive = activeAction === actionKey;
                                        const isProcessing = processingActions.has(actionKey);
                                        
                                        return (
                                            <motion.button
                                                key={actionKey}
                                                layout
                                                initial={{ scale: 1 }}
                                                animate={{
                                                    scale: isActive ? 0.95 : 1,
                                                    backgroundColor: isActive ? `${action.color}/20` : 'transparent'
                                                }}
                                                whileTap={{ scale: 0.9 }}
                                                transition={{ duration: 0.1 }}
                                                onClick={() => handleActionPress(actionKey)}
                                                className={`relative flex flex-col items-center justify-center p-3 rounded-xl ${
                                                    isProcessing
                                                        ? `${action.color}/20 animate-pulse`
                                                        : `${action.color}/10 hover:${action.color}/20`
                                                } transition-all`}
                                            >
                                                {/* Action Icon */}
                                                <div className={`relative ${isProcessing ? 'animate-spin' : ''}`}>
                                                    <action.icon 
                                                        className={`w-6 h-6 text-${action.color}-400 ${
                                                            isProcessing ? 'opacity-50' : ''
                                                        }`} 
                                                    />
                                                    
                                                    {/* Processing Indicator */}
                                                    {isProcessing && (
                                                        <div className="absolute inset-0 flex items-center justify-center">
                                                            <div className="w-8 h-8 border-2 border-white/30 border-t-transparent rounded-full animate-spin" />
                                                        </div>
                                                    )}
                                                </div>
                                                
                                                {/* Action Label */}
                                                <span className={`text-xs text-white/60 mt-1 ${
                                                    isProcessing ? 'opacity-50' : ''
                                                }`}>
                                                    {action.label}
                                                </span>
                                                
                                                {/* Haptic Feedback Indicator */}
                                                <AnimatePresence>
                                                    {hapticFeedback && (
                                                        <motion.div
                                                            initial={{ scale: 0, opacity: 0 }}
                                                            animate={{ scale: 1, opacity: 1 }}
                                                            exit={{ scale: 0, opacity: 0 }}
                                                            className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full"
                                                        />
                                                    )}
                                                </AnimatePresence>
                                                
                                                {/* Notification Badge */}
                                                {actionKey === 'notifications' && notifications > 0 && (
                                                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                                                        <span className="text-xs text-white font-bold">
                                                            {notifications > 9 ? '9+' : notifications}
                                                        </span>
                                                    </div>
                                                )}
                                                
                                                {/* Security Indicator */}
                                                {action.requiresAuth && !userVerified && (
                                                    <div className="absolute -top-1 -left-1">
                                                        <Lock className="w-3 h-3 text-yellow-400" />
                                                    </div>
                                                )}
                                            </motion.button>
                                        );
                                    })}
                                    
                                    {/* More Actions Button */}
                                    <motion.button
                                        layout
                                        initial={{ scale: 1 }}
                                        whileTap={{ scale: 0.9 }}
                                        onClick={() => setShowQuickActions(!showQuickActions)}
                                        className="flex flex-col items-center justify-center p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-all"
                                    >
                                        <div className="relative">
                                            {showQuickActions ? (
                                                <X className="w-6 h-6 text-white/60" />
                                            ) : (
                                                <ChevronUp className="w-6 h-6 text-white/60" />
                                            )}
                                        </div>
                                        <span className="text-xs text-white/60 mt-1">
                                            {showQuickActions ? 'Less' : 'More'}
                                        </span>
                                    </motion.button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {/* Biometric Verification Modal */}
                    <AnimatePresence>
                        {biometricPrompt && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
                            >
                                <motion.div
                                    initial={{ scale: 0.9, y: 20 }}
                                    animate={{ scale: 1, y: 0 }}
                                    exit={{ scale: 0.9, y: 20 }}
                                    className="bg-black/90 backdrop-blur-xl rounded-2xl p-6 max-w-sm w-full border border-white/10"
                                >
                                    <div className="text-center">
                                        <div className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <Shield className="w-8 h-8 text-yellow-400" />
                                        </div>
                                        
                                        <h3 className="text-lg font-semibold text-white mb-2">
                                            Authentication Required
                                        </h3>
                                        
                                        <p className="text-white/60 text-sm mb-6">
                                            This action requires biometric verification for your security.
                                        </p>
                                        
                                        <div className="space-y-3">
                                            <button
                                                onClick={handleBiometricVerification}
                                                className="w-full px-4 py-3 bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl transition-colors flex items-center justify-center space-x-2"
                                            >
                                                <Fingerprint className="w-5 h-5" />
                                                <span>Verify with Biometrics</span>
                                            </button>
                                            
                                            <button
                                                onClick={() => setBiometricPrompt(false)}
                                                className="w-full px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default MobileThumbZone;
