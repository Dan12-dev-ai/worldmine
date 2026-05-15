/**
 * 🌍 ENTERPRISE COMMAND CENTER (GLOBAL DASHBOARD V3.0)
 * Multi-panel high-density operational workspace
 * Modular widget system with drag-and-drop
 */

import React, { useState, useRef, useEffect } from 'react'
import { 
  LayoutDashboard, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertTriangle, 
  Zap, 
  DollarSign,
  Globe,
  ShieldCheck,
  Clock,
  Maximize2,
  Pin,
  Settings
} from 'lucide-react'

// Widget registry
const WIDGETS = [
  { id: 'portfolio', name: 'Portfolio Value', icon: DollarSign, size: 'large' },
  { id: 'market-status', name: 'Market Status', icon: Activity, size: 'medium' },
  { id: 'alerts', name: 'Active Alerts', icon: AlertTriangle, size: 'medium' },
  { id: 'ai-health', name: 'AI System Health', icon: Zap, size: 'medium' },
  { id: 'latency', name: 'System Latency', icon: Clock, size: 'small' },
  { id: 'throughput', name: 'Transaction Throughput', icon: TrendingUp, size: 'medium' },
  { id: 'global-map', name: 'Global Market Map', icon: Globe, size: 'large' },
  { id: 'risk-score', name: 'Portfolio Risk Score', icon: ShieldCheck, size: 'medium' }
]

// Widget sizes
const WIDGET_SIZES = {
  small: 'col-span-1 row-span-1',
  medium: 'col-span-2 row-span-1',
  large: 'col-span-2 row-span-2'
}

// Modular Widget Component
interface WidgetProps {
  widget: any
  isPinned?: boolean
  onRemove?: () => void
  onPin?: () => void
}

const DashboardWidget: React.FC<WidgetProps> = ({ 
  widget, 
  isPinned = false, 
  onRemove, 
  onPin 
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const Icon = widget.icon

  const renderWidgetContent = () => {
    switch (widget.id) {
      case 'portfolio':
        return (
          <div className="space-y-4">
            <p className="text-4xl font-bold text-[var(--text-primary)] font-display">$2.84M</p>
            <p className="text-sm text-[var(--trust-success)] flex items-center">
              <TrendingUp className="w-4 h-4 mr-1.5" /> +4.2% Today
            </p>
            <div className="h-24 bg-gradient-to-r from-[var(--accent-cyan-soft)] to-[var(--accent-gold-soft)] rounded-lg border border-[var(--border-subtle)]" />
          </div>
        )
      case 'market-status':
        return (
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-[var(--trust-success)] rounded-full animate-pulse-glow"></div>
              <span className="text-sm font-semibold text-[var(--trust-success)]">MARKET OPEN</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[var(--text-tertiary)]">Copper</span>
                <span className="text-[var(--trust-success)]">+2.1%</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-[var(--text-tertiary)]">Gold</span>
                <span className="text-[var(--trust-danger)]">-0.8%</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-[var(--text-tertiary)]">Lithium</span>
                <span className="text-[var(--trust-success)]">+5.4%</span>
              </div>
            </div>
          </div>
        )
      case 'alerts':
        return (
          <div className="space-y-3">
            <p className="text-3xl font-bold text-[var(--text-primary)] font-display">3</p>
            <div className="space-y-2">
              <div className="flex items-center space-x-2 p-2 bg-[var(--trust-warning-soft)] rounded-lg border border-[var(--trust-warning)]/20">
                <AlertTriangle className="w-3.5 h-3.5 text-[var(--trust-warning)]" />
                <span className="text-xs text-[var(--trust-warning)]">Supply chain risk</span>
              </div>
              <div className="flex items-center space-x-2 p-2 bg-[var(--trust-danger-soft)] rounded-lg border border-[var(--trust-danger)]/20">
                <ShieldCheck className="w-3.5 h-3.5 text-[var(--trust-danger)]" />
                <span className="text-xs text-[var(--trust-danger)]">Verification needed</span>
              </div>
            </div>
          </div>
        )
      case 'ai-health':
        return (
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-[var(--trust-success)]" />
              <span className="text-sm font-semibold text-[var(--trust-success)]">AI LIVE</span>
            </div>
            <p className="text-xs text-[var(--text-tertiary)]">5 agents active</p>
            <div className="grid grid-cols-5 gap-1 mt-2">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="w-full aspect-square bg-[var(--trust-success-soft)] rounded border border-[var(--trust-success)]/30" />
              ))}
            </div>
          </div>
        )
      case 'latency':
        return (
          <div className="flex items-center justify-between">
            <span className="text-xs text-[var(--text-tertiary)]">Latency</span>
            <span className="text-lg font-bold font-mono text-[var(--trust-success)]">45ms</span>
          </div>
        )
      case 'throughput':
        return (
          <div className="space-y-2">
            <p className="text-2xl font-bold font-mono text-[var(--text-primary)]">1,247 TPS</p>
            <p className="text-xs text-[var(--text-tertiary)]">Transaction throughput</p>
          </div>
        )
      case 'risk-score':
        return (
          <div className="space-y-3">
            <p className="text-3xl font-bold text-[var(--accent-gold)] font-display">82</p>
            <p className="text-xs text-[var(--text-tertiary)]">Portfolio Risk Score</p>
            <div className="w-full h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-[var(--trust-success)] to-[var(--accent-gold)]" style={{ width: '82%' }}></div>
            </div>
          </div>
        )
      default:
        return (
          <div className="h-full flex items-center justify-center">
            <p className="text-sm text-[var(--text-tertiary)]">Widget: {widget.name}</p>
          </div>
        )
    }
  }

  return (
    <div 
      className={`
        glass p-4 rounded-xl border border-[var(--border-subtle)]
        transition-all duration-200
        ${isHovered ? 'border-[var(--accent-cyan)]/40 shadow-lg shadow-[var(--accent-cyan)]/10' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Widget Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Icon className={`w-4 h-4 ${widget.id === 'alerts' ? 'text-[var(--trust-warning)]' : widget.id === 'portfolio' ? 'text-[var(--accent-gold)]' : 'text-[var(--accent-cyan)]'}`} />
          <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider">
            {widget.name}
          </h3>
        </div>
        
        {/* Widget Controls */}
        {isHovered && (
          <div className="flex items-center space-x-1">
            {onPin && (
              <button 
                onClick={onPin}
                className={`p-1 rounded hover:bg-[var(--bg-tertiary)] ${isPinned ? 'text-[var(--accent-gold)]' : 'text-[var(--text-tertiary)]'}`}
              >
                <Pin className="w-3.5 h-3.5" />
              </button>
            )}
            <button className="p-1 rounded hover:bg-[var(--bg-tertiary)] text-[var(--text-tertiary)]">
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
            {onRemove && (
              <button 
                onClick={onRemove}
                className="p-1 rounded hover:bg-[var(--trust-danger-soft)] text-[var(--text-tertiary)] hover:text-[var(--trust-danger)]"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Widget Content */}
      <div className="h-[calc(100%-2.5rem)]">
        {renderWidgetContent()}
      </div>
    </div>
  )
}

export const EnterpriseCommandCenter: React.FC = () => {
  const [activeWidgets, setActiveWidgets] = useState<string[]>(['portfolio', 'market-status', 'alerts', 'ai-health', 'throughput', 'risk-score'])
  const [pinnedWidgets, setPinnedWidgets] = useState<string[]>(['portfolio'])
  const [showAddWidget, setShowAddWidget] = useState(false)

  const getWidgetById = (id: string) => WIDGETS.find(w => w.id === id)

  const toggleWidget = (widgetId: string) => {
    if (activeWidgets.includes(widgetId)) {
      setActiveWidgets(activeWidgets.filter(id => id !== widgetId))
    } else {
      setActiveWidgets([...activeWidgets, widgetId])
    }
  }

  const togglePin = (widgetId: string) => {
    if (pinnedWidgets.includes(widgetId)) {
      setPinnedWidgets(pinnedWidgets.filter(id => id !== widgetId))
    } else {
      setPinnedWidgets([...pinnedWidgets, widgetId])
    }
  }

  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">Enterprise Command Center</h1>
          <p className="text-sm text-[var(--text-tertiary)]">High-density operational workspace - drag, resize, pin widgets</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => setShowAddWidget(!showAddWidget)}
            className="flex items-center space-x-2 px-4 py-2 bg-[var(--accent-cyan)] text-white rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity"
          >
            <Settings className="w-4 h-4" />
            <span>Add Widget</span>
          </button>
        </div>
      </div>

      {/* WIDGET SELECTOR */}
      {showAddWidget && (
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Available Widgets</h3>
          <div className="flex flex-wrap gap-2">
            {WIDGETS.map(widget => {
              const Icon = widget.icon
              const isActive = activeWidgets.includes(widget.id)
              
              return (
                <button
                  key={widget.id}
                  onClick={() => toggleWidget(widget.id)}
                  className={`
                    flex items-center space-x-2 px-3 py-2 rounded-lg border text-sm
                    transition-all
                    ${isActive 
                      ? 'bg-[var(--accent-cyan-soft)] border-[var(--accent-cyan)]/40 text-[var(--accent-cyan)]' 
                      : 'bg-[var(--bg-tertiary)] border-[var(--border-subtle)] text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{widget.name}</span>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* DASHBOARD GRID - MODULAR WIDGET SYSTEM */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 auto-rows-[200px]">
        {activeWidgets.map(widgetId => {
          const widget = getWidgetById(widgetId)
          if (!widget) return null
          
          return (
            <div 
              key={widget.id} 
              className={`${WIDGET_SIZES[widget.size as keyof typeof WIDGET_SIZES]}`}
            >
              <DashboardWidget 
                widget={widget}
                isPinned={pinnedWidgets.includes(widget.id)}
                onPin={() => togglePin(widget.id)}
                onRemove={() => toggleWidget(widget.id)}
              />
            </div>
          )
        })}
      </div>

      {/* REAL-TIME SYSTEM INDICATORS (ALWAYS VISIBLE) */}
      <div className="glass p-3 rounded-xl border border-[var(--border-subtle)] flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-[var(--trust-success)] rounded-full animate-pulse-glow"></div>
            <span className="text-xs text-[var(--text-secondary)]">System: HEALTHY</span>
          </div>
          <div className="flex items-center space-x-2">
            <Zap className="w-3.5 h-3.5 text-[var(--trust-success)]" />
            <span className="text-xs text-[var(--text-secondary)]">AI: LIVE</span>
          </div>
          <div className="flex items-center space-x-2">
            <Activity className="w-3.5 h-3.5 text-[var(--accent-cyan)]" />
            <span className="text-xs text-[var(--text-secondary)]">WebSocket: CONNECTED</span>
          </div>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <Clock className="w-3.5 h-3.5 text-[var(--text-tertiary)]" />
            <span className="text-xs font-mono text-[var(--text-secondary)]">45ms</span>
          </div>
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-3.5 h-3.5 text-[var(--text-tertiary)]" />
            <span className="text-xs font-mono text-[var(--text-secondary)]">1.2K TPS</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EnterpriseCommandCenter
