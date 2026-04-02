import React, { useEffect, useState } from 'react';

/**
 * KeepAlive Component - Prevents Render Free Tier from sleeping
 * Pings the backend API every 10 minutes to keep it active
 */
const KeepAlive: React.FC = () => {
  const [isAlive, setIsAlive] = useState<boolean>(true);
  const [lastPing, setLastPing] = useState<string>('');
  const [errorCount, setErrorCount] = useState<number>(0);

  useEffect(() => {
    const pingBackend = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'https://worldmine-api.onrender.com';
        const response = await fetch(`${apiUrl}/api/health`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Worldmine-KeepAlive/1.0'
          },
          cache: 'no-cache'
        });

        if (response.ok) {
          const data = await response.json();
          setIsAlive(true);
          setLastPing(new Date().toLocaleTimeString());
          setErrorCount(0);
          console.log('✅ Backend ping successful:', data);
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
      } catch (error) {
        console.error('❌ Backend ping failed:', error);
        setErrorCount(prev => prev + 1);
        
        // Only mark as dead after 3 consecutive failures
        if (errorCount >= 2) {
          setIsAlive(false);
        }
      }
    };

    // Initial ping
    pingBackend();

    // Set up interval - every 10 minutes (600,000 ms)
    const interval = setInterval(pingBackend, 10 * 60 * 1000);

    // Cleanup
    return () => clearInterval(interval);
  }, [errorCount]);

  // This component is invisible - it just runs in the background
  return null;
};

export default KeepAlive;
