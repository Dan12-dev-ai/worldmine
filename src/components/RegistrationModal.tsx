import React, { useState } from 'react'
import { X, ChevronDown } from 'lucide-react'
import { Button } from './ui/button'
import { useMarketplaceStore } from '../store/marketplaceStore'

const RegistrationModal: React.FC = () => {
  const { userType, setUserType, setIsRegistrationModalOpen, setUserProfile } = useMarketplaceStore()
  const [formData, setFormData] = useState({
    companyName: '',
    contactName: '',
    email: '',
    phone: '',
    location: '',
    taxId: '',
    bankDetails: '',
    materialsOffered: '',
    materialsWanted: ''
  })

  const handleUserTypeSelect = (type: 'seller' | 'buyer') => {
    setUserType(type)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!userType) return

    setUserProfile({
      companyName: formData.companyName,
      contactName: formData.contactName,
      email: formData.email,
      userType: userType,
      kycStatus: 'pending',
      twoFactorEnabled: true
    })
    
    setIsRegistrationModalOpen(false)
  }

  const handleClose = () => {
    setIsRegistrationModalOpen(false)
  }

  if (!userType) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="glass-morphism border border-glass-white/20 rounded-2xl p-8 max-w-md w-full">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white font-orbitron">
              Join DEDAN
            </h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <p className="text-gray-300 mb-8 text-center">
            Are you a Seller or Buyer?
          </p>

          <div className="space-y-4">
            <Button
              onClick={() => handleUserTypeSelect('seller')}
              variant="cyber"
              className="w-full h-14 text-lg font-semibold"
            >
              Seller
            </Button>
            <Button
              onClick={() => handleUserTypeSelect('buyer')}
              variant="gold"
              className="w-full h-14 text-lg font-semibold"
            >
              Buyer
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-50 p-2 sm:p-4">
      <div className="glass-morphism border border-glass-white/20 rounded-2xl sm:rounded-3xl p-4 sm:p-8 max-w-4xl w-full max-h-[95vh] overflow-y-auto relative bg-cyber-dark/80 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 sm:top-6 sm:right-6 text-gray-500 hover:text-white transition-colors z-10"
        >
          <X className="w-5 h-5 sm:w-6 sm:h-6" />
        </button>

        <h2 className="text-xl sm:text-2xl font-bold text-white font-orbitron mb-6 sm:mb-8 tracking-tight pr-8">
          New User Registration - <span className="text-neon-cyan">Are you a Seller or Buyer?</span>
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            {/* Left Column */}
            <div className="space-y-6">
              <div className="relative group">
                <input
                  type="text"
                  required
                  value={formData.companyName}
                  onChange={(e) => setFormData({...formData, companyName: e.target.value})}
                  className="w-full bg-cyber-navy/40 border border-glass-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 transition-all"
                  placeholder="Company Name"
                />
              </div>

              <div className="relative group">
                <textarea
                  required
                  value={userType === 'seller' ? formData.materialsOffered : formData.materialsWanted}
                  onChange={(e) => userType === 'seller' 
                    ? setFormData({...formData, materialsOffered: e.target.value})
                    : setFormData({...formData, materialsWanted: e.target.value})
                  }
                  className="w-full bg-cyber-navy/40 border border-glass-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 transition-all min-h-[120px]"
                  placeholder={userType === 'seller' ? "Materials Offered" : "Materials Wanted"}
                />
                <button type="button" className="absolute right-4 bottom-4 text-neon-cyan hover:scale-110 transition-transform">
                  <span className="text-xl">+</span>
                </button>
              </div>

              <div className="relative group">
                <input
                  type="text"
                  required
                  value={formData.taxId}
                  onChange={(e) => setFormData({...formData, taxId: e.target.value})}
                  className="w-full bg-cyber-navy/40 border border-glass-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 transition-all"
                  placeholder="Tax ID"
                />
                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <div className="relative group">
                <textarea
                  required
                  value={formData.bankDetails}
                  onChange={(e) => setFormData({...formData, bankDetails: e.target.value})}
                  className="w-full bg-cyber-navy/40 border border-glass-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 transition-all min-h-[100px]"
                  placeholder="Bank Details"
                />
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              <div className="relative group">
                <input
                  type="text"
                  required
                  className="w-full bg-cyber-navy/40 border border-glass-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 transition-all"
                  placeholder="Contact Info"
                />
                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <div className="relative group">
                <input
                  type="text"
                  required
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="w-full bg-cyber-navy/40 border border-glass-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 transition-all"
                  placeholder="Location"
                />
                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <div className="relative group">
                <textarea
                  required
                  className="w-full bg-cyber-navy/40 border border-glass-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 transition-all min-h-[100px]"
                  placeholder="Bank Details"
                />
                <ChevronDown className="absolute right-4 top-4 w-4 h-4 text-gray-500" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Button type="button" variant="ghost" className="h-12 rounded-xl border border-glass-white/20 text-gray-400 hover:text-white">
                  Document Upload
                </Button>
                <Button type="submit" variant="cyber" className="h-12 rounded-xl bg-neon-emerald/20 border-neon-emerald/50 text-neon-emerald hover:bg-neon-emerald/30">
                  Document Upload
                </Button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RegistrationModal
