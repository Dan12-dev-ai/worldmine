import React, { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

interface ProtectedAdminRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const ProtectedAdminRoute: React.FC<ProtectedAdminRouteProps> = ({ 
  children, 
  fallback 
}) => {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const ADMIN_USER_ID = import.meta.env.VITE_ADMIN_USER_ID || 'YOUR_ADMIN_USER_ID_HERE';
  const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL!,
    import.meta.env.VITE_SUPABASE_ANON_KEY!
  );

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check if user is authenticated
      const { data: { user }, error: authError } = await supabase.auth.getUser();
      
      if (authError) {
        throw new Error('Authentication error');
      }

      if (!user) {
        // User not authenticated, redirect to home
        window.location.href = '/';
        return;
      }

      // CRITICAL SECURITY CHECK: Verify user is the admin
      const isAdminUser = user.id === ADMIN_USER_ID;
      
      if (!isAdminUser) {
        // Log unauthorized access attempt
        console.error('UNAUTHORIZED_ADMIN_ACCESS', {
          timestamp: new Date().toISOString(),
          user_id: user.id,
          attempted_admin_id: ADMIN_USER_ID,
          ip_address: await getClientIP(),
          user_agent: navigator.userAgent
        });

        // Redirect non-admin users immediately
        window.location.href = '/';
        return;
      }

      setIsAdmin(true);

    } catch (error) {
      console.error('Admin access check failed:', error);
      setError('Failed to verify admin access');
      
      // Redirect on error as a safety measure
      setTimeout(() => {
        window.location.href = '/';
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  const getClientIP = async (): Promise<string> => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return 'unknown';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-cyber-dark flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan mx-auto"></div>
          <p className="text-gray-400">Verifying admin access...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-cyber-dark flex items-center justify-center">
        <div className="text-center space-y-4 glass-morphism rounded-xl p-8 max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
          <h2 className="text-xl font-bold text-white">Access Error</h2>
          <p className="text-gray-400">{error}</p>
          <p className="text-sm text-gray-500">Redirecting to home page...</p>
        </div>
      </div>
    );
  }

  if (isAdmin === false) {
    // This should redirect automatically, but provide a fallback
    return fallback || (
      <div className="min-h-screen bg-cyber-dark flex items-center justify-center">
        <div className="text-center space-y-4 glass-morphism rounded-xl p-8 max-w-md">
          <ShieldCheck className="w-12 h-12 text-yellow-500 mx-auto" />
          <h2 className="text-xl font-bold text-white">Access Denied</h2>
          <p className="text-gray-400">Admin access required</p>
          <p className="text-sm text-gray-500">Redirecting to home page...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedAdminRoute;
