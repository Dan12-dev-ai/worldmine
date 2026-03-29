import React from 'react'
import { Home, Store, TrendingUp, Wallet } from 'lucide-react'
import { Button } from './ui/button'
import { useMarketplaceStore } from '../store/marketplaceStore'

const MobileBottomNav: React.FC = () => {
  const { activeTab, setActiveTab } = useMarketplaceStore()
  
  const navItems = [
    { icon: Home, label: 'Home' },
    { icon: Store, label: 'Marketplace' },
    { icon: TrendingUp, label: 'Sell Materials' },
    { icon: Wallet, label: 'Wallet' }
  ]

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 glass-morphism border-t border-glass-white/20 z-40">
      <div className="flex items-center justify-around py-2">
        {navItems.map((item, index) => (
          <Button
            key={index}
            variant="ghost"
            size="sm"
            className={`flex flex-col items-center space-y-1 h-auto py-2 px-3 ${
              activeTab === item.label ? 'text-neon-cyan' : 'text-gray-400'
            }`}
            onClick={() => setActiveTab(item.label)}
          >
            <item.icon className="w-5 h-5" />
            <span className="text-xs">{item.label}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}

export default MobileBottomNav
