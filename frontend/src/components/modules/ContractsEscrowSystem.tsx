/**
 * 🧾 CONTRACTS & ESCROW SYSTEM MODULE
 * Smart Contracts, Escrow Status, Transaction History
 */

import React, { useState, useEffect } from 'react'
import { FileText, ShieldCheck, Clock, Activity, Plus, DollarSign, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { EscrowService } from '../../lib/api/escrow'
import { Escrow as ApiEscrow } from '../../lib/types'

interface Escrow {
  id: string
  transaction_id: string
  buyer_id: string
  seller_id: string
  amount: number
  currency: string
  status: 'created' | 'funded' | 'released' | 'disputed' | 'cancelled' | 'refunded'
  created_at: string
  funded_at?: string
  released_at?: string
  dispute_reason?: string
}

export const ContractsEscrowSystem: React.FC = () => {
  const [escrows, setEscrows] = useState<Escrow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newEscrow, setNewEscrow] = useState({
    transaction_id: '',
    buyer_id: '',
    seller_id: '',
    amount: 0,
    currency: 'USD'
  })

  // Fetch escrows from API
  useEffect(() => {
    const fetchEscrows = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await EscrowService.getEscrows()
        setEscrows(response.data.map((apiEscrow: ApiEscrow) => ({
          id: apiEscrow.id,
          transaction_id: apiEscrow.transaction_id,
          buyer_id: apiEscrow.buyer_id,
          seller_id: apiEscrow.seller_id,
          amount: apiEscrow.amount,
          currency: apiEscrow.currency,
          status: apiEscrow.status,
          created_at: apiEscrow.created_at,
          funded_at: apiEscrow.funded_at,
          released_at: apiEscrow.released_at,
          dispute_reason: apiEscrow.dispute_reason
        })))
      } catch (err) {
        setError('Failed to load escrows. Please try again later.')
        console.error('Error fetching escrows:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchEscrows()
  }, [])

  // Handle create escrow
  const handleCreateEscrow = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await EscrowService.createEscrow(newEscrow)
      setEscrows(prev => [...prev, {
        id: response.data.id,
        transaction_id: response.data.transaction_id,
        buyer_id: response.data.buyer_id,
        seller_id: response.data.seller_id,
        amount: response.data.amount,
        currency: response.data.currency,
        status: response.data.status,
        created_at: response.data.created_at
      }])
      setShowCreateForm(false)
      setNewEscrow({ transaction_id: '', buyer_id: '', seller_id: '', amount: 0, currency: 'USD' })
    } catch (err) {
      setError('Failed to create escrow. Please try again.')
      console.error('Error creating escrow:', err)
    } finally {
      setLoading(false)
    }
  }

  // Handle fund escrow
  const handleFundEscrow = async (escrowId: string) => {
    setLoading(true)
    try {
      await EscrowService.fundEscrow(escrowId)
      setEscrows(prev => prev.map(e => 
        e.id === escrowId ? { ...e, status: 'funded' as const, funded_at: new Date().toISOString() } : e
      ))
    } catch (err) {
      setError('Failed to fund escrow. Please try again.')
      console.error('Error funding escrow:', err)
    } finally {
      setLoading(false)
    }
  }

  // Handle release escrow
  const handleReleaseEscrow = async (escrowId: string) => {
    setLoading(true)
    try {
      await EscrowService.releaseEscrow(escrowId)
      setEscrows(prev => prev.map(e => 
        e.id === escrowId ? { ...e, status: 'released' as const, released_at: new Date().toISOString() } : e
      ))
    } catch (err) {
      setError('Failed to release escrow. Please try again.')
      console.error('Error releasing escrow:', err)
    } finally {
      setLoading(false)
    }
  }

  // Handle dispute escrow
  const handleDisputeEscrow = async (escrowId: string, reason: string) => {
    setLoading(true)
    try {
      await EscrowService.disputeEscrow(escrowId, reason)
      setEscrows(prev => prev.map(e => 
        e.id === escrowId ? { ...e, status: 'disputed' as const, dispute_reason: reason } : e
      ))
    } catch (err) {
      setError('Failed to dispute escrow. Please try again.')
      console.error('Error disputing escrow:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'created':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'funded':
        return <DollarSign className="w-4 h-4 text-blue-500" />
      case 'released':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'disputed':
        return <AlertCircle className="w-4 h-4 text-orange-500" />
      case 'cancelled':
      case 'refunded':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return <Activity className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'created':
        return 'bg-yellow-100 text-yellow-800'
      case 'funded':
        return 'bg-blue-100 text-blue-800'
      case 'released':
        return 'bg-green-100 text-green-800'
      case 'disputed':
        return 'bg-orange-100 text-orange-800'
      case 'cancelled':
      case 'refunded':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] font-display">Contracts & Escrow</h1>
          <p className="text-sm text-[var(--text-tertiary)]">Smart contracts and escrow management</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 px-4 py-2 bg-[var(--accent-primary)] text-white rounded-lg hover:bg-[var(--accent-primary)]/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Escrow
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-300 text-red-800 rounded-lg">
          {error}
        </div>
      )}

      {showCreateForm && (
        <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
          <h2 className="text-lg font-semibold mb-4 text-[var(--text-primary)]">Create New Escrow</h2>
          <form onSubmit={handleCreateEscrow} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Transaction ID</label>
              <input
                type="text"
                value={newEscrow.transaction_id}
                onChange={(e) => setNewEscrow({ ...newEscrow, transaction_id: e.target.value })}
                className="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)] text-[var(--text-primary)]"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Buyer ID</label>
              <input
                type="text"
                value={newEscrow.buyer_id}
                onChange={(e) => setNewEscrow({ ...newEscrow, buyer_id: e.target.value })}
                className="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)] text-[var(--text-primary)]"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Seller ID</label>
              <input
                type="text"
                value={newEscrow.seller_id}
                onChange={(e) => setNewEscrow({ ...newEscrow, seller_id: e.target.value })}
                className="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)] text-[var(--text-primary)]"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Amount</label>
                <input
                  type="number"
                  value={newEscrow.amount}
                  onChange={(e) => setNewEscrow({ ...newEscrow, amount: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)] text-[var(--text-primary)]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Currency</label>
                <select
                  value={newEscrow.currency}
                  onChange={(e) => setNewEscrow({ ...newEscrow, currency: e.target.value })}
                  className="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)] text-[var(--text-primary)]"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-[var(--accent-primary)] text-white rounded-lg hover:bg-[var(--accent-primary)]/90 transition-colors disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Escrow'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-[var(--border-subtle)] rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="glass p-6 rounded-xl border border-[var(--border-subtle)]">
        <h2 className="text-lg font-semibold mb-4 text-[var(--text-primary)]">Escrow Transactions</h2>
        
        {loading && escrows.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Activity className="w-8 h-8 text-[var(--text-tertiary)] mx-auto mb-2 animate-spin" />
              <p className="text-sm text-[var(--text-secondary)]">Loading escrows...</p>
            </div>
          </div>
        ) : escrows.length === 0 ? (
          <div className="flex items-center justify-center h-64 border-2 border-dashed border-[var(--border-subtle)] rounded-lg">
            <div className="text-center">
              <ShieldCheck className="w-12 h-12 text-[var(--text-tertiary)] mx-auto mb-3" />
              <p className="text-sm text-[var(--text-secondary)]">No escrows found</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {escrows.map((escrow) => (
              <div key={escrow.id} className="p-4 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-secondary)]">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(escrow.status)}
                    <div>
                      <p className="font-medium text-[var(--text-primary)]">{escrow.transaction_id}</p>
                      <p className="text-xs text-[var(--text-tertiary)]">Created: {new Date(escrow.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(escrow.status)}`}>
                    {escrow.status.toUpperCase()}
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-4 mb-3 text-sm">
                  <div>
                    <p className="text-[var(--text-tertiary)]">Amount</p>
                    <p className="font-medium text-[var(--text-primary)]">{escrow.amount} {escrow.currency}</p>
                  </div>
                  <div>
                    <p className="text-[var(--text-tertiary)]">Buyer</p>
                    <p className="font-medium text-[var(--text-primary)]">{escrow.buyer_id}</p>
                  </div>
                  <div>
                    <p className="text-[var(--text-tertiary)]">Seller</p>
                    <p className="font-medium text-[var(--text-primary)]">{escrow.seller_id}</p>
                  </div>
                </div>

                {escrow.dispute_reason && (
                  <div className="mb-3 p-2 bg-orange-50 border border-orange-200 rounded text-sm text-orange-800">
                    <strong>Dispute:</strong> {escrow.dispute_reason}
                  </div>
                )}

                <div className="flex gap-2">
                  {escrow.status === 'created' && (
                    <button
                      onClick={() => handleFundEscrow(escrow.id)}
                      disabled={loading}
                      className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                    >
                      Fund
                    </button>
                  )}
                  {escrow.status === 'funded' && (
                    <button
                      onClick={() => handleReleaseEscrow(escrow.id)}
                      disabled={loading}
                      className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
                    >
                      Release
                    </button>
                  )}
                  {escrow.status === 'funded' && (
                    <button
                      onClick={() => handleDisputeEscrow(escrow.id, 'Product not as described')}
                      disabled={loading}
                      className="px-3 py-1 text-sm bg-orange-500 text-white rounded hover:bg-orange-600 disabled:opacity-50"
                    >
                      Dispute
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ContractsEscrowSystem
