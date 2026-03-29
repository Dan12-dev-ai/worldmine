import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-cyber-dark flex items-center justify-center p-6 text-center">
          <div className="glass-morphism border border-red-500/30 rounded-3xl p-12 max-w-lg">
            <h1 className="text-4xl font-bold text-white font-orbitron mb-4">System Anomaly</h1>
            <p className="text-gray-400 mb-8">The neural link has been disrupted. Please attempt to re-initialize the connection.</p>
            <button
              onClick={() => window.location.reload()}
              className="px-8 py-3 bg-neon-cyan/20 border border-neon-cyan text-neon-cyan rounded-xl font-bold uppercase tracking-widest hover:bg-neon-cyan/30 transition-all"
            >
              Re-Initialize
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
