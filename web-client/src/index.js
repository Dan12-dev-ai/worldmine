/**
 * DEDAN Mine - Main Application Entry Point (v5.0.0)
 * Production-ready with analytics and error tracking
 * Serverless optimization for zero system distraction
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import AnalyticsProvider from './components/AnalyticsProvider';

// Performance monitoring
const startPerformanceTracking = () => {
  // Track initial load time
  const loadTime = performance.now();
  console.log(`Initial load time: ${loadTime.toFixed(2)}ms`);
  
  // Track Core Web Vitals
  if ('PerformanceObserver' in window) {
    // Track Largest Contentful Paint (LCP)
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lastEntry = entries[entries.length - 1];
      console.log(`LCP: ${Math.round(lastEntry.renderTime || lastEntry.startTime)}ms`);
    }).observe({ entryTypes: ['largest-contentful-paint'] });

    // Track First Input Delay (FID)
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lastEntry = entries[entries.length - 1];
      console.log(`FID: ${Math.round(lastEntry.processingStart - lastEntry.startTime)}ms`);
    }).observe({ entryTypes: ['first-input'] });

    // Track Cumulative Layout Shift (CLS)
    let clsValue = 0;
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      }
      console.log(`CLS: ${(clsValue * 1000).toFixed(2)}`);
    }).observe({ entryTypes: ['layout-shift'] });
  }
};

// Error boundary for production
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    
    // Log error to monitoring service
    console.error('Application Error:', error, errorInfo);
    
    // Track error in analytics
    if (window.gtag) {
      window.gtag('event', 'exception', {
        description: error.toString(),
        fatal: false,
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          fontFamily: 'Arial, sans-serif'
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
              cursor: 'pointer'
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

// Initialize application
const root = ReactDOM.createRoot(document.getElementById('root'));

// Start performance tracking
startPerformanceTracking();

// Render application with analytics and error boundary
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <AnalyticsProvider>
        <App />
      </AnalyticsProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
