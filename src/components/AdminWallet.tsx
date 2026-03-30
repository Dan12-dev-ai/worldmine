import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Wallet, 
  TrendingUp, 
  AlertTriangle, 
  ShieldCheck, 
  Clock, 
  CheckCircle, 
  XCircle,
  ArrowUpRight,
  Activity,
  DollarSign,
  Fingerprint,
  Eye,
  EyeOff
} from 'lucide-react';
import { Button } from './ui/button';
import { webauthnService } from '../services/webauthnService';
import { createClient } from '@supabase/supabase-js';

// Types
interface PlatformFinances {
  total_commissions: number;
  total_fees: number;
  available_balance: number;
  pending_withdrawals: number;
  total_withdrawn: number;
  last_updated: string;
}

interface Withdrawal {
  id: string;
  amount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  withdrawal_address: string;
  transaction_hash?: string;
  created_at: string;
  processed_at?: string;
  biometric_verified: boolean;
}

interface AdminDashboardData extends PlatformFinances {
  pending_count: number;
  processing_count: number;
  withdrawals_24h: number;
}

const AdminWallet: React.FC = () => {
  const { t } = useTranslation();
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [withdrawals, setWithdrawals] = useState<Withdrawal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showBalance, setShowBalance] = useState(false);
  const [withdrawalAmount, setWithdrawalAmount] = useState('');
  const [withdrawalAddress, setWithdrawalAddress] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [biometricRequired, setBiometricRequired] = useState(false);
  const [pendingWithdrawalId, setPendingWithdrawalId] = useState<string | null>(null);

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  const ADMIN_USER_ID = process.env.NEXT_PUBLIC_ADMIN_USER_ID || 'YOUR_ADMIN_USER_ID_HERE';

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        setIsAdmin(false);
        return;
      }

      // Check if user is the admin
      const isAdminUser = user.id === ADMIN_USER_ID;
      setIsAdmin(isAdminUser);

      if (isAdminUser) {
        await loadDashboardData();
        await loadWithdrawals();
      }
    } catch (error) {
      console.error('Admin access check failed:', error);
      setIsAdmin(false);
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardData = async () => {
    try {
      const { data, error } = await supabase
        .from('admin_dashboard')
        .select('*')
        .single();

      if (error) throw error;
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const loadWithdrawals = async () => {
    try {
      const { data, error } = await supabase
        .from('withdrawals')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;
      setWithdrawals(data || []);
    } catch (error) {
      console.error('Failed to load withdrawals:', error);
    }
  };

  const handleWithdrawal = async () => {
    if (!withdrawalAmount || parseFloat(withdrawalAmount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    if (!withdrawalAddress.trim()) {
      alert('Please enter a withdrawal address');
      return;
    }

    const amount = parseFloat(withdrawalAmount);
    
    if (dashboardData && amount > dashboardData.available_balance) {
      alert('Insufficient balance');
      return;
    }

    setIsProcessing(true);
    setBiometricRequired(true);

    try {
      // Generate idempotency key
      const idempotencyKey = `withdrawal_${Date.now()}_${Math.random().toString(36).substring(7)}`;

      // Create withdrawal request
      const response = await fetch('/api/admin/withdrawal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
          'X-Idempotency-Key': idempotencyKey,
        },
        body: JSON.stringify({
          amount,
          withdrawal_address: withdrawalAddress.trim(),
          idempotency_key: idempotencyKey,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Withdrawal failed');
      }

      setPendingWithdrawalId(result.withdrawal_id);
      
      // Show biometric verification prompt
      const biometricSuccess = await verifyBiometric();
      
      if (biometricSuccess) {
        await completeWithdrawal(result.withdrawal_id);
        setWithdrawalAmount('');
        setWithdrawalAddress('');
        await loadDashboardData();
        await loadWithdrawals();
      } else {
        // Cancel withdrawal if biometric fails
        await cancelWithdrawal(result.withdrawal_id);
        alert('Biometric verification failed. Withdrawal cancelled.');
      }
    } catch (error) {
      console.error('Withdrawal error:', error);
      alert(error instanceof Error ? error.message : 'Withdrawal failed');
    } finally {
      setIsProcessing(false);
      setBiometricRequired(false);
      setPendingWithdrawalId(null);
    }
  };

  const verifyBiometric = async (): Promise<boolean> => {
    try {
      const result = await webauthnService.authenticate({
        challenge: new Uint8Array(32),
        allowCredentials: [],
        userVerification: 'required',
      });

      return result.success;
    } catch (error) {
      console.error('Biometric verification failed:', error);
      return false;
    }
  };

  const completeWithdrawal = async (withdrawalId: string) => {
    try {
      const response = await fetch(`/api/admin/withdrawal/${withdrawalId}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to complete withdrawal');
      }
    } catch (error) {
      console.error('Complete withdrawal error:', error);
      throw error;
    }
  };

  const cancelWithdrawal = async (withdrawalId: string) => {
    try {
      const response = await fetch(`/api/admin/withdrawal/${withdrawalId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to cancel withdrawal');
      }
    } catch (error) {
      console.error('Cancel withdrawal error:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'processing':
        return <Activity className="w-4 h-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'cancelled':
        return <XCircle className="w-4 h-4 text-gray-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 8,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan"></div>
      </div>
    );
  }

  if (isAdmin === false) {
    // Redirect non-admin users
    useEffect(() => {
      window.location.href = '/';
    }, []);
    return null;
  }

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <p className="text-gray-400">Failed to load admin dashboard</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cyber-dark p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ShieldCheck className="w-8 h-8 text-neon-cyan" />
            <div>
              <h1 className="text-3xl font-bold text-white">Admin Wallet</h1>
              <p className="text-gray-400">Secure Commission Management</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-500">Admin Access</span>
          </div>
        </div>

        {/* Dashboard Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-morphism rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <DollarSign className="w-8 h-8 text-green-500" />
              <button
                onClick={() => setShowBalance(!showBalance)}
                className="text-gray-400 hover:text-white"
              >
                {showBalance ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <h3 className="text-sm text-gray-400 mb-2">Available Balance</h3>
            <p className="text-2xl font-bold text-white">
              {showBalance ? formatCurrency(dashboardData.available_balance) : '••••••••'}
            </p>
          </div>

          <div className="glass-morphism rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-8 h-8 text-blue-500" />
              <span className="text-xs text-blue-500">Total</span>
            </div>
            <h3 className="text-sm text-gray-400 mb-2">Total Commissions</h3>
            <p className="text-2xl font-bold text-white">{formatCurrency(dashboardData.total_commissions)}</p>
          </div>

          <div className="glass-morphism rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <Clock className="w-8 h-8 text-yellow-500" />
              <span className="text-xs text-yellow-500">{dashboardData.pending_count}</span>
            </div>
            <h3 className="text-sm text-gray-400 mb-2">Pending Withdrawals</h3>
            <p className="text-2xl font-bold text-white">{formatCurrency(dashboardData.pending_withdrawals)}</p>
          </div>

          <div className="glass-morphism rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <ArrowUpRight className="w-8 h-8 text-purple-500" />
              <span className="text-xs text-purple-500">{dashboardData.withdrawals_24h}</span>
            </div>
            <h3 className="text-sm text-gray-400 mb-2">24h Withdrawals</h3>
            <p className="text-2xl font-bold text-white">{formatCurrency(dashboardData.total_withdrawn)}</p>
          </div>
        </div>

        {/* Withdrawal Form */}
        <div className="glass-morphism rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center space-x-2">
            <Fingerprint className="w-6 h-6 text-neon-cyan" />
            <span>Secure Withdrawal</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Amount (USD)
              </label>
              <input
                type="number"
                value={withdrawalAmount}
                onChange={(e) => setWithdrawalAmount(e.target.value)}
                placeholder="0.00"
                step="0.00000001"
                min="0"
                max={dashboardData.available_balance}
                className="w-full px-4 py-2 bg-cyber-dark/50 border border-glass-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50"
                disabled={isProcessing}
              />
              <p className="text-xs text-gray-500 mt-1">
                Available: {formatCurrency(dashboardData.available_balance)}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Withdrawal Address
              </label>
              <input
                type="text"
                value={withdrawalAddress}
                onChange={(e) => setWithdrawalAddress(e.target.value)}
                placeholder="Enter withdrawal address"
                className="w-full px-4 py-2 bg-cyber-dark/50 border border-glass-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50"
                disabled={isProcessing}
              />
            </div>
          </div>

          {biometricRequired && (
            <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
              <div className="flex items-center space-x-3">
                <Fingerprint className="w-6 h-6 text-yellow-500 animate-pulse" />
                <div>
                  <p className="text-yellow-500 font-medium">Biometric Verification Required</p>
                  <p className="text-sm text-gray-400">Please complete biometric authentication to proceed</p>
                </div>
              </div>
            </div>
          )}

          <div className="mt-6">
            <Button
              onClick={handleWithdrawal}
              disabled={isProcessing || !withdrawalAmount || !withdrawalAddress}
              className="bg-neon-cyan hover:bg-neon-cyan/80 text-black font-bold"
            >
              {isProcessing ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                  <span>Processing...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Fingerprint className="w-4 h-4" />
                  <span>Withdraw with Biometric</span>
                </div>
              )}
            </Button>
          </div>
        </div>

        {/* Recent Withdrawals */}
        <div className="glass-morphism rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-6">Recent Withdrawals</h2>
          
          <div className="space-y-4">
            {withdrawals.map((withdrawal) => (
              <div key={withdrawal.id} className="flex items-center justify-between p-4 bg-black/30 rounded-lg">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(withdrawal.status)}
                  <div>
                    <p className="text-white font-medium">{formatCurrency(withdrawal.amount)}</p>
                    <p className="text-sm text-gray-400">
                      {new Date(withdrawal.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-400 capitalize">{withdrawal.status}</p>
                  {withdrawal.transaction_hash && (
                    <p className="text-xs text-neon-cyan truncate max-w-[200px]">
                      {withdrawal.transaction_hash}
                    </p>
                  )}
                </div>
              </div>
            ))}
            
            {withdrawals.length === 0 && (
              <div className="text-center py-8">
                <Wallet className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400">No withdrawals yet</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminWallet;
