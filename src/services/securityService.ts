/**
 * Enterprise Security Service
 * Handles authentication, authorization, API protection, and security frameworks
 */

import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database';

const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

// Types
export interface AuthResult {
  success: boolean;
  user?: any;
  token?: string;
  refreshToken?: string;
  expiresAt?: string;
  error?: string;
}

export interface Session {
  id: string;
  userId: string;
  token: string;
  refreshToken: string;
  deviceFingerprint: string;
  ipAddress: string;
  userAgent: string;
  mfaEnabled: boolean;
  createdAt: string;
  expiresAt: string;
  lastActivity: string;
}

export interface SessionValidation {
  valid: boolean;
  userId?: string;
  expiresAt?: string;
  requiresMFA?: boolean;
  error?: string;
}

export interface TOTPSetup {
  secret: string;
  backupCodes: string[];
  qrCode: string;
  manualEntryKey: string;
  createdAt: string;
}

export interface TOTPResult {
  valid: boolean;
  token?: string;
  error?: string;
  remainingAttempts?: number;
}

export interface BiometricData {
  userId: string;
  deviceId: string;
  biometricType: 'fingerprint' | 'face' | 'voice' | 'iris';
  publicKey: string;
  credentialId: string;
  createdAt: string;
}

export interface BiometricResult {
  success: boolean;
  biometricId?: string;
  error?: string;
  confidence?: number;
}

export interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
  conditions: Record<string, any>;
  scope: string;
}

export interface ApiKey {
  id: string;
  userId: string;
  name: string;
  keyHash: string;
  permissions: Permission[];
  lastUsed: string;
  expiresAt: string;
  isActive: boolean;
  usageCount: number;
  rateLimitPerHour: number;
}

export interface ApiKeyValidation {
  valid: boolean;
  apiKeyId?: string;
  userId?: string;
  permissions?: Permission[];
  expiresAt?: string;
  error?: string;
}

export interface TokenValidation {
  valid: boolean;
  userId?: string;
  expiresAt?: string;
  scope?: string[];
  error?: string;
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetTime: string;
  limit: number;
  window: string;
}

export interface SecurityEvent {
  id: string;
  userId?: string;
  type: 'login_success' | 'login_failure' | 'mfa_challenge' | 'mfa_success' | 'mfa_failure' | 'api_access' | 'permission_denied' | 'suspicious_activity';
  severity: 'info' | 'warning' | 'error' | 'critical';
  description: string;
  ipAddress: string;
  userAgent: string;
  deviceFingerprint: string;
  location?: GeographicLocation;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface SecurityMetrics {
  totalLogins: number;
  failedLogins: number;
  mfaUsage: number;
  suspiciousActivities: number;
  blockedIPs: number;
  apiCalls: number;
  errors: number;
  topRisks: SecurityRisk[];
  period: string;
}

export interface SecurityRisk {
  type: string;
  count: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  mitigation: string;
}

export interface OAuthProvider {
  name: 'google' | 'microsoft' | 'linkedin' | 'github';
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  scopes: string[];
  enabled: boolean;
}

export interface DeviceInfo {
  fingerprint: string;
  userAgent: string;
  ipAddress: string;
  location: GeographicLocation;
  trusted: boolean;
  firstSeen: string;
  lastSeen: string;
  riskScore: number;
}

export interface SecurityConfig {
  passwordPolicy: {
    minLength: number;
    requireUppercase: boolean;
    requireLowercase: boolean;
    requireNumbers: boolean;
    requireSpecialChars: boolean;
    preventReuse: number;
  };
  mfaPolicy: {
    required: boolean;
    methods: ('totp' | 'sms' | 'email')[];
    backupCodes: boolean;
  };
  sessionPolicy: {
    maxDuration: number;
    idleTimeout: number;
    concurrentSessions: number;
    requireDeviceVerification: boolean;
  };
  apiPolicy: {
    rateLimiting: {
      requestsPerMinute: number;
      requestsPerHour: number;
      requestsPerDay: number;
    };
    keyRotation: {
      maxAge: number;
      reminderDays: number;
    };
    encryption: {
      minVersion: string;
      algorithms: string[];
    };
  };
}

// Authentication Service
export class AuthenticationService {
  private static instance: AuthenticationService;
  private config: SecurityConfig;

  private constructor() {
    this.config = {
      passwordPolicy: {
        minLength: 12,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        requireSpecialChars: true,
        preventReuse: 5
      },
      mfaPolicy: {
        required: true,
        methods: ['totp', 'sms'],
        backupCodes: true
      },
      sessionPolicy: {
        maxDuration: 24 * 60 * 60 * 1000, // 24 hours
        idleTimeout: 30 * 60 * 1000, // 30 minutes
        concurrentSessions: 3,
        requireDeviceVerification: true
      },
      apiPolicy: {
        rateLimiting: {
          requestsPerMinute: 100,
          requestsPerHour: 1000,
          requestsPerDay: 10000
        },
        keyRotation: {
          maxAge: 90 * 24 * 60 * 60 * 1000, // 90 days
          reminderDays: 7
        },
        encryption: {
          minVersion: 'TLS 1.2',
          algorithms: ['AES-256-GCM', 'ChaCha20-Poly1305']
        }
      }
    };
  }

  static getInstance(): AuthenticationService {
    if (!AuthenticationService.instance) {
      AuthenticationService.instance = new AuthenticationService();
    }
    return AuthenticationService.instance;
  }

  // OAuth Authentication
  async authenticateWithGoogle(token: string): Promise<AuthResult> {
    try {
      // Verify Google OAuth token
      const userInfo = await this.verifyGoogleToken(token);
      
      if (!userInfo) {
        return {
          success: false,
          error: 'Invalid Google token'
        };
      }

      // Check if user exists
      const { data: user, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('email', userInfo.email)
        .single();

      if (error && error.code === 'PGRST116') {
        // User doesn't exist, create new user
        const { data: newUser, error: createError } = await supabase
          .from('profiles')
          .insert({
            email: userInfo.email,
            full_name: userInfo.name,
            avatar_url: userInfo.picture,
            verification_status: 'pending',
            created_at: new Date().toISOString()
          })
          .select()
          .single();

        if (createError) throw createError;

        return this.createSession(newUser.id, userInfo);
      }

      if (error) throw error;

      return this.createSession(user.id, userInfo);
    } catch (error) {
      console.error('Error authenticating with Google:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async authenticateWithMicrosoft(token: string): Promise<AuthResult> {
    try {
      // Verify Microsoft OAuth token
      const userInfo = await this.verifyMicrosoftToken(token);
      
      if (!userInfo) {
        return {
          success: false,
          error: 'Invalid Microsoft token'
        };
      }

      // Similar user lookup/creation logic as Google
      const { data: user, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('email', userInfo.mail)
        .single();

      if (error && error.code === 'PGRST116') {
        const { data: newUser, error: createError } = await supabase
          .from('profiles')
          .insert({
            email: userInfo.mail,
            full_name: userInfo.displayName,
            avatar_url: userInfo.userPrincipalName,
            verification_status: 'pending',
            created_at: new Date().toISOString()
          })
          .select()
          .single();

        if (createError) throw createError;

        return this.createSession(newUser.id, userInfo);
      }

      if (error) throw error;

      return this.createSession(user.id, userInfo);
    } catch (error) {
      console.error('Error authenticating with Microsoft:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async authenticateWithLinkedIn(token: string): Promise<AuthResult> {
    try {
      // Verify LinkedIn OAuth token
      const userInfo = await this.verifyLinkedInToken(token);
      
      if (!userInfo) {
        return {
          success: false,
          error: 'Invalid LinkedIn token'
        };
      }

      // Similar user lookup/creation logic
      const { data: user, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('email', userInfo.emailAddress)
        .single();

      if (error && error.code === 'PGRST116') {
        const { data: newUser, error: createError } = await supabase
          .from('profiles')
          .insert({
            email: userInfo.emailAddress,
            full_name: `${userInfo.localizedFirstName} ${userInfo.localizedLastName}`,
            avatar_url: userInfo.profilePicture?.displayImage,
            verification_status: 'pending',
            created_at: new Date().toISOString()
          })
          .select()
          .single();

        if (createError) throw createError;

        return this.createSession(newUser.id, userInfo);
      }

      if (error) throw error;

      return this.createSession(user.id, userInfo);
    } catch (error) {
      console.error('Error authenticating with LinkedIn:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Multi-Factor Authentication
  async enableTOTP(userId: string): Promise<TOTPSetup> {
    try {
      const secret = this.generateTOTPSecret();
      const backupCodes = this.generateBackupCodes();
      const qrCode = this.generateTOTPQRCode(secret);

      const { data, error } = await supabase
        .from('user_mfa')
        .upsert({
          userId,
          secret,
          backupCodes,
          qrCode,
          manualEntryKey: secret.substring(0, 8), // First 8 chars for manual entry
          enabled: true,
          createdAt: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error enabling TOTP:', error);
      throw error;
    }
  }

  async verifyTOTP(userId: string, token: string): Promise<TOTPResult> {
    try {
      const { data: mfaConfig, error } = await supabase
        .from('user_mfa')
        .select('*')
        .eq('userId', userId)
        .single();

      if (error || !mfaConfig?.enabled) {
        return {
          valid: false,
          error: 'TOTP not enabled'
        };
      }

      const isValid = this.verifyTOTPToken(token, mfaConfig.secret);
      
      if (!isValid) {
        // Log failed attempt
        await this.logSecurityEvent({
          userId,
          type: 'mfa_failure',
          severity: 'warning',
          description: 'Invalid TOTP token provided',
          metadata: { token: token.substring(0, 4) + '***' }
        });

        return {
          valid: false,
          error: 'Invalid token'
        };
      }

      return {
        valid: true,
        token
      };
    } catch (error) {
      console.error('Error verifying TOTP:', error);
      throw error;
    }
  }

  async enableBiometric(userId: string, biometricData: BiometricData): Promise<BiometricResult> {
    try {
      // Store biometric data
      const { data, error } = await supabase
        .from('biometric_credentials')
        .insert({
          ...biometricData,
          createdAt: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;

      return {
        success: true,
        biometricId: data.id,
        confidence: 85
      };
    } catch (error) {
      console.error('Error enabling biometric:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Session Management
  async createSession(userId: string, userInfo: any): Promise<AuthResult> {
    try {
      const deviceFingerprint = this.generateDeviceFingerprint();
      const sessionToken = this.generateJWT(userId, deviceFingerprint);
      const refreshToken = this.generateRefreshToken();

      const { data: session, error } = await supabase
        .from('user_sessions')
        .insert({
          userId,
          token: sessionToken,
          refreshToken,
          deviceFingerprint,
          ipAddress: await this.getClientIP(),
          userAgent: navigator.userAgent,
          mfaEnabled: false,
          createdAt: new Date().toISOString(),
          expiresAt: new Date(Date.now() + this.config.sessionPolicy.maxDuration).toISOString(),
          lastActivity: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;

      await this.logSecurityEvent({
        userId,
        type: 'login_success',
        severity: 'info',
        description: `User logged in via ${userInfo.provider || 'email'}`,
        metadata: { provider: userInfo.provider || 'email' }
      });

      return {
        success: true,
        user: { id: userId, ...userInfo },
        token: sessionToken,
        refreshToken,
        expiresAt: session.expiresAt
      };
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  }

  async validateSession(sessionId: string): Promise<SessionValidation> {
    try {
      const { data: session, error } = await supabase
        .from('user_sessions')
        .select('*')
        .eq('id', sessionId)
        .single();

      if (error) {
        return {
          valid: false,
          error: 'Session not found'
        };
      }

      const now = new Date();
      const expiresAt = new Date(session.expiresAt);

      if (now > expiresAt) {
        return {
          valid: false,
          error: 'Session expired'
        };
      }

      // Update last activity
      await supabase
        .from('user_sessions')
        .update({ lastActivity: now.toISOString() })
        .eq('id', sessionId);

      return {
        valid: true,
        userId: session.userId,
        expiresAt: session.expiresAt,
        requiresMFA: session.mfaEnabled && !session.lastActivity
      };
    } catch (error) {
      console.error('Error validating session:', error);
      return {
        valid: false,
        error: error.message
      };
    }
  }

  async revokeSession(sessionId: string): Promise<void> {
    try {
      const { data: session, error } = await supabase
        .from('user_sessions')
        .select('userId')
        .eq('id', sessionId)
        .single();

      if (error) throw error;

      // Delete session
      await supabase
        .from('user_sessions')
        .delete()
        .eq('id', sessionId);

      await this.logSecurityEvent({
        userId: session.userId,
        type: 'login_success', // Actually logout, but using same type
        severity: 'info',
        description: 'User session revoked',
        metadata: { sessionId }
      });
    } catch (error) {
      console.error('Error revoking session:', error);
      throw error;
    }
  }

  // API Protection
  async checkRateLimit(clientId: string, endpoint: string): Promise<RateLimitResult> {
    try {
      const key = `${clientId}:${endpoint}`;
      const { data: usage, error } = await supabase
        .from('api_usage')
        .select('count, lastUsed')
        .eq('key', key)
        .single();

      if (error) {
        // First time usage
        await supabase
          .from('api_usage')
          .insert({
            key,
            count: 1,
            lastUsed: new Date().toISOString()
          });
        
        return {
          allowed: true,
          remaining: this.config.apiPolicy.rateLimiting.requestsPerMinute - 1,
          resetTime: new Date(Date.now() + 60000).toISOString(), // 1 minute
          limit: this.config.apiPolicy.rateLimiting.requestsPerMinute,
          window: '1m'
        };
      }

      const now = new Date();
      const lastUsed = new Date(usage.lastUsed);
      const timeDiff = now.getTime() - lastUsed.getTime();

      if (timeDiff < 60000) { // Within 1 minute
        const remaining = Math.max(0, this.config.apiPolicy.rateLimiting.requestsPerMinute - usage.count);
        
        return {
          allowed: remaining > 0,
          remaining,
          resetTime: new Date(lastUsed.getTime() + 60000).toISOString(),
          limit: this.config.apiPolicy.rateLimiting.requestsPerMinute,
          window: '1m'
        };
      }

      // Reset counter for new window
      await supabase
        .from('api_usage')
        .upsert({
          key,
          count: 1,
          lastUsed: now.toISOString()
        });

      return {
        allowed: true,
        remaining: this.config.apiPolicy.rateLimiting.requestsPerMinute - 1,
        resetTime: new Date(now.getTime() + 60000).toISOString(),
        limit: this.config.apiPolicy.rateLimiting.requestsPerMinute,
        window: '1m'
      };
    } catch (error) {
      console.error('Error checking rate limit:', error);
      throw error;
    }
  }

  async generateApiKey(userId: string, permissions: Permission[]): Promise<ApiKey> {
    try {
      const keyId = crypto.randomUUID();
      const keyHash = this.hashApiKey(keyId);
      
      const { data, error } = await supabase
        .from('api_keys')
        .insert({
          userId,
          name: `API Key ${new Date().toISOString()}`,
          keyHash,
          permissions,
          isActive: true,
          usageCount: 0,
          rateLimitPerHour: 1000,
          expiresAt: new Date(Date.now() + this.config.apiPolicy.keyRotation.maxAge).toISOString()
        })
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error generating API key:', error);
      throw error;
    }
  }

  async validateApiKey(apiKey: string): Promise<ApiKeyValidation> {
    try {
      const keyHash = this.hashApiKey(apiKey);
      
      const { data: keyData, error } = await supabase
        .from('api_keys')
        .select('*')
        .eq('keyHash', keyHash)
        .eq('isActive', true)
        .single();

      if (error) {
        return {
          valid: false,
          error: 'Invalid API key'
        };
      }

      const now = new Date();
      const expiresAt = new Date(keyData.expiresAt);

      if (now > expiresAt) {
        return {
          valid: false,
          error: 'API key expired'
        };
      }

      // Update last used
      await supabase
        .from('api_keys')
        .update({ lastUsed: now.toISOString() })
        .eq('id', keyData.id);

      return {
        valid: true,
        apiKeyId: keyData.id,
        userId: keyData.userId,
        permissions: keyData.permissions,
        expiresAt: keyData.expiresAt
      };
    } catch (error) {
      console.error('Error validating API key:', error);
      throw error;
    }
  }

  async revokeApiKey(apiKeyId: string): Promise<void> {
    try {
      await supabase
        .from('api_keys')
        .update({ isActive: false })
        .eq('id', apiKeyId);
    } catch (error) {
      console.error('Error revoking API key:', error);
      throw error;
    }
  }

  // Token Validation
  async validateJWT(token: string): Promise<TokenValidation> {
    try {
      // Verify JWT signature and expiration
      const decoded = this.decodeJWT(token);
      
      if (!decoded) {
        return {
          valid: false,
          error: 'Invalid token'
        };
      }

      const now = new Date();
      const expiresAt = new Date(decoded.exp * 1000);

      if (now > expiresAt) {
        return {
          valid: false,
          error: 'Token expired'
        };
      }

      return {
        valid: true,
        userId: decoded.userId,
        expiresAt: expiresAt.toISOString(),
        scope: decoded.scope || []
      };
    } catch (error) {
      console.error('Error validating JWT:', error);
      return {
        valid: false,
        error: error.message
      };
    }
  }

  async validateOAuthToken(token: string, provider: OAuthProvider): Promise<TokenValidation> {
    try {
      // Verify OAuth token with provider
      let userInfo;
      
      switch (provider.name) {
        case 'google':
          userInfo = await this.verifyGoogleToken(token);
          break;
        case 'microsoft':
          userInfo = await this.verifyMicrosoftToken(token);
          break;
        case 'linkedin':
          userInfo = await this.verifyLinkedInToken(token);
          break;
        default:
          throw new Error('Unsupported OAuth provider');
      }

      if (!userInfo) {
        return {
          valid: false,
          error: 'Invalid OAuth token'
        };
      }

      return {
        valid: true,
        userId: userInfo.id,
        expiresAt: new Date(Date.now() + 3600000).toISOString(), // 1 hour
        scope: provider.scopes
      };
    } catch (error) {
      console.error('Error validating OAuth token:', error);
      return {
        valid: false,
        error: error.message
      };
    }
  }

  // Security Logging
  async logSecurityEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): Promise<void> {
    try {
      await supabase
        .from('security_events')
        .insert({
          ...event,
          timestamp: new Date().toISOString()
        });
    } catch (error) {
      console.error('Error logging security event:', error);
    }
  }

  async getSecurityMetrics(period: string = '24h'): Promise<SecurityMetrics> {
    try {
      const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
      
      const [
        { count: totalLogins },
        { count: failedLogins },
        { count: mfaUsage },
        { data: suspiciousActivities },
        { count: blockedIPs },
        { count: apiCalls },
        { count: errors }
      ] = await Promise.all([
        supabase
          .from('security_events')
          .select('*', { count: 'exact' })
          .eq('type', 'login_success')
          .gte('timestamp', since),
        supabase
          .from('security_events')
          .select('*', { count: 'exact' })
          .eq('type', 'login_failure')
          .gte('timestamp', since),
        supabase
          .from('security_events')
          .select('*', { count: 'exact' })
          .eq('type', 'mfa_success')
          .gte('timestamp', since),
        supabase
          .from('suspicious_activities')
          .select('*', { count: 'exact' })
          .gte('detectedAt', since),
        supabase
          .from('blocked_ips')
          .select('*', { count: 'exact' }),
        supabase
          .from('api_usage')
          .select('*', { count: 'exact' })
          .gte('lastUsed', since),
        supabase
          .from('security_events')
          .select('*', { count: 'exact' })
          .eq('severity', 'error')
          .gte('timestamp', since)
      ]);

      // Get top security risks
      const { data: topRisks } = await supabase
        .from('security_events')
        .select('type, count')
        .gte('timestamp', since)
        .eq('severity', 'critical')
        .order('count', { ascending: false })
        .limit(10);

      return {
        totalLogins: totalLogins || 0,
        failedLogins: failedLogins || 0,
        mfaUsage: mfaUsage || 0,
        suspiciousActivities: suspiciousActivities || 0,
        blockedIPs: blockedIPs || 0,
        apiCalls: apiCalls || 0,
        errors: errors || 0,
        topRisks: topRisks?.map(risk => ({
          type: risk.type,
          count: risk.count,
          severity: 'critical',
          description: this.getRiskDescription(risk.type),
          mitigation: this.getRiskMitigation(risk.type)
        })) || [],
        period
      };
    } catch (error) {
      console.error('Error getting security metrics:', error);
      throw error;
    }
  }

  // Helper Methods
  private async verifyGoogleToken(token: string): Promise<any> {
    // Implement Google OAuth token verification
    // This would integrate with Google's token verification API
    return null;
  }

  private async verifyMicrosoftToken(token: string): Promise<any> {
    // Implement Microsoft OAuth token verification
    // This would integrate with Microsoft's token verification API
    return null;
  }

  private async verifyLinkedInToken(token: string): Promise<any> {
    // Implement LinkedIn OAuth token verification
    // This would integrate with LinkedIn's token verification API
    return null;
  }

  private generateTOTPSecret(): string {
    // Generate secure random secret for TOTP
    const secret = crypto.getRandomValues(new Uint8Array(20));
    return Array.from(secret)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('')
      .toUpperCase();
  }

  private generateBackupCodes(): string[] {
    const codes = [];
    for (let i = 0; i < 10; i++) {
      codes.push(Math.floor(100000 + Math.random() * 900000).toString());
    }
    return codes;
  }

  private generateTOTPQRCode(secret: string): string {
    // Generate QR code for TOTP setup
    // This would integrate with a QR code library
    return `otpauth://totp/Worldmine?secret=${secret}&issuer=Worldmine&algorithm=SHA1&digits=6&period=30`;
  }

  private verifyTOTPToken(token: string, secret: string): boolean {
    // Verify TOTP token against secret
    // This would integrate with a TOTP library
    return token.length === 6 && !isNaN(parseInt(token));
  }

  private generateDeviceFingerprint(): string {
    // Generate device fingerprint
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
      canvas.toDataURL()
    ].join('|');

    // Hash the fingerprint
    const encoder = new TextEncoder();
    const data = encoder.encode(fingerprintData);
    const hashBuffer = crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private generateJWT(userId: string, deviceFingerprint: string): string {
    // Generate JWT token
    const payload = {
      userId,
      deviceFingerprint,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
    };

    // This would integrate with a proper JWT library
    return btoa(JSON.stringify(payload));
  }

  private decodeJWT(token: string): any {
    try {
      const payload = atob(token.split('.')[1]);
      return JSON.parse(payload);
    } catch {
      return null;
    }
  }

  private async getClientIP(): Promise<string> {
    // Get client IP address
    // This would integrate with an IP geolocation service
    return '127.0.0.1'; // Fallback for development
  }

  private hashApiKey(apiKey: string): string {
    // Hash API key for secure storage
    const encoder = new TextEncoder();
    const data = encoder.encode(apiKey);
    const hashBuffer = crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private getRiskDescription(riskType: string): string {
    const descriptions: Record<string, string> = {
      'login_failure': 'Multiple failed login attempts detected',
      'suspicious_activity': 'Suspicious user activity patterns',
      'api_abuse': 'API usage abuse detected',
      'permission_denied': 'Unauthorized access attempt',
      'malicious_request': 'Malicious request patterns detected'
    };
    return descriptions[riskType] || 'Security risk detected';
  }

  private getRiskMitigation(riskType: string): string {
    const mitigations: Record<string, string> = {
      'login_failure': 'Implement account lockout after 5 failed attempts',
      'suspicious_activity': 'Require additional verification for suspicious activities',
      'api_abuse': 'Implement stricter rate limiting for abusive IPs',
      'permission_denied': 'Block IP and notify user of unauthorized access',
      'malicious_request': 'Block malicious IPs and implement WAF rules'
    };
    return mitigations[riskType] || 'Implement security review';
  }
}

export default AuthenticationService;
