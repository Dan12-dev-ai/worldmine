/**
 * DEDAN Mine - Web Vitals Reporting
 *
 * Collects Core Web Vitals (CLS, FID, FCP, LCP, TTFB) and forwards them to the
 * onPerfEntry callback. Uses the native PerformanceObserver API so it adds no
 * runtime dependency; metrics unsupported by the browser are silently skipped.
 */

const reportWebVitals = (onPerfEntry) => {
  if (typeof onPerfEntry !== 'function') {
    return;
  }

  const report = (metric) => {
    try {
      onPerfEntry(metric);
    } catch (error) {
      // Never let vitals reporting break the app
      console.warn('Web vitals callback failed', error);
    }
  };

  // Time to First Byte
  const navEntry = performance.getEntriesByType?.('navigation')?.[0];
  if (navEntry) {
    report({ name: 'TTFB', value: navEntry.responseStart, delta: navEntry.responseStart });
  }

  // First Contentful Paint / Largest Contentful Paint
  if (typeof PerformanceObserver !== 'undefined') {
    try {
      const paintObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const name = entry.name === 'first-contentful-paint' ? 'FCP' : entry.name;
          report({ name, value: entry.startTime, delta: entry.startTime });
        }
      });
      paintObserver.observe({ type: 'paint', buffered: true });

      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const last = entries[entries.length - 1];
        if (last) {
          report({ name: 'LCP', value: last.startTime, delta: last.startTime });
        }
      });
      lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

      // Cumulative Layout Shift
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        }
        report({ name: 'CLS', value: clsValue, delta: clsValue });
      });
      clsObserver.observe({ type: 'layout-shift', buffered: true });
    } catch (error) {
      // PerformanceObserver entry types are not universally supported
      console.warn('Web vitals observers unavailable', error);
    }
  }
};

export default reportWebVitals;
