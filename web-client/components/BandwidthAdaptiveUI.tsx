/**
 * Bandwidth Adaptive UI Component - DEDAN Mine
 * Automatically detects slow connections and switches to High-Efficiency Mode
 * Disables 3D/Satellite video while keeping ZK-Auth active
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface BandwidthInfo {
  downlink: number;      // Mbps
  rtt: number;          // Round trip time in ms
  effectiveType: string; // 'slow-2g', '2g', '3g', '4g'
  saveData: boolean;     // Data saver mode
}

interface UIConfig {
  mode: 'full' | 'high-efficiency';
  animations: boolean;
  threeD: boolean;
  satelliteVideo: boolean;
  particleEffects: boolean;
  holographicElements: boolean;
  zkAuth: boolean;       // Always active
  imageQuality: 'high' | 'medium' | 'low';
  videoQuality: '1080p' | '720p' | '480p' | 'disabled';
}

const BandwidthAdaptiveUI: React.FC<{
  children: React.ReactNode;
  onModeChange?: (mode: 'full' | 'high-efficiency') => void;
}> = ({ children, onModeChange }) => {
  const [bandwidthInfo, setBandwidthInfo] = useState<BandwidthInfo | null>(null);
  const [uiConfig, setUIConfig] = useState<UIConfig>({
    mode: 'full',
    animations: true,
    threeD: true,
    satelliteVideo: true,
    particleEffects: true,
    holographicElements: true,
    zkAuth: true,        // ZK-Auth always active
    imageQuality: 'high',
    videoQuality: '1080p'
  });
  const [connectionTest, setConnectionTest] = useState<'testing' | 'complete' | 'failed'>('testing');

  // Bandwidth detection
  const detectBandwidth = useCallback(async (): Promise<BandwidthInfo> => {
    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection;

    if (connection) {
      return {
        downlink: connection.downlink || 0,
        rtt: connection.rtt || 0,
        effectiveType: connection.effectiveType || 'unknown',
        saveData: connection.saveData || false
      };
    }

    // Fallback: Manual bandwidth test
    return await performManualBandwidthTest();
  }, []);

  // Manual bandwidth test
  const performManualBandwidthTest = async (): Promise<BandwidthInfo> => {
    const startTime = Date.now();
    const testSize = 1024 * 1024; // 1MB test
    
    try {
      const response = await fetch('/api/bandwidth-test', {
        method: 'POST',
        body: JSON.stringify({ size: testSize }),
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await response.arrayBuffer();
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000; // seconds
      
      const downlink = (testSize * 8) / (duration * 1024 * 1024); // Mbps
      const rtt = await measureRTT();
      
      // Determine effective type
      let effectiveType = '4g';
      if (downlink < 0.05) effectiveType = 'slow-2g';
      else if (downlink < 0.15) effectiveType = '2g';
      else if (downlink < 0.5) effectiveType = '3g';
      
      return {
        downlink,
        rtt,
        effectiveType,
        saveData: false
      };
    } catch (error) {
      console.error('Bandwidth test failed:', error);
      return {
        downlink: 0,
        rtt: 1000,
        effectiveType: 'slow-2g',
        saveData: true
      };
    }
  };

  // Measure round trip time
  const measureRTT = async (): Promise<number> => {
    const start = Date.now();
    try {
      await fetch('/api/ping', { method: 'HEAD' });
      return Date.now() - start;
    } catch {
      return 1000; // Fallback high RTT
    }
  };

  // Determine UI mode based on bandwidth
  const determineUIMode = useCallback((bandwidth: BandwidthInfo): UIConfig => {
    const { downlink, effectiveType, saveData } = bandwidth;
    
    // High-efficiency mode conditions
    const needsHighEfficiency = 
      saveData ||
      effectiveType === 'slow-2g' ||
      effectiveType === '2g' ||
      downlink < 0.1 ||  // Less than 100 kbps
      bandwidth.rtt > 1000; // More than 1 second RTT

    if (needsHighEfficiency) {
      return {
        mode: 'high-efficiency',
        animations: false,
        threeD: false,
        satelliteVideo: false,
        particleEffects: false,
        holographicElements: false,
        zkAuth: true,        // ZK-Auth always active
        imageQuality: 'low',
        videoQuality: 'disabled'
      };
    }

    // Medium efficiency for 3g
    if (effectiveType === '3g' || downlink < 0.5) {
      return {
        mode: 'high-efficiency',
        animations: true,    // Keep some animations
        threeD: false,
        satelliteVideo: false,
        particleEffects: false,
        holographicElements: false,
        zkAuth: true,
        imageQuality: 'medium',
        videoQuality: '480p'
      };
    }

    // Full mode for good connections
    return {
      mode: 'full',
      animations: true,
      threeD: true,
      satelliteVideo: true,
      particleEffects: true,
      holographicElements: true,
      zkAuth: true,
      imageQuality: 'high',
      videoQuality: '1080p'
    };
  }, []);

  // Initialize bandwidth detection
  useEffect(() => {
    const initializeBandwidthDetection = async () => {
      try {
        const bandwidth = await detectBandwidth();
        setBandwidthInfo(bandwidth);
        
        const config = determineUIMode(bandwidth);
        setUIConfig(config);
        setConnectionTest('complete');
        
        onModeChange?.(config.mode);
      } catch (error) {
        console.error('Bandwidth detection failed:', error);
        setConnectionTest('failed');
        
        // Fallback to high-efficiency mode
        const fallbackConfig = {
          mode: 'high-efficiency' as const,
          animations: false,
          threeD: false,
          satelliteVideo: false,
          particleEffects: false,
          holographicElements: false,
          zkAuth: true,
          imageQuality: 'low' as const,
          videoQuality: 'disabled' as const
        };
        setUIConfig(fallbackConfig);
        onModeChange?.('high-efficiency');
      }
    };

    initializeBandwidthDetection();

    // Set up periodic rechecking
    const interval = setInterval(initializeBandwidthDetection, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [detectBandwidth, determineUIMode, onModeChange]);

  // Listen for connection changes
  useEffect(() => {
    const connection = (navigator as any).connection;
    
    if (connection) {
      const handleChange = () => {
        detectBandwidth().then(bandwidth => {
          setBandwidthInfo(bandwidth);
          const config = determineUIMode(bandwidth);
          setUIConfig(config);
          onModeChange?.(config.mode);
        });
      };

      connection.addEventListener('change', handleChange);
      return () => connection.removeEventListener('change', handleChange);
    }
  }, [detectBandwidth, determineUIMode, onModeChange]);

  // Memoized context value
  const contextValue = useMemo(() => ({
    bandwidthInfo,
    uiConfig,
    connectionTest,
    isHighEfficiency: uiConfig.mode === 'high-efficiency',
    isZKAuthActive: uiConfig.zkAuth
  }), [bandwidthInfo, uiConfig, connectionTest]);

  // Animation variants
  const containerVariants = {
    full: {
      transition: { duration: 0.3, ease: "easeInOut" }
    },
    'high-efficiency': {
      transition: { duration: 0.1, ease: "easeOut" }
    }
  };

  return (
    <BandwidthContext.Provider value={contextValue}>
      <motion.div
        className="bandwidth-adaptive-container"
        variants={containerVariants}
        animate={uiConfig.mode}
        style={{
          '--animation-duration': uiConfig.animations ? '0.3s' : '0s',
          '--image-quality': uiConfig.imageQuality,
          '--video-quality': uiConfig.videoQuality,
          '--particle-effects': uiConfig.particleEffects ? 'block' : 'none',
          '--3d-transforms': uiConfig.threeD ? 'preserve-3d' : 'flat',
          '--satellite-video': uiConfig.satelliteVideo ? 'block' : 'none',
          '--holographic-elements': uiConfig.holographicElements ? 'block' : 'none'
        } as React.CSSProperties}
      >
        {/* Connection Status Indicator */}
        <AnimatePresence>
          {connectionTest === 'testing' && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="connection-status testing"
            >
              <div className="status-indicator testing">
                <div className="pulse-dot" />
                Testing connection...
              </div>
            </motion.div>
          )}
          
          {connectionTest === 'failed' && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="connection-status failed"
            >
              <div className="status-indicator failed">
                <div className="error-dot" />
                Connection test failed - Using high-efficiency mode
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Mode Indicator */}
        {bandwidthInfo && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="mode-indicator"
          >
            <div className={`mode-badge ${uiConfig.mode}`}>
              {uiConfig.mode === 'high-efficiency' ? '⚡ High-Efficiency' : '🚀 Full Mode'}
            </div>
            <div className="bandwidth-info">
              {bandwidthInfo.downlink.toFixed(1)} Mbps • {bandwidthInfo.effectiveType}
            </div>
          </motion.div>
        )}

        {/* ZK-Auth Status (Always Active) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="zk-auth-status"
        >
          <div className="zk-auth-indicator active">
            <div className="shield-icon">🛡️</div>
            Zero-Knowledge Auth: Active
          </div>
        </motion.div>

        {/* Main Content */}
        <motion.main
          className="main-content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: uiConfig.animations ? 0.5 : 0.1 }}
        >
          {children}
        </motion.main>

        {/* Performance Stats (Development Only) */}
        {process.env.NODE_ENV === 'development' && bandwidthInfo && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="performance-stats"
          >
            <div className="stats-grid">
              <div className="stat">
                <label>Downlink:</label>
                <span>{bandwidthInfo.downlink.toFixed(2)} Mbps</span>
              </div>
              <div className="stat">
                <label>RTT:</label>
                <span>{bandwidthInfo.rtt} ms</span>
              </div>
              <div className="stat">
                <label>Type:</label>
                <span>{bandwidthInfo.effectiveType}</span>
              </div>
              <div className="stat">
                <label>Save Data:</label>
                <span>{bandwidthInfo.saveData ? 'Yes' : 'No'}</span>
              </div>
              <div className="stat">
                <label>Mode:</label>
                <span>{uiConfig.mode}</span>
              </div>
              <div className="stat">
                <label>ZK-Auth:</label>
                <span>{uiConfig.zkAuth ? 'Active' : 'Inactive'}</span>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </BandwidthContext.Provider>
  );
};

// Context for sharing bandwidth info
interface BandwidthContextType {
  bandwidthInfo: BandwidthInfo | null;
  uiConfig: UIConfig;
  connectionTest: 'testing' | 'complete' | 'failed';
  isHighEfficiency: boolean;
  isZKAuthActive: boolean;
}

const BandwidthContext = React.createContext<BandwidthContextType | null>(null);

// Hook for using bandwidth context
export const useBandwidthAdaptive = (): BandwidthContextType => {
  const context = React.useContext(BandwidthContext);
  if (!context) {
    throw new Error('useBandwidthAdaptive must be used within BandwidthAdaptiveUI');
  }
  return context;
};

// HOC for adapting components
export const withBandwidthAdaptation = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return React.forwardRef<any, P>((props, ref) => {
    const { uiConfig } = useBandwidthAdaptive();
    
    return (
      <Component
        {...props}
        ref={ref}
        uiConfig={uiConfig}
      />
    );
  });
};

export default BandwidthAdaptiveUI;
