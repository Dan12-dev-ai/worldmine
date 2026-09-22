/**
 * World Mine — top-level error boundary.
 * Replaces the inline class in the legacy entry (index.js) with a typed,
 * design-system-styled component. Preserves analytics exception tracking.
 */
import React from 'react';

interface Props { children: React.ReactNode }
interface State { hasError: boolean; message: string | null }

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
  }
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, message: null };
  }

  static getDerivedStateFromError(error: unknown): State {
    return { hasError: true, message: error instanceof Error ? error.message : String(error) };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // PRESERVED: legacy analytics exception event
    window.gtag?.('event', 'exception', { description: error.toString(), fatal: false });
    console.error('Application Error:', error, errorInfo);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div style={{
        minHeight: '60vh', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', gap: 16,
        padding: 'var(--space-7) var(--gutter)', textAlign: 'center',
      }} role="alert">
        <h1 style={{ fontSize: 'var(--text-h2)', margin: 0 }}>Something went wrong</h1>
        <p style={{ color: 'var(--wm-fog)', maxWidth: '48ch', margin: 0 }}>
          We're sorry, but something went wrong. Please refresh the page and try again.
        </p>
        {this.state.message && (
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-caption)', color: 'var(--wm-ash)', margin: 0 }}>
            {this.state.message}
          </p>
        )}
        <button type="button" className="wm-btn wm-btn-primary" onClick={() => window.location.reload()}>
          Refresh Page
        </button>
      </div>
    );
  }
}
