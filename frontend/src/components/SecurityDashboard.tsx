/**
 * 🔐 DEDAN 2.0 - Enterprise Security Dashboard
 * User-friendly but uncompromising security features
 * MFA setup, session management, security monitoring
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, Key, Smartphone, Mail, AlertTriangle,
  CheckCircle, Clock, Eye, EyeOff,
  Lock, Unlock, RefreshCw, Trash2,
  Activity, Globe, Fingerprint, Users,
  Settings, Download, Copy, ExternalLink
} from 'lucide-react';

interface SecuritySession {
  id: string;
  device: string;
  location: string;
  ipAddress: string;
  browser: string;
  lastActive: string;
  isCurrent: boolean;
  trustLevel: 'trusted' | 'unknown' | 'suspicious';
}

interface MFAMethod {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  enabled: boolean;
  setupRequired: boolean;
  lastUsed?: string;
}

interface SecurityEvent {
  id: string;
  type: 'login' | 'logout' | 'mfa_enabled' | 'password_change' | 'suspicious_activity' | 'withdrawal' | 'api_key_created';
  title: string;
  description: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  resolved: boolean;
  ipAddress: string;
  location: string;
}

interface APIKey {
  id: string;
  name: string;
  permissions: string[];
  keyPreview: string;
  createdAt: string;
  lastUsed?: string;
  expiresAt?: string;
  isActive: boolean;
}

interface WithdrawalAddress {
  id: string;
  address: string;
  network: string;
  label: string;
  addedAt: string;
  isVerified: boolean;
  transactions: number;
}

const SecurityDashboard: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState<'overview' | 'mfa' | 'sessions' | 'api_keys' | 'withdrawal_whitelist' | 'events'>('overview');
  const [securityScore, setSecurityScore] = useState(85);
  const [sessions, setSessions] = useState<SecuritySession[]>([]);
  const [mfaMethods, setMfaMethods] = useState<MFAMethod[]>([]);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [withdrawalAddresses, setWithdrawalAddresses] = useState<WithdrawalAddress[]>([]);
  const [showPassword, setShowPassword] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [mfaSetupStep, setMfaSetupStep] = useState(0);
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);

  // Mock data generation
  const generateMockSessions = (): SecuritySession[] => {
    return [
      {
        id: '1',
        device: 'Chrome on Windows',
        location: 'New York, United States',
        ipAddress: '192.168.1.1',
        browser: 'Chrome 120.0',
        lastActive: new Date().toISOString(),
        isCurrent: true,
        trustLevel: 'trusted'
      },
      {
        id: '2',
        device: 'Safari on iPhone',
        location: 'San Francisco, United States',
        ipAddress: '192.168.1.2',
        browser: 'Safari 17.0',
        lastActive: new Date(Date.now() - 3600000).toISOString(),
        isCurrent: false,
        trustLevel: 'trusted'
      },
      {
        id: '3',
        device: 'Firefox on Linux',
        location: 'Unknown',
        ipAddress: '192.168.1.3',
        browser: 'Firefox 121.0',
        lastActive: new Date(Date.now() - 7200000).toISOString(),
        isCurrent: false,
        trustLevel: 'suspicious'
      }
    ];
  };

  const generateMockMfaMethods = (): MFAMethod[] => {
    return [
      {
        id: 'totp',
        name: 'Authenticator App',
        description: 'Use TOTP apps like Google Authenticator or Authy',
        icon: <Smartphone className="w-5 h-5" />,
        enabled: true,
        setupRequired: false,
        lastUsed: new Date(Date.now() - 86400000).toISOString()
      },
      {
        id: 'sms',
        name: 'SMS Authentication',
        description: 'Receive verification codes via SMS',
        icon: <Mail className="w-5 h-5" />,
        enabled: true,
        setupRequired: false,
        lastUsed: new Date(Date.now() - 172800000).toISOString()
      },
      {
        id: 'hardware_key',
        name: 'Hardware Security Key',
        description: 'Use YubiKey or other FIDO2 compatible keys',
        icon: <Key className="w-5 h-5" />,
        enabled: false,
        setupRequired: true
      },
      {
        id: 'biometric',
        name: 'Biometric Authentication',
        description: 'Face ID, Touch ID, or Windows Hello',
        icon: <Fingerprint className="w-5 h-5" />,
        enabled: true,
        setupRequired: false,
        lastUsed: new Date().toISOString()
      }
    ];
  };

  const generateMockSecurityEvents = (): SecurityEvent[] => {
    return [
      {
        id: '1',
        type: 'login',
        title: 'Successful Login',
        description: 'Logged in from Chrome on Windows',
        timestamp: new Date().toISOString(),
        severity: 'low',
        resolved: true,
        ipAddress: '192.168.1.1',
        location: 'New York, United States'
      },
      {
        id: '2',
        type: 'mfa_enabled',
        title: 'MFA Enabled',
        description: 'Two-factor authentication was enabled',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        severity: 'medium',
        resolved: true,
        ipAddress: '192.168.1.1',
        location: 'New York, United States'
      },
      {
        id: '3',
        type: 'suspicious_activity',
        title: 'Suspicious Login Attempt',
        description: 'Failed login attempt from unknown device',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        severity: 'high',
        resolved: true,
        ipAddress: '192.168.1.100',
        location: 'Unknown'
      }
    ];
  };

  // Initialize data
  useEffect(() => {
    setSessions(generateMockSessions());
    setMfaMethods(generateMockMfaMethods());
    setSecurityEvents(generateMockSecurityEvents());
    calculateSecurityScore();
  }, []);

  // Calculate security score
  const calculateSecurityScore = useCallback(() => {
    const enabledMfa = generateMockMfaMethods().filter(method => method.enabled).length;
    const trustedSessions = generateMockSessions().filter(session => session.trustLevel === 'trusted').length;
    const suspiciousEvents = generateMockSecurityEvents().filter(event => event.severity === 'high' || event.severity === 'critical').length;
    
    let score = 50; // Base score
    score += enabledMfa * 15; // MFA methods
    score += trustedSessions * 5; // Trusted sessions
    score -= suspiciousEvents * 20; // Security incidents
    
    score = Math.max(0, Math.min(100, score));
    setSecurityScore(score);
  }, []);

  // Terminate session
  const terminateSession = useCallback((sessionId: string) => {
    setSessions(prev => prev.filter(session => session.id !== sessionId));
    calculateSecurityScore();
  }, [calculateSecurityScore]);

  // Setup MFA
  const setupMFA = useCallback(async (methodId: string) => {
    setIsProcessing(true);
    setMfaSetupStep(1);
    
    // Simulate MFA setup process
    if (methodId === 'totp') {
      // Generate QR code for TOTP setup
      const secret = 'JBSWY3DPEHPK3PXP'; // Mock secret
      setQrCode(`otpauth://totp/DEDAN:user?secret=${secret}&issuer=DEDAN`);
      
      // Generate backup codes
      const codes = Array.from({ length: 10 }, (_, i) => 
        Math.random().toString(36).substring(2, 10).toUpperCase()
      );
      setBackupCodes(codes);
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    setMfaSetupStep(2);
    setIsProcessing(false);
  }, []);

  // Enable MFA method
  const enableMFAMethod = useCallback((methodId: string) => {
    setMfaMethods(prev => prev.map(method => 
      method.id === methodId 
        ? { ...method, enabled: true, setupRequired: false }
        : method
    ));
    calculateSecurityScore();
  }, [calculateSecurityScore]);

  // Disable MFA method
  const disableMFAMethod = useCallback((methodId: string) => {
    setMfaMethods(prev => prev.map(method => 
      method.id === methodId 
        ? { ...method, enabled: false }
        : method
    ));
    calculateSecurityScore();
  }, [calculateSecurityScore]);

  // Create API key
  const createAPIKey = useCallback(async () => {
    setIsProcessing(true);
    
    // Simulate API key creation
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const newKey: APIKey = {
      id: `key_${Date.now()}`,
      name: 'Trading Bot API Key',
      permissions: ['read', 'trade', 'withdraw'],
      keyPreview: 'dedan_live_' + '*'.repeat(32),
      createdAt: new Date().toISOString(),
      isActive: true
    };
    
    setApiKeys(prev => [newKey, ...prev]);
    setIsProcessing(false);
  }, []);

  // Revoke API key
  const revokeAPIKey = useCallback((keyId: string) => {
    setApiKeys(prev => prev.filter(key => key.id !== keyId));
  }, []);

  // Add withdrawal address
  const addWithdrawalAddress = useCallback(async (address: string, network: string, label: string) => {
    setIsProcessing(true);
    
    // Simulate address verification
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const newAddress: WithdrawalAddress = {
      id: `addr_${Date.now()}`,
      address,
      network,
      label,
      addedAt: new Date().toISOString(),
      isVerified: true,
      transactions: 0
    };
    
    setWithdrawalAddresses(prev => [newAddress, ...prev]);
    setIsProcessing(false);
  }, []);

  // Remove withdrawal address
  const removeWithdrawalAddress = useCallback((addressId: string) => {
    setWithdrawalAddresses(prev => prev.filter(addr => addr.id !== addressId));
  }, []);

  // Change password
  const changePassword = useCallback(async () => {
    if (newPassword !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    
    setIsProcessing(true);
    
    // Simulate password change
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    alert('Password changed successfully');
    setNewPassword('');
    setConfirmPassword('');
    setShowPassword(false);
    setIsProcessing(false);
  }, [newPassword, confirmPassword]);

  const getSecurityScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getSecurityScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Security Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Security Score Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">Security Score</h2>
                <p className="text-slate-400">Overall security posture of your account</p>
              </div>
              <div className="text-center">
                <div className={`text-6xl font-bold ${getSecurityScoreColor(securityScore)}`}>
                  {securityScore}
                </div>
                <div className={`text-lg ${getSecurityScoreColor(securityScore)}`}>
                  {getSecurityScoreLabel(securityScore)}
                </div>
              </div>
            </div>
            
            {/* Security Recommendations */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              {securityScore < 80 && (
                <div className="flex items-center space-x-3 p-3 bg-yellow-500/20 border border-yellow-500/50 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                  <div className="text-sm text-yellow-400">
                    Enable hardware security key for maximum protection
                  </div>
                </div>
              )}
              {securityScore < 90 && (
                <div className="flex items-center space-x-3 p-3 bg-blue-500/20 border border-blue-500/50 rounded-lg">
                  <Shield className="w-5 h-5 text-blue-400" />
                  <div className="text-sm text-blue-400">
                    Consider enabling additional MFA methods
                  </div>
                </div>
              )}
              <div className="flex items-center space-x-3 p-3 bg-green-500/20 border border-green-500/50 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <div className="text-sm text-green-400">
                  Account security is actively monitored
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="flex space-x-1 border-b border-slate-700">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'mfa', label: 'MFA' },
              { id: 'sessions', label: 'Sessions' },
              { id: 'api_keys', label: 'API Keys' },
              { id: 'withdrawal_whitelist', label: 'Whitelist' },
              { id: 'events', label: 'Events' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-6 py-3 font-medium transition-colors border-b-2 ${
                  activeTab === tab.id 
                    ? 'text-blue-400 border-blue-500' 
                    : 'text-slate-400 border-transparent hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Quick Stats */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                    <h3 className="text-lg font-semibold mb-4">Security Overview</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">MFA Methods</span>
                        <span className="text-green-400">
                          {mfaMethods.filter(m => m.enabled).length}/4 enabled
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Active Sessions</span>
                        <span className="text-blue-400">
                          {sessions.filter(s => s.isCurrent).length} of {sessions.length}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">API Keys</span>
                        <span className="text-purple-400">{apiKeys.length}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Whitelisted Addresses</span>
                        <span className="text-yellow-400">{withdrawalAddresses.length}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                  <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    {securityEvents.slice(0, 5).map(event => (
                      <div key={event.id} className="flex items-start space-x-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          event.severity === 'critical' ? 'bg-red-500' :
                          event.severity === 'high' ? 'bg-red-400' :
                          event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                        }`} />
                        <div className="flex-1">
                          <div className="font-medium text-sm">{event.title}</div>
                          <div className="text-slate-400 text-xs">
                            {new Date(event.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* MFA Tab */}
            {activeTab === 'mfa' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                  <h3 className="text-lg font-semibold mb-4">Multi-Factor Authentication</h3>
                  <p className="text-slate-400 mb-6">
                    Add an extra layer of security to your account. Enable multiple MFA methods for maximum protection.
                  </p>
                  
                  <div className="space-y-4">
                    {mfaMethods.map(method => (
                      <div key={method.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-lg ${
                            method.enabled ? 'bg-green-500/20 text-green-400' : 'bg-slate-600 text-slate-400'
                          }`}>
                            {method.icon}
                          </div>
                          <div>
                            <div className="font-medium">{method.name}</div>
                            <div className="text-sm text-slate-400">{method.description}</div>
                            {method.lastUsed && (
                              <div className="text-xs text-slate-500">
                                Last used: {new Date(method.lastUsed).toLocaleDateString()}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {method.enabled ? (
                            <button
                              onClick={() => disableMFAMethod(method.id)}
                              className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors"
                            >
                              Disable
                            </button>
                          ) : (
                            <button
                              onClick={() => setupMFA(method.id)}
                              disabled={isProcessing}
                              className="px-3 py-1 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm rounded-lg transition-colors"
                            >
                              {method.setupRequired ? 'Setup' : 'Enable'}
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* MFA Setup Modal */}
                <AnimatePresence>
                  {mfaSetupStep > 0 && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="bg-slate-800 border border-slate-700 rounded-xl p-8 max-w-md w-full"
                      >
                        <h3 className="text-xl font-bold mb-6">Setup Authenticator App</h3>
                        
                        {mfaSetupStep === 1 && (
                          <div className="text-center">
                            <div className="mb-6">
                              <div className="w-48 h-48 bg-white p-4 rounded-lg mx-auto">
                                {/* QR Code would go here */}
                                <div className="w-full h-full flex items-center justify-center text-slate-800">
                                  <QrCode className="w-32 h-32" />
                                </div>
                              </div>
                            </div>
                            <p className="text-slate-400 mb-4">
                              Scan this QR code with your authenticator app
                            </p>
                            <button
                              onClick={() => setMfaSetupStep(2)}
                              className="bg-blue-500 hover:bg-blue-600 text-white font-medium px-6 py-3 rounded-lg transition-colors"
                            >
                              Continue
                            </button>
                          </div>
                        )}
                        
                        {mfaSetupStep === 2 && (
                          <div>
                            <div className="mb-6">
                              <h4 className="font-semibold mb-2">Backup Codes</h4>
                              <p className="text-slate-400 text-sm mb-4">
                                Save these backup codes in a secure location. You can use them if you lose access to your authenticator.
                              </p>
                              <div className="grid grid-cols-2 gap-2">
                                {backupCodes.map((code, index) => (
                                  <div key={index} className="bg-slate-700 p-2 rounded font-mono text-sm">
                                    {code}
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div className="flex space-x-3">
                              <button
                                onClick={() => setMfaSetupStep(0)}
                                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-medium py-3 rounded-lg transition-colors"
                              >
                                Back
                              </button>
                              <button
                                onClick={() => {
                                  enableMFAMethod('totp');
                                  setMfaSetupStep(0);
                                }}
                                className="flex-1 bg-green-500 hover:bg-green-600 text-white font-medium py-3 rounded-lg transition-colors"
                              >
                                Complete Setup
                              </button>
                            </div>
                          </div>
                        )}
                      </motion.div>
                    </div>
                  )}
                </AnimatePresence>
              </div>
            )}

            {/* Sessions Tab */}
            {activeTab === 'sessions' && (
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h3 className="text-lg font-semibold mb-4">Active Sessions</h3>
                <p className="text-slate-400 mb-6">
                  Manage and monitor all devices logged into your account.
                </p>
                
                <div className="space-y-4">
                  {sessions.map(session => (
                    <div key={session.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full ${
                          session.trustLevel === 'trusted' ? 'bg-green-500' :
                          session.trustLevel === 'suspicious' ? 'bg-red-500' : 'bg-yellow-500'
                        }`} />
                        <div>
                          <div className="font-medium">{session.device}</div>
                          <div className="text-sm text-slate-400">
                            {session.location} • {session.ipAddress}
                          </div>
                          <div className="text-xs text-slate-500">
                            Last active: {new Date(session.lastActive).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {session.isCurrent && (
                          <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-lg">
                            Current
                          </span>
                        )}
                        {!session.isCurrent && (
                          <button
                            onClick={() => terminateSession(session.id)}
                            className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors"
                          >
                            Terminate
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* API Keys Tab */}
            {activeTab === 'api_keys' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">API Keys</h3>
                  <button
                    onClick={createAPIKey}
                    disabled={isProcessing}
                    className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium px-4 py-2 rounded-lg transition-colors"
                  >
                    Create New Key
                  </button>
                </div>
                
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                  <div className="space-y-4">
                    {apiKeys.map(key => (
                      <div key={key.id} className="border border-slate-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <div className="font-medium">{key.name}</div>
                            <div className="text-sm text-slate-400">
                              Created: {new Date(key.createdAt).toLocaleDateString()}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${
                              key.isActive ? 'bg-green-500' : 'bg-red-500'
                            }`} />
                            <button
                              onClick={() => revokeAPIKey(key.id)}
                              className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors"
                            >
                              Revoke
                            </button>
                          </div>
                        </div>
                        <div className="text-sm text-slate-400 mb-2">
                          Key: {key.keyPreview}
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {key.permissions.map(perm => (
                            <span key={perm} className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded">
                              {perm}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Withdrawal Whitelist Tab */}
            {activeTab === 'withdrawal_whitelist' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                  <h3 className="text-lg font-semibold mb-4">Withdrawal Whitelist</h3>
                  <p className="text-slate-400 mb-6">
                    Add trusted withdrawal addresses to enhance security.
                  </p>
                  
                  <div className="space-y-4">
                    {withdrawalAddresses.map(addr => (
                      <div key={addr.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
                        <div>
                          <div className="font-medium">{addr.label}</div>
                          <div className="text-sm text-slate-400 font-mono">
                            {addr.address}
                          </div>
                          <div className="text-xs text-slate-500">
                            {addr.network} • {addr.transactions} transactions
                          </div>
                        </div>
                        <button
                          onClick={() => removeWithdrawalAddress(addr.id)}
                          className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Security Events Tab */}
            {activeTab === 'events' && (
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h3 className="text-lg font-semibold mb-4">Security Events</h3>
                
                <div className="space-y-4">
                  {securityEvents.map(event => (
                    <div key={event.id} className="border border-slate-700 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className={`w-3 h-3 rounded-full ${
                              event.severity === 'critical' ? 'bg-red-500' :
                              event.severity === 'high' ? 'bg-red-400' :
                              event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                            }`} />
                            <span className={`px-2 py-1 text-xs rounded ${
                              event.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                              event.severity === 'high' ? 'bg-red-400/20 text-red-300' :
                              event.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'
                            }`}>
                              {event.severity.toUpperCase()}
                            </span>
                            <span className="font-medium">{event.title}</span>
                          </div>
                          <div className="text-sm text-slate-400">{event.description}</div>
                          <div className="text-xs text-slate-500 mt-2">
                            {new Date(event.timestamp).toLocaleString()} • {event.location}
                          </div>
                        </div>
                        {event.resolved && (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SecurityDashboard;
