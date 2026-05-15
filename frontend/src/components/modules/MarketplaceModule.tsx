/**
 * 🏪 MARKETPLACE MODULE (PHYSICAL COMMODITIES)
 * Mineral Listings, Verified Sellers, Buyer Requests, Escrow Transactions
 */

import React from 'react'
import { ShoppingCart, Users, FileText, ShieldCheck, Search, Filter } from 'lucide-react'

export const MarketplaceModule: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">Marketplace (Physical)</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Verified physical mineral listings with escrow protection</p>
        </div>
        <div className="flex items-center space-x-3">
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

      {/* MARKETPLACE STATS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <ShoppingCart className="w-5 h-5 text-[var(--accent-cyan)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">847</p>
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

      {/* LISTINGS PLACEHOLDER */}
      <div className="glass p-8 rounded-xl border border-[var(--border-subtle)]">
        <div className="h-96 flex items-center justify-center border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
          <div className="text-center">
            <ShoppingCart className="w-12 h-12 text-[var(--text-tertiary)] mx-auto mb-3" />
            <p className="text-sm text-[var(--text-secondary)]">Mineral listings will appear here</p>
            <p className="text-xs text-[var(--text-tertiary)] mt-1">Integrating existing MarketplaceInterface</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MarketplaceModule
