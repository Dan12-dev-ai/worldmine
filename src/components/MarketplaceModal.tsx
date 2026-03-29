import React, { useState } from 'react'
import { X, TrendingUp, MapPin, Star, Box } from 'lucide-react'
import { commodities, listings } from '../data/commodities'
import { Button } from './ui/button'
import { useMarketplaceStore } from '../store/marketplaceStore'
import ListingCard from './ListingCard'

const MarketplaceModal: React.FC = () => {
  const { selectedCommodity, setIsMarketplaceModalOpen } = useMarketplaceStore()
  const [isARLoading, setIsARLoading] = useState(false)

  const commodity = commodities.find(c => c.id === selectedCommodity)
  const filteredListings = listings.filter(l => l.commodity === selectedCommodity)

  const handleClose = () => {
    setIsMarketplaceModalOpen(false)
  }

  if (!commodity) return null

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="glass-morphism border border-glass-white/20 rounded-2xl p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <img
              src={commodity.image}
              alt={commodity.name}
              className="w-16 h-16 rounded-xl object-cover"
            />
            <div>
              <h2 className="text-3xl font-bold text-white font-orbitron">
                {commodity.name} Marketplace
              </h2>
              <div className="flex items-center space-x-3 mt-1">
                <p className="text-gray-300 text-sm">{commodity.description}</p>
                <div className="h-4 w-px bg-white/20"></div>
                <button 
                  onClick={() => {
                    setIsARLoading(true);
                    setTimeout(() => setIsARLoading(false), 2000);
                  }}
                  className="flex items-center space-x-1.5 text-neon-cyan hover:text-white transition-colors group"
                >
                  <Box className={`w-4 h-4 ${isARLoading ? 'animate-spin' : 'group-hover:scale-110'}`} />
                  <span className="text-[10px] font-black uppercase tracking-widest">
                    {isARLoading ? 'Loading AR...' : 'AR Material Preview'}
                  </span>
                </button>
              </div>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Market Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="glass-morphism border border-glass-white/20 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Current Price</span>
              <TrendingUp className="w-4 h-4 text-neon-emerald" />
            </div>
            <div className="text-2xl font-bold text-white">
              ${commodity.price.toLocaleString()}
            </div>
            <div className={`text-sm ${commodity.change >= 0 ? 'text-neon-emerald' : 'text-red-500'}`}>
              {commodity.change >= 0 ? '+' : ''}{commodity.change}%
            </div>
          </div>

          <div className="glass-morphism border border-glass-white/20 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">24h Volume</span>
              <div className="w-4 h-4 bg-neon-cyan rounded-full animate-pulse"></div>
            </div>
            <div className="text-2xl font-bold text-white">
              {(Math.random() * 10000 + 5000).toFixed(0)}
            </div>
            <div className="text-sm text-gray-400">tons</div>
          </div>

          <div className="glass-morphism border border-glass-white/20 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Active Sellers</span>
              <Star className="w-4 h-4 text-neon-gold" />
            </div>
            <div className="text-2xl font-bold text-white">
              {Math.floor(Math.random() * 50 + 20)}
            </div>
            <div className="text-sm text-gray-400">verified</div>
          </div>

          <div className="glass-morphism border border-glass-white/20 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Avg. Delivery</span>
              <MapPin className="w-4 h-4 text-neon-cyan" />
            </div>
            <div className="text-2xl font-bold text-white">
              {Math.floor(Math.random() * 14 + 7)}
            </div>
            <div className="text-sm text-gray-400">days</div>
          </div>
        </div>

        {/* Listings */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white">
              Available Listings ({filteredListings.length})
            </h3>
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm">Price: Low to High</Button>
              <Button variant="ghost" size="sm">Verified Only</Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredListings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>

          {filteredListings.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                No listings available for {commodity.name} at the moment.
              </div>
              <Button variant="cyber">
                Set Up Price Alert
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MarketplaceModal
