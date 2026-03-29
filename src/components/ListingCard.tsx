import React from 'react'
import { MapPin, Star, Video, Box, ShieldCheck, Zap } from 'lucide-react'
import { Button } from './ui/button'
import { Listing } from '../data/commodities'
import { useMarketplaceStore } from '../store/marketplaceStore'

interface ListingCardProps {
  listing: Listing
}

const ListingCard: React.FC<ListingCardProps> = React.memo(({ listing }) => {
  const { setSelectedListing, setIsTransactionModalOpen, setActiveTab } = useMarketplaceStore()

  const handleBuyNow = () => {
    setSelectedListing(listing.id)
    setIsTransactionModalOpen(true)
  }

  const handleStartDiscussion = () => {
    setActiveTab('Negotiation Room')
  }

  return (
    <div className="glass-morphism border border-white/10 rounded-3xl overflow-hidden group hover:border-neon-cyan/50 transition-all duration-500 flex flex-col bg-cyber-dark/40">
      {/* Material Image */}
      <div className="relative h-56 overflow-hidden">
        <img
          src={listing.image}
          alt={listing.title}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-cyber-dark to-transparent opacity-60"></div>
        
        {/* Top Badges */}
        <div className="absolute top-4 left-4 flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <div className="bg-black/60 backdrop-blur-md border border-white/20 rounded-full px-3 py-1 flex items-center space-x-2">
              <div className="w-1.5 h-1.5 bg-neon-emerald rounded-full animate-pulse"></div>
              <span className="text-[10px] text-white font-bold uppercase">Live</span>
            </div>
            <div className="bg-neon-gold/20 backdrop-blur-md border border-neon-gold/50 rounded-full px-3 py-1 flex items-center space-x-1">
              <Star className="w-3 h-3 text-neon-gold fill-current" />
              <span className="text-[10px] text-neon-gold font-bold">PREMIUM</span>
            </div>
          </div>
          <div className="bg-neon-cyan/20 backdrop-blur-md border border-neon-cyan/50 rounded-full px-3 py-1 flex items-center self-start space-x-1">
            <Zap className="w-3 h-3 text-neon-cyan" />
            <span className="text-[10px] text-neon-cyan font-bold uppercase">AI Best Match</span>
          </div>
        </div>

        {/* Sustainability Score */}
        <div className="absolute bottom-4 right-4 bg-neon-emerald/10 backdrop-blur-md border border-neon-emerald/30 rounded-lg px-3 py-1 text-center">
          <div className="text-[8px] text-neon-emerald font-bold uppercase">Sustainability</div>
          <div className="text-sm font-bold text-white">A+ (94)</div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 flex-1 flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-bold text-white mb-1 group-hover:text-neon-cyan transition-colors">{listing.title}</h3>
            <div className="flex items-center text-gray-500 text-xs">
              <MapPin className="w-3 h-3 mr-1" />
              {listing.location}
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-white">${listing.price.toLocaleString()}</div>
            <div className="text-[10px] text-gray-500 font-bold uppercase">Per Metric Ton</div>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-6">
          <span className="px-2 py-1 rounded bg-white/5 border border-white/10 text-[9px] text-gray-400 font-bold uppercase">FOB Terms</span>
          <div className="px-2 py-1 rounded bg-neon-emerald/5 border border-neon-emerald/20 text-[9px] text-neon-emerald font-bold uppercase flex items-center">
            <ShieldCheck className="w-2.5 h-2.5 mr-1" />
            Verified Seller
          </div>
          <span className="px-2 py-1 rounded bg-white/5 border border-white/10 text-[9px] text-gray-400 font-bold uppercase">Ready to Ship</span>
        </div>

        {/* Actions */}
        <div className="space-y-3 mt-auto">
          <div className="grid grid-cols-2 gap-3">
            <Button onClick={handleBuyNow} variant="cyber" className="h-11 font-bold uppercase tracking-widest text-xs">Buy Now</Button>
            <Button variant="ghost" className="h-11 border border-white/10 font-bold uppercase tracking-widest text-xs hover:bg-white/5">Make Offer</Button>
          </div>
          <Button onClick={handleStartDiscussion} variant="ghost" className="w-full h-11 border border-neon-cyan/30 text-neon-cyan font-bold uppercase tracking-widest text-xs hover:bg-neon-cyan/5">
            <Video className="w-4 h-4 mr-2" />
            Live Video Discussion
          </Button>
          <Button variant="ghost" className="w-full h-11 border border-white/10 text-gray-400 font-bold uppercase tracking-widest text-xs hover:text-white">
            <Box className="w-4 h-4 mr-2" />
            AR Material Preview
          </Button>
        </div>
      </div>
    </div>
  )
})

export default ListingCard
