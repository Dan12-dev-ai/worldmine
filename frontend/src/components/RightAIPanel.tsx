/**
 * 🔷 RIGHT AI PANEL - CONTEXTUAL INTELLIGENCE ASSISTANT
 * Screen-aware, action-suggesting AI system (not passive chatbot)
 */

import React, { useState } from 'react'
import { 
  X, 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Search, 
  Zap, 
  MessageSquare, 
  FileText, 
  TrendingDown,
  Shield
} from 'lucide-react'

interface RightAIPanelProps {
  activeModule: string
  onClose: () => void
}

const AI_SUGGESTIONS = {
  dashboard: [
    { id: 1, type: 'insight', label: 'Explain market overview', icon: Brain, color: 'text-[var(--accent-cyan)]' },
    { id: 2, type: 'analysis', label: 'Find best trade opportunity', icon: TrendingUp, color: 'text-[var(--trust-success)]' },
    { id: 3, type: 'alert', label: 'Analyze current risk', icon: AlertTriangle, color: 'text-[var(--trust-warning)]' },
    { id: 4, type: 'search', label: 'Show recent news', icon: Search, color: 'text-[var(--text-secondary)]' }
  ],
  marketplace: [
    { id: 1, type: 'analysis', label: 'Compare top 5 sellers', icon: Search, color: 'text-[var(--accent-cyan)]' },
    { id: 2, type: 'insight', label: 'Analyze this listing', icon: FileText, color: 'text-[var(--trust-success)]' },
    { id: 3, type: 'alert', label: 'Check for fraud signals', icon: AlertTriangle, color: 'text-[var(--trust-warning)]' },
    { id: 4, type: 'optimization', label: 'Suggest fair price', icon: TrendingUp, color: 'text-[var(--accent-gold)]' }
  ],
  trading: [
    { id: 1, type: 'insight', label: 'Explain chart pattern', icon: TrendingUp, color: 'text-[var(--accent-cyan)]' },
    { id: 2, type: 'analysis', label: 'Calculate risk/reward', icon: TrendingDown, color: 'text-[var(--trust-warning)]' },
    { id: 3, type: 'optimization', label: 'Optimize entry point', icon: Zap, color: 'text-[var(--accent-gold)]' },
    { id: 4, type: 'alert', label: 'Check liquidity', icon: Search, color: 'text-[var(--text-secondary)]' }
  ],
  logistics: [
    { id: 1, type: 'optimization', label: 'Optimize shipping route', icon: Zap, color: 'text-[var(--accent-cyan)]' },
    { id: 2, type: 'insight', label: 'Track supply chain', icon: Search, color: 'text-[var(--trust-success)]' },
    { id: 3, type: 'alert', label: 'Check for delays', icon: AlertTriangle, color: 'text-[var(--trust-warning)]' },
    { id: 4, type: 'analysis', label: 'Compare carriers', icon: FileText, color: 'text-[var(--text-secondary)]' }
  ],
  default: [
    { id: 1, type: 'insight', label: 'Summarize market today', icon: Brain, color: 'text-[var(--accent-cyan)]' },
    { id: 2, type: 'analysis', label: 'Find opportunities', icon: Search, color: 'text-[var(--trust-success)]' },
    { id: 3, type: 'alert', label: 'Scan for risks', icon: Shield, color: 'text-[var(--trust-warning)]' },
    { id: 4, type: 'optimization', label: 'Optimize portfolio', icon: TrendingUp, color: 'text-[var(--accent-gold)]' }
  ]
}

const AI_QUICK_ACTIONS = [
  { id: 'explain', label: 'Explain This', icon: MessageSquare, color: 'text-[var(--accent-cyan)]' },
  { id: 'risk', label: 'Check Risk', icon: Shield, color: 'text-[var(--trust-warning)]' },
  { id: 'optimize', label: 'Optimize', icon: Zap, color: 'text-[var(--accent-gold)]' }
]

export const RightAIPanel: React.FC<RightAIPanelProps> = ({
  activeModule,
  onClose
}) => {
  const [chatInput, setChatInput] = useState<string>('')
  const [isProcessing, setIsProcessing] = useState<boolean>(false)

  const suggestions = AI_SUGGESTIONS[activeModule as keyof typeof AI_SUGGESTIONS] || AI_SUGGESTIONS.default

  const getModuleTitle = () => {
    const titles: Record<string, string> = {
      dashboard: 'Global Dashboard',
      marketplace: 'Marketplace',
      trading: 'Digital Trading',
      logistics: 'Logistics',
      'ai-intelligence': 'AI Intelligence',
      'mineral-intelligence': 'Mineral News',
      communication: 'Communication',
      contracts: 'Contracts',
      'user-control': 'User Control',
      settings: 'Settings',
      developers: 'Developers',
      help: 'Help'
    }
    return titles[activeModule] || 'Global Platform'
  }

  const handleSuggestionClick = (suggestion: any) => {
    setIsProcessing(true)
    setTimeout(() => {
      setIsProcessing(false)
    }, 1500)
  }

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (chatInput.trim()) {
      setIsProcessing(true)
      setTimeout(() => {
        setIsProcessing(false)
        setChatInput('')
      }, 2000)
    }
  }

  return (
    <aside className="w-80 bg-[var(--bg-secondary)] border-l border-[var(--border-subtle)] flex flex-col h-full">
      {/* PANEL HEADER */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 bg-gradient-to-br from-[var(--accent-purple)] to-[var(--accent-cyan)] rounded-lg flex items-center justify-center">
            <Brain className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-[var(--text-primary)]">AI Assistant</h3>
            <p className="text-[10px] text-[var(--text-tertiary)]">Context-aware for {getModuleTitle()}</p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="p-1.5 rounded-md hover:bg-[var(--bg-tertiary)] text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* AI STATUS INDICATOR */}
      <div className="px-4 py-3 border-b border-[var(--border-subtle)]">
        <div className="flex items-center space-x-2 px-3 py-2 bg-[var(--trust-success-soft)] rounded-lg border border-[var(--trust-success)]/30">
          <div className="w-2 h-2 bg-[var(--trust-success)] rounded-full animate-pulse-glow"></div>
          <span className="text-xs font-semibold text-[var(--trust-success)]">LISTENING & READING SCREEN</span>
        </div>
      </div>

      {/* CONTEXTUAL SUGGESTIONS */}
      <div className="p-4 border-b border-[var(--border-subtle)]">
        <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest mb-3">
          QUICK ACTIONS
        </p>
        <div className="grid grid-cols-3 gap-2 mb-4">
          {AI_QUICK_ACTIONS.map((action) => {
            const Icon = action.icon
            return (
              <button
                key={action.id}
                className="flex flex-col items-center justify-center p-2.5 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border-subtle)] hover:bg-[var(--bg-elevated)] hover:border-[var(--accent-cyan)]/30 transition-all"
              >
                <Icon className={`w-4.5 h-4.5 mb-1 ${action.color}`} />
                <span className="text-[10px] text-[var(--text-secondary)]">{action.label}</span>
              </button>
            )
          })}
        </div>

        <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest mb-3">
          AI SUGGESTIONS FOR {getModuleTitle().toUpperCase()}
        </p>
        <div className="space-y-2">
          {suggestions.map((suggestion) => {
            const Icon = suggestion.icon
            return (
              <button
                key={suggestion.id}
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={isProcessing}
                className="w-full text-left p-3 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border-subtle)] hover:bg-[var(--bg-elevated)] hover:border-[var(--accent-cyan)]/30 transition-all group disabled:opacity-50"
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4.5 h-4.5 flex-shrink-0 ${suggestion.color}`} />
                  <span className="text-sm text-[var(--text-primary)] group-hover:text-[var(--accent-cyan)] transition-colors">
                    {suggestion.label}
                  </span>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* CHAT INTERFACE */}
      <div className="flex-1 flex flex-col p-4">
        <div className="flex-1 overflow-y-auto mb-4">
          <div className="p-3 bg-[var(--bg-elevated)] rounded-lg border border-[var(--border-subtle)]">
            <p className="text-xs text-[var(--text-secondary)]">
              Hi! I'm your AI mining & commodity intelligence assistant. I'm analyzing the current screen and ready to help.
            </p>
          </div>
        </div>

        {/* INPUT */}
        <form onSubmit={handleSendMessage} className="relative">
          <input
            type="text"
            placeholder="Ask anything about {getModuleTitle()}..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            disabled={isProcessing}
            className="w-full pl-4 pr-12 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--accent-cyan)] focus:ring-1 focus:ring-[var(--accent-cyan)] disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!chatInput.trim() || isProcessing}
            className="absolute right-1.5 top-1/2 transform -translate-y-1/2 p-1.5 bg-gradient-to-r from-[var(--accent-cyan)] to-[var(--accent-purple)] rounded-md text-white hover:opacity-90 transition-opacity disabled:opacity-30"
          >
            <Zap className="w-4 h-4" />
          </button>
        </form>
      </div>
    </aside>
  )
}

export default RightAIPanel
