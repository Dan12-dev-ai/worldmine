import React, { useState } from 'react'
import { Search, Bell, MessageCircle, Circle, Mic } from 'lucide-react'
import DedanLogo from './DedanLogo'
import { Button } from './ui/button'
import { useMarketplaceStore } from '../store/marketplaceStore'

const Navbar: React.FC = () => {
  const { activeTab, setActiveTab } = useMarketplaceStore()
  const [lang, setLang] = useState('EN')

  const translations: Record<string, Record<string, string>> = {
    EN: {
      Home: 'Home',
      Marketplace: 'Marketplace',
      'Sell Materials': 'Sell Materials',
      'Buy Materials': 'Buy Materials',
      'My Deals': 'My Deals',
      'AI Agents': 'AI Agents',
      'Dispute Resolution': 'Dispute Resolution',
      'Live Discussions': 'Live Discussions',
      Analytics: 'Analytics',
      Wallet: 'Wallet',
      SearchPlaceholder: 'AI auto-suggest search...'
    },
    FR: {
      Home: 'Accueil',
      Marketplace: 'Marché',
      'Sell Materials': 'Vendre des Matériaux',
      'Buy Materials': 'Acheter des Matériaux',
      'My Deals': 'Mes Affaires',
      'AI Agents': 'Agents IA',
      'Dispute Resolution': 'Résolution de Litiges',
      'Live Discussions': 'Discussions en Direct',
      Analytics: 'Analytique',
      Wallet: 'Portefeuille',
      SearchPlaceholder: 'Recherche suggérée par IA...'
    },
    AR: {
      Home: 'الرئيسية',
      Marketplace: 'السوق',
      'Sell Materials': 'بيع المواد',
      'Buy Materials': 'شراء المواد',
      'My Deals': 'صفقاتي',
      'AI Agents': 'وكلاء الذكاء الاصطناعي',
      'Dispute Resolution': 'حل النزاعات',
      'Live Discussions': 'نقاشات مباشرة',
      Analytics: 'التحليلات',
      Wallet: 'المحفظة',
      SearchPlaceholder: 'بحث مقترح بالذكاء الاصطناعي...'
    }
  }

  const tabs = [
    'Home',
    'Marketplace',
    'Sell Materials',
    'Buy Materials',
    'My Deals',
    'AI Agents',
    'Dispute Resolution',
    'Live Discussions',
    'Analytics',
    'Wallet'
  ]

  return (
    <div className="glass-morphism border-b border-glass-white/20 sticky top-0 z-50">
      <div className="flex items-center justify-between px-4 sm:px-6 py-3">
        {/* Logo */}
        <DedanLogo className="scale-75 sm:scale-90" />

        {/* Search Bar - Hidden on small mobile */}
        <div className="hidden md:flex flex-1 max-w-2xl mx-4 lg:mx-12">
          <div className="relative group w-full">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 group-focus-within:text-neon-cyan transition-colors" />
            <input
              type="text"
              placeholder={translations[lang].SearchPlaceholder}
              className="w-full pl-12 pr-12 py-2 bg-cyber-dark/50 border border-glass-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/20 transition-all"
            />
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
              <Mic className="w-4 h-4 text-gray-500 hover:text-neon-cyan cursor-pointer transition-colors" />
            </div>
          </div>
        </div>

        {/* Navigation Tabs - Desktop Only */}
        <div className="hidden xl:flex items-center space-x-6">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`text-sm font-medium transition-all hover:text-neon-cyan relative whitespace-nowrap ${
                activeTab === tab
                  ? 'text-neon-cyan neon-text'
                  : 'text-gray-400'
              }`}
            >
              {translations[lang][tab] || tab}
              {activeTab === tab && (
                <div className="absolute -bottom-[22px] left-0 right-0 h-0.5 bg-neon-cyan shadow-[0_0_8px_rgba(0,255,255,0.8)]" />
              )}
            </button>
          ))}
        </div>

        {/* Right Icons */}
        <div className="flex items-center space-x-2 sm:space-x-4 ml-4">
          {/* Language Toggle */}
          <div className="hidden lg:flex items-center bg-white/5 border border-white/10 rounded-full p-1 hover:border-neon-cyan/50 transition-colors">
            {['EN', 'FR', 'AR'].map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-2 py-0.5 rounded-full text-[10px] font-bold transition-all ${
                  lang === l 
                    ? 'bg-neon-cyan text-black shadow-[0_0_10px_rgba(0,255,255,0.5)]' 
                    : 'text-gray-500 hover:text-white'
                }`}
              >
                {l}
              </button>
            ))}
          </div>

          <div className="hidden sm:flex items-center space-x-1 mr-2">
            <span className="text-sm font-medium text-white">Live</span>
            <div className="flex items-center space-x-1 bg-neon-emerald/10 border border-neon-emerald/30 rounded-full px-2 py-0.5">
              <Circle className="w-1.5 h-1.5 text-neon-emerald fill-current animate-pulse" />
              <span className="text-[10px] text-neon-emerald font-bold">40%</span>
            </div>
          </div>

          <div className="flex items-center space-x-1 sm:space-x-2">
            <Button variant="ghost" size="icon" className="text-gray-400 hover:text-neon-cyan h-8 w-8 sm:h-9 sm:w-9">
              <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-gray-400 hover:text-neon-cyan h-8 w-8 sm:h-9 sm:w-9 relative">
              <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 w-1.5 h-1.5 sm:w-2 sm:h-2 bg-red-500 rounded-full border border-cyber-dark"></span>
            </Button>
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full overflow-hidden border border-glass-white/20 hover:border-neon-cyan transition-colors cursor-pointer">
              <img 
                src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=faces" 
                alt="Profile" 
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation / Tablet Navigation */}
      <div className="xl:hidden overflow-x-auto scrollbar-hide border-t border-glass-white/10">
        <div className="flex space-x-6 px-6 py-3">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`text-xs sm:text-sm font-medium whitespace-nowrap transition-all hover:text-neon-cyan relative ${
                activeTab === tab
                  ? 'text-neon-cyan neon-text'
                  : 'text-gray-400'
              }`}
            >
              {tab}
              {activeTab === tab && (
                <div className="absolute -bottom-3 left-0 right-0 h-0.5 bg-neon-cyan" />
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Navbar
