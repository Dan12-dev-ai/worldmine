import { createClient } from '@supabase/supabase-js';
import { WebAuthnService } from './webauthnService';

// Types
export interface SecureWithdrawalRequest {
  amount: number;
  currency: string;
  address: string;
  addressType: 'bank_account' | 'crypto_wallet';
  idempotencyKey: string;
  totpToken?: string;
}

export interface WithdrawalResponse {
  success: boolean;
  transactionId?: string;
  error?: string;
  securityHold?: {
    type: string;
    holdUntil: string;
    reason: string;
  };
  requiresApproval?: {
    approvalUrl: string;
    expiresAt: string;
  };
}

export interface SecurityCheckResult {
  passed: boolean;
  reason?: string;
  requiresBiometric?: boolean;
  requiresTOTP?: boolean;
  requiresApproval?: boolean;
}

export interface DeviceFingerprint {
  fingerprint: string;
  userAgent: string;
  ipAddress: string;
  geolocation?: {
    country: string;
    city: string;
    coordinates: [number, number];
  };
}

export interface BiometricVerification {
  success: boolean;
  hash: string;
  credentialId: string;
}

export interface TOTPVerification {
  success: boolean;
  token: string;
}

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

export class SecureWithdrawalService {
  private static instance: SecureWithdrawalService;
  private deviceFingerprint: DeviceFingerprint | null = null;

  private constructor() {}

  static getInstance(): SecureWithdrawalService {
    if (!SecureWithdrawalService.instance) {
      SecureWithdrawalService.instance = new SecureWithdrawalService();
    }
    return SecureWithdrawalService.instance;
  }

  // Generate device fingerprint
  async generateDeviceFingerprint(): Promise<DeviceFingerprint> {
    if (this.deviceFingerprint) {
      return this.deviceFingerprint;
    }

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillText('Device fingerprint', 2, 2);
    }

    const fingerprintData = [
      navigator.userAgent,
      navigator.language,
      screen.width + 'x' + screen.height,
      new Date().getTimezoneOffset(),
      canvas.toDataURL(),
      (navigator as any).hardwareConcurrency || 'unknown',
      (navigator as any).deviceMemory || 'unknown',
      navigator.platform
    ].join('|');

    // Hash the fingerprint
    const encoder = new TextEncoder();
    const data = encoder.encode(fingerprintData);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const fingerprint = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    // Get geolocation
    let geolocation;
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });
      
      geolocation = {
        country: 'ET', // Would use geocoding service
        city: 'Addis Ababa',
        coordinates: [position.coords.longitude, position.coords.latitude] as [number, number]
      };
    } catch (error) {
      console.warn('Geolocation not available:', error);
    }

    this.deviceFingerprint = {
      fingerprint,
      userAgent: navigator.userAgent,
      ipAddress: await this.getClientIP(),
      geolocation
    };

    return this.deviceFingerprint;
  }

  // Get client IP (placeholder - would use proper IP service)
  private async getClientIP(): Promise<string> {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch (error) {
      console.warn('Could not get client IP:', error);
      return '127.0.0.1';
    }
  }

  // Pre-flight security checks
  async performPreFlightChecks(userId: string): Promise<SecurityCheckResult> {
    try {
      const fingerprint = await this.generateDeviceFingerprint();

      // Check if user is authenticated
      const { data: user } = await supabase.auth.getUser();
      if (!user.user || user.user.id !== userId) {
        return { passed: false, reason: 'User not authenticated' };
      }

      // Check user's security settings
      const { data: settings, error } = await supabase
        .from('security_settings')
        .select('*')
        .eq('user_id', userId)
        .single();

      if (error || !settings) {
        return { passed: false, reason: 'Security settings not found' };
      }

      const result: SecurityCheckResult = { passed: true };

      // Check if biometric re-auth is required
      if (settings.require_biometric_reauth) {
        result.requiresBiometric = true;
      }

      // Check if TOTP is required
      if (settings.require_totp && settings.totp_enabled) {
        result.requiresTOTP = true;
      }

      // Check if trusted device is required
      if (settings.trusted_device_required) {
        const { data: device } = await supabase
          .from('trusted_devices')
          .select('id')
          .eq('user_id', userId)
          .eq('fingerprint', fingerprint.fingerprint)
          .eq('is_active', true)
          .single();

        if (!device) {
          return { 
            passed: false, 
            reason: 'Trusted device required',
            requiresBiometric: true
          };
        }
      }

      return result;
    } catch (error) {
      console.error('Pre-flight check error:', error);
      return { passed: false, reason: 'Pre-flight check failed' };
    }
  }

  // Perform biometric verification
  async performBiometricVerification(): Promise<BiometricVerification> {
    try {
      const challenge = new Uint8Array(32);
      crypto.getRandomValues(challenge);

      // For now, return a mock verification
      // In production, integrate with actual WebAuthn API
      const hash = Array.from(challenge).map(b => b.toString(16).padStart(2, '0')).join('');

      return {
        success: true,
        hash,
        credentialId: 'mock-credential-id'
      };
    } catch (error) {
      console.error('Biometric verification error:', error);
      return {
        success: false,
        hash: '',
        credentialId: ''
      };
    }
  }

  // Perform TOTP verification
  async performTOTPVerification(token: string): Promise<TOTPVerification> {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) {
        return { success: false, token: '' };
      }

      // Verify TOTP token with backend
      const { data, error } = await supabase.functions.invoke('verify-totp', {
        body: {
          userId: user.data.user.id,
          token
        }
      });

      if (error || !data?.valid) {
        return { success: false, token };
      }

      return {
        success: true,
        token
      };
    } catch (error) {
      console.error('TOTP verification error:', error);
      return {
        success: false,
        token: ''
      };
    }
  }

  // Process secure withdrawal
  async processWithdrawal(
    userId: string,
    request: SecureWithdrawalRequest
  ): Promise<WithdrawalResponse> {
    try {
      const fingerprint = await this.generateDeviceFingerprint();

      // Get biometric hash
      const biometricResult = await this.performBiometricVerification();
      if (!biometricResult.success) {
        return {
          success: false,
          error: 'Biometric verification failed'
        };
      }

      // Prepare withdrawal request
      const withdrawalRequest = {
        userId,
        amount: request.amount,
        currency: request.currency,
        address: request.address,
        addressType: request.addressType,
        idempotencyKey: request.idempotencyKey,
        deviceFingerprint: fingerprint.fingerprint,
        biometricHash: biometricResult.hash,
        totpToken: request.totpToken,
        ipAddress: fingerprint.ipAddress,
        userAgent: fingerprint.userAgent,
        geolocation: fingerprint.geolocation
      };

      // Call secure withdrawal function
      const { data, error } = await supabase.functions.invoke('handleSecureWithdrawal', {
        body: withdrawalRequest
      });

      if (error) {
        console.error('Withdrawal processing error:', error);
        return {
          success: false,
          error: error.message || 'Withdrawal processing failed'
        };
      }

      return data as WithdrawalResponse;
    } catch (error) {
      console.error('Secure withdrawal error:', error);
      return {
        success: false,
        error: 'Secure withdrawal failed'
      };
    }
  }

  // Check if address is whitelisted
  async isAddressWhitelisted(userId: string, address: string): Promise<boolean> {
    try {
      const { data, error } = await supabase
        .from('whitelisted_addresses')
        .select('id')
        .eq('user_id', userId)
        .eq('address', address)
        .eq('is_active', true)
        .single();

      if (error || !data) {
        return false;
      }

      return true;
    } catch (error) {
      console.error('Address whitelist check error:', error);
      return false;
    }
  }

  // Check daily withdrawal limit
  async checkDailyLimit(userId: string, amount: number, currency: string = 'USD'): Promise<{
    withinLimit: boolean;
    currentTotal: number;
    limit: number;
    requiresApproval: boolean;
  }> {
    try {
      const { data, error } = await supabase.rpc('check_daily_withdrawal_limit', {
        p_user_id: userId,
        p_amount: amount,
        p_currency: currency
      });

      if (error || !data) {
        throw error;
      }

      const result = data[0];
      return {
        withinLimit: result.within_limit,
        currentTotal: parseFloat(result.current_daily_total),
        limit: parseFloat(result.daily_limit),
        requiresApproval: result.requires_approval
      };
    } catch (error) {
      console.error('Daily limit check error:', error);
      return {
        withinLimit: false,
        currentTotal: 0,
        limit: 0,
        requiresApproval: true
      };
    }
  }

  // Get security holds for user
  async getSecurityHolds(userId: string): Promise<Array<{
    id: string;
    reason: string;
    amount?: number;
    currency?: string;
    address?: string;
    holdUntil: string;
    isActive: boolean;
    createdAt: string;
  }>> {
    try {
      const { data, error } = await supabase
        .from('security_holds')
        .select('*')
        .eq('user_id', userId)
        .eq('is_active', true)
        .order('created_at', { ascending: false });

      if (error) {
        throw error;
      }

      return data || [];
    } catch (error) {
      console.error('Get security holds error:', error);
      return [];
    }
  }

  // Get whitelisted addresses for user
  async getWhitelistedAddresses(userId: string): Promise<Array<{
    id: string;
    type: 'bank_account' | 'crypto_wallet';
    name: string;
    address: string;
    bankName?: string;
    accountNumber?: string;
    walletType?: string;
    isActive: boolean;
    addedAt: string;
    cooldownUntil?: string;
  }>> {
    try {
      const { data, error } = await supabase
        .from('whitelisted_addresses')
        .select('*')
        .eq('user_id', userId)
        .order('added_at', { ascending: false });

      if (error) {
        throw error;
      }

      return data || [];
    } catch (error) {
      console.error('Get whitelisted addresses error:', error);
      return [];
    }
  }

  // Get trusted devices for user
  async getTrustedDevices(userId: string): Promise<Array<{
    id: string;
    name: string;
    fingerprint: string;
    userAgent: string;
    ipAddress: string;
    location: {
      country: string;
      city: string;
      coordinates: [number, number];
    };
    firstSeen: string;
    lastUsed: string;
    isActive: boolean;
    isVerified: boolean;
  }>> {
    try {
      const { data, error } = await supabase
        .from('trusted_devices')
        .select('*')
        .eq('user_id', userId)
        .order('last_used', { ascending: false });

      if (error) {
        throw error;
      }

      return data || [];
    } catch (error) {
      console.error('Get trusted devices error:', error);
      return [];
    }
  }

  // Add trusted device
  async addTrustedDevice(userId: string, deviceName: string): Promise<boolean> {
    try {
      const fingerprint = await this.generateDeviceFingerprint();

      // Require biometric verification
      const biometricResult = await this.performBiometricVerification();
      if (!biometricResult.success) {
        return false;
      }

      const { error } = await supabase
        .from('trusted_devices')
        .insert({
          user_id: userId,
          name: deviceName,
          fingerprint: fingerprint.fingerprint,
          user_agent: fingerprint.userAgent,
          ip_address: fingerprint.ipAddress,
          location: fingerprint.geolocation,
          first_seen: new Date().toISOString(),
          last_used: new Date().toISOString(),
          is_active: true,
          is_verified: true
        });

      return !error;
    } catch (error) {
      console.error('Add trusted device error:', error);
      return false;
    }
  }

  // Add whitelisted address
  async addWhitelistedAddress(
    userId: string,
    addressData: {
      type: 'bank_account' | 'crypto_wallet';
      name: string;
      address: string;
      bankName?: string;
      accountNumber?: string;
      walletType?: string;
    }
  ): Promise<boolean> {
    try {
      // Require biometric verification
      const biometricResult = await this.performBiometricVerification();
      if (!biometricResult.success) {
        return false;
      }

      const { error } = await supabase
        .from('whitelisted_addresses')
        .insert({
          user_id: userId,
          ...addressData,
          is_active: true,
          added_at: new Date().toISOString()
        });

      return !error;
    } catch (error) {
      console.error('Add whitelisted address error:', error);
      return false;
    }
  }

  // Generate idempotency key
  generateIdempotencyKey(): string {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2, 15);
    return `withdrawal_${timestamp}_${random}`;
  }

  // Validate withdrawal amount
  validateAmount(amount: number): { isValid: boolean; error?: string } {
    if (amount <= 0) {
      return { isValid: false, error: 'Amount must be greater than 0' };
    }

    if (amount > 1000000) {
      return { isValid: false, error: 'Amount exceeds maximum limit' };
    }

    // Check for more than 2 decimal places
    if (amount * 100 !== Math.floor(amount * 100)) {
      return { isValid: false, error: 'Amount can have maximum 2 decimal places' };
    }

    return { isValid: true };
  }

  // Validate address format
  validateAddress(address: string, type: 'bank_account' | 'crypto_wallet'): { isValid: boolean; error?: string } {
    if (!address || address.trim().length === 0) {
      return { isValid: false, error: 'Address is required' };
    }

    if (type === 'bank_account') {
      // Basic bank account validation
      if (address.length < 10 || address.length > 30) {
        return { isValid: false, error: 'Invalid bank account number length' };
      }
      if (!/^[0-9]+$/.test(address)) {
        return { isValid: false, error: 'Bank account must contain only numbers' };
      }
    } else {
      // Basic crypto wallet validation
      if (address.length < 20 || address.length > 100) {
        return { isValid: false, error: 'Invalid wallet address length' };
      }
      if (!/^[a-zA-Z0-9]+$/.test(address)) {
        return { isValid: false, error: 'Wallet address contains invalid characters' };
      }
    }

    return { isValid: true };
  }

  // Get withdrawal status
  async getWithdrawalStatus(transactionId: string): Promise<{
    status: string;
    amount: number;
    currency: string;
    address: string;
    createdAt: string;
    completedAt?: string;
  }> {
    try {
      const { data, error } = await supabase
        .from('withdrawals')
        .select('*')
        .eq('id', transactionId)
        .single();

      if (error || !data) {
        throw error;
      }

      return {
        status: data.status,
        amount: parseFloat(data.amount),
        currency: data.currency,
        address: data.withdrawal_address,
        createdAt: data.created_at,
        completedAt: data.completed_at
      };
    } catch (error) {
      console.error('Get withdrawal status error:', error);
      throw error;
    }
  }

  // Cancel withdrawal
  async cancelWithdrawal(transactionId: string, userId: string): Promise<boolean> {
    try {
      // Require biometric verification
      const biometricResult = await this.performBiometricVerification();
      if (!biometricResult.success) {
        return false;
      }

      const { error } = await supabase
        .from('withdrawals')
        .update({ status: 'cancelled' })
        .eq('id', transactionId)
        .eq('user_id', userId)
        .eq('status', 'pending');

      return !error;
    } catch (error) {
      console.error('Cancel withdrawal error:', error);
      return false;
    }
  }
}

export default SecureWithdrawalService;
