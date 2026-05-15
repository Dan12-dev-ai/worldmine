/**
 * 🌍 WORLD-MINE ENTERPRISE GLOBAL LAYOUT
 * Principal Frontend Architecture - Unified Interface Operating System
 */

import React, { useState, useEffect } from 'react'
import { 
  LayoutDashboard, 
  ShoppingCart, 
  TrendingUp, 
  Truck, 
  Brain, 
  Newspaper, 
  Video, 
  FileText, 
  User, 
  Settings, 
  Code, 
  HelpCircle,
  Search,
  Bell,
  ShieldCheck,
  Activity,
  Clock,
  ChevronDown,
  Command,
  Globe
} from 'lucide-react'

import { EnterpriseSidebar } from './EnterpriseSidebar'
import { TopStatusBar } from './TopStatusBar'
import { RightAIPanel } from './RightAIPanel'
import { GlobalDashboard } from './modules/GlobalDashboard'
import { MarketplaceModule } from './modules/MarketplaceModule'
import { TradingHubModule } from './modules/TradingHubModule'
import { LogisticsModule } from './modules/LogisticsModule'
import { AIIntelligenceCenter } from './modules/AIIntelligenceCenter'
import { MineralIntelligenceHub } from './modules/MineralIntelligenceHub'
import { CommunicationHub } from './modules/CommunicationHub'
import { ContractsEscrowSystem } from './modules/ContractsEscrowSystem'
import { UserControlCenter } from './modules/UserControlCenter'
import { SystemSettingsCenter } from './modules/SystemSettingsCenter'
import { DevelopersAPIHub } from './modules/DevelopersAPIHub'
import { HelpSupportSystem } from './modules/HelpSupportSystem'

// ============================================
// NAVIGATION CONFIGURATION (12 MODULES)
// ============================================
const NAVIGATION_MODULES = [
  {
    id: 'dashboard',
    label: 'Global Dashboard',
    icon: LayoutDashboard,
    category: 'Core'
  },
  {
    id: 'marketplace',
    label: 'Marketplace (Physical)',
    icon: ShoppingCart,
    category: 'Marketplace'
  },
  {
    id: 'trading',
    label: 'Digital Trading Hub',
    icon: TrendingUp,
    category: 'Trading'
  },
  {
    id: 'logistics',
    label: 'Logistics & Supply Chain',
    icon: Truck,
    category: 'Operations'
  },
  {
    id: 'ai-intelligence',
    label: 'AI Intelligence Center',
    icon: Brain,
    category: 'AI'
  },
  {
    id: 'mineral-intelligence',
    label: 'Live Mineral Intelligence',
    icon: Newspaper,
    category: 'Intelligence'
  },
  {
    id: 'communication',
    label: 'Communication Hub',
    icon: Video,
    category: 'Collaboration'
  },
  {
    id: 'contracts',
    label: 'Contracts & Escrow',
    icon: FileText,
    category: 'Legal'
  },
  {
    id: 'user-control',
    label: 'User Control Center',
    icon: User,
    category: 'Account'
  },
  {
    id: 'settings',
    label: 'System Settings',
    icon: Settings,
    category: 'Settings'
  },
  {
    id: 'developers',
    label: 'Developers / API',
    icon: Code,
    category: 'Enterprise'
  },
  {
    id: 'help',
    label: 'Help & Support',
    icon: HelpCircle,
    category: 'Support'
  }
]

// ============================================
// MAIN GLOBAL LAYOUT COMPONENT
// ============================================
export const EnterpriseGlobalLayout: React.FC = () => {
  const [activeModule, setActiveModule] = useState<string>('dashboard')
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false)
  const [aiPanelOpen, setAiPanelOpen] = useState<boolean>(true)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState<boolean>(false)
  const [searchQuery, setSearchQuery] = useState<string>('')

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(!commandPaletteOpen)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [commandPaletteOpen])

  // Render active module
  const renderActiveModule = () => {
    switch (activeModule) {
      case 'dashboard': return <GlobalDashboard />
      case 'marketplace': return <MarketplaceModule />
      case 'trading': return <TradingHubModule />
      case 'logistics': return <LogisticsModule />
      case 'ai-intelligence': return <AIIntelligenceCenter />
      case 'mineral-intelligence': return <MineralIntelligenceHub />
      case 'communication': return <CommunicationHub />
      case 'contracts': return <ContractsEscrowSystem />
      case 'user-control': return <UserControlCenter />
      case 'settings': return <SystemSettingsCenter />
      case 'developers': return <DevelopersAPIHub />
      case 'help': return <HelpSupportSystem />
      default: return <GlobalDashboard />
    }
  }

  return (
    <div className="flex h-screen w-full bg-[var(--bg-primary)] overflow-hidden">
      {/* 🔷 LEFT SIDEBAR - ENTERPRISE NAVIGATION */}
      <EnterpriseSidebar 
        activeModule={activeModule}
        setActiveModule={setActiveModule}
        modules={NAVIGATION_MODULES}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
      />

      {/* MAIN CONTENT AREA */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* 🔷 TOP STATUS BAR - REAL-TIME SYSTEM STATE */}
        <TopStatusBar 
          activeModule={activeModule}
          modules={NAVIGATION_MODULES}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          commandPaletteOpen={commandPaletteOpen}
          setCommandPaletteOpen={setCommandPaletteOpen}
        />

        {/* 🔷 MAIN WORKSPACE - DYNAMIC MODULE AREA */}
        <main className="flex-1 overflow-hidden flex">
          <div className="flex-1 overflow-y-auto p-6">
            {renderActiveModule()}
          </div>

          {/* 🔷 RIGHT AI PANEL - CONTEXTUAL ASSISTANT */}
          {aiPanelOpen && (
            <RightAIPanel 
              activeModule={activeModule}
              onClose={() => setAiPanelOpen(false)}
            />
          )}
        </main>
      </div>
    </div>
  )
}

export default EnterpriseGlobalLayout
