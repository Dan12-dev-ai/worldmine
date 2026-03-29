import React from 'react'
import { Commodity } from '../data/commodities'

interface CommodityCardProps {
  commodity: Commodity
  onClick: () => void
}

const CommodityCard: React.FC<CommodityCardProps> = React.memo(({ commodity, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="relative h-16 w-full rounded-xl overflow-hidden cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-neon-cyan/20 group border border-glass-white/20"
    >
      {/* Background Image */}
      <img
        src={commodity.image}
        alt={commodity.name}
        className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 brightness-[0.4] group-hover:brightness-[0.6]"
      />
      
      {/* Content Overlay */}
      <div className="absolute inset-0 flex items-center px-6">
        <h3 className="text-xl font-bold text-white font-orbitron tracking-wide drop-shadow-md group-hover:text-neon-cyan transition-colors">
          {commodity.name}
        </h3>
      </div>

      {/* Hover Border Effect */}
      <div className="absolute inset-0 border-2 border-transparent group-hover:border-neon-cyan/30 rounded-xl transition-colors duration-300" />
    </div>
  )
})

export default CommodityCard
