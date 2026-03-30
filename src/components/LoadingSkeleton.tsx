import React from 'react';
import { motion } from 'framer-motion';

interface LoadingSkeletonProps {
  className?: string;
  height?: string;
  width?: string;
  lines?: number;
  variant?: 'text' | 'card' | 'list' | 'news';
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  className = '', 
  height = 'h-4', 
  width = 'w-full',
  lines = 1,
  variant = 'text'
}) => {
  const baseClasses = 'bg-gray-700 rounded-lg animate-pulse';
  
  if (variant === 'card') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`glass-morphism rounded-2xl p-6 ${className}`}
      >
        <div className="space-y-4">
          <div className={`${baseClasses} h-48 w-full mb-4`} />
          <div className="space-y-2">
            <div className={`${baseClasses} h-4 w-3/4`} />
            <div className={`${baseClasses} h-4 w-1/2`} />
          </div>
          <div className={`${baseClasses} h-24 w-full`} />
        </div>
      </motion.div>
    );
  }

  if (variant === 'list') {
    return (
      <div className={`space-y-4 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-morphism rounded-xl p-4"
          >
            <div className="flex items-start space-x-4">
              <div className={`${baseClasses} h-12 w-12 rounded-full`} />
              <div className="flex-1 space-y-2">
                <div className={`${baseClasses} h-4 w-3/4`} />
                <div className={`${baseClasses} h-3 w-1/2`} />
                <div className={`${baseClasses} h-16 w-full`} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    );
  }

  if (variant === 'news') {
    return (
      <div className={`space-y-6 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.15 }}
            className="glass-morphism rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`${baseClasses} h-6 w-32 rounded`} />
              <div className={`${baseClasses} h-6 w-20 rounded`} />
            </div>
            <div className={`${baseClasses} h-20 w-full mb-3`} />
            <div className="flex items-center space-x-2 mb-4">
              <div className={`${baseClasses} h-4 w-4 rounded-full`} />
              <div className={`${baseClasses} h-4 w-24 rounded`} />
            </div>
            <div className={`${baseClasses} h-16 w-full`} />
          </motion.div>
        ))}
      </div>
    );
  }

  // Default text skeleton
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: index * 0.05 }}
          className={`${baseClasses} ${height} ${width}`}
        />
      ))}
    </div>
  );
};

// Latency simulation component
export const LatencySimulator: React.FC<{
  children: React.ReactNode;
  delay: number;
  fallback?: React.ReactNode;
}> = ({ children, delay, fallback }) => {
  const [isLoading, setIsLoading] = React.useState(true);
  const [hasError, setHasError] = React.useState(false);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (delay > 3000) { // Consider >3s as error
        setHasError(true);
      } else {
        setIsLoading(false);
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  if (hasError) {
    return (
      <div className="glass-morphism rounded-xl p-8 text-center">
        <div className="text-red-500 mb-4">
          <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 2v3a1 1 0 001-2v-3a1 1 0 00-2-1V9a1 1 0 002-1z" clipRule="evenodd" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">Connection Timeout</h3>
        <p className="text-gray-400">
          Request is taking longer than expected. This might be due to network issues or high server load.
        </p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-neon-cyan text-black rounded-lg hover:bg-neon-cyan/80 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (isLoading) {
    return fallback || <LoadingSkeleton variant="card" />;
  }

  return <>{children}</>;
};

// Network status indicator
export const NetworkStatus: React.FC<{
  latency: number;
  status: 'connected' | 'slow' | 'disconnected';
}> = ({ latency, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'text-green-500';
      case 'slow': return 'text-yellow-500';
      case 'disconnected': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'connected': return '●';
      case 'slow': return '◐';
      case 'disconnected': return '●';
      default: return '○';
    }
  };

  return (
    <div className="flex items-center space-x-2 text-sm">
      <span className={`${getStatusColor()} font-mono`}>
        {getStatusIcon()}
      </span>
      <span className="text-gray-400">
        {latency}ms
      </span>
      <span className={`capitalize ${getStatusColor()}`}>
        {status}
      </span>
    </div>
  );
};

export default LoadingSkeleton;
