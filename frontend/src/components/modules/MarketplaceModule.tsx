/**
 * 🏪 MARKETPLACE MODULE (PHYSICAL COMMODITIES)
 * Mineral Listings, Verified Sellers, Buyer Requests, Escrow Transactions
 */

import React, { useState, useEffect } from 'react'
import { ShoppingCart, Users, FileText, ShieldCheck, Search, Filter, Activity } from 'lucide-react'
import { MarketplaceService } from '../../lib/api/marketplace'

interface Listing {
  id: string
  title: string
  mineral_type: string
  quantity: number
  unit_price: number
  currency: string
  seller_id: string
  status: string
}

export const MarketplaceModule: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([])
  const [activeListingsCount, setActiveListingsCount] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch marketplace data from API
  useEffect(() => {
    const fetchMarketplaceData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await MarketplaceService.getListings()
        setListings(response.data.map((apiListing: any) => ({
          id: apiListing.id,
          title: apiListing.title,
          mineral_type: apiListing.mineral_type,
          quantity: apiListing.quantity,
          unit_price: apiListing.unit_price,
          currency: apiListing.currency,
          seller_id: apiListing.seller_id,
          status: apiListing.status
        })))
        setActiveListingsCount(response.data.filter((l: any) => l.status === 'active').length)
      } catch (err) {
        setError('Failed to load marketplace data. Please try again later.')
        console.error('Error fetching marketplace data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchMarketplaceData()
  }, [])
  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">Marketplace (Physical)</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Verified physical mineral listings with escrow protection</p>
        </div>
        <div className="flex items-center space-x-3">
          {loading && <Activity className="w-4 h-4 text-[var(--accent-primary)] animate-spin" />}
          <button className="flex items-center space-x-2 px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]">
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
            <input
              type="text"
              placeholder="Search minerals..."
              className="pl-9 pr-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] placeholder-[var(--text-tertiary)]"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-300 text-red-800 rounded-lg">
          {error}
        </div>
      )}

      {/* MARKETPLACE STATS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <ShoppingCart className="w-5 h-5 text-[var(--accent-cyan)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">{activeListingsCount}</p>
              <p className="text-xs text-[var(--text-tertiary)]">Active Listings</p>
            </div>
          </div>
        </div>
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <Users className="w-5 h-5 text-[var(--accent-gold)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">2,341</p>
              <p className="text-xs text-[var(--text-tertiary)]">Verified Sellers</p>
            </div>
          </div>
        </div>
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <FileText className="w-5 h-5 text-[var(--accent-purple)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">156</p>
              <p className="text-xs text-[var(--text-tertiary)]">Pending Escrow</p>
            </div>
          </div>
        </div>
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <ShieldCheck className="w-5 h-5 text-[var(--trust-success)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">99.2%</p>
              <p className="text-xs text-[var(--text-tertiary)]">Success Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* LISTINGS */}
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Recent Listings</h3>
        
        {loading && listings.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Activity className="w-8 h-8 text-[var(--text-tertiary)] mx-auto mb-2 animate-spin" />
              <p className="text-sm text-[var(--text-secondary)]">Loading listings...</p>
            </div>
          </div>
        ) : listings.length === 0 ? (
          <div className="flex items-center justify-center h-64 border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
            <div className="text-center">
              <ShoppingCart className="w-12 h-12 text-[var(--text-tertiary)] mx-auto mb-3" />
              <p className="text-sm text-[var(--text-secondary)]">No listings found</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {listings.slice(0, 6).map((listing) => (
              <div key={listing.id} className="p-4 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)] hover:border-[var(--accent-primary)] transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <span className="px-2 py-1 text-xs font-medium bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] rounded">
                    {listing.mineral_type}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium ${
                    listing.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {listing.status.toUpperCase()}
                  </span>
                </div>
                <h4 className="font-medium text-[var(--text-primary)] mb-2">{listing.title}</h4>
                <div className="flex items-center justify-between">
                  <p className="text-lg font-bold text-[var(--text-primary)]">
                    ${listing.unit_price.toLocaleString()}/{listing.currency}
                  </p>
                  <p className="text-sm text-[var(--text-tertiary)]">{listing.quantity} units</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MarketplaceModule
