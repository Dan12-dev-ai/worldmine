/**
 * 👤 USER CONTROL CENTER MODULE
 * Profile, KYC, Wallet, Security Settings
 */

import React, { useState, useEffect } from 'react'
import { User, Shield, Wallet, Activity, CreditCard, ArrowUpRight, ArrowDownRight, Lock, Bell } from 'lucide-react'
import { WalletService } from '../../lib/api/wallet'
import { AuthService } from '../../lib/api/auth'
import { Wallet as ApiWallet, Transaction as ApiTransaction } from '../../lib/types'

interface Wallet {
  id: string
  user_id: string
  balance: number
  currency: string
  is_active: boolean
}

interface Transaction {
  id: string
  wallet_id: string
  type: 'deposit' | 'withdrawal' | 'transfer' | 'escrow' | 'refund'
  amount: number
  currency: string
  status: 'pending' | 'completed' | 'failed' | 'cancelled'
  created_at: string
}

interface UserProfile {
  id: string
  email: string
  first_name: string
  last_name: string
  phone: string
  is_verified: boolean
  created_at: string
}

export const UserControlCenter: React.FC = () => {
  const [wallets, setWallets] = useState<Wallet[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'profile' | 'wallet' | 'security'>('profile')

  // Fetch user data from API
  useEffect(() => {
    const fetchUserData = async () => {
      setLoading(true)
      setError(null)
      try {
        // Fetch user profile
        const userResponse = await AuthService.getCurrentUser()
        setUserProfile({
          id: userResponse.data.id,
          email: userResponse.data.email,
          first_name: userResponse.data.first_name || '',
          last_name: userResponse.data.last_name || '',
          phone: userResponse.data.phone || '',
          is_verified: userResponse.data.is_verified,
          created_at: userResponse.data.created_at
        })

        // Fetch wallets
        const walletsResponse = await WalletService.getWallets()
        setWallets(walletsResponse.data.map((apiWallet: ApiWallet) => ({
          id: apiWallet.id,
          user_id: apiWallet.user_id,
          balance: apiWallet.balance,
          currency: apiWallet.currency,
          is_active: apiWallet.is_active
        })))

        // Fetch transactions (from first wallet if available)
        if (walletsResponse.data.length > 0) {
          const transactionsResponse = await WalletService.getTransactions({ wallet_id: walletsResponse.data[0].id })
          setTransactions(transactionsResponse.data.map((apiTx: ApiTransaction) => ({
            id: apiTx.id,
            wallet_id: apiTx.wallet_id,
            type: apiTx.type,
            amount: apiTx.amount,
            currency: apiTx.currency,
            status: apiTx.status,
            created_at: apiTx.created_at
          })))
        }
      } catch (err) {
        setError('Failed to load user data. Please try again later.')
        console.error('Error fetching user data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchUserData()
  }, [])
  const getVerificationStatusColor = (isVerified: boolean) => {
    return isVerified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
  }

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'deposit':
        return <ArrowDownRight className="w-4 h-4 text-green-500" />
      case 'withdrawal':
        return <ArrowUpRight className="w-4 h-4 text-red-500" />
      case 'transfer':
        return <Activity className="w-4 h-4 text-blue-500" />
      default:
        return <CreditCard className="w-4 h-4 text-gray-500" />
    }
  }

  const getTransactionColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600'
      case 'pending':
        return 'text-yellow-600'
      case 'failed':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">User Control Center</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Profile, identity, and wallet management</p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-300 text-red-800 rounded-lg">
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-[var(--border-subtle)]">
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'profile'
              ? 'text-[var(--accent-primary)] border-b-2 border-[var(--accent-primary)]'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          <User className="w-4 h-4 inline mr-2" />
          Profile
        </button>
        <button
          onClick={() => setActiveTab('wallet')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'wallet'
              ? 'text-[var(--accent-primary)] border-b-2 border-[var(--accent-primary)]'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          <Wallet className="w-4 h-4 inline mr-2" />
          Wallet
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'security'
              ? 'text-[var(--accent-primary)] border-b-2 border-[var(--accent-primary)]'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          <Shield className="w-4 h-4 inline mr-2" />
          Security
        </button>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="space-y-6">
          {loading && !userProfile ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <Activity className="w-8 h-8 text-[var(--text-tertiary)] mx-auto mb-2 animate-spin" />
                <p className="text-sm text-[var(--text-secondary)]">Loading profile...</p>
              </div>
            </div>
          ) : userProfile ? (
            <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
              <h2 className="text-lg font-semibold mb-4 text-[var(--text-primary)]">Profile Information</h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-tertiary)] mb-1">Full Name</label>
                  <p className="text-[var(--text-primary)]">{userProfile.first_name} {userProfile.last_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-tertiary)] mb-1">Email</label>
                  <p className="text-[var(--text-primary)]">{userProfile.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-tertiary)] mb-1">Phone</label>
                  <p className="text-[var(--text-primary)]">{userProfile.phone || 'Not set'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-tertiary)] mb-1">Verification Status</label>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getVerificationStatusColor(userProfile.is_verified)}`}>
                    {userProfile.is_verified ? 'VERIFIED' : 'PENDING'}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-tertiary)] mb-1">Member Since</label>
                  <p className="text-[var(--text-primary)]">{new Date(userProfile.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass p-8 rounded-xl border border-[var(--border-subtle)]">
              <div className="flex items-center justify-center h-64 border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
                <div className="text-center">
                  <User className="w-12 h-12 text-[var(--text-tertiary)] mx-auto mb-3" />
                  <p className="text-sm text-[var(--text-secondary)]">No profile data available</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Wallet Tab */}
      {activeTab === 'wallet' && (
        <div className="space-y-6">
          {/* Wallet Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {wallets.map((wallet) => (
              <div key={wallet.id} className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
                <div className="flex items-center justify-between mb-4">
                  <Wallet className="w-8 h-8 text-[var(--accent-primary)]" />
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    wallet.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {wallet.is_active ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                </div>
                <p className="text-2xl font-bold text-[var(--text-primary)]">
                  {wallet.balance.toLocaleString()} {wallet.currency}
                </p>
                <p className="text-sm text-[var(--text-tertiary)]">Available Balance</p>
              </div>
            ))}
            {wallets.length === 0 && (
              <div className="glass p-6 rounded-xl border border-dashed border-[var(--border-subtle)]">
                <div className="flex items-center justify-center h-32">
                  <div className="text-center">
                    <Wallet className="w-8 h-8 text-[var(--text-tertiary)] mx-auto mb-2" />
                    <p className="text-sm text-[var(--text-secondary)]">No wallets found</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Transaction History */}
          <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
            <h2 className="text-lg font-semibold mb-4 text-[var(--text-primary)]">Recent Transactions</h2>
            
            {loading && transactions.length === 0 ? (
              <div className="flex items-center justify-center h-32">
                <div className="text-center">
                  <Activity className="w-6 h-6 text-[var(--text-tertiary)] mx-auto mb-2 animate-spin" />
                  <p className="text-sm text-[var(--text-secondary)]">Loading transactions...</p>
                </div>
              </div>
            ) : transactions.length === 0 ? (
              <div className="flex items-center justify-center h-32 border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
                <div className="text-center">
                  <Activity className="w-8 h-8 text-[var(--text-tertiary)] mx-auto mb-3" />
                  <p className="text-sm text-[var(--text-secondary)]">No transactions found</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {transactions.map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between p-3 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)]">
                    <div className="flex items-center gap-3">
                      {getTransactionIcon(tx.type)}
                      <div>
                        <p className="font-medium text-[var(--text-primary)] capitalize">{tx.type}</p>
                        <p className="text-xs text-[var(--text-tertiary)]">{new Date(tx.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${tx.type === 'deposit' ? 'text-green-600' : 'text-red-600'}`}>
                        {tx.type === 'deposit' ? '+' : '-'}{tx.amount} {tx.currency}
                      </p>
                      <p className={`text-xs ${getTransactionColor(tx.status)}`}>
                        {tx.status.toUpperCase()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="space-y-6">
          <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
            <h2 className="text-lg font-semibold mb-4 text-[var(--text-primary)]">Security Settings</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-[var(--border-subtle)] rounded-lg">
                <div className="flex items-center gap-3">
                  <Lock className="w-5 h-5 text-[var(--accent-primary)]" />
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">Password</p>
                    <p className="text-sm text-[var(--text-tertiary)]">Manage your password</p>
                  </div>
                </div>
                <button className="px-4 py-2 text-sm border border-[var(--border-subtle)] rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] transition-colors">
                  Change
                </button>
              </div>

              <div className="flex items-center justify-between p-4 border border-[var(--border-subtle)] rounded-lg">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-[var(--accent-primary)]" />
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">Two-Factor Authentication</p>
                    <p className="text-sm text-[var(--text-tertiary)]">Add an extra layer of security</p>
                  </div>
                </div>
                <button className="px-4 py-2 text-sm border border-[var(--border-subtle)] rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] transition-colors">
                  Enable
                </button>
              </div>

              <div className="flex items-center justify-between p-4 border border-[var(--border-subtle)] rounded-lg">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-[var(--accent-primary)]" />
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">Notifications</p>
                    <p className="text-sm text-[var(--text-tertiary)]">Manage security alerts</p>
                  </div>
                </div>
                <button className="px-4 py-2 text-sm border border-[var(--border-subtle)] rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] transition-colors">
                  Configure
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserControlCenter
