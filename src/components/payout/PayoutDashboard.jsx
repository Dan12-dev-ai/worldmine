/**
 * DEDAN Mine - Universal Payout Dashboard
 * Ethiopian Sovereign Payout Gateway - NBE 2026 Compliant
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Smartphone, 
  Building, 
  Globe, 
  Shield, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  TrendingUp,
  Banknote,
  CreditCard,
  Wallet,
  Eye,
  EyeOff,
  Lock,
  Unlock
} from 'lucide-react';

// Translation data
const translations = {
  am: {
    title: "ዴዳንን የገንዝታት መዝርዝ",
    subtitle: "የኢትዮጵያ ንዳይነት የገንዝታት መስርዮት - NBE 2026 ተማማና",
    instantTelebirr: "አስታን ቴለብር",
    localBank: "የአገለር ባንክ",
    globalPayoneer: "ዓለለም ፔይኖነር",
    web3Wallet: "Web3 ዋሌል",
    amount: "መጠንያ",
    currency: "ገንዝታት",
    selectRail: "የገንዝታት መንገዛት",
    biometricVerify: "ባልክ ማረጋጥ",
    processing: "በሂደግ ላይ...",
    completed: "ተጠናነ",
    securityCheck: "የደህንታ ምርም",
    nbeCompliant: "NBE ተማማና",
    exportPermit: "የማሽግ ፍቃሽ",
    taxDeduction: "የግብር ቀረጽ",
    netAmount: "የተረፈ ዕይዝታት",
    confirmPayout: "የገንዝታትን ማረጋጥ",
    emergencyStop: "የአደጋና ማቆለች",
    securityFreeze: "የደህንታ ማቆለች"
  },
  en: {
    title: "Universal Payout Orchestrator",
    subtitle: "Ethiopian Sovereign Payout Gateway - NBE 2026 Compliant",
    instantTelebirr: "Instant Telebirr",
    localBank: "Local Bank",
    globalPayoneer: "Global Payoneer",
    web3Wallet: "Web3 Wallet",
    amount: "Amount",
    currency: "Currency",
    selectRail: "Select Payout Rail",
    biometricVerify: "Biometric Verify",
    processing: "Processing...",
    completed: "Completed",
    securityCheck: "Security Check",
    nbeCompliant: "NBE Compliant",
    exportPermit: "Export Permit",
    taxDeduction: "Tax Deduction",
    netAmount: "Net Amount",
    confirmPayout: "Confirm Payout",
    emergencyStop: "Emergency Stop",
    securityFreeze: "Security Freeze"
  }
};

const PayoutDashboard = () => {
  const [language, setLanguage] = useState('am');
  const [selectedRail, setSelectedRail] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('ETB');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showBiometric, setShowBiometric] = useState(false);
  const [payoutStatus, setPayoutStatus] = useState('');
  const [taxCalculation, setTaxCalculation] = useState(null);
  const [showSecurityAlert, setShowSecurityAlert] = useState(false);
  const [biometricVerified, setBiometricVerified] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [chapaConfig, setChapaConfig] = useState(null);
  const [payoneerConfig, setPayoneerConfig] = useState(null);

  const t = translations[language];

  const payoutRails = [
    {
      id: 'local_hub',
      name: t.instantTelebirr,
      icon: Smartphone,
      color: 'from-green-500 to-emerald-600',
      description: 'Instant payout to Telebirr or local banks',
      biometricRequired: true,
      supportedMethods: ['chapa', 'telebirr', 'bank_transfer']
    },
    {
      id: 'institutional_hub',
      name: t.globalPayoneer,
      icon: Globe,
      color: 'from-blue-500 to-indigo-600',
      description: 'International payouts via Payoneer or SWIFT',
      biometricRequired: false,
      supportedMethods: ['payoneer', 'swift']
    },
    {
      id: 'sovereign_crypto_bridge',
      name: t.web3Wallet,
      icon: Wallet,
      color: 'from-purple-500 to-violet-600',
      description: 'NBE compliant crypto payouts',
      biometricRequired: false,
      supportedMethods: ['web3_wallet'],
      nbeDisclaimer: true
    }
  ];

  useEffect(() => {
    // Initialize Chapa and Payoneer configs
    initializePaymentConfigs();
    
    // Calculate taxes when amount changes
    if (amount && parseFloat(amount) > 0) {
      calculateTaxes();
    }
  }, [amount, currency]);

  const initializePaymentConfigs = async () => {
    try {
      // Chapa Configuration (NBE Compliant)
      const chapaResponse = await fetch('/api/v1/payout/chapa/config', {
        headers: {
          'Authorization': 'Bearer valid_token'
        }
      });
      const chapaData = await chapaResponse.json();
      setChapaConfig(chapaData);

      // Payoneer Configuration (FXD/04/2026 Compliant)
      const payoneerResponse = await fetch('/api/v1/payout/payoneer/config', {
        headers: {
          'Authorization': 'Bearer valid_token'
        }
      });
      const payoneerData = await payoneerResponse.json();
      setPayoneerConfig(payoneerData);
    } catch (error) {
      console.error('Payment config initialization error:', error);
    }
  };

  const calculateTaxes = async () => {
    try {
      const response = await fetch('/api/v1/payout/tax/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid_token'
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          user_type: 'individual'
        })
      });
      
      const data = await response.json();
      setTaxCalculation(data);
    } catch (error) {
      console.error('Tax calculation error:', error);
    }
  };

  const handlePayout = async () => {
    if (!selectedRail || !amount) return;
    
    setIsProcessing(true);
    
    try {
      const destination = getDestinationForRail(selectedRail);
      
      // Pre-security check
      const securityResponse = await fetch('/api/v1/payout/security/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid_token'
        },
        body: JSON.stringify({
          user_id: 'demo_user',
          amount: parseFloat(amount),
          currency: currency,
          rail: selectedRail,
          destination: destination
        })
      });

      const securityResult = await securityResponse.json();
      
      if (!securityResult.success || !securityResult.security_result.approved) {
        setShowSecurityAlert(true);
        setIsProcessing(false);
        return;
      }
      
      // Process payout based on rail
      let payoutResponse;
      
      if (selectedRail === 'local_hub') {
        if (destination.method === 'chapa') {
          payoutResponse = await processChapaPayout(destination);
        } else if (destination.method === 'telebirr') {
          payoutResponse = await processTelebirrPayout(destination);
        } else {
          payoutResponse = await processBankTransfer(destination);
        }
      } else if (selectedRail === 'institutional_hub') {
        if (destination.method === 'payoneer') {
          payoutResponse = await processPayoneerPayout(destination);
        } else {
          payoutResponse = await processSWIFTPayout(destination);
        }
      } else if (selectedRail === 'sovereign_crypto_bridge') {
        payoutResponse = await processCryptoPayout(destination);
      }
      
      if (payoutResponse.success) {
        setPayoutStatus('completed');
        setShowBiometric(false);
      } else {
        setPayoutStatus('failed');
      }
      
    } catch (error) {
      console.error('Payout error:', error);
      setPayoutStatus('failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const processChapaPayout = async (destination) => {
    try {
      const response = await fetch('/api/v1/payout/chapa/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid_token'
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          currency: currency,
          recipient: destination.chapa_phone,
          reference: `DEDAN-${Date.now()}`,
          webhook_url: chapaConfig?.webhook_url,
          biometric_hash: biometricVerified ? 'verified_hash' : null,
          nbe_compliance: true
        })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Chapa payout error:', error);
      return { success: false, error: error.message };
    }
  };

  const processTelebirrPayout = async (destination) => {
    try {
      const response = await fetch('/api/v1/payout/telebirr/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid_token'
        },
        body: JSON.stringify({
          merchant_id: chapaConfig?.merchant_id,
          amount: parseFloat(amount),
          currency: currency,
          recipient: destination.telebirr_number,
          reference: `DEDAN-${Date.now()}`,
          webhook_url: chapaConfig?.webhook_url,
          biometric_hash: biometricVerified ? 'verified_hash' : null
        })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Telebirr payout error:', error);
      return { success: false, error: error.message };
    }
  };

  const processPayoneerPayout = async (destination) => {
    try {
      const response = await fetch('/api/v1/payout/payoneer/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid_token'
        },
        body: JSON.stringify({
          client_id: payoneerConfig?.client_id,
          partner_id: payoneerConfig?.partner_id,
          amount: parseFloat(amount),
          currency: currency,
          recipient_email: destination.email,
          recipient_id: destination.payoneer_id,
          description: `DEDAN Mine Payout - ${Date.now()}`,
          reference: `DEDAN-${Date.now()}`,
          fx_directive: 'FXD/04/2026',
          nbe_compliance: true
        })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Payoneer payout error:', error);
      return { success: false, error: error.message };
    }
  };

  const processCryptoPayout = async (destination) => {
    try {
      const response = await fetch('/api/v1/payout/crypto/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid_token'
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          currency: currency,
          token: destination.token,
          network: destination.network,
          wallet_address: destination.wallet_address,
          reference: `DEDAN-${Date.now()}`,
          nbe_compliance: true,
          nbe_disclaimer: true
        })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Crypto payout error:', error);
      return { success: false, error: error.message };
    }
  };

  const getDestinationForRail = (rail) => {
    switch (rail) {
      case 'local_hub':
        return {
          method: 'chapa',
          chapa_phone: '+251912345678',
          bank_name: 'Commercial Bank of Ethiopia',
          account_number: '100012345678'
        };
      case 'institutional_hub':
        return {
          method: 'payoneer',
          email: 'user@example.com',
          payoneer_id: '123456789'
        };
      case 'sovereign_crypto_bridge':
        return {
          method: 'web3_wallet',
          token: 'USDT',
          network: 'BEP-20',
          wallet_address: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4'
        };
      default:
        return {};
    }
  };

  const handleBiometricVerification = async () => {
    try {
      const response = await fetch('/api/v1/payout/biometric/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid_token'
        },
        body: JSON.stringify({
          biometric_data: {
            face_scan: true,
            fingerprint: true,
            voice_recognition: true
          }
        })
      });
      
      const result = await response.json();
      
      if (result.success && result.verification_result.verified) {
        setBiometricVerified(true);
        setShowBiometric(false);
      }
    } catch (error) {
      console.error('Biometric verification error:', error);
    }
  };

  const handleEmergencyStop = () => {
    setPayoutStatus('emergency_stop');
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white p-4">
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            {t.title}
          </h1>
          <p className="text-gray-300 text-lg">
            {t.subtitle}
          </p>
          <div className="flex justify-center gap-4 mt-4">
            <button
              onClick={() => setLanguage('am')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                language === 'am' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              አማርኛ
            </button>
            <button
              onClick={() => setLanguage('en')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                language === 'en' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              English
            </button>
          </div>
        </motion.div>
      </div>

      {/* Security Alert */}
      <AnimatePresence>
        {showSecurityAlert && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <div className="bg-gray-800 rounded-2xl p-8 max-w-md mx-4 border-2 border-red-500">
              <div className="flex items-center mb-4">
                <AlertCircle className="w-8 h-8 text-red-500 mr-3" />
                <h3 className="text-xl font-bold text-red-400">{t.securityFreeze}</h3>
              </div>
              <p className="text-gray-300 mb-6">
                Suspicious activity detected. Your payout request has been frozen for 24 hours.
                Please complete liveness verification to proceed.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => setShowSecurityAlert(false)}
                  className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => setShowBiometric(true)}
                  className="flex-1 bg-red-600 text-white px-4 py-3 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Verify Identity
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Biometric Verification Modal */}
      <AnimatePresence>
        {showBiometric && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <div className="bg-gray-800 rounded-2xl p-8 max-w-md mx-4">
              <div className="flex items-center mb-6">
                <Shield className="w-8 h-8 text-blue-500 mr-3" />
                <h3 className="text-xl font-bold">{t.biometricVerify}</h3>
              </div>
              <div className="space-y-4">
                <div className="bg-gray-700 rounded-lg p-6 text-center">
                  <div className="w-24 h-24 bg-blue-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <Eye className="w-12 h-12 text-white" />
                  </div>
                  <p className="text-gray-300 mb-4">
                    Please look at the camera for biometric verification
                  </p>
                  <div className="flex justify-center">
                    <div className="animate-pulse flex space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleBiometricVerification}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  {isProcessing ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span className="ml-2">{t.processing}</span>
                    </div>
                  ) : (
                    'Start Verification'
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Payout Rails Selection */}
          {payoutRails.map((rail, index) => (
            <motion.div
              key={rail.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              onClick={() => setSelectedRail(rail.id)}
              className={`relative bg-gray-800 rounded-2xl p-6 cursor-pointer transition-all duration-300 border-2 ${
                selectedRail === rail.id 
                  ? 'border-blue-500 shadow-2xl shadow-blue-500/20' 
                  : 'border-gray-700 hover:border-gray-600 hover:shadow-xl'
              }`}
            >
              <div className={`absolute top-4 right-4 p-3 rounded-lg bg-gradient-to-r ${rail.color}`}>
                <rail.icon className="w-6 h-6 text-white" />
              </div>
              <div className="mt-8">
                <h3 className="text-xl font-bold mb-2">{rail.name}</h3>
                <p className="text-gray-400 text-sm mb-4">{rail.description}</p>
                {rail.biometricRequired && (
                  <div className="flex items-center text-blue-400 text-sm">
                    <Shield className="w-4 h-4 mr-2" />
                    Biometric Required
                  </div>
                )}
                {rail.nbeDisclaimer && (
                  <div className="mt-2 p-2 bg-yellow-900 border border-yellow-600 rounded text-xs text-yellow-300">
                    ⚠️ NBE Compliant - No Birr P2P
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Payout Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-gray-800 rounded-2xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold mb-6">{t.selectRail}</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {t.amount}
              </label>
              <div className="relative">
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                />
                <div className="absolute right-3 top-3 text-gray-400">
                  <Banknote className="w-5 h-5" />
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {t.currency}
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="ETB">ETB - Ethiopian Birr</option>
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="USDT">USDT - Tether</option>
              </select>
            </div>
          </div>

          {/* Tax Calculation Display */}
          {taxCalculation && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="bg-gray-700 rounded-lg p-6 mb-6"
            >
              <h3 className="text-lg font-semibold mb-4 text-blue-400">Tax Calculation</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Gross Amount:</span>
                  <span>{taxCalculation.gross_amount.toFixed(2)} {currency}</span>
                </div>
                <div className="flex justify-between text-red-400">
                  <span>{t.taxDeduction}:</span>
                  <span>-{taxCalculation.total_deductions.toFixed(2)} {currency}</span>
                </div>
                <div className="flex justify-between font-bold text-green-400">
                  <span>{t.netAmount}:</span>
                  <span>{taxCalculation.net_amount.toFixed(2)} {currency}</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={handlePayout}
              disabled={!selectedRail || !amount || isProcessing}
              className={`flex-1 py-4 rounded-lg font-medium transition-all ${
                isProcessing
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white'
              }`}
            >
              {isProcessing ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  <span>{t.processing}</span>
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  {t.confirmPayout}
                </div>
              )}
            </button>
            
            <button
              onClick={handleEmergencyStop}
              className="px-6 py-4 rounded-lg font-medium bg-red-600 hover:bg-red-700 text-white transition-colors"
            >
              <div className="flex items-center">
                <Lock className="w-5 h-5 mr-2" />
                {t.emergencyStop}
              </div>
            </button>
          </div>
        </motion.div>

        {/* Status Display */}
        {payoutStatus && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`rounded-2xl p-8 text-center ${
              payoutStatus === 'completed' 
                ? 'bg-green-900 border-2 border-green-500' 
                : payoutStatus === 'emergency_stop'
                ? 'bg-red-900 border-2 border-red-500'
                : 'bg-yellow-900 border-2 border-yellow-500'
            }`}
          >
            <div className="flex items-center justify-center mb-4">
              {payoutStatus === 'completed' ? (
                <CheckCircle className="w-12 h-12 text-green-400" />
              ) : payoutStatus === 'emergency_stop' ? (
                <Lock className="w-12 h-12 text-red-400" />
              ) : (
                <Clock className="w-12 h-12 text-yellow-400" />
              )}
            </div>
            <h3 className="text-2xl font-bold mb-2">
              {payoutStatus === 'completed' ? t.completed : 
               payoutStatus === 'emergency_stop' ? t.emergencyStop : 
               t.processing}
            </h3>
            <p className="text-gray-300">
              {payoutStatus === 'completed' 
                ? 'Your payout has been processed successfully.'
                : payoutStatus === 'emergency_stop'
                ? 'Emergency stop has been activated.'
                : 'Your payout is being processed.'}
            </p>
          </motion.div>
        )}

        {/* Compliance Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-gray-800 rounded-2xl p-6 border border-gray-700"
        >
          <div className="flex items-center mb-4">
            <Shield className="w-6 h-6 text-green-500 mr-3" />
            <h3 className="text-lg font-semibold">{t.nbeCompliant}</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>NBE 2026 Directives</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>FXD/04/2026 Compliant</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>Satellite Provenance</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>Post-Quantum Security</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PayoutDashboard;
