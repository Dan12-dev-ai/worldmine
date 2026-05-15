/**
 * ⚙️ SYSTEM SETTINGS CENTER (ENTERPRISE-GRADE)
 * Security, Account, Wallet, Market, AI, Notifications, UI, Globalization
 */

import React, { useState } from 'react'
import { 
  Shield, 
  User, 
  Wallet, 
  TrendingUp, 
  Brain, 
  Bell, 
  Palette, 
  Globe,
  Check,
  ChevronRight,
  Lock,
  Smartphone,
  History,
  Key,
  AlertTriangle,
  Clock,
  Eye,
  EyeOff
} from 'lucide-react'

const SETTINGS_CATEGORIES = [
  { id: 'security', label: 'Security Settings', icon: Shield, color: 'text-[var(--trust-success)]' },
  { id: 'account', label: 'Account & Identity', icon: User, color: 'text-[var(--accent-cyan)]' },
  { id: 'wallet', label: 'Wallet & Finance', icon: Wallet, color: 'text-[var(--accent-gold)]' },
  { id: 'market', label: 'Market Preferences', icon: TrendingUp, color: 'text-[var(--accent-purple)]' },
  { id: 'ai', label: 'AI Assistant', icon: Brain, color: 'text-[var(--accent-purple)]' },
  { id: 'notifications', label: 'Notifications', icon: Bell, color: 'text-[var(--accent-cyan)]' },
  { id: 'ui', label: 'UI/UX Personalization', icon: Palette, color: 'text-[var(--text-secondary)]' },
  { id: 'global', label: 'Globalization', icon: Globe, color: 'text-[var(--accent-gold)]' }
]

export const SystemSettingsCenter: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<string>('security')

  const renderSettingsCategory = () => {
    switch (activeCategory) {
      case 'security': return <SecuritySettings />
      case 'account': return <AccountIdentitySettings />
      case 'wallet': return <WalletFinanceSettings />
      case 'market': return <MarketPreferences />
      case 'ai': return <AIAssistantSettings />
      case 'notifications': return <NotificationSettings />
      case 'ui': return <UIPersonalization />
      case 'global': return <GlobalizationSettings />
      default: return <SecuritySettings />
    }
  }

  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">System Settings</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Enterprise-grade platform configuration</p>
        </div>
      </div>

      {/* SETTINGS LAYOUT */}
      <div className="flex gap-6">
        {/* CATEGORIES SIDEBAR */}
        <div className="w-64 flex-shrink-0">
          <div className="glass p-3 rounded-xl border border-[var(--border-subtle)] sticky top-6">
            <h3 className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest px-3 py-2">
              SETTINGS CATEGORIES
            </h3>
            <div className="space-y-1">
              {SETTINGS_CATEGORIES.map((category) => {
                const Icon = category.icon
                const isActive = activeCategory === category.id
                
                return (
                  <button
                    key={category.id}
                    onClick={() => setActiveCategory(category.id)}
                    className={`
                      w-full flex items-center justify-between px-3 py-2.5 rounded-lg
                      transition-all duration-200
                      ${isActive 
                        ? 'bg-gradient-to-r from-[var(--accent-cyan-soft)] to-transparent border-l-2 border-[var(--accent-cyan)] text-[var(--accent-cyan)]'
                        : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-[var(--text-primary)]'
                      }
                    `}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`w-4.5 h-4.5 ${isActive ? 'text-[var(--accent-cyan)]' : category.color}`} />
                      <span className="text-sm font-medium">{category.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-4 h-4" />}
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* SETTINGS CONTENT */}
        <div className="flex-1">
          {renderSettingsCategory()}
        </div>
      </div>
    </div>
  )
}

// ============================================
// 🔐 SECURITY SETTINGS
// ============================================
const SecuritySettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <Shield className="w-5 h-5 text-[var(--trust-success)]" />
          <span>Security Settings</span>
        </h2>

        <div className="space-y-5">
          {/* TWO-FACTOR AUTHENTICATION */}
          <SettingCard 
            title="Two-Factor Authentication"
            description="Add an extra layer of security to your account"
            icon={Lock}
            enabled={true}
          />

          {/* DEVICE MANAGEMENT */}
          <SettingCard 
            title="Device Management"
            description="View and manage devices that have access to your account"
            icon={Smartphone}
            enabled={false}
          />

          {/* SESSION CONTROL */}
          <SettingCard 
            title="Session Control"
            description="View and terminate active sessions"
            icon={History}
            enabled={false}
          />

          {/* LOGIN HISTORY */}
          <SettingCard 
            title="Login History"
            description="Review all login attempts and activity"
            icon={Clock}
            enabled={false}
          />

          {/* API ACCESS CONTROL */}
          <SettingCard 
            title="API Access Control"
            description="Manage API keys and webhook access"
            icon={Key}
            enabled={false}
          />

          {/* RISK-BASED AUTHENTICATION */}
          <SettingCard 
            title="Risk-Based Authentication"
            description="Adaptive security based on risk assessment"
            icon={AlertTriangle}
            enabled={false}
          />
        </div>
      </div>
    </div>
  )
}

// ============================================
// 👤 ACCOUNT & IDENTITY
// ============================================
const AccountIdentitySettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <User className="w-5 h-5 text-[var(--accent-cyan)]" />
          <span>Account & Identity</span>
        </h2>

        <div className="space-y-5">
          <SettingCard 
            title="KYC Verification Status"
            description="Your identity verification level"
            icon={Check}
            enabled={true}
          />
          <SettingCard 
            title="Business Profile Management"
            description="Update your company information"
            icon={User}
            enabled={false}
          />
          <SettingCard 
            title="Compliance Documents"
            description="Upload and manage legal documents"
            icon={FileText}
            enabled={false}
          />
          <SettingCard 
            title="Identity Trust Score"
            description="View your credibility metrics"
            icon={Activity}
            enabled={false}
          />
        </div>
      </div>
    </div>
  )
}

// ============================================
// 💳 WALLET & FINANCE SETTINGS
// ============================================
const WalletFinanceSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <Wallet className="w-5 h-5 text-[var(--accent-gold)]" />
          <span>Wallet & Finance</span>
        </h2>

        <div className="space-y-5">
          <SettingCard title="Wallet Management" description="Manage your payment wallets" icon={Wallet} enabled={false} />
          <SettingCard title="Currency Preferences" description="Select your default currency" icon={Globe} enabled={false} />
          <SettingCard title="Transaction Limits" description="Set daily and monthly limits" icon={Lock} enabled={false} />
          <SettingCard title="Escrow Preferences" description="Configure escrow settings" icon={ShieldCheck} enabled={false} />
          <SettingCard title="Payment Method Controls" description="Manage your payment methods" icon={CreditCard} enabled={false} />
        </div>
      </div>
    </div>
  )
}

// ============================================
// 📊 MARKET PREFERENCES
// ============================================
const MarketPreferences: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-[var(--accent-purple)]" />
          <span>Market Preferences</span>
        </h2>

        <div className="space-y-5">
          <SettingCard title="Preferred Commodities" description="Select commodities to prioritize" icon={Package} enabled={false} />
          <SettingCard title="Price Alert Settings" description="Configure price notifications" icon={Bell} enabled={false} />
          <SettingCard title="Risk Tolerance Configuration" description="Set your risk parameters" icon={AlertTriangle} enabled={false} />
          <SettingCard title="Auto-Notification Rules" description="Customize what alerts you receive" icon={Settings} enabled={false} />
        </div>
      </div>
    </div>
  )
}

// ============================================
// 🧠 AI ASSISTANT SETTINGS
// ============================================
const AIAssistantSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <Brain className="w-5 h-5 text-[var(--accent-purple)]" />
          <span>AI Assistant Settings</span>
        </h2>

        <div className="space-y-5">
          <SettingCard title="Enable/Disable AI Suggestions" description="Toggle AI recommendations" icon={Eye} enabled={true} />
          <SettingCard title="Risk Explanation Level" description="Low/Medium/High detail" icon={AlertTriangle} enabled={false} />
          <SettingCard title="Trading Insights Visibility" description="Show/hide trading insights" icon={TrendingUp} enabled={false} />
          <SettingCard title="Voice Assistant Settings" description="Configure voice commands" icon={Mic} enabled={false} />
          <SettingCard title="Language Model Preference" description="Select your AI model" icon={Brain} enabled={false} />
        </div>
      </div>
    </div>
  )
}

// ============================================
// 🔔 NOTIFICATION SETTINGS
// ============================================
const NotificationSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <Bell className="w-5 h-5 text-[var(--accent-cyan)]" />
          <span>Notification Center</span>
        </h2>

        <div className="space-y-5">
          <SettingCard title="Market Alerts" description="Price and market movement alerts" icon={TrendingUp} enabled={false} />
          <SettingCard title="Trade Updates" description="Transaction status notifications" icon={Activity} enabled={false} />
          <SettingCard title="Logistics Tracking Alerts" description="Shipment and delivery updates" icon={Truck} enabled={false} />
          <SettingCard title="AI Insights Notifications" description="New AI analysis reports" icon={Brain} enabled={false} />
          <SettingCard title="Emergency Risk Alerts" description="Critical security and risk alerts" icon={AlertTriangle} enabled={true} />
        </div>
      </div>
    </div>
  )
}

// ============================================
// 🎨 UI/UX PERSONALIZATION
// ============================================
const UIPersonalization: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <Palette className="w-5 h-5 text-[var(--text-secondary)]" />
          <span>UI/UX Personalization</span>
        </h2>

        <div className="space-y-5">
          <SettingCard title="Theme Selection" description="Cyber Luxury / Dark Industrial / Financial Mode" icon={Palette} enabled={false} />
          <SettingCard title="Density Mode" description="Compact / Standard / Analyst Mode" icon={Maximize2} enabled={false} />
          <SettingCard title="Chart Style Preferences" description="Customize chart appearance" icon={BarChart3} enabled={false} />
          <SettingCard title="Dashboard Layout Customization" description="Arrange your dashboard" icon={Layout} enabled={false} />
        </div>
      </div>
    </div>
  )
}

// ============================================
// 🌍 GLOBALIZATION SETTINGS
// ============================================
const GlobalizationSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center space-x-2">
          <Globe className="w-5 h-5 text-[var(--accent-gold)]" />
          <span>Globalization Settings</span>
        </h2>

        <div className="space-y-5">
          <SettingCard title="Language Switching" description="Select your interface language" icon={Globe} enabled={false} />
          <SettingCard title="Timezone Settings" description="Set your local timezone" icon={Clock} enabled={false} />
          <SettingCard title="Regional Compliance Mode" description="Adjust to local regulations" icon={Shield} enabled={false} />
          <SettingCard title="Currency Display Format" description="Number and currency formatting" icon={DollarSign} enabled={false} />
        </div>
      </div>
    </div>
  )
}

// ============================================
// REUSABLE SETTING CARD COMPONENT
// ============================================
interface SettingCardProps {
  title: string
  description: string
  icon: React.ElementType
  enabled: boolean
}

const SettingCard: React.FC<SettingCardProps> = ({ title, description, icon: Icon, enabled }) => {
  return (
    <div className="flex items-center justify-between p-4 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border-subtle)] hover:border-[var(--accent-cyan)]/30 transition-all">
      <div className="flex items-center space-x-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${enabled ? 'bg-[var(--trust-success-soft)]' : 'bg-[var(--bg-secondary)]'}`}>
          <Icon className={`w-5 h-5 ${enabled ? 'text-[var(--trust-success)]' : 'text-[var(--text-tertiary)]'}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-[var(--text-primary)]">{title}</h4>
          <p className="text-xs text-[var(--text-tertiary)] mt-0.5">{description}</p>
        </div>
      </div>
      <div className="flex items-center space-x-3">
        {enabled ? (
          <div className="flex items-center space-x-2 px-3 py-1 bg-[var(--trust-success-soft)] rounded-full border border-[var(--trust-success)]/30">
            <Check className="w-3.5 h-3.5 text-[var(--trust-success)]" />
            <span className="text-[10px] font-semibold text-[var(--trust-success)]">ACTIVE</span>
          </div>
        ) : (
          <button className="px-3 py-1.5 bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-md text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:border-[var(--accent-cyan)] transition-all">
            Configure
          </button>
        )}
      </div>
    </div>
  )
}

// Missing icon components (stubs for compilation)
const FileText = () => null
const ShieldCheck = () => null
const CreditCard = () => null
const Package = () => null
const Settings = () => null
const Mic = () => null
const Maximize2 = () => null
const BarChart3 = () => null
const Layout = () => null
const DollarSign = () => null
const Truck = () => null

export default SystemSettingsCenter
