import React, { useState } from 'react'
import { X, Shield, ShieldCheck, Lock, AlertCircle, CheckCircle } from 'lucide-react'
import { Button } from './ui/button'
import { listings } from '../data/commodities'
import { useMarketplaceStore } from '../store/marketplaceStore'

const TransactionModal: React.FC = () => {
  const { selectedListing, setIsTransactionModalOpen, addTransaction, addSecurityLog } = useMarketplaceStore()
  const [isProcessing, setIsProcessing] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [step, setStep] = useState<'details' | '2fa' | 'escrow'>('details')
  const [twoFactorCode, setTwoFactorCode] = useState('')

  const listing = listings.find(l => l.id === selectedListing)

  if (!listing) return null

  const handleStartTransaction = () => {
    setStep('2fa')
    addSecurityLog({
      id: Math.random().toString(),
      event: `2FA challenge initiated for ${listing.title}`,
      time: new Date().toLocaleTimeString(),
      status: 'secure'
    })
  }

  const handleVerify2FA = () => {
    if (twoFactorCode.length === 6) {
      setStep('escrow')
      addSecurityLog({
        id: Math.random().toString(),
        event: `2FA verified. Escrow wallet created.`,
        time: new Date().toLocaleTimeString(),
        status: 'secure'
      })
    }
  }

  const handleCompleteEscrow = async () => {
    setIsProcessing(true)
    
    // Simulate smart contract execution
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    const commission = listing.price * 0.02
    
    // Add to history
    addTransaction({
      id: Math.random().toString(36).substr(2, 9),
      listingTitle: listing.title,
      amount: listing.price,
      date: new Date().toLocaleDateString(),
      status: 'Completed',
      commission: commission
    })

    addSecurityLog({
      id: Math.random().toString(),
      event: `Smart contract ${Math.random().toString(36).substr(2, 6)} executed successfully. Commission of $${commission.toFixed(2)} paid.`,
      time: new Date().toLocaleTimeString(),
      status: 'secure'
    })

    setIsProcessing(false)
    setIsComplete(true)
    
    // Auto close after showing success
    setTimeout(() => {
      setIsTransactionModalOpen(false)
      setIsComplete(false)
    }, 3000)
  }

  const handleClose = () => {
    if (!isProcessing) {
      setIsTransactionModalOpen(false)
      setIsComplete(false)
      setStep('details')
    }
  }

  if (isComplete) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="glass-morphism border border-neon-emerald/30 rounded-2xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-neon-emerald/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-neon-emerald" />
          </div>
          
          <h2 className="text-2xl font-bold text-white mb-4">Transaction Secured!</h2>
          
          <div className="space-y-3 mb-6">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Commission Earned:</span>
              <span className="text-neon-emerald font-semibold">+${(listing.price * 0.02).toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Security Audit:</span>
              <span className="text-neon-emerald font-semibold flex items-center">
                <ShieldCheck className="w-4 h-4 mr-1" /> Passed
              </span>
            </div>
          </div>
          
          <p className="text-gray-300 text-sm">
            Funds have been securely transferred via smart contract
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="glass-morphism border border-glass-white/20 rounded-3xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto relative">
        <button
          onClick={handleClose}
          className="absolute top-6 right-6 text-gray-500 hover:text-white transition-colors"
          disabled={isProcessing}
        >
          <X className="w-6 h-6" />
        </button>

        {step === 'details' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white font-orbitron flex items-center">
              <Shield className="w-6 h-6 text-neon-cyan mr-3" />
              Secure Smart Contract
            </h2>

            <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
              <div className="flex items-center space-x-4 mb-4">
                <img src={listing.image} className="w-16 h-16 rounded-lg object-cover" />
                <div>
                  <h3 className="text-lg font-bold text-white">{listing.title}</h3>
                  <p className="text-sm text-gray-400">${listing.price.toLocaleString()} per ton</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
                <div className="flex items-center text-xs text-gray-400">
                  <Lock className="w-3 h-3 mr-1 text-neon-emerald" />
                  Encrypted Connection
                </div>
                <div className="flex items-center text-xs text-gray-400">
                  <ShieldCheck className="w-3 h-3 mr-1 text-neon-cyan" />
                  Anti-Fraud Active
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center p-3 bg-neon-cyan/5 border border-neon-cyan/20 rounded-xl">
                <AlertCircle className="w-5 h-5 text-neon-cyan mr-3 flex-shrink-0" />
                <p className="text-xs text-gray-300">
                  By proceeding, you initiate a multi-sig smart contract. Funds will be held in escrow until delivery is verified.
                </p>
              </div>
              <Button onClick={handleStartTransaction} variant="cyber" className="w-full h-12 text-base font-bold uppercase tracking-widest">
                Initiate Secure Purchase
              </Button>
            </div>
          </div>
        )}

        {step === '2fa' && (
          <div className="space-y-8 text-center py-6">
            <div className="w-16 h-16 bg-neon-cyan/10 rounded-full flex items-center justify-center mx-auto">
              <Lock className="w-8 h-8 text-neon-cyan" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white font-orbitron mb-2">Verification Required</h2>
              <p className="text-gray-400">Enter the 6-digit code from your security app</p>
            </div>
            <input
              type="text"
              maxLength={6}
              value={twoFactorCode}
              onChange={(e) => setTwoFactorCode(e.target.value)}
              className="w-full max-w-[200px] mx-auto text-center text-4xl font-bold bg-transparent border-b-2 border-neon-cyan text-white focus:outline-none tracking-[1rem]"
              placeholder="000000"
            />
            <Button onClick={handleVerify2FA} disabled={twoFactorCode.length !== 6} variant="cyber" className="w-full h-12">
              Verify Identity
            </Button>
          </div>
        )}

        {step === 'escrow' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white font-orbitron">Escrow Bridge</h2>
              <div className="flex items-center text-neon-emerald text-xs">
                <div className="w-2 h-2 bg-neon-emerald rounded-full animate-pulse mr-2" />
                Secure Protocol Active
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-white/5 rounded-xl border border-white/10 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Escrow Address</span>
                  <span className="text-white font-mono">0x7d...f9a2</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Transaction ID</span>
                  <span className="text-white font-mono">TXN-{Math.random().toString(36).substr(2, 6)}</span>
                </div>
              </div>

              <div className="p-4 border border-neon-cyan/30 rounded-xl bg-neon-cyan/5">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-bold text-white">Security Audit Status</h4>
                  <div className="flex items-center space-x-1 bg-neon-emerald/20 border border-neon-emerald/40 px-2 py-0.5 rounded-full">
                    <ShieldCheck className="w-3 h-3 text-neon-emerald" />
                    <span className="text-[10px] text-neon-emerald font-black uppercase tracking-widest">Safe</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center text-xs text-neon-emerald">
                    <CheckCircle className="w-3 h-3 mr-2" />
                    Seller Reputation & KYC Verified
                  </div>
                  <div className="flex items-center text-xs text-neon-emerald">
                    <CheckCircle className="w-3 h-3 mr-2" />
                    Commodity Origin & Logistics Validated
                  </div>
                  <div className="flex items-center text-xs text-neon-emerald">
                    <CheckCircle className="w-3 h-3 mr-2" />
                    AI Anti-Fraud System Monitoring Active
                  </div>
                </div>
              </div>

              <Button onClick={handleCompleteEscrow} disabled={isProcessing} variant="cyber" className="w-full h-14 relative">
                {isProcessing ? (
                  <div className="flex items-center">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3" />
                    Executing Smart Contract...
                  </div>
                ) : (
                  'Authorize & Deposit Funds'
                )}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TransactionModal
