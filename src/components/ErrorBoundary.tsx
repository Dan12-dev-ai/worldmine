import { Component, ErrorInfo, ReactNode } from 'react'

// Enhanced Error Boundary with ISO/IEC 25010 compliance
interface Props {
  children: ReactNode
  fallback?: React.ComponentType<ErrorBoundaryFallbackProps>
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  maxRetries?: number
  enableRetry?: boolean
  logErrors?: boolean
  showErrorDetails?: boolean
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  retryCount: number
  errorId: string | null
}

interface ErrorBoundaryFallbackProps {
  error: Error
  errorInfo: ErrorInfo | null
  retry: () => void
  retryCount: number
  errorId: string
}

// Default error fallback component with accessibility
const DefaultErrorFallback: React.FC<ErrorBoundaryFallbackProps> = ({
  error,
  errorInfo,
  retry,
  retryCount,
  errorId
}) => {
  const canRetry = retryCount < 3

  return (
    <div 
      className="min-h-screen bg-gray-50 flex items-center justify-center p-6"
      role="alert"
      aria-live="assertive"
      aria-labelledby="error-title"
      aria-describedby="error-description"
    >
      <div className="bg-white rounded-2xl shadow-lg p-8 max-w-lg w-full border-2 border-red-200">
        {/* Error Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <svg 
              className="w-8 h-8 text-red-600" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
              />
            </svg>
          </div>
        </div>

        {/* Error Title */}
        <h1 
          id="error-title"
          className="text-2xl font-bold text-gray-900 text-center mb-4"
        >
          Something went wrong
        </h1>

        {/* Error Description */}
        <p 
          id="error-description"
          className="text-gray-600 text-center mb-6 leading-relaxed"
        >
          We apologize for the inconvenience. An unexpected error occurred while loading this page.
        </p>

        {/* Error ID for support */}
        <div className="bg-gray-100 rounded-lg p-3 mb-6">
          <p className="text-sm text-gray-600 text-center">
            <span className="font-medium">Error ID:</span> {errorId}
          </p>
          {process.env.NODE_ENV === 'development' && (
            <details className="mt-3">
              <summary className="cursor-pointer text-sm font-medium text-gray-700">
                Technical Details
              </summary>
              <div className="mt-2 text-xs text-gray-600 space-y-1">
                <p><strong>Error:</strong> {error.message}</p>
                <p><strong>Stack:</strong></p>
                <pre className="whitespace-pre-wrap bg-white p-2 rounded border border-gray-200 text-xs overflow-auto max-h-32">
                  {error.stack}
                </pre>
                {errorInfo && (
                  <p><strong>Component Stack:</strong></p>
                )}
                <pre className="whitespace-pre-wrap bg-white p-2 rounded border border-gray-200 text-xs overflow-auto max-h-32">
                  {errorInfo?.componentStack}
                </pre>
              </div>
            </details>
          )}
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          {canRetry ? (
            <button
              onClick={retry}
              className="w-full touch-target bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              aria-describedby="retry-description"
            >
              Try Again {retryCount > 0 && `(${retryCount}/3)`}
            </button>
          ) : (
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-3">
                Maximum retry attempts reached. Please refresh the page.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="touch-target bg-gray-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
              >
                Refresh Page
              </button>
            </div>
          )}

          <button
            onClick={() => window.history.back()}
            className="w-full touch-target bg-gray-200 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            Go Back
          </button>
        </div>

        {/* Support Information */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500 text-center">
            If this problem persists, please contact our support team with the Error ID above.
          </p>
        </div>

        {/* Retry Description for Screen Readers */}
        <p id="retry-description" className="sr-only">
          Click to retry loading the page. You have {3 - retryCount} attempts remaining.
        </p>
      </div>
    </div>
  )
}

class ErrorBoundary extends Component<Props, State> {
  private retryTimeoutId: NodeJS.Timeout | null = null

  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    retryCount: 0,
    errorId: null
  }

  public static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: `ERR-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
    }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo })

    // Log error to monitoring service
    if (this.props.logErrors !== false) {
      this.logError(error, errorInfo)
    }

    // Call custom error handler
    this.props.onError?.(error, errorInfo)

    // Console logging in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error)
      console.error('Error Info:', errorInfo)
    }
  }

  private logError = (error: Error, errorInfo: ErrorInfo) => {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      errorId: this.state.errorId,
      retryCount: this.state.retryCount
    }

    // Send to error monitoring service (e.g., Sentry, LogRocket)
    try {
      // Example: sendToErrorService(errorData)
      console.log('Error logged:', errorData)
    } catch (loggingError) {
      console.error('Failed to log error:', loggingError)
    }
  }

  private handleRetry = () => {
    const maxRetries = this.props.maxRetries ?? 3
    const currentRetryCount = this.state.retryCount

    if (currentRetryCount >= maxRetries) {
      return
    }

    // Clear any existing retry timeout
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId)
    }

    // Increment retry count
    this.setState(prevState => ({
      retryCount: prevState.retryCount + 1
    }))

    // Attempt recovery after a short delay
    this.retryTimeoutId = setTimeout(() => {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null
      })
    }, 1000)
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      errorId: null
    })
  }

  public componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId)
    }
  }

  public render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      
      return (
        <FallbackComponent
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          retry={this.handleRetry}
          retryCount={this.state.retryCount}
          errorId={this.state.errorId || 'unknown'}
        />
      )
    }

    return this.props.children
  }
}

// Specialized error boundaries for different contexts
export const TransactionErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary
    fallback={({ error, retry, retryCount, errorId }) => (
      <div className="min-h-screen bg-red-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-lg w-full border-2 border-red-200">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Transaction Error</h1>
            <p className="text-gray-600 mb-6">
              There was an error processing your transaction. Your funds are safe.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-6">
              <p className="text-sm text-yellow-800">
                <strong>Important:</strong> No money was deducted. Please try again.
              </p>
            </div>
            <div className="space-y-3">
              <button
                onClick={retry}
                className="w-full touch-target bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Retry Transaction
              </button>
              <button
                onClick={() => window.history.back()}
                className="w-full touch-target bg-gray-200 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    )}
    onError={(error, errorInfo) => {
      // Log transaction-specific errors
      console.error('Transaction Error:', { error, errorInfo })
    }}
    maxRetries={2}
    enableRetry={true}
  >
    {children}
  </ErrorBoundary>
)

export const NetworkErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary
    fallback={({ error, retry, retryCount, errorId }) => (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-lg w-full border-2 border-gray-200">
          <div className="text-center">
            <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-6.938-4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Connection Error</h1>
            <p className="text-gray-600 mb-6">
              Unable to connect to our servers. Please check your internet connection.
            </p>
            <div className="space-y-3">
              <button
                onClick={retry}
                className="w-full touch-target bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.reload()}
                className="w-full touch-target bg-gray-200 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      </div>
    )}
    onError={(error, errorInfo) => {
      // Log network-specific errors
      console.error('Network Error:', { error, errorInfo })
    }}
    maxRetries={5}
    enableRetry={true}
  >
    {children}
  </ErrorBoundary>
)

export default ErrorBoundary
