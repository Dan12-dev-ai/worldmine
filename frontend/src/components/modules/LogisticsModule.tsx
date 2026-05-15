/**
 * 🚚 LOGISTICS & SUPPLY CHAIN MODULE
 * Shipment Tracking, Route Optimization, Mine-to-Buyer Flow
 */

import React from 'react'
import { Truck, Map, Navigation, PackageCheck } from 'lucide-react'

export const LogisticsModule: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">Logistics & Supply Chain</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Real-time shipment tracking and route optimization</p>
        </div>
      </div>

      {/* LOGISTICS OVERVIEW */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <Truck className="w-5 h-5 text-[var(--accent-cyan)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">42</p>
              <p className="text-xs text-[var(--text-tertiary)]">Active Shipments</p>
            </div>
          </div>
        </div>
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <Map className="w-5 h-5 text-[var(--accent-gold)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">18</p>
              <p className="text-xs text-[var(--text-tertiary)]">Routes Optimized</p>
            </div>
          </div>
        </div>
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <PackageCheck className="w-5 h-5 text-[var(--trust-success)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">1,247</p>
              <p className="text-xs text-[var(--text-tertiary)]">Deliveries Completed</p>
            </div>
          </div>
        </div>
        <div className="glass p-4 rounded-xl border border-[var(--border-subtle)]">
          <div className="flex items-center space-x-3">
            <Navigation className="w-5 h-5 text-[var(--accent-purple)]" />
            <div>
              <p className="text-2xl font-bold text-[var(--text-primary)] font-display">98.5%</p>
              <p className="text-xs text-[var(--text-tertiary)]">On-Time Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* SHIPMENT TRACKING */}
      <div className="glass p-8 rounded-xl border border-[var(--border-subtle)]">
        <div className="h-96 flex items-center justify-center border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
          <div className="text-center">
            <Map className="w-12 h-12 text-[var(--text-tertiary)] mx-auto mb-3" />
            <p className="text-sm text-[var(--text-secondary)]">Shipment tracking map</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LogisticsModule
