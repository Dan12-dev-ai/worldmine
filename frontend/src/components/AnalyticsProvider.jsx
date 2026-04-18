 /**
 * DEDAN Mine - Analytics Provider (v5.0.0)
 * Google Analytics 4 and Sentry integration for global insights
 * Track 1,000,000+ users and catch frontend crashes instantly
 * Production-ready analytics with privacy compliance
 */

import React, { useEffect, useCallback } from 'react';
import * as Sentry from '@sentry/react';

// Google Analytics 4 configuration
const GA4_MEASUREMENT_ID = process.env.REACT_APP_GA_ID || 'G-XXXXXXXXXX';

// Sentry configuration
const SENTRY_DSN = process.env.REACT_APP_SENTRY_DSN;

// Initialize Sentry if enabled
if (SENTRY_DSN && process.env.REACT_APP_ENABLE_SENTRY === 'true') {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: process.env.REACT_APP_ENV || 'production',
    release: process.env.REACT_APP_VERSION || 'v5.0.0',
    tracesSampleRate: 0.1, // 10% of transactions for performance monitoring
    profilesSampleRate: 0.1, // 10% of profiles for performance monitoring
    integrations: [
      new Sentry.BrowserTracing(),
      new Sentry.Replay({
        maskAllText: false,
        blockAllMedia: false,
      }),
    ],
    beforeSend(event) {
      // Filter out sensitive data
      if (event.exception) {
        const error = event.exception.values?.[0];
        if (error?.value?.includes('password') || 
            error?.value?.includes('token') || 
            error?.value?.includes('secret')) {
          return null; // Don't send sensitive errors
        }
      }
      return event;
    },
  });
}

// Google Analytics 4 tracking functions
const trackPageView = (page, title) => {
  try {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', GA4_MEASUREMENT_ID, {
        page_title: title,
        page_location: page,
      });
    }
  } catch (error) {
    console.warn('GA4 tracking error:', error);
  }
};

const trackEvent = (eventName, parameters = {}) => {
  try {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', eventName, {
        event_category: 'dedan_mine',
        ...parameters,
      });
    }
  } catch (error) {
    console.warn('GA4 event tracking error:', error);
  }
};

const trackUserAction = (action, context = {}) => {
  try {
    // Track in GA4
    trackEvent('user_action', {
      action_type: action,
      ...context,
    });

    // Track in Sentry for performance
    Sentry.addBreadcrumb({
      category: 'user_action',
      message: action,
      level: 'info',
      data: context,
    });
  } catch (error) {
    console.warn('User action tracking error:', error);
  }
};

const trackPerformance = (metricName, value, context = {}) => {
  try {
    // Track in GA4
    trackEvent('performance_metric', {
      metric_name: metricName,
      metric_value: value,
      ...context,
    });

    // Track in Sentry for performance monitoring
    Sentry.addBreadcrumb({
      category: 'performance',
      message: `${metricName}: ${value}ms`,
      level: 'info',
      data: { metricName, value, ...context },
    });
  } catch (error) {
    console.warn('Performance tracking error:', error);
  }
};

const trackError = (error, context = {}) => {
  try {
    // Track in GA4
    trackEvent('error', {
      error_type: error.name || 'unknown',
      error_message: error.message || 'Unknown error',
      ...context,
    });

    // Track in Sentry for error monitoring
    Sentry.captureException(error, {
      tags: context,
      extra: {
        userAgent: navigator.userAgent,
        url: window.location.href,
        timestamp: new Date().toISOString(),
      },
    });
  } catch (e) {
    console.warn('Error tracking failed:', e);
  }
};

const trackUser = (userId, properties = {}) => {
  try {
    // Set user ID in GA4
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', GA4_MEASUREMENT_ID, {
        user_id: userId,
        ...properties,
      });
    }

    // Set user in Sentry
    Sentry.setUser({
      id: userId,
      ...properties,
    });
  } catch (error) {
    console.warn('User tracking error:', error);
  }
};

// Custom hook for analytics
const useAnalytics = () => {
  const pageView = useCallback((title) => {
    const page = window.location.pathname + window.location.search;
    trackPageView(page, title);
  }, []);

  const event = useCallback((eventName, parameters = {}) => {
    trackEvent(eventName, parameters);
  }, []);

  const userAction = useCallback((action, context = {}) => {
    trackUserAction(action, context);
  }, []);

  const performance = useCallback((metricName, value, context = {}) => {
    trackPerformance(metricName, value, context);
  }, []);

  const error = useCallback((error, context = {}) => {
    trackError(error, context);
  }, []);

  const setUser = useCallback((userId, properties = {}) => {
    trackUser(userId, properties);
  }, []);

  return {
    pageView,
    event,
    userAction,
    performance,
    error,
    setUser,
  };
};

// Analytics Provider Component
const AnalyticsProvider = ({ children }) => {
  useEffect(() => {
    // Load Google Analytics 4 script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_MEASUREMENT_ID}`;
    
    document.head.appendChild(script);

    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag() {
      window.dataLayer.push(arguments);
    };
    
    window.gtag('js', new Date());
    window.gtag('config', GA4_MEASUREMENT_ID, {
      send_page_view: false, // We'll handle page views manually
    });

    // Track initial page view
    trackPageView(window.location.pathname + window.location.search, document.title);

    // Cleanup
    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, []);

  // Track page changes
  useEffect(() => {
    const handleRouteChange = () => {
      trackPageView(window.location.pathname + window.location.search, document.title);
    };

    // Listen for route changes (simplified - in production use router events)
    window.addEventListener('popstate', handleRouteChange);
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
    };
  }, []);

  // Track performance metrics
  useEffect(() => {
    // Track Core Web Vitals
    const trackWebVitals = () => {
      try {
        // Track Largest Contentful Paint (LCP)
        new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const lastEntry = entries[entries.length - 1];
          trackPerformance('LCP', Math.round(lastEntry.renderTime || lastEntry.startTime), {
            element: lastEntry.element?.tagName || 'unknown',
            url: lastEntry.url || window.location.href,
          });
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // Track First Input Delay (FID)
        new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const lastEntry = entries[entries.length - 1];
          trackPerformance('FID', Math.round(lastEntry.processingStart - lastEntry.startTime), {
            eventType: lastEntry.name || 'unknown',
          });
        }).observe({ entryTypes: ['first-input'] });

        // Track Cumulative Layout Shift (CLS)
        let clsValue = 0;
        new PerformanceObserver((entryList) => {
          for (const entry of entryList.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          trackPerformance('CLS', Math.round(clsValue * 1000) / 1000, {
            entries: entryList.getEntries().length,
          });
        }).observe({ entryTypes: ['layout-shift'] });
      } catch (error) {
        console.warn('Web Vitals tracking error:', error);
      }
    };

    if ('PerformanceObserver' in window) {
      trackWebVitals();
    }
  }, []);

  // Track errors globally
  useEffect(() => {
    const handleError = (event) => {
      const error = event.error || new Error(event.message);
      trackError(error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: error.stack,
      });
    };

    const handleUnhandledRejection = (event) => {
      const error = new Error(event.reason);
      trackError(error, {
        type: 'unhandled_promise_rejection',
        reason: event.reason,
      });
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return children;
};

// Export analytics functions for direct use
export {
  trackPageView,
  trackEvent,
  trackUserAction,
  trackPerformance,
  trackError,
  trackUser,
};

export default AnalyticsProvider;
