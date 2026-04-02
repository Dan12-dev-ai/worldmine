import { createClient } from '@supabase/supabase-js';
import { WebAuthnService } from '../services/webauthnService';

// Compliance Configuration
const COMPLIANCE_CONFIG = {
  NBE_LIMIT: 3000, // Ethiopian National Bank transaction limit
  SANCTIONS_CHECK_INTERVAL: 24 * 60 * 60 * 1000, // 24 hours
  GDPR_RETENTION_DAYS: 365,
  PCI_TOKENIZATION_PROVIDER: 'stripe', // or 'chapa' for Ethiopia
  KYC_TIERS: {
    TIER_1: { maxTransaction: 1000, requirements: ['email', 'phone'] },
    TIER_2: { maxTransaction: 10000, requirements: ['email', 'phone', 'id_verification', 'liveness'] },
    TIER_3: { maxTransaction: 50000, requirements: ['email', 'phone', 'id_verification', 'liveness', 'proof_of_address'] }
  }
};

// Global Sanctions Lists (simplified for demo)
const SANCTIONS_LISTS = {
  OFAC: ['US_SANCTIONED_ENTITY_1', 'US_SANCTIONED_ENTITY_2'],
  UN: ['UN_SANCTIONED_ENTITY_1', 'UN_SANCTIONED_ENTITY_2'],
  EU: ['EU_SANCTIONED_ENTITY_1', 'EU_SANCTIONED_ENTITY_2']
};

export interface KYCProfile {
  userId: string;
  tier: 1 | 2 | 3;
  email: string;
  phone: string;
  idVerification?: {
    documentType: 'passport' | 'national_id' | 'driver_license';
    documentNumber: string;
    issuedDate: string;
    expiryDate: string;
    issuingCountry: string;
    verificationStatus: 'pending' | 'approved' | 'rejected';
  };
  livenessCheck?: {
    status: 'pending' | 'approved' | 'rejected';
    timestamp: string;
    confidenceScore: number;
  };
  proofOfAddress?: {
    documentType: 'utility_bill' | 'bank_statement' | 'government_letter';
    documentUrl: string;
    verificationStatus: 'pending' | 'approved' | 'rejected';
  };
  lastSanctionsCheck: string;
  sanctionsStatus: 'clear' | 'flagged' | 'blocked';
  riskScore: number; // 0-100
  createdAt: string;
  updatedAt: string;
}

export interface SanctionsScreeningResult {
  userId: string;
  screenedAt: string;
  matches: {
    list: keyof typeof SANCTIONS_LISTS;
    entity: string;
    confidence: number;
  }[];
  status: 'clear' | 'flagged' | 'blocked';
  requiresManualReview: boolean;
}

export interface TransactionMonitoringResult {
  transactionId: string;
  userId: string;
  amount: number;
  currency: string;
  timestamp: string;
  riskFactors: {
    amount: boolean; // > $3,000 NBE limit
    frequency: boolean; // Unusual pattern
    location: boolean; // High-risk jurisdiction
    counterpart: boolean; // Sanctioned entity
  };
  riskScore: number;
  status: 'approved' | 'flagged' | 'blocked';
  requiresManualReview: boolean;
  reason: string;
}

export interface ESignatureComplianceLog {
  contractId: string;
  userId: string;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  biometricHash: string;
  contractSha256: string;
  termsVersion: string;
  consentGiven: boolean;
  nonRepudiationData: {
    deviceFingerprint: string;
    geoLocation: {
      country: string;
      city: string;
      coordinates: [number, number];
    };
    sessionToken: string;
  };
}

export interface GDPRDataExport {
  userId: string;
  exportDate: string;
  personalData: {
    profile: any;
    transactions: any[];
    contracts: any[];
    kycData: any;
    auditLogs: any[];
  };
  format: 'json' | 'csv';
  status: 'processing' | 'completed' | 'failed';
}

export interface ConsentLog {
  userId: string;
  consentType: 'terms_of_service' | 'privacy_policy' | 'contract_terms';
  version: string;
  consentGiven: boolean;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  method: 'click' | 'biometric' | 'electronic_signature';
}

export class ComplianceService {
  private supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL!,
    import.meta.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  private async generateDeviceFingerprint(): Promise<string> {
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
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // KYC Management
  async initializeKYC(userId: string, tier: 1 | 2 | 3, email: string, phone: string): Promise<KYCProfile> {
    const profile: KYCProfile = {
      userId,
      tier,
      email,
      phone,
      lastSanctionsCheck: new Date().toISOString(),
      sanctionsStatus: 'clear',
      riskScore: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    const { data, error } = await this.supabase
      .from('kyc_profiles')
      .insert(profile)
      .select()
      .single();

    if (error) throw new Error(`KYC initialization failed: ${error.message}`);
    return data;
  }

  async updateKYCTier(userId: string, newTier: 1 | 2 | 3): Promise<KYCProfile> {
    const { data, error } = await this.supabase
      .from('kyc_profiles')
      .update({ 
        tier: newTier, 
        updatedAt: new Date().toISOString(),
        sanctionsStatus: 'flagged' // Re-screen on tier upgrade
      })
      .eq('userId', userId)
      .select()
      .single();

    if (error) throw new Error(`KYC tier update failed: ${error.message}`);
    
    // Trigger sanctions screening
    await this.screenUserForSanctions(userId);
    
    return data;
  }

  async submitIDVerification(userId: string, verificationData: KYCProfile['idVerification']): Promise<void> {
    const { error } = await this.supabase
      .from('kyc_profiles')
      .update({ 
        idVerification: verificationData,
        updatedAt: new Date().toISOString()
      })
      .eq('userId', userId);

    if (error) throw new Error(`ID verification submission failed: ${error.message}`);
  }

  async performLivenessCheck(userId: string): Promise<void> {
    // Simulate liveness check with AI service
    const livenessResult = {
      status: 'approved' as const,
      timestamp: new Date().toISOString(),
      confidenceScore: 0.95
    };

    const { error } = await this.supabase
      .from('kyc_profiles')
      .update({ 
        livenessCheck: livenessResult,
        updatedAt: new Date().toISOString()
      })
      .eq('userId', userId);

    if (error) throw new Error(`Liveness check failed: ${error.message}`);
  }

  // Sanctions Screening
  async screenUserForSanctions(userId: string): Promise<SanctionsScreeningResult> {
    const { data: profile } = await this.supabase
      .from('kyc_profiles')
      .select('*')
      .eq('userId', userId)
      .single();

    if (!profile) throw new Error('KYC profile not found');

    const matches = [];
    let requiresManualReview = false;

    // Simulate sanctions screening
    for (const [listName, entities] of Object.entries(SANCTIONS_LISTS)) {
      for (const entity of entities) {
        // In production, this would integrate with actual sanctions APIs
        const confidence = Math.random(); // Simulated confidence score
        if (confidence > 0.7) {
          matches.push({
            list: listName as keyof typeof SANCTIONS_LISTS,
            entity,
            confidence
          });
          requiresManualReview = true;
        }
      }
    }

    const status = matches.length > 0 ? (requiresManualReview ? 'flagged' : 'blocked') : 'clear';
    const result: SanctionsScreeningResult = {
      userId,
      screenedAt: new Date().toISOString(),
      matches,
      status,
      requiresManualReview
    };

    // Update KYC profile
    await this.supabase
      .from('kyc_profiles')
      .update({ 
        sanctionsStatus: status,
        lastSanctionsCheck: new Date().toISOString(),
        riskScore: matches.length > 0 ? 80 : 10,
        updatedAt: new Date().toISOString()
      })
      .eq('userId', userId);

    // Log screening result
    await this.supabase
      .from('compliance_audit_log')
      .insert({
        userId,
        action: 'sanctions_screening',
        details: result,
        severity: status === 'clear' ? 'info' : 'critical',
        createdAt: new Date().toISOString()
      });

    return result;
  }

  // Transaction Monitoring
  async monitorTransaction(transactionId: string, userId: string, amount: number, currency: string): Promise<TransactionMonitoringResult> {
    const riskFactors = {
      amount: amount > COMPLIANCE_CONFIG.NBE_LIMIT,
      frequency: false, // Would check transaction frequency
      location: false, // Would check user location
      counterpart: false // Would check counterparty sanctions
    };

    const riskScore = Object.values(riskFactors).filter(Boolean).length * 25;
    const requiresManualReview = riskScore >= 50 || amount > COMPLIANCE_CONFIG.NBE_LIMIT;
    
    const status = requiresManualReview ? 'flagged' : 'approved';
    const reason = requiresManualReview 
      ? `Transaction flagged: Amount $${amount} exceeds NBE limit of $${COMPLIANCE_CONFIG.NBE_LIMIT}`
      : 'Transaction approved';

    const result: TransactionMonitoringResult = {
      transactionId,
      userId,
      amount,
      currency,
      timestamp: new Date().toISOString(),
      riskFactors,
      riskScore,
      status,
      requiresManualReview,
      reason
    };

    // Log monitoring result
    await this.supabase
      .from('transaction_monitoring')
      .insert(result);

    if (requiresManualReview) {
      await this.supabase
        .from('compliance_alerts')
        .insert({
          alertType: 'transaction_flagged',
          userId,
          details: result,
          severity: 'high',
          createdAt: new Date().toISOString()
        });
    }

    return result;
  }

  // E-Signature Compliance
  async logESignatureCompliance(
    contractId: string, 
    userId: string, 
    biometricHash: string, 
    contractSha256: string,
    termsVersion: string
  ): Promise<ESignatureComplianceLog> {
    // Generate device fingerprint
    const fingerprint = await this.generateDeviceFingerprint();
    
    // Get IP and location (in production, use proper geolocation service)
    const ipAddress = '192.168.1.100'; // Would get from request
    const geoLocation = {
      country: 'ET', // Ethiopia
      city: 'Addis Ababa',
      coordinates: [9.1450, 40.4897] as [number, number]
    };

    const complianceLog: ESignatureComplianceLog = {
      contractId,
      userId,
      timestamp: new Date().toISOString(),
      ipAddress,
      userAgent: navigator.userAgent,
      biometricHash,
      contractSha256,
      termsVersion,
      consentGiven: true,
      nonRepudiationData: {
        deviceFingerprint,
        geoLocation,
        sessionToken: Math.random().toString(36).substring(7)
      }
    };

    // Store compliance log
    const { data, error } = await this.supabase
      .from('esignature_compliance_logs')
      .insert(complianceLog)
      .select()
      .single();

    if (error) throw new Error(`E-signature compliance logging failed: ${error.message}`);

    return data;
  }

  // GDPR Compliance
  async exportUserData(userId: string, format: 'json' | 'csv' = 'json'): Promise<GDPRDataExport> {
    // Collect all user data
    const [profile, transactions, contracts, kycData, auditLogs] = await Promise.all([
      this.supabase.from('user_profiles').select('*').eq('userId', userId),
      this.supabase.from('transactions').select('*').eq('userId', userId),
      this.supabase.from('contracts').select('*').or(`seller_id.eq.${userId},buyer_id.eq.${userId}`),
      this.supabase.from('kyc_profiles').select('*').eq('userId', userId),
      this.supabase.from('compliance_audit_log').select('*').eq('userId', userId)
    ]);

    const exportData: GDPRDataExport = {
      userId,
      exportDate: new Date().toISOString(),
      personalData: {
        profile: profile.data || [],
        transactions: transactions.data || [],
        contracts: contracts.data || [],
        kycData: kycData.data || [],
        auditLogs: auditLogs.data || []
      },
      format,
      status: 'completed'
    };

    // Log export request
    await this.supabase
      .from('gdpr_requests')
      .insert({
        userId,
        requestType: 'data_export',
        status: 'completed',
        completedAt: new Date().toISOString(),
        createdAt: new Date().toISOString()
      });

    return exportData;
  }

  async requestAccountDeletion(userId: string, reason: string): Promise<void> {
    // Log deletion request
    await this.supabase
      .from('gdpr_requests')
      .insert({
        userId,
        requestType: 'account_deletion',
        reason,
        status: 'pending',
        createdAt: new Date().toISOString()
      });

    // Schedule deletion after 30 days (GDPR requirement)
    const deletionDate = new Date();
    deletionDate.setDate(deletionDate.getDate() + 30);

    await this.supabase
      .from('scheduled_deletions')
      .insert({
        userId,
        scheduledFor: deletionDate.toISOString(),
        status: 'scheduled',
        createdAt: new Date().toISOString()
      });
  }

  // Consent Management
  async logConsent(
    userId: string, 
    consentType: ConsentLog['consentType'], 
    version: string, 
    method: ConsentLog['method']
  ): Promise<void> {
    const consentLog: ConsentLog = {
      userId,
      consentType,
      version,
      consentGiven: true,
      timestamp: new Date().toISOString(),
      ipAddress: '192.168.1.100', // Would get from request
      userAgent: navigator.userAgent,
      method
    };

    await this.supabase
      .from('consent_logs')
      .insert(consentLog);
  }

  // PCI DSS Compliance
  async tokenizePayment(paymentData: {
    cardNumber: string;
    expiryDate: string;
    cvv: string;
    holderName: string;
  }): Promise<{ token: string; last4: string }> {
    // In production, integrate with Stripe or Chapa
    // Never store raw card data
    
    // Simulate tokenization
    const token = `tok_${Math.random().toString(36).substring(2, 15)}`;
    const last4 = paymentData.cardNumber.slice(-4);

    return { token, last4 };
  }

  // Compliance Reporting
  async generateComplianceReport(_startDate: string, _endDate: string): Promise<{
    summary: {
      totalUsers: number;
      kycCompliant: number;
      sanctionsScreened: number;
      transactionsMonitored: number;
      alertsGenerated: number;
    };
    details: any;
  }> {
    const [users, kycProfiles, sanctions, transactions, alerts] = await Promise.all([
      this.supabase.from('user_profiles').select('id', { count: 'exact' }),
      this.supabase.from('kyc_profiles').select('*', { count: 'exact' }),
      this.supabase.from('sanctions_screening_results').select('*', { count: 'exact' }),
      this.supabase.from('transaction_monitoring').select('*', { count: 'exact' }),
      this.supabase.from('compliance_alerts').select('*', { count: 'exact' })
    ]);

    return {
      summary: {
        totalUsers: users.count || 0,
        kycCompliant: kycProfiles.count || 0,
        sanctionsScreened: sanctions.count || 0,
        transactionsMonitored: transactions.count || 0,
        alertsGenerated: alerts.count || 0
      },
      details: {
        users: users.data,
        kycProfiles: kycProfiles.data,
        sanctions: sanctions.data,
        transactions: transactions.data,
        alerts: alerts.data
      }
    };
  }
}

export default ComplianceService;
