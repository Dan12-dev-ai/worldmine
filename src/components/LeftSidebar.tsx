import React from 'react'
import DedanLogo from './DedanLogo'
import { useMarketplaceStore } from '../store/marketplaceStore'

const LeftSidebar: React.FC = () => {
  const { setSelectedCommodity, setIsMarketplaceModalOpen } = useMarketplaceStore()

  const handleCommodityClick = (commodityId: string) => {
    setSelectedCommodity(commodityId)
    setIsMarketplaceModalOpen(true)
  }

  const customCommodities = [
    { id: 'copper', name: 'Copper', image: 'https://images.unsplash.com/photo-1536619493521-1ba5d2c25532?w=400&h=200&fit=crop' },
    { id: 'aluminium', name: 'Aluminium', image: 'https://images.unsplash.com/photo-1584011018116-f03655337736?w=400&h=200&fit=crop' },
    { id: 'gold', name: 'Gold', image: 'https://images.unsplash.com/photo-1610375461246-83df859d849d?w=400&h=200&fit=crop' },
    { id: 'rare-earths', name: 'Rare Earths', image: 'https://images.unsplash.com/photo-1590487817434-a35d1b7e7b85?w=400&h=200&fit=crop' }
  ]

  return (
    <div className="w-full h-full glass-morphism p-6 xl:p-8 flex flex-col overflow-y-auto scrollbar-hide">
      {/* Large Sidebar Logo Area */}
      <div className="mb-12">
        <DedanLogo className="scale-110 origin-left" />
      </div>

      <div className="space-y-6">
        {customCommodities.map((commodity) => (
          <div
            key={commodity.id}
            onClick={() => handleCommodityClick(commodity.id)}
            className="relative h-24 w-full rounded-2xl overflow-hidden cursor-pointer transition-all duration-500 hover:scale-[1.05] hover:shadow-[0_0_30px_rgba(0,255,255,0.2)] group border border-white/10"
          >
            <img
              src={commodity.image}
              alt={commodity.name}
              className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 brightness-[0.4] group-hover:brightness-[0.6]"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent"></div>
            <div className="absolute inset-0 flex items-center px-8">
              <h3 className="text-2xl font-black text-white font-orbitron tracking-tighter group-hover:text-neon-cyan transition-colors drop-shadow-2xl">
                {commodity.name}
              </h3>
            </div>
            <div className="absolute bottom-0 left-0 w-1 h-full bg-neon-cyan opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default LeftSidebar
