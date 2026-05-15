/**
 * 🔷 TOP STATUS BAR - REAL-TIME CONTROL SYSTEM
 * Global system state, alerts, latency, AI health, active operations
 */

import React, { useState, useEffect } from 'react'
import { 
  Search, 
  Bell, 
  ShieldCheck, 
  Activity, 
  Clock, 
  ChevronDown,
  Command,
  Globe,
  Wifi,
  AlertTriangle,
  Zap
} from 'lucide-react'

interface NavigationModule {
  id: string
  label: string
}

interface TopStatusBarProps {
  activeModule: string
  modules: NavigationModule[]
  searchQuery: string
  setSearchQuery: (query: string) => void
  commandPaletteOpen: boolean
  setCommandPaletteOpen: (open: boolean) => void
}

export const TopStatusBar: React.FC<TopStatusBarProps> = ({
  activeModule,
  modules,
  searchQuery,
  setSearchQuery,
  commandPaletteOpen,
  setCommandPaletteOpen
}) => {
  const [systemLatency, setSystemLatency] = useState<number>(45)
  const [activeAlerts, setActiveAlerts] = useState<number>(2)
  const [marketStatus, setMarketStatus] = useState<'open' | 'volatile' | 'stable'>('stable')
  const [time, setTime] = useState<string>('')

  // Update clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: true 
      }))
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  // Simulate latency updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemLatency(Math.floor(Math.random() * 80) + 20)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  // Get active module label
  const activeModuleLabel = modules.find(m => m.id === activeModule)?.label || 'Global Dashboard'

  // Market status colors
  const getMarketStatusColor = () => {
    switch (marketStatus) {
      case 'volatile': return 'text-[var(--trust-warning)]'
      case 'stable': return 'text-[var(--trust-success)]'
      case 'open': return 'text-[var(--accent-cyan)]'
      default: return 'text-[var(--text-secondary)]'
    }
  }

  const getMarketStatusBg = () => {
    switch (marketStatus) {
      case 'volatile': return 'bg-[var(--trust-warning-soft)]'
      case 'stable': return 'bg-[var(--trust-success-soft)]'
      case 'open': return 'bg-[var(--accent-cyan-soft)]'
      default: return 'bg-[var(--bg-tertiary)]'
    }
  }

  // Latency color
  const getLatencyColor = () => {
    if (systemLatency < 50) return 'text-[var(--trust-success)]'
    if (systemLatency < 100) return 'text-[var(--trust-warning)]'
    return 'text-[var(--trust-danger)]'
  }

  return (
    <header className="h-14 bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)] flex items-center px-4 justify-between z-20">
      {/* LEFT: MODULE & SEARCH */}
      <div className="flex items-center space-x-4">
        {/* MODULE BREADCRUMB */}
        <div className="flex items-center space-x-2">
          <h2 className="text-sm font-bold text-[var(--text-primary)]">{activeModuleLabel}</h2>
          <div className={`w-2 h-2 rounded-full ${getMarketStatusBg()}`}></div>
        </div>

        {/* SEARCH BAR */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
          <input
            type="text"
            placeholder="Search modules, assets, commands..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 pr-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--accent-cyan)] focus:ring-1 focus:ring-[var(--accent-cyan)] w-80"
          />
        </div>

        {/* COMMAND PALETTE BUTTON */}
        <button
          onClick={() => setCommandPaletteOpen(!commandPaletteOpen)}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-[var(--bg-tertiary)] border border-[var(--border-subtle)] rounded-md text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] hover:text-[var(--text-primary)] transition-colors"
        >
          <Command className="w-3.5 h-3.5" />
          <span className="font-mono">⌘K</span>
        </button>
      </div>

      {/* RIGHT: SYSTEM STATUS INDICATORS */}
      <div className="flex items-center space-x-4">
        {/* MARKET STATUS */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-[var(--border-subtle)]">
          <Activity className="w-4 h-4 text-[var(--accent-cyan)]" />
          <span className={`text-xs font-semibold ${getMarketStatusColor()}`}>
            {marketStatus.toUpperCase()}
          </span>
        </div>

        {/* LATENCY */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-[var(--border-subtle)]">
          <Wifi className="w-4 h-4 text-[var(--text-tertiary)]" />
          <span className={`text-xs font-mono font-semibold ${getLatencyColor()}`}>
            {systemLatency}ms
          </span>
        </div>

        {/* ACTIVE ALERTS */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-[var(--border-subtle)]">
          <AlertTriangle className="w-4 h-4 text-[var(--trust-warning)]" />
          <span className="text-xs font-semibold text-[var(--trust-warning)]">
            {activeAlerts}
          </span>
        </div>

        {/* TIME */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-[var(--border-subtle)]">
          <Clock className="w-4 h-4 text-[var(--text-tertiary)]" />
          <span className="text-xs font-mono font-semibold text-[var(--text-secondary)]">
            {time}
          </span>
        </div>

        {/* GLOBAL */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-[var(--border-subtle)]">
          <Globe className="w-4 h-4 text-[var(--accent-purple)]" />
          <span className="text-xs font-semibold text-[var(--text-secondary)]">EN</span>
        </div>

        {/* NOTIFICATIONS */}
        <button className="relative p-2 rounded-lg border border-[var(--border-subtle)] hover:bg-[var(--bg-tertiary)] transition-colors">
          <Bell className="w-4.5 h-4.5 text-[var(--text-secondary)]" />
          {activeAlerts > 0 && (
            <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-[var(--trust-danger)] rounded-full border border-[var(--bg-secondary)]"></div>
          )}
        </button>

        {/* AI HEALTH */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[var(--trust-success-soft)] border border-[var(--trust-success)]/30">
          <Zap className="w-4 h-4 text-[var(--trust-success)]" />
          <span className="text-xs font-semibold text-[var(--trust-success)]">AI LIVE</span>
        </div>
      </div>
    </header>
  )
}

export default TopStatusBar
