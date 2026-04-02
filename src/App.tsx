import React, { useEffect, useState } from 'react'
import Navbar from './components/Navbar'
import LeftSidebar from './components/LeftSidebar'
import MainContent from './components/MainContent'
import RightSidebar from './components/RightSidebar'
import BottomWorkflowBar from './components/BottomWorkflowBar'
import MobileBottomNav from './components/MobileBottomNav'
import RegistrationModal from './components/RegistrationModal'
import TransactionModal from './components/TransactionModal'
import MarketplaceModal from './components/MarketplaceModal'
import BackgroundParticles from './components/BackgroundParticles'
import KeepAlive from './components/KeepAlive'
import { useMarketplaceStore } from './store/marketplaceStore'
import { Mic } from 'lucide-react'
import { Button } from './components/ui/button'
import ErrorBoundary from './components/ErrorBoundary'

const App: React.FC = () => {
  const [isListening, setIsListening] = useState(false)
  const {
    isRegistrationModalOpen,
    isTransactionModalOpen,
    isMarketplaceModalOpen,
    loadTransactions
  } = useMarketplaceStore()

  useEffect(() => {
    loadTransactions()
  }, [loadTransactions])

  return (
    <ErrorBoundary>
      {/* KeepAlive Component - Prevents Render from sleeping */}
      <KeepAlive />
      
      <div className="min-h-screen bg-cyber-dark relative overflow-hidden">
        {/* Background Particles */}
        <BackgroundParticles />

        {/* Main Layout */}
        <div className="relative z-10 flex flex-col h-screen">
          {/* Top Navigation */}
          <Navbar />

          {/* Main Content Area */}
          <div className="flex flex-1 overflow-hidden relative">
            {/* Left Sidebar - Hidden on mobile/tablet/small laptop */}
            <div className="hidden lg:block w-64 xl:w-80 border-r border-glass-white/20">
              <LeftSidebar />
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-w-0">
              <MainContent />
              {/* Show workflow bar on larger screens, hide on mobile where BottomNav exists */}
              <div className="hidden sm:block">
                <BottomWorkflowBar />
              </div>
            </main>

            {/* Right Sidebar - Hidden on mobile/tablet/laptop */}
            <div className="hidden xl:block w-80 border-l border-glass-white/20">
              <RightSidebar />
            </div>
          </div>

          {/* Mobile Bottom Navigation - Visible on mobile/tablet only */}
          <div className="sm:hidden">
            <MobileBottomNav />
          </div>
        </div>

        {/* Modals */}
        {isRegistrationModalOpen && <RegistrationModal />}
        {isTransactionModalOpen && <TransactionModal />}
        {isMarketplaceModalOpen && <MarketplaceModal />}

        {/* Floating Voice Command Button */}
        <div className="fixed bottom-24 right-8 z-[100] group">
          <div className={`absolute inset-0 bg-neon-cyan/20 blur-xl rounded-full scale-150 animate-pulse transition-opacity ${isListening ? 'opacity-100' : 'opacity-0'}`}></div>
          <Button 
            onClick={() => setIsListening(!isListening)}
            className={`w-16 h-16 rounded-full shadow-[0_0_30px_rgba(0,255,255,0.3)] transition-all duration-500 flex items-center justify-center border-2 ${
              isListening 
                ? 'bg-neon-cyan border-white scale-110 shadow-[0_0_50px_rgba(0,255,255,0.6)]' 
                : 'bg-cyber-dark border-neon-cyan/50 hover:border-neon-cyan hover:scale-110'
            }`}
          >
            <Mic className={`w-7 h-7 transition-colors ${isListening ? 'text-black' : 'text-neon-cyan group-hover:text-white'}`} />
          </Button>
          <div className={`absolute right-full mr-4 top-1/2 -translate-y-1/2 bg-black/80 backdrop-blur-md border border-neon-cyan/30 px-4 py-2 rounded-xl whitespace-nowrap text-xs font-bold text-white transition-all duration-500 ${isListening ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4 pointer-events-none'}`}>
            <span className="flex items-center">
              <div className="w-1.5 h-1.5 bg-neon-cyan rounded-full mr-2 animate-ping"></div>
              Listening for "DEDAN"...
            </span>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App
