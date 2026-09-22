/**
 * World Mine — application entry (TS successor to legacy index.js).
 * Preserves: root mount, index.css, error boundary, analytics provider,
 * web-vitals reporting. Adds: i18n init (via App import), design tokens.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './design-system/tokens.css';
import './design-system/shell.css';
import App from './app/App';
import reportWebVitals from './reportWebVitals';
import AnalyticsProvider from './components/AnalyticsProvider';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AnalyticsProvider>
      <App />
    </AnalyticsProvider>
  </React.StrictMode>,
);

reportWebVitals();
