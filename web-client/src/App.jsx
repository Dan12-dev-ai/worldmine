/**
 * DEDAN Mine - Main Application Component (v5.0.0)
 * Production-ready with analytics integration
 * Serverless optimization for zero system distraction
 */

import React, { useEffect, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import './index.css';
import { useAnalytics } from './components/AnalyticsProvider';
import GlobalSwarmDashboard from './components/GlobalSwarmDashboard';

// Lazy load components for serverless optimization
const SpatialLiquidGlassUI = React.lazy(() => import('./components/SpatialLiquidGlassUI'));
const UniversalCheckoutUI = React.lazy(() => import('./components/UniversalCheckoutUI'));
const AgenticDashboard = React.lazy(() => import('./components/AgenticDashboard'));
const MobileThumbZone = React.lazy(() => import('./components/MobileThumbZone'));

// Create React Query client for serverless optimization
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 1,
    },
  },
});

// Loading component for lazy loading
const LoadingSpinner = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#000',
    color: '#fff',
    fontFamily: 'Arial, sans-serif'
  }}>
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: '40px',
        height: '40px',
        border: '4px solid #333',
        borderTop: '4px solid #007bff',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 20px'
      }} />
      <p>Loading DEDAN Mine...</p>
    </div>
    <style>
      {`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}
    </style>
  </div>
);

// Error boundary component for route-level errors
const RouteErrorBoundary = ({ children }) => {
  const { error } = useAnalytics();
  
  return (
    <React.Suspense fallback={<LoadingSpinner />}>
      <ErrorBoundaryWrapper>
        {children}
      </ErrorBoundaryWrapper>
    </React.Suspense>
  );
};

class ErrorBoundaryWrapper extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    const { error: trackError } = useAnalytics();
    trackError(error, {
      component: 'RouteErrorBoundary',
      errorInfo,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          backgroundColor: '#000',
          color: '#fff',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <h1>Something went wrong</h1>
          <p>We're sorry, but something went wrong. Please refresh the page and try again.</p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '20px'
            }}
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Main App component
const App = () => {
  const { pageView, setUser, userAction } = useAnalytics();

  useEffect(() => {
    // Track initial page view
    pageView('DEDAN Mine - World-Class Mineral Trading Platform');
    
    // Set anonymous user ID for tracking
    const userId = localStorage.getItem('user_id') || `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('user_id', userId);
    setUser(userId, {
      first_visit: new Date().toISOString(),
      user_agent: navigator.userAgent,
    });
    
    // Track app initialization
    userAction('app_initialized', {
      timestamp: new Date().toISOString(),
      user_agent: navigator.userAgent,
      screen_resolution: `${window.screen.width}x${window.screen.height}`,
    });
  }, [pageView, setUser, userAction]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            {/* Main dashboard */}
            <Route
              path="/"
              element={
                <RouteErrorBoundary>
                  <SpatialLiquidGlassUI />
                </RouteErrorBoundary>
              }
            />
            
            {/* Universal checkout */}
            <Route
              path="/checkout"
              element={
                <RouteErrorBoundary>
                  <UniversalCheckoutUI />
                </RouteErrorBoundary>
              }
            />
            
            {/* Agentic dashboard */}
            <Route
              path="/dashboard"
              element={
                <RouteErrorBoundary>
                  <AgenticDashboard />
                </RouteErrorBoundary>
              }
            />
            
            {/* Global Swarm Dashboard */}
            <Route
              path="/swarm"
              element={
                <RouteErrorBoundary>
                  <GlobalSwarmDashboard />
                </RouteErrorBoundary>
              }
            />
            
            {/* Mobile thumb zone */}
            <Route
              path="/mobile"
              element={
                <RouteErrorBoundary>
                  <MobileThumbZone />
                </RouteErrorBoundary>
              }
            />
            
            {/* Catch all routes - redirect to main dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
