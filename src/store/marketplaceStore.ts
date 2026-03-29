import { create } from 'zustand'
import { saveTransaction, getAllTransactions, Transaction as DBTransaction } from '../utils/db'

type Transaction = DBTransaction

interface UserProfile {
  companyName: string
  contactName: string
  email: string
  userType: 'seller' | 'buyer'
  kycStatus: 'unverified' | 'pending' | 'verified'
  twoFactorEnabled: boolean
}

interface SecurityLog {
  id: string
  event: string
  time: string
  status: 'secure' | 'warning' | 'critical'
}

interface MarketplaceStore {
  selectedCommodity: string | null
  isMarketplaceModalOpen: boolean
  isRegistrationModalOpen: boolean
  isTransactionModalOpen: boolean
  selectedListing: string | null
  userType: 'seller' | 'buyer' | null
  userProfile: UserProfile | null
  transactions: Transaction[]
  securityLogs: SecurityLog[]
  activeTab: string
  walletBalance: number
  pendingCommission: number
  isLoading: boolean
  
  setSelectedCommodity: (commodity: string | null) => void
  setIsMarketplaceModalOpen: (open: boolean) => void
  setIsRegistrationModalOpen: (open: boolean) => void
  setIsTransactionModalOpen: (open: boolean) => void
  setSelectedListing: (listing: string | null) => void
  setUserType: (type: 'seller' | 'buyer' | null) => void
  setUserProfile: (profile: UserProfile | null) => void
  addTransaction: (transaction: Transaction) => Promise<void>
  loadTransactions: () => Promise<void>
  addSecurityLog: (log: SecurityLog) => void
  setActiveTab: (tab: string) => void
  updateWallet: (amount: number, isCommission?: boolean) => void
  withdrawCommission: () => void
}

const STORAGE_KEY = 'dedan_marketplace_user'

const getInitialUser = (): UserProfile | null => {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) return null
  try {
    const parsed = JSON.parse(stored)
    return {
      ...parsed,
      kycStatus: parsed.kycStatus || 'unverified',
      twoFactorEnabled: parsed.twoFactorEnabled || false
    }
  } catch (e) {
    return null
  }
}

export const useMarketplaceStore = create<MarketplaceStore>((set) => ({
  selectedCommodity: null,
  isMarketplaceModalOpen: false,
  isRegistrationModalOpen: !getInitialUser(),
  isTransactionModalOpen: false,
  selectedListing: null,
  userType: getInitialUser()?.userType || null,
  userProfile: getInitialUser(),
  transactions: [],
  securityLogs: [
    { id: '1', event: 'Quantum-Shield Firewall initialized', time: '10:00:01', status: 'secure' },
    { id: '2', event: 'Multi-sig encryption keys rotated', time: '10:05:22', status: 'secure' },
    { id: '3', event: 'Deep-packet inspection active (Node: 124)', time: '10:15:45', status: 'secure' }
  ],
  activeTab: 'Home',
  walletBalance: 42850.00,
  pendingCommission: 0,
  isLoading: false,
  
  setSelectedCommodity: (commodity: string | null) => set({ selectedCommodity: commodity }),
  setIsMarketplaceModalOpen: (open: boolean) => set({ isMarketplaceModalOpen: open }),
  setIsRegistrationModalOpen: (open: boolean) => set({ isRegistrationModalOpen: open }),
  setIsTransactionModalOpen: (open: boolean) => set({ isTransactionModalOpen: open }),
  setSelectedListing: (listing: string | null) => set({ selectedListing: listing }),
  setUserType: (type: 'seller' | 'buyer' | null) => set({ userType: type }),
  setUserProfile: (profile: UserProfile | null) => {
    if (profile) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
    set({ userProfile: profile, userType: profile?.userType || null })
  },
  loadTransactions: async () => {
    set({ isLoading: true })
    try {
      const transactions = await getAllTransactions()
      set({ transactions: transactions.reverse(), isLoading: false })
    } catch (e) {
      set({ isLoading: false })
    }
  },
  addTransaction: async (transaction: Transaction) => {
    set({ isLoading: true })
    try {
      await saveTransaction(transaction)
      set((state: MarketplaceStore) => ({ 
        transactions: [transaction, ...state.transactions],
        walletBalance: state.walletBalance + (transaction.status === 'Completed' ? transaction.commission : 0),
        isLoading: false
      }))
    } catch (e) {
      set({ isLoading: false })
      console.error('Failed to save transaction:', e)
    }
  },
  addSecurityLog: (log: SecurityLog) => set((state: MarketplaceStore) => ({
    securityLogs: [log, ...state.securityLogs.slice(0, 9)]
  })),
  setActiveTab: (tab: string) => set({ activeTab: tab }),
  updateWallet: (amount: number, isCommission = false) => set((state: MarketplaceStore) => ({
    walletBalance: state.walletBalance + (isCommission ? 0 : amount),
    pendingCommission: state.pendingCommission + (isCommission ? amount : 0)
  })),
  withdrawCommission: () => set((state: MarketplaceStore) => {
    if (state.pendingCommission <= 0) return state
    const withdrawalAmount = state.pendingCommission
    return {
      walletBalance: state.walletBalance + withdrawalAmount,
      pendingCommission: 0,
      securityLogs: [
        { 
          id: Math.random().toString(36).substr(2, 9), 
          event: `Commission withdrawal of $${withdrawalAmount.toLocaleString()} processed to main wallet`, 
          time: new Date().toLocaleTimeString(), 
          status: 'secure' 
        },
        ...state.securityLogs
      ]
    }
  }),
}))
