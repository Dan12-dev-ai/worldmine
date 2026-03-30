import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Bell, MessageCircle, Circle, Mic, Globe, Shield, AlertTriangle } from 'lucide-react';
import DedanLogo from './DedanLogo';
import { Button } from './ui/button';
import { useMarketplaceStore } from '../store/marketplaceStore';
import { fraudDetection, SecurityAlert } from '../services/fraudDetection';

interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  uptime: number;
  activeUsers: number;
  securityLevel: number;
}

const GlobalNavbar: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { activeTab, setActiveTab } = useMarketplaceStore();
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    status: 'healthy',
    uptime: 99.9,
    activeUsers: 1247,
    securityLevel: 95
  });
  const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([]);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'am', name: 'አማርኛ', flag: '🇪🇹' }
  ];

  const tabs = [
    { id: 'marketplace', label: t('navbar.marketplace'), icon: '🏪' },
    { id: 'contracts', label: t('navbar.contracts'), icon: '📄' },
    { id: 'News', label: 'News', icon: '📰' },
    { id: 'profile', label: t('navbar.profile'), icon: '👤' },
    { id: 'settings', label: t('navbar.settings'), icon: '⚙️' }
  ];

  useEffect(() => {
    const loadSecurityAlerts = () => {
      const userId = 'current_user'; // This would come from auth context
      const alerts = fraudDetection.getAlerts(userId);
      setSecurityAlerts(alerts.filter(alert => alert.severity === 'high'));
    };

    loadSecurityAlerts();
    const interval = setInterval(loadSecurityAlerts, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
    setShowLanguageMenu(false);
  };

  const getHealthStatusColor = (status: SystemHealth['status']) => {
    switch (status) {
      case 'healthy': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'critical': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getHealthStatusIcon = (status: SystemHealth['status']) => {
    switch (status) {
      case 'healthy': return <Circle className="w-2 h-2 fill-current" />;
      case 'warning': return <AlertTriangle className="w-2 h-2" />;
      case 'critical': return <AlertTriangle className="w-2 h-2" />;
      default: return <Circle className="w-2 h-2" />;
    }
  };

  return (
    <div className="glass-morphism border-b border-glass-white/20 sticky top-0 z-50">
      <div className="flex items-center justify-between px-4 sm:px-6 py-3">
        {/* Logo */}
        <DedanLogo className="scale-75 sm:scale-90" />

        {/* Search Bar */}
        <div className="hidden md:flex flex-1 max-w-2xl mx-4 lg:mx-12">
          <div className="relative group w-full">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 group-focus-within:text-neon-cyan transition-colors" />
            <input
              type="text"
              placeholder={t('marketplace.search')}
              className="w-full pl-12 pr-12 py-2 bg-cyber-dark/50 border border-glass-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/20 transition-all"
            />
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
              <Mic className="w-4 h-4 text-gray-500 hover:text-neon-cyan cursor-pointer transition-colors" />
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="hidden lg:flex items-center space-x-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`text-sm font-medium transition-all hover:text-neon-cyan relative whitespace-nowrap flex items-center space-x-1 ${
                activeTab === tab.id
                  ? 'text-neon-cyan neon-text'
                  : 'text-gray-400'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {activeTab === tab.id && (
                <div className="absolute -bottom-[22px] left-0 right-0 h-0.5 bg-neon-cyan shadow-[0_0_8px_rgba(0,255,255,0.8)]" />
              )}
            </button>
          ))}
        </div>

        {/* Right Icons */}
        <div className="flex items-center space-x-2 sm:space-x-4 ml-4">
          {/* Language Switcher */}
          <div className="relative">
            <button
              onClick={() => setShowLanguageMenu(!showLanguageMenu)}
              className="hidden lg:flex items-center space-x-2 bg-white/5 border border-white/10 rounded-full px-3 py-1.5 hover:border-neon-cyan/50 transition-colors"
            >
              <Globe className="w-4 h-4 text-gray-400" />
              <span className="text-xs font-medium text-white">
                {languages.find(lang => lang.code === i18n.language)?.flag || '🇺🇸'}
              </span>
            </button>

            {showLanguageMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-cyber-dark border border-glass-white/20 rounded-lg shadow-lg z-50">
                {languages.map((language) => (
                  <button
                    key={language.code}
                    onClick={() => handleLanguageChange(language.code)}
                    className={`w-full flex items-center space-x-3 px-4 py-2 text-sm hover:bg-white/5 transition-colors ${
                      i18n.language === language.code ? 'bg-white/10 text-neon-cyan' : 'text-gray-300'
                    }`}
                  >
                    <span className="text-lg">{language.flag}</span>
                    <span>{language.name}</span>
                    {i18n.language === language.code && (
                      <div className="w-2 h-2 bg-neon-cyan rounded-full"></div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* System Health Badge */}
          <div className="hidden sm:flex items-center space-x-2 bg-white/5 border border-white/10 rounded-full px-3 py-1.5">
            <div className={`flex items-center space-x-1 ${getHealthStatusColor(systemHealth.status)}`}>
              {getHealthStatusIcon(systemHealth.status)}
              <span className="text-xs font-bold">{systemHealth.uptime}%</span>
            </div>
            <div className="text-xs text-gray-400">
              {systemHealth.activeUsers.toLocaleString()} users
            </div>
          </div>

          {/* Security Alerts */}
          {securityAlerts.length > 0 && (
            <div className="relative">
              <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-400 h-8 w-8 sm:h-9 sm:w-9">
                <Shield className="w-4 h-4 sm:w-5 sm:h-5" />
                <span className="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 w-1.5 h-1.5 sm:w-2 sm:h-2 bg-red-500 rounded-full border border-cyber-dark animate-pulse"></span>
              </Button>
            </div>
          )}

          {/* Standard Icons */}
          <div className="flex items-center space-x-1 sm:space-x-2">
            <Button variant="ghost" size="icon" className="text-gray-400 hover:text-neon-cyan h-8 w-8 sm:h-9 sm:w-9">
              <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-gray-400 hover:text-neon-cyan h-8 w-8 sm:h-9 sm:w-9 relative">
              <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 w-1.5 h-1.5 sm:w-2 sm:h-2 bg-blue-500 rounded-full border border-cyber-dark"></span>
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

      {/* Mobile Navigation */}
      <div className="lg:hidden overflow-x-auto scrollbar-hide border-t border-glass-white/10">
        <div className="flex space-x-6 px-6 py-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`text-xs sm:text-sm font-medium whitespace-nowrap transition-all hover:text-neon-cyan relative flex items-center space-x-1 ${
                activeTab === tab.id
                  ? 'text-neon-cyan neon-text'
                  : 'text-gray-400'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {activeTab === tab.id && (
                <div className="absolute -bottom-3 left-0 right-0 h-0.5 bg-neon-cyan" />
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GlobalNavbar;
