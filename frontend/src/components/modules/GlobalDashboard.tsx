/**
 * 🏠 GLOBAL DASHBOARD MODULE
 * Market Overview, Portfolio Exposure, Risk Alerts, Global Activity Feed
 */

import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertTriangle, Zap } from 'lucide-react'
import { WalletService } from '../../lib/api/wallet'
import { TradingService } from '../../lib/api/trading'

export const GlobalDashboard: React.FC = () => {
  const [portfolioValue, setPortfolioValue] = useState<number>(0)
  const [activeAlerts, setActiveAlerts] = useState<number>(0)
  const [todayVolume, setTodayVolume] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch dashboard data from API
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true)
      setError(null)
      try {
        // Fetch wallet data for portfolio value
        const walletsResponse = await WalletService.getWallets()
        const totalBalance = walletsResponse.data.reduce((sum, wallet) => sum + wallet.balance, 0)
        setPortfolioValue(totalBalance)

        // Fetch trading data for volume
        const priceResponse = await TradingService.getCurrentPrice('copper')
        // Use price as a proxy for volume for now
        setTodayVolume(priceResponse.data.price / 1000000)

      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.')
        console.error('Error fetching dashboard data:', err)
        // Set fallback values
        setPortfolioValue(2847500)
        setActiveAlerts(3)
        setTodayVolume(12.8)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()

    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">Global Dashboard</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Real-time market intelligence and portfolio overview</p>
        </div>
        <div className="flex items-center space-x-2">
          {loading && <Activity className="w-4 h-4 text-[var(--accent-primary)] animate-spin" />}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-300 text-red-800 rounded-lg">
          {error}
        </div>
      )}

      {/* TOP METRICS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* PORTFOLIO VALUE */}
        <div className="glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">Portfolio Value</span>
            <DollarSign className="w-4 h-4 text-[var(--accent-gold)]" />
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] font-display">
            ${portfolioValue.toLocaleString()}
          </p>
          <p className="text-xs text-[var(--trust-success)] mt-2 flex items-center">
            <TrendingUp className="w-3.5 h-3.5 mr-1" /> +4.2% Today
          </p>
        </div>

        {/* ACTIVE ALERTS */}
        <div className="glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">Active Alerts</span>
            <AlertTriangle className="w-4 h-4 text-[var(--trust-warning)]" />
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] font-display">{activeAlerts}</p>
          <p className="text-xs text-[var(--text-tertiary)] mt-2">Requires attention</p>
        </div>

        {/* TODAY'S VOLUME */}
        <div className="glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">Today's Volume</span>
            <Activity className="w-4 h-4 text-[var(--accent-cyan)]" />
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] font-display">{todayVolume}M</p>
          <p className="text-xs text-[var(--trust-success)] mt-2 flex items-center">
            <TrendingUp className="w-3.5 h-3.5 mr-1" /> +18.5% vs yesterday
          </p>
        </div>

        {/* AI SYSTEM HEALTH */}
        <div className="glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">AI System</span>
            <Zap className="w-4 h-4 text-[var(--trust-success)]" />
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] font-display">LIVE</p>
          <p className="text-xs text-[var(--trust-success)] mt-2">12 agents active</p>
        </div>
      </div>

      {/* MAIN CONTENT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* MARKET OVERVIEW */}
        <div className="lg:col-span-2 glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Market Overview</h3>
          <div className="h-64 flex items-center justify-center border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
            <p className="text-sm text-[var(--text-tertiary)]">Market charts will appear here</p>
          </div>
        </div>

        {/* GLOBAL ACTIVITY FEED */}
        <div className="glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Global Activity</h3>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-start space-x-3 p-2.5 bg-[var(--bg-tertiary)] rounded-lg">
                <div className="w-2 h-2 rounded-full bg-[var(--accent-cyan)] mt-2 flex-shrink-0"></div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-[var(--text-primary)]">Trade executed</p>
                  <p className="text-[10px] text-[var(--text-tertiary)]">Copper • 2 hours ago</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GlobalDashboard
