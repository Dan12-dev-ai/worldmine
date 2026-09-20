/**
 * 💹 DIGITAL TRADING HUB MODULE
 * Order Book, Price Charts, Liquidity View, Trade Execution
 */

import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, BarChart3, Activity } from 'lucide-react'
import { TradingService } from '../../lib/api/trading'

export const TradingHubModule: React.FC = () => {
  const [selectedMineral, setSelectedMineral] = useState<string>('copper')
  const [currentPrice, setCurrentPrice] = useState<number>(0)
  const [priceChange, setPriceChange] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch trading data from API
  useEffect(() => {
    const fetchTradingData = async () => {
      setLoading(true)
      setError(null)
      try {
        const priceResponse = await TradingService.getCurrentPrice(selectedMineral)
        setCurrentPrice(priceResponse.data.price)
        setPriceChange(priceResponse.data.change)
      } catch (err) {
        setError('Failed to load trading data. Please try again later.')
        console.error('Error fetching trading data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchTradingData()

    // Refresh data every 5 seconds
    const interval = setInterval(fetchTradingData, 5000)
    return () => clearInterval(interval)
  }, [selectedMineral])
  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">Digital Trading Hub</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Real-time commodity derivatives and spot trading</p>
        </div>
        <div className="flex items-center space-x-3">
          {loading && <Activity className="w-4 h-4 text-[var(--accent-primary)] animate-spin" />}
          <div className="px-3 py-1.5 bg-[var(--trust-success-soft)] rounded-lg border border-[var(--trust-success)]/30">
            <span className="text-xs font-semibold text-[var(--trust-success)]">ORDER BOOK LIVE</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-300 text-red-800 rounded-lg">
          {error}
        </div>
      )}

      {/* PRICE DISPLAY */}
      <div className="glass p-5 rounded-xl border border-[var(--border-subtle)]">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-[var(--text-tertiary)] uppercase tracking-wider">Current Price</p>
            <p className="text-3xl font-bold text-[var(--text-primary)] font-display">
              ${currentPrice.toLocaleString()}
            </p>
          </div>
          <div className={`flex items-center ${priceChange >= 0 ? 'text-[var(--trust-success)]' : 'text-[var(--trust-danger)]'}`}>
            {priceChange >= 0 ? <TrendingUp className="w-5 h-5 mr-2" /> : <TrendingDown className="w-5 h-5 mr-2" />}
            <span className="text-lg font-semibold">{priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%</span>
          </div>
        </div>
      </div>

      {/* TRADING INTERFACE */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* PRICE CHART */}
        <div className="lg:col-span-2 glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Price Chart</h3>
          <div className="h-80 flex items-center justify-center border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-[var(--text-tertiary)] mx-auto mb-3" />
              <p className="text-sm text-[var(--text-secondary)]">Trading charts will appear here</p>
            </div>
          </div>
        </div>

        {/* ORDER BOOK */}
        <div className="glass p-5 rounded-xl border border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Order Book</h3>
          <div className="h-80 flex items-center justify-center border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
            <div className="text-center">
              <Activity className="w-12 h-12 text-[var(--text-tertiary)] mx-auto mb-3" />
              <p className="text-sm text-[var(--text-secondary)]">Order book interface</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TradingHubModule
