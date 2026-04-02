import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { WebAuthnService } from '../services/webauthnService';

// Types
interface TrustedDevice {
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
}

interface WhitelistedAddress {
  id: string;
  type: 'bank_account' | 'crypto_wallet';
  name: string;
  address: string;
  bankName?: string;
  accountNumber?: string;
  walletType?: string;
  isActive: boolean;
  addedAt: string;
  lastUsed?: string;
  cooldownUntil?: string;
}

interface SecuritySettings {
  dailyWithdrawalLimit: number;
  requireSecondaryApproval: boolean;
  requireBiometricReauth: boolean;
  requireTOTP: boolean;
  trustedDeviceRequired: boolean;
  emailVerified: boolean;
  totpEnabled: boolean;
  biometricEnabled: boolean;
}

interface SecurityHold {
  id: string;
  userId: string;
  reason: 'new_device' | 'address_change' | 'limit_exceeded' | 'suspicious_activity';
  amount?: number;
  currency?: string;
  address?: string;
  deviceId?: string;
  holdUntil: string;
  isActive: boolean;
  createdAt: string;
  resolvedAt?: string;
  resolvedBy?: string;
  notes?: string;
}

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.SUPABASE_SERVICE_ROLE_KEY!
);

const webauthn = new WebAuthnService();

export const SecuritySettings: React.FC = () => {
  const [settings, setSettings] = useState<SecuritySettings | null>(null);
  const [trustedDevices, setTrustedDevices] = useState<TrustedDevice[]>([]);
  const [whitelistedAddresses, setWhitelistedAddresses] = useState<WhitelistedAddress[]>([]);
  const [securityHolds, setSecurityHolds] = useState<SecurityHold[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'devices' | 'addresses' | 'holds' | 'settings'>('devices');
  const [showAddDeviceModal, setShowAddDeviceModal] = useState(false);
  const [showAddAddressModal, setShowAddAddressModal] = useState(false);
  const [totpSecret, setTotpSecret] = useState<string>('');
  const [totpQR, setTotpQR] = useState<string>('');
  const [showTOTPSetup, setShowTOTPSetup] = useState(false);

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      // Load settings
      const { data: settingsData } = await supabase
        .from('security_settings')
        .select('*')
        .eq('user_id', user.data.user.id)
        .single();

      if (settingsData) {
        setSettings(settingsData);
      }

      // Load trusted devices
      const { data: devicesData } = await supabase
        .from('trusted_devices')
        .select('*')
        .eq('user_id', user.data.user.id)
        .order('last_used', { ascending: false });

      setTrustedDevices(devicesData || []);

      // Load whitelisted addresses
      const { data: addressesData } = await supabase
        .from('whitelisted_addresses')
        .select('*')
        .eq('user_id', user.data.user.id)
        .order('added_at', { ascending: false });

      setWhitelistedAddresses(addressesData || []);

      // Load security holds
      const { data: holdsData } = await supabase
        .from('security_holds')
        .select('*')
        .eq('user_id', user.data.user.id)
        .eq('is_active', true)
        .order('created_at', { ascending: false });

      setSecurityHolds(holdsData || []);
    } catch (error) {
      console.error('Error loading security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateDeviceFingerprint = async (): Promise<string> => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillText('Device fingerprint', 2, 2);
    }
    
    const fingerprint = [
      navigator.userAgent,
      navigator.language,
      screen.width + 'x' + screen.height,
      new Date().getTimezoneOffset(),
      canvas.toDataURL()
    ].join('|');

    // Hash the fingerprint
    const encoder = new TextEncoder();
    const data = encoder.encode(fingerprint);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  const addTrustedDevice = async () => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      // Require biometric verification
      const biometricResult = await webauthn.authenticate({
        challenge: new Uint8Array(32),
        allowCredentials: [],
        userVerification: 'required'
      });

      if (!biometricResult) {
        throw new Error('Biometric verification failed');
      }

      const fingerprint = await generateDeviceFingerprint();
      
      // Get geolocation
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      const deviceData = {
        user_id: user.data.user.id,
        name: `${navigator.platform} - ${new Date().toLocaleDateString()}`,
        fingerprint,
        user_agent: navigator.userAgent,
        ip_address: await getClientIP(),
        location: {
          country: 'ET', // Would use geocoding service
          city: 'Addis Ababa',
          coordinates: [position.coords.longitude, position.coords.latitude] as [number, number]
        },
        first_seen: new Date().toISOString(),
        last_used: new Date().toISOString(),
        is_active: true,
        is_verified: true
      };

      const { error } = await supabase
        .from('trusted_devices')
        .insert(deviceData);

      if (error) throw error;

      setShowAddDeviceModal(false);
      loadSecurityData();
    } catch (error) {
      console.error('Error adding trusted device:', error);
    }
  };

  const removeTrustedDevice = async (deviceId: string) => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      // Require biometric verification
      const biometricResult = await webauthn.authenticate({
        challenge: new Uint8Array(32),
        allowCredentials: [],
        userVerification: 'required'
      });

      if (!biometricResult) {
        throw new Error('Biometric verification failed');
      }

      const { error } = await supabase
        .from('trusted_devices')
        .update({ is_active: false })
        .eq('id', deviceId)
        .eq('user_id', user.data.user.id);

      if (error) throw error;

      loadSecurityData();
    } catch (error) {
      console.error('Error removing trusted device:', error);
    }
  };

  const addWhitelistedAddress = async (addressData: {
    type: 'bank_account' | 'crypto_wallet';
    name: string;
    address: string;
    bankName?: string;
    accountNumber?: string;
    walletType?: string;
  }) => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      // Check if address is already in cooldown
      const { data: existingAddress } = await supabase
        .from('whitelisted_addresses')
        .select('cooldown_until')
        .eq('user_id', user.data.user.id)
        .eq('address', addressData.address)
        .single();

      if (existingAddress && existingAddress.cooldown_until && new Date(existingAddress.cooldown_until) > new Date()) {
        throw new Error('Address is in cooldown period');
      }

      // Require biometric verification
      const biometricResult = await webauthn.authenticate({
        challenge: new Uint8Array(32),
        allowCredentials: [],
        userVerification: 'required'
      });

      if (!biometricResult) {
        throw new Error('Biometric verification failed');
      }

      const newAddress = {
        user_id: user.data.user.id,
        ...addressData,
        is_active: true,
        added_at: new Date().toISOString()
      };

      const { error } = await supabase
        .from('whitelisted_addresses')
        .insert(newAddress);

      if (error) throw error;

      setShowAddAddressModal(false);
      loadSecurityData();
    } catch (error) {
      console.error('Error adding whitelisted address:', error);
    }
  };

  const removeWhitelistedAddress = async (addressId: string) => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      // Require biometric verification
      const biometricResult = await webauthn.authenticate({
        challenge: new Uint8Array(32),
        allowCredentials: [],
        userVerification: 'required'
      });

      if (!biometricResult) {
        throw new Error('Biometric verification failed');
      }

      // Set 48-hour cooldown
      const cooldownUntil = new Date();
      cooldownUntil.setHours(cooldownUntil.getHours() + 48);

      const { error } = await supabase
        .from('whitelisted_addresses')
        .update({ 
          is_active: false,
          cooldown_until: cooldownUntil.toISOString()
        })
        .eq('id', addressId)
        .eq('user_id', user.data.user.id);

      if (error) throw error;

      loadSecurityData();
    } catch (error) {
      console.error('Error removing whitelisted address:', error);
    }
  };

  const enableTOTP = async () => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      // Generate TOTP secret
      const secret = generateTOTPSecret();
      setTotpSecret(secret);

      // Generate QR code
      const qrCode = await generateTOTPQRCode(secret, user.data.user.email!);
      setTotpQR(qrCode);

      setShowTOTPSetup(true);
    } catch (error) {
      console.error('Error enabling TOTP:', error);
    }
  };

  const verifyTOTP = async (token: string) => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      // Verify TOTP token
      const isValid = verifyTOTPToken(totpSecret, token);
      if (!isValid) {
        throw new Error('Invalid TOTP token');
      }

      // Enable TOTP in settings
      const { error } = await supabase
        .from('security_settings')
        .update({ totp_enabled: true })
        .eq('user_id', user.data.user.id);

      if (error) throw error;

      setShowTOTPSetup(false);
      loadSecurityData();
    } catch (error) {
      console.error('Error verifying TOTP:', error);
    }
  };

  const updateSettings = async (newSettings: Partial<SecuritySettings>) => {
    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      const { error } = await supabase
        .from('security_settings')
        .update(newSettings)
        .eq('user_id', user.data.user.id);

      if (error) throw error;

      loadSecurityData();
    } catch (error) {
      console.error('Error updating settings:', error);
    }
  };

  const getClientIP = async (): Promise<string> => {
    // In production, use a proper IP geolocation service
    return '192.168.1.100';
  };

  const generateTOTPSecret = (): string => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let secret = '';
    for (let i = 0; i < 32; i++) {
      secret += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return secret;
  };

  const generateTOTPQRCode = async (secret: string, email: string): Promise<string> => {
    // In production, use a proper QR code generation library
    const otpauth = `otpauth://totp/Worldmine:${email}?secret=${secret}&issuer=Worldmine`;
    return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(otpauth)}`;
  };

  const verifyTOTPToken = (secret: string, token: string): boolean => {
    // In production, use a proper TOTP verification library
    // This is a simplified implementation
    return token.length === 6 && /^\d{6}$/.test(token);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading security settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Security Settings</h1>
            <p className="text-gray-600 mt-1">Manage your account security and withdrawal settings</p>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('devices')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'devices'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Trusted Devices ({trustedDevices.filter(d => d.isActive).length})
              </button>
              <button
                onClick={() => setActiveTab('addresses')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'addresses'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Whitelisted Addresses ({whitelistedAddresses.filter(a => a.isActive).length})
              </button>
              <button
                onClick={() => setActiveTab('holds')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'holds'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Security Holds ({securityHolds.filter(h => h.isActive).length})
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'settings'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Security Settings
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Trusted Devices Tab */}
            {activeTab === 'devices' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Trusted Devices</h2>
                  <button
                    onClick={() => setShowAddDeviceModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Add Device
                  </button>
                </div>

                <div className="space-y-4">
                  {trustedDevices.map((device) => (
                    <div key={device.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{device.name}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            First seen: {new Date(device.firstSeen).toLocaleDateString()}
                          </p>
                          <p className="text-sm text-gray-600">
                            Last used: {new Date(device.lastUsed).toLocaleDateString()}
                          </p>
                          <p className="text-sm text-gray-600">
                            Location: {device.location.city}, {device.location.country}
                          </p>
                          {device.isVerified && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-2">
                              Verified
                            </span>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          {device.isActive && (
                            <button
                              onClick={() => removeTrustedDevice(device.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Whitelisted Addresses Tab */}
            {activeTab === 'addresses' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Whitelisted Addresses</h2>
                  <button
                    onClick={() => setShowAddAddressModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Add Address
                  </button>
                </div>

                <div className="space-y-4">
                  {whitelistedAddresses.map((address) => (
                    <div key={address.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{address.name}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            Type: {address.type === 'bank_account' ? 'Bank Account' : 'Crypto Wallet'}
                          </p>
                          <p className="text-sm text-gray-600">
                            Address: {address.address}
                          </p>
                          {address.bankName && (
                            <p className="text-sm text-gray-600">Bank: {address.bankName}</p>
                          )}
                          {address.walletType && (
                            <p className="text-sm text-gray-600">Wallet: {address.walletType}</p>
                          )}
                          <p className="text-sm text-gray-600">
                            Added: {new Date(address.addedAt).toLocaleDateString()}
                          </p>
                          {address.cooldownUntil && new Date(address.cooldownUntil) > new Date() && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 mt-2">
                              In cooldown until {new Date(address.cooldownUntil).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          {address.isActive && (
                            <button
                              onClick={() => removeWhitelistedAddress(address.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Security Holds Tab */}
            {activeTab === 'holds' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-6">Security Holds</h2>
                
                <div className="space-y-4">
                  {securityHolds.map((hold) => (
                    <div key={hold.id} className="border border-yellow-200 bg-yellow-50 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">
                            {hold.reason.replace('_', ' ').toUpperCase()}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            Hold until: {new Date(hold.holdUntil).toLocaleDateString()}
                          </p>
                          {hold.amount && (
                            <p className="text-sm text-gray-600">
                              Amount: ${hold.amount} {hold.currency}
                            </p>
                          )}
                          {hold.address && (
                            <p className="text-sm text-gray-600">
                              Address: {hold.address}
                            </p>
                          )}
                          <p className="text-sm text-gray-600">
                            Created: {new Date(hold.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            hold.isActive 
                              ? 'bg-yellow-100 text-yellow-800' 
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {hold.isActive ? 'Active' : 'Resolved'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Security Settings Tab */}
            {activeTab === 'settings' && settings && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-6">Security Configuration</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Daily Withdrawal Limit ($)
                    </label>
                    <input
                      type="number"
                      value={settings.dailyWithdrawalLimit}
                      onChange={(e) => updateSettings({ dailyWithdrawalLimit: Number(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.requireSecondaryApproval}
                        onChange={(e) => updateSettings({ requireSecondaryApproval: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Require secondary approval for large withdrawals</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.requireBiometricReauth}
                        onChange={(e) => updateSettings({ requireBiometricReauth: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Require biometric re-authentication</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.requireTOTP}
                        onChange={(e) => updateSettings({ requireTOTP: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Require TOTP verification</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.trustedDeviceRequired}
                        onChange={(e) => updateSettings({ trustedDeviceRequired: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Require trusted device</span>
                    </label>
                  </div>

                  <div className="pt-4 border-t border-gray-200">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Two-Factor Authentication</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">TOTP Authentication</span>
                        {settings.totpEnabled ? (
                          <span className="text-green-600 text-sm">Enabled</span>
                        ) : (
                          <button
                            onClick={enableTOTP}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                          >
                            Enable
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Device Modal */}
      {showAddDeviceModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Trusted Device</h3>
            <p className="text-gray-600 mb-6">
              To add this device as trusted, you'll need to verify your identity using biometric authentication.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={addTrustedDevice}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
              >
                Verify and Add Device
              </button>
              <button
                onClick={() => setShowAddDeviceModal(false)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Address Modal */}
      {showAddAddressModal && (
        <AddAddressModal
          onClose={() => setShowAddAddressModal(false)}
          onAdd={addWhitelistedAddress}
        />
      )}

      {/* TOTP Setup Modal */}
      {showTOTPSetup && (
        <TOTPSetupModal
          secret={totpSecret}
          qrCode={totpQR}
          onClose={() => setShowTOTPSetup(false)}
          onVerify={verifyTOTP}
        />
      )}
    </div>
  );
};

// Add Address Modal Component
const AddAddressModal: React.FC<{
  onClose: () => void;
  onAdd: (data: any) => void;
}> = ({ onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    type: 'bank_account' as 'bank_account' | 'crypto_wallet',
    name: '',
    address: '',
    bankName: '',
    accountNumber: '',
    walletType: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAdd(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Whitelisted Address</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="bank_account">Bank Account</option>
              <option value="crypto_wallet">Crypto Wallet</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <input
              type="text"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {formData.type === 'bank_account' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bank Name</label>
                <input
                  type="text"
                  value={formData.bankName}
                  onChange={(e) => setFormData({ ...formData, bankName: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Account Number</label>
                <input
                  type="text"
                  value={formData.accountNumber}
                  onChange={(e) => setFormData({ ...formData, accountNumber: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </>
          )}

          {formData.type === 'crypto_wallet' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Wallet Type</label>
              <input
                type="text"
                value={formData.walletType}
                onChange={(e) => setFormData({ ...formData, walletType: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Bitcoin, Ethereum"
              />
            </div>
          )}

          <div className="flex space-x-3 pt-4">
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
            >
              Add Address
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// TOTP Setup Modal Component
const TOTPSetupModal: React.FC<{
  secret: string;
  qrCode: string;
  onClose: () => void;
  onVerify: (token: string) => void;
}> = ({ secret, qrCode, onClose, onVerify }) => {
  const [token, setToken] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onVerify(token);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Setup TOTP Authentication</h3>
        
        <div className="text-center mb-6">
          <img src={qrCode} alt="TOTP QR Code" className="mx-auto mb-4" />
          <p className="text-sm text-gray-600 mb-2">Scan this QR code with your authenticator app</p>
          <p className="text-xs text-gray-500">Or enter this secret manually: {secret}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Verification Code</label>
            <input
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="000000"
              maxLength={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-lg"
              required
            />
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
            >
              Verify
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SecuritySettings;
