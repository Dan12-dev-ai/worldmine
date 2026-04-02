/**
 * User Trust and Verification Service
 * Handles KYC, identity verification, mining license validation, and document authenticity
 */

import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database';

const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

// Types
export interface KYCData {
  userId: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  nationality: string;
  address: Address;
  phone: string;
  email: string;
  idDocument?: VerificationDocument;
  addressProof?: VerificationDocument;
  selfie?: VerificationDocument;
  businessRegistration?: VerificationDocument;
  taxId?: string;
}

export interface VerificationDocument {
  id: string;
  type: 'id_document' | 'passport' | 'drivers_license' | 'address_proof' | 'selfie' | 'business_registration' | 'mining_license' | 'environmental_certificate' | 'quality_certificate';
  url: string;
  thumbnail?: string;
  size: number;
  uploadedAt: string;
  status: 'pending' | 'verified' | 'rejected';
  extractedData?: any;
}

export interface KYCSession {
  id: string;
  userId: string;
  status: 'initiated' | 'pending_documents' | 'under_review' | 'verified' | 'rejected';
  provider: 'stripe_identity' | 'sumsub' | 'onfido';
  sessionId: string;
  expiresAt: string;
  createdAt: string;
}

export interface KYCStatus {
  status: 'not_started' | 'initiated' | 'pending_documents' | 'under_review' | 'verified' | 'rejected';
  level: 0 | 1 | 2 | 3; // Verification levels
  requirements: string[];
  nextSteps: string[];
  estimatedTime: string;
}

export interface MiningLicense {
  id: string;
  licenseNumber: string;
  issuingCountry: string;
  licenseType: 'exploration' | 'extraction' | 'processing' | 'export' | 'trading';
  mineralTypes: string[];
  expiryDate: string;
  status: 'active' | 'expired' | 'suspended' | 'revoked';
  documentUrl: string;
  verified: boolean;
  verifiedAt?: string;
}

export interface LicenseValidation {
  valid: boolean;
  license: MiningLicense;
  issues: string[];
  warnings: string[];
  expiryStatus: 'valid' | 'expiring_soon' | 'expired';
  authenticityScore: number; // 0-100
}

export interface AuthenticityResult {
  authentic: boolean;
  confidence: number; // 0-100
  issues: string[];
  warnings: string[];
  analysisDetails: {
    documentIntegrity: boolean;
    metadataConsistency: boolean;
    visualAnalysis: boolean;
    digitalSignature: boolean;
  };
}

export interface IdentityData {
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  nationality: string;
  address: Address;
  phone: string;
  email: string;
  idNumber?: string;
  passportNumber?: string;
  driversLicenseNumber?: string;
}

export interface VerificationResult {
  success: boolean;
  verificationId: string;
  status: string;
  confidence?: number;
  issues?: string[];
  extractedData?: any;
}

export interface DocumentVerification {
  authentic: boolean;
  confidence: number;
  documentType: string;
  extractedFields: Record<string, any>;
  securityFeatures: {
    hologram: boolean;
    watermark: boolean;
    microprint: boolean;
    digitalSignature: boolean;
  };
  issues: string[];
}

export interface ExpiryStatus {
  valid: boolean;
  daysUntilExpiry: number;
  status: 'valid' | 'expiring_soon' | 'expired';
  expiryDate: string;
}

// Verification Provider Interfaces
export interface VerificationProvider {
  name: string;
  verifyIdentity(data: IdentityData): Promise<VerificationResult>;
  verifyDocument(document: VerificationDocument): Promise<DocumentVerification>;
  checkVerificationStatus(sessionId: string): Promise<KYCStatus>;
}

// Stripe Identity Provider
export class StripeIdentityProvider implements VerificationProvider {
  name = 'stripe_identity';
  private stripe: any;

  constructor() {
    // Initialize Stripe Identity
    this.stripe = null; // Will be initialized with actual Stripe SDK
  }

  async verifyIdentity(data: IdentityData): Promise<VerificationResult> {
    try {
      const verificationSession = await this.stripe.identity.verificationSessions.create({
        type: 'id_number',
        metadata: {
          firstName: data.firstName,
          lastName: data.lastName,
          dateOfBirth: data.dateOfBirth,
          nationality: data.nationality
        }
      });

      return {
        success: true,
        verificationId: verificationSession.id,
        status: verificationSession.status,
        confidence: 85
      };
    } catch (error) {
      return {
        success: false,
        verificationId: '',
        status: 'failed',
        issues: [error.message]
      };
    }
  }

  async verifyDocument(document: VerificationDocument): Promise<DocumentVerification> {
    try {
      // Use Stripe's document verification API
      const verification = await this.stripe.identity.verificationReports.create({
        document: {
          front: document.url,
          type: this.mapDocumentType(document.type)
        }
      });

      return {
        authentic: verification.status === 'verified',
        confidence: verification.confidence || 80,
        documentType: document.type,
        extractedFields: verification.extractedFields || {},
        securityFeatures: {
          hologram: verification.securityFeatures?.hologram || false,
          watermark: verification.securityFeatures?.watermark || false,
          microprint: verification.securityFeatures?.microprint || false,
          digitalSignature: verification.securityFeatures?.digitalSignature || false
        },
        issues: verification.issues || []
      };
    } catch (error) {
      return {
        authentic: false,
        confidence: 0,
        documentType: document.type,
        extractedFields: {},
        securityFeatures: {
          hologram: false,
          watermark: false,
          microprint: false,
          digitalSignature: false
        },
        issues: [error.message]
      };
    }
  }

  async checkVerificationStatus(sessionId: string): Promise<KYCStatus> {
    try {
      const session = await this.stripe.identity.verificationSessions.retrieve(sessionId);
      
      return {
        status: this.mapStripeStatus(session.status),
        level: session.status === 'verified' ? 3 : 1,
        requirements: session.requirements || [],
        nextSteps: this.getNextSteps(session.status),
        estimatedTime: '1-3 business days'
      };
    } catch (error) {
      return {
        status: 'failed',
        level: 0,
        requirements: [],
        nextSteps: ['Contact support'],
        estimatedTime: 'Unknown'
      };
    }
  }

  private mapDocumentType(type: string): string {
    const mapping: Record<string, string> = {
      'id_document': 'id_number',
      'passport': 'passport',
      'drivers_license': 'driving_license',
      'address_proof': 'proof_of_address',
      'selfie': 'selfie'
    };
    return mapping[type] || 'document';
  }

  private mapStripeStatus(status: string): KYCStatus['status'] {
    const mapping: Record<string, KYCStatus['status']> = {
      'requires_input': 'pending_documents',
      'processing': 'under_review',
      'verified': 'verified',
      'requires_action': 'rejected'
    };
    return mapping[status] || 'failed';
  }

  private getNextSteps(status: string): string[] {
    const steps: Record<string, string[]> = {
      'requires_input': ['Upload required documents'],
      'processing': ['Wait for review', 'Check email for updates'],
      'verified': ['Verification complete', 'Full platform access granted'],
      'requires_action': ['Review rejection reasons', 'Contact support if needed']
    };
    return steps[status] || ['Contact support'];
  }
}

// Sumsub Provider
export class SumsubProvider implements VerificationProvider {
  name = 'sumsub';
  private sumsub: any;

  constructor() {
    // Initialize Sumsub SDK
    this.sumsub = null; // Will be initialized with Sumsub SDK
  }

  async verifyIdentity(data: IdentityData): Promise<VerificationResult> {
    try {
      const applicant = await this.sumsub.applications.create({
        externalUserId: data.email,
        info: {
          firstName: data.firstName,
          lastName: data.lastName,
          dateOfBirth: data.dateOfBirth,
          nationality: data.nationality,
          address: data.address
        }
      });

      return {
        success: true,
        verificationId: applicant.id,
        status: applicant.reviewStatus,
        confidence: 90
      };
    } catch (error) {
      return {
        success: false,
        verificationId: '',
        status: 'failed',
        issues: [error.message]
      };
    }
  }

  async verifyDocument(document: VerificationDocument): Promise<DocumentVerification> {
    try {
      const inspection = await this.sumsub.inspections.create({
        type: this.mapDocumentType(document.type),
        imageId: document.id,
        countryCode: document.metadata?.countryCode || 'US'
      });

      return {
        authentic: inspection.result === 'OK',
        confidence: inspection.confidence || 85,
        documentType: document.type,
        extractedFields: inspection.extractedData || {},
        securityFeatures: {
          hologram: inspection.securityFeatures?.hologram || false,
          watermark: inspection.securityFeatures?.watermark || false,
          microprint: inspection.securityFeatures?.microprint || false,
          digitalSignature: inspection.securityFeatures?.digitalSignature || false
        },
        issues: inspection.issues || []
      };
    } catch (error) {
      return {
        authentic: false,
        confidence: 0,
        documentType: document.type,
        extractedFields: {},
        securityFeatures: {
          hologram: false,
          watermark: false,
          microprint: false,
          digitalSignature: false
        },
        issues: [error.message]
      };
    }
  }

  async checkVerificationStatus(sessionId: string): Promise<KYCStatus> {
    try {
      const application = await this.sumsub.applications.get(sessionId);
      
      return {
        status: this.mapSumsubStatus(application.reviewStatus),
        level: application.reviewStatus === 'COMPLETED' ? 3 : 1,
        requirements: application.requiredDocs?.map((doc: any) => doc.type) || [],
        nextSteps: this.getNextSteps(application.reviewStatus),
        estimatedTime: '1-5 business days'
      };
    } catch (error) {
      return {
        status: 'failed',
        level: 0,
        requirements: [],
        nextSteps: ['Contact support'],
        estimatedTime: 'Unknown'
      };
    }
  }

  private mapDocumentType(type: string): string {
    const mapping: Record<string, string> = {
      'id_document': 'IDENTITY',
      'passport': 'PASSPORT',
      'drivers_license': 'DRIVING_LICENSE',
      'address_proof': 'PROOF_OF_ADDRESS',
      'selfie': 'SELFIE',
      'business_registration': 'BUSINESS_REGISTRATION',
      'mining_license': 'MINING_LICENSE'
    };
    return mapping[type] || 'DOCUMENT';
  }

  private mapSumsubStatus(status: string): KYCStatus['status'] {
    const mapping: Record<string, KYCStatus['status']> = {
      'INIT': 'pending_documents',
      'PRECHECKED': 'under_review',
      'COMPLETED': 'verified',
      'REJECTED': 'rejected'
    };
    return mapping[status] || 'failed';
  }

  private getNextSteps(status: string): string[] {
    const steps: Record<string, string[]> = {
      'INIT': ['Upload required documents'],
      'PRECHECKED': ['Wait for review', 'Check email for updates'],
      'COMPLETED': ['Verification complete', 'Full platform access granted'],
      'REJECTED': ['Review rejection reasons', 'Contact support if needed']
    };
    return steps[status] || ['Contact support'];
  }
}

// Main Verification Service
export class VerificationService {
  private static instance: VerificationService;
  private providers: Map<string, VerificationProvider> = new Map();

  private constructor() {
    // Initialize verification providers
    this.providers.set('stripe_identity', new StripeIdentityProvider());
    this.providers.set('sumsub', new SumsubProvider());
  }

  static getInstance(): VerificationService {
    if (!VerificationService.instance) {
      VerificationService.instance = new VerificationService();
    }
    return VerificationService.instance;
  }

  // KYC Management
  async initiateKYC(userId: string, kycData: KYCData, provider: string = 'stripe_identity'): Promise<KYCSession> {
    try {
      const verificationProvider = this.providers.get(provider);
      if (!verificationProvider) {
        throw new Error('Verification provider not supported');
      }

      // Create KYC session
      const { data: session, error } = await supabase
        .from('kyc_sessions')
        .insert({
          userId,
          status: 'initiated',
          provider,
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 hours
          createdAt: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;

      // Start identity verification
      const identityResult = await verificationProvider.verifyIdentity({
        firstName: kycData.firstName,
        lastName: kycData.lastName,
        dateOfBirth: kycData.dateOfBirth,
        nationality: kycData.nationality,
        address: kycData.address,
        phone: kycData.phone,
        email: kycData.email
      });

      // Update session with verification result
      await supabase
        .from('kyc_sessions')
        .update({
          status: identityResult.success ? 'pending_documents' : 'rejected',
          sessionId: identityResult.verificationId
        })
        .eq('id', session.id);

      return session;
    } catch (error) {
      console.error('Error initiating KYC:', error);
      throw error;
    }
  }

  async uploadDocument(
    sessionId: string,
    document: VerificationDocument
  ): Promise<VerificationDocument> {
    try {
      // Upload document to storage
      const { data: uploadedDoc, error } = await supabase
        .from('verification_documents')
        .insert({
          ...document,
          status: 'pending'
        })
        .select()
        .single();

      if (error) throw error;

      // Update session status
      await supabase
        .from('kyc_sessions')
        .update({
          status: 'pending_documents'
        })
        .eq('id', sessionId);

      return uploadedDoc;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }

  async checkVerificationStatus(sessionId: string): Promise<KYCStatus> {
    try {
      const { data: session, error } = await supabase
        .from('kyc_sessions')
        .select('*')
        .eq('id', sessionId)
        .single();

      if (error) throw error;

      const provider = this.providers.get(session.provider);
      if (!provider) {
        throw new Error('Verification provider not supported');
      }

      return await provider.checkVerificationStatus(session.sessionId);
    } catch (error) {
      console.error('Error checking verification status:', error);
      throw error;
    }
  }

  async getVerificationLevel(userId: string): Promise<VerificationLevel> {
    try {
      const { data: session, error } = await supabase
        .from('kyc_sessions')
        .select('status, level')
        .eq('userId', userId)
        .order('createdAt', { ascending: false })
        .limit(1)
        .single();

      if (error) {
        return {
          status: 'not_started',
          level: 0,
          requirements: ['Complete KYC process'],
          nextSteps: ['Start identity verification'],
          estimatedTime: '5-10 minutes'
        };
      }

      return {
        status: session.status as KYCStatus['status'],
        level: session.level || 1,
        requirements: [],
        nextSteps: [],
        estimatedTime: 'Completed'
      };
    } catch (error) {
      console.error('Error getting verification level:', error);
      throw error;
    }
  }

  // Mining License Validation
  async validateLicense(
    licenseNumber: string,
    issuingCountry: string,
    licenseType: string
  ): Promise<LicenseValidation> {
    try {
      // Check if license exists in our database
      const { data: existingLicense, error } = await supabase
        .from('mining_licenses')
        .select('*')
        .eq('licenseNumber', licenseNumber)
        .eq('issuingCountry', issuingCountry)
        .eq('licenseType', licenseType)
        .single();

      if (error) {
        return {
          valid: false,
          license: null as any,
          issues: ['License not found in records'],
          warnings: [],
          expiryStatus: {
            valid: false,
            daysUntilExpiry: 0,
            status: 'expired',
            expiryDate: ''
          },
          authenticityScore: 0
        };
      }

      // Check expiry
      const expiryDate = new Date(existingLicense.expiryDate);
      const now = new Date();
      const daysUntilExpiry = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

      const expiryStatus: ExpiryStatus = {
        valid: daysUntilExpiry > 0,
        daysUntilExpiry,
        status: daysUntilExpiry > 30 ? 'valid' : daysUntilExpiry > 0 ? 'expiring_soon' : 'expired',
        expiryDate: existingLicense.expiryDate
      };

      // Perform authenticity check
      const authenticityResult = await this.verifyLicenseAuthenticity(existingLicense);

      return {
        valid: expiryStatus.valid && existingLicense.verified,
        license: existingLicense,
        issues: [
          ...(expiryStatus.status === 'expired' ? ['License has expired'] : []),
          ...(!existingLicense.verified ? ['License not verified'] : []),
          ...authenticityResult.issues
        ],
        warnings: [
          ...(expiryStatus.status === 'expiring_soon' ? ['License expires soon'] : [])
        ],
        expiryStatus,
        authenticityScore: authenticityResult.confidence
      };
    } catch (error) {
      console.error('Error validating license:', error);
      throw error;
    }
  }

  async verifyAuthenticity(license: MiningLicense): Promise<AuthenticityResult> {
    try {
      // AI-powered document analysis
      const analysis = await this.analyzeDocument(license.documentUrl);

      return {
        authentic: analysis.authentic,
        confidence: analysis.confidence,
        issues: analysis.issues,
        warnings: analysis.warnings,
        analysisDetails: {
          documentIntegrity: analysis.documentIntegrity,
          metadataConsistency: analysis.metadataConsistency,
          visualAnalysis: analysis.visualAnalysis,
          digitalSignature: analysis.digitalSignature
        }
      };
    } catch (error) {
      console.error('Error verifying authenticity:', error);
      return {
        authentic: false,
        confidence: 0,
        issues: [error.message],
        warnings: [],
        analysisDetails: {
          documentIntegrity: false,
          metadataConsistency: false,
          visualAnalysis: false,
          digitalSignature: false
        }
      };
    }
  }

  private async analyzeDocument(documentUrl: string): Promise<any> {
    // In production, integrate with AI service for document analysis
    // For now, return mock analysis
    return {
      authentic: true,
      confidence: 85,
      documentIntegrity: true,
      metadataConsistency: true,
      visualAnalysis: true,
      digitalSignature: true,
      issues: [],
      warnings: []
    };
  }

  async checkExpiry(licenseId: string): Promise<ExpiryStatus> {
    try {
      const { data: license, error } = await supabase
        .from('mining_licenses')
        .select('expiryDate')
        .eq('id', licenseId)
        .single();

      if (error) {
        return {
          valid: false,
          daysUntilExpiry: 0,
          status: 'expired',
          expiryDate: ''
        };
      }

      const expiryDate = new Date(license.expiryDate);
      const now = new Date();
      const daysUntilExpiry = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

      return {
        valid: daysUntilExpiry > 0,
        daysUntilExpiry,
        status: daysUntilExpiry > 30 ? 'valid' : daysUntilExpiry > 0 ? 'expiring_soon' : 'expired',
        expiryDate: license.expiryDate
      };
    } catch (error) {
      console.error('Error checking expiry:', error);
      throw error;
    }
  }

  // Document Management
  async getUserDocuments(userId: string): Promise<VerificationDocument[]> {
    try {
      const { data, error } = await supabase
        .from('verification_documents')
        .select('*')
        .eq('userId', userId)
        .order('uploadedAt', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error getting user documents:', error);
      throw error;
    }
  }

  async updateDocumentStatus(
    documentId: string,
    status: VerificationDocument['status'],
    extractedData?: any
  ): Promise<VerificationDocument> {
    try {
      const { data, error } = await supabase
        .from('verification_documents')
        .update({
          status,
          extractedData
        })
        .eq('id', documentId)
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error updating document status:', error);
      throw error;
    }
  }

  // Trust Score Calculation
  async calculateTrustScore(userId: string): Promise<number> {
    try {
      // Get user's verification status
      const kycStatus = await this.getVerificationLevel(userId);
      
      // Get user's transaction history
      const { data: transactions } = await supabase
        .from('transactions')
        .select('status, amount')
        .eq('buyerId', userId);

      // Get user's reviews
      const { data: reviews } = await supabase
        .from('reviews')
        .select('rating')
        .eq('reviewerId', userId);

      // Calculate trust score (0-100)
      let score = 0;

      // KYC verification (40 points)
      if (kycStatus.level === 3) score += 40;
      else if (kycStatus.level === 2) score += 25;
      else if (kycStatus.level === 1) score += 10;

      // Transaction history (30 points)
      const completedTransactions = transactions?.filter(tx => tx.status === 'completed') || [];
      if (completedTransactions.length > 10) score += 30;
      else if (completedTransactions.length > 5) score += 20;
      else if (completedTransactions.length > 0) score += 10;

      // Reviews (30 points)
      const avgRating = reviews?.length 
        ? reviews.reduce((sum: number, review: any) => sum + review.rating, 0) / reviews.length
        : 0;
      if (avgRating >= 4.5) score += 30;
      else if (avgRating >= 4.0) score += 20;
      else if (avgRating >= 3.5) score += 10;

      // Account age (bonus points)
      const accountAge = Date.now() - new Date(kycStatus.estimatedTime).getTime();
      const daysOld = Math.floor(accountAge / (1000 * 60 * 60 * 24));
      if (daysOld > 365) score += 10;
      else if (daysOld > 180) score += 5;

      return Math.min(score, 100);
    } catch (error) {
      console.error('Error calculating trust score:', error);
      throw error;
    }
  }
}

export default VerificationService;
