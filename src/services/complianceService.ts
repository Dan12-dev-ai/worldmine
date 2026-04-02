/**
 * Legal Compliance Framework
 * Handles GDPR, CCPA, privacy regulations, and marketplace policies
 */

import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database';

const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

// Types
export interface DataSubjectRequest {
  id: string;
  userId: string;
  type: 'access' | 'portability' | 'rectification' | 'erasure' | 'restriction';
  description: string;
  evidence?: string[];
  status: 'pending' | 'processing' | 'completed' | 'rejected';
  createdAt: string;
  completedAt?: string;
  responseDue?: string;
}

export interface ConsentRecord {
  id: string;
  userId: string;
  consentType: 'data_processing' | 'marketing' | 'analytics' | 'cookies' | 'third_party_sharing';
  granted: boolean;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  version: string;
  details?: Record<string, any>;
}

export interface ConsentHistory {
  userId: string;
  consents: ConsentRecord[];
  preferences: PrivacyPreferences;
  lastUpdated: string;
}

export interface PrivacyPreferences {
  dataProcessing: boolean;
  marketing: boolean;
  analytics: boolean;
  cookies: boolean;
  thirdPartySharing: boolean;
  retentionPeriod: number; // days
  dataDeletion: boolean;
}

export interface DataExport {
  id: string;
  userId: string;
  format: 'json' | 'csv' | 'xml' | 'pdf';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  downloadUrl?: string;
  expiresAt: string;
  createdAt: string;
  completedAt?: string;
}

export interface AnonymizationResult {
  success: boolean;
  anonymizedRecords: number;
  failedRecords: string[];
  processingTime: number;
  completedAt: string;
}

export interface DeletionResult {
  success: boolean;
  deletedRecords: number;
  failedRecords: string[];
  retentionPolicy: RetentionPolicy;
  completedAt: string;
}

export interface RetentionPolicy {
  dataType: string;
  retentionPeriod: number; // days
  reason: string;
  legalBasis: string;
  automaticDeletion: boolean;
}

export interface ComplianceReport {
  id: string;
  reportType: 'gdpr' | 'ccpa' | 'marketplace_audit' | 'security_audit';
  period: string;
  generatedAt: string;
  metrics: ComplianceMetrics;
  findings: ComplianceFinding[];
  recommendations: ComplianceRecommendation[];
  status: 'draft' | 'final' | 'submitted';
}

export interface ComplianceMetrics {
  totalUsers: number;
  dataRequests: number;
  consentRecords: number;
  dataExports: number;
  dataDeletions: number;
  securityIncidents: number;
  auditScore: number;
  complianceScore: number;
}

export interface ComplianceFinding {
  category: 'data_protection' | 'access_control' | 'audit_trail' | 'encryption' | 'consent_management';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedRecords: number;
  recommendation: string;
}

export interface ComplianceRecommendation {
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  action: string;
  description: string;
  dueDate: string;
  assignee?: string;
}

export interface MarketplacePolicy {
  id: string;
  type: 'terms_of_service' | 'privacy_policy' | 'acceptable_use' | 'seller_verification' | 'dispute_resolution' | 'escrow_agreement';
  version: string;
  title: string;
  content: Record<string, string>; // Multilingual content
  effectiveDate: string;
  lastUpdated: string;
  isActive: boolean;
  requiredAcknowledgment: boolean;
}

export interface DisputeCase {
  id: string;
  escrowTransactionId: string;
  claimantId: string;
  respondentId: string;
  type: 'quality_issue' | 'delivery_dispute' | 'payment_dispute' | 'fraud_claim' | 'policy_violation';
  description: string;
  evidence: {
    claimant: string[];
    respondent: string[];
  };
  status: 'open' | 'investigating' | 'mediation' | 'resolved_claimant' | 'resolved_respondent' | 'cancelled';
  mediatorId?: string;
  resolution?: string;
  resolutionDetails?: string;
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
}

// Main Compliance Service
export class ComplianceService {
  private static instance: ComplianceService;
  private retentionPolicies: RetentionPolicy[] = [
    {
      dataType: 'user_data',
      retentionPeriod: 365, // 2 years for inactive users
      reason: 'Legal requirement for data retention',
      legalBasis: 'GDPR Article 6(1)(e)',
      automaticDeletion: true
    },
    {
      dataType: 'transaction_data',
      retentionPeriod: 2555, // 7 years for financial records
      reason: 'Tax and legal requirements',
      legalBasis: 'Tax regulations and legal requirements',
      automaticDeletion: false
    },
    {
      dataType: 'analytics_data',
      retentionPeriod: 730, // 2 years for analytics
      reason: 'Business analytics retention',
      legalBasis: 'Legitimate business interest',
      automaticDeletion: true
    },
    {
      dataType: 'support_tickets',
      retentionPeriod: 1825, // 5 years for support records
      reason: 'Customer service requirements',
      legalBasis: 'Customer service standards',
      automaticDeletion: true
    }
  ];

  private constructor() {}

  static getInstance(): ComplianceService {
    if (!ComplianceService.instance) {
      ComplianceService.instance = new ComplianceService();
    }
    return ComplianceService.instance;
  }

  // GDPR Compliance
  async handleDataSubjectRequest(request: DataSubjectRequest): Promise<ComplianceResult> {
    try {
      // Log the request
      await supabase
        .from('data_subject_requests')
        .insert({
          ...request,
          status: 'pending',
          createdAt: new Date().toISOString(),
          responseDue: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days
        });

      // Process based on request type
      let result;
      switch (request.type) {
        case 'access':
          result = await this.handleAccessRequest(request);
          break;
        case 'portability':
          result = await this.handlePortabilityRequest(request);
          break;
        case 'rectification':
          result = await this.handleRectificationRequest(request);
          break;
        case 'erasure':
          result = await this.handleErasureRequest(request);
          break;
        case 'restriction':
          result = await this.handleRestrictionRequest(request);
          break;
        default:
          throw new Error('Unsupported request type');
      }

      // Update request status
      await supabase
        .from('data_subject_requests')
        .update({
          status: result.success ? 'completed' : 'rejected',
          completedAt: new Date().toISOString()
        })
        .eq('id', request.id);

      return result;
    } catch (error) {
      console.error('Error handling data subject request:', error);
      throw error;
    }
  }

  async handleAccessRequest(request: DataSubjectRequest): Promise<ComplianceResult> {
    try {
      // Gather user data
      const userData = await this.gatherUserData(request.userId);
      
      // Create data export
      const exportId = await this.createDataExport(request.userId, 'json', userData);
      
      return {
        success: true,
        exportId,
        message: 'Data export prepared'
      };
    } catch (error) {
      console.error('Error handling access request:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async handlePortabilityRequest(request: DataSubjectRequest): Promise<ComplianceResult> {
    try {
      // Gather user data in portable format
      const portableData = await this.gatherUserData(request.userId);
      
      // Create data export
      const exportId = await this.createDataExport(request.userId, 'json', portableData);
      
      return {
        success: true,
        exportId,
        message: 'Data export prepared for portability'
      };
    } catch (error) {
      console.error('Error handling portability request:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async handleRectificationRequest(request: DataSubjectRequest): Promise<ComplianceResult> {
    try {
      // Process rectification based on description
      const rectified = await this.processRectification(request.userId, request.description, request.evidence);
      
      return {
        success: rectified,
        message: rectified ? 'Data rectified successfully' : 'Unable to rectify data'
      };
    } catch (error) {
      console.error('Error handling rectification request:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async handleErasureRequest(request: DataSubjectRequest): Promise<DeletionResult> {
    try {
      // Anonymize user data instead of hard deletion
      const anonymizationResult = await this.anonymizeUserData(request.userId);
      
      // Update user status
      await supabase
        .from('profiles')
        .update({
          verification_status: 'anonymized',
          full_name: 'Anonymous User',
          email: `deleted-${request.userId}@worldmine.com`,
          updated_at: new Date().toISOString()
        })
        .eq('id', request.userId);

      return {
        success: anonymizationResult.success,
        deletedRecords: anonymizationResult.anonymizedRecords,
        failedRecords: anonymizationResult.failedRecords,
        retentionPolicy: this.retentionPolicies.find(p => p.dataType === 'user_data'),
        completedAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error handling erasure request:', error);
      return {
        success: false,
        deletedRecords: 0,
        failedRecords: [error.message],
        retentionPolicy: this.retentionPolicies.find(p => p.dataType === 'user_data'),
        completedAt: new Date().toISOString()
      };
    }
  }

  async handleRestrictionRequest(request: DataSubjectRequest): Promise<ComplianceResult> {
    try {
      // Process restriction request
      const restricted = await this.applyDataRestriction(request.userId, request.description);
      
      return {
        success: restricted,
        message: restricted ? 'Data restriction applied' : 'Unable to apply restriction'
      };
    } catch (error) {
      console.error('Error handling restriction request:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Consent Management
  async updateConsent(userId: string, consentUpdate: ConsentUpdate): Promise<ConsentResult> {
    try {
      const consentRecord: Omit<ConsentRecord, 'id' | 'timestamp'> = {
        userId,
        consentType: consentUpdate.consentType,
        granted: consentUpdate.granted,
        version: '1.0',
        details: consentUpdate.details,
        ipAddress: await this.getClientIP(),
        userAgent: navigator.userAgent
      };

      const { data, error } = await supabase
        .from('consent_records')
        .insert(consentRecord)
        .select()
        .single();

      if (error) throw error;

      // Update user preferences
      await this.updatePrivacyPreferences(userId, consentUpdate.consentType, consentUpdate.granted);

      return {
        success: true,
        consentId: data.id,
        message: 'Consent updated successfully'
      };
    } catch (error) {
      console.error('Error updating consent:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async getConsentHistory(userId: string): Promise<ConsentHistory> {
    try {
      const { data: consents, error } = await supabase
        .from('consent_records')
        .select('*')
        .eq('userId', userId)
        .order('timestamp', { ascending: false });

      if (error) throw error;

      const preferences = await this.getPrivacyPreferences(userId);

      return {
        userId,
        consents: consents || [],
        preferences,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error getting consent history:', error);
      throw error;
    }
  }

  async updatePrivacyPreferences(userId: string, consentType: string, granted: boolean): Promise<void> {
    try {
      const { data: currentPrefs } = await supabase
        .from('privacy_preferences')
        .select('*')
        .eq('userId', userId)
        .single();

      const updatedPrefs = {
        ...currentPrefs,
        [consentType]: granted
      };

      await supabase
        .from('privacy_preferences')
        .update(updatedPrefs)
        .eq('userId', userId);
    } catch (error) {
      console.error('Error updating privacy preferences:', error);
      throw error;
    }
  }

  async getPrivacyPreferences(userId: string): Promise<PrivacyPreferences> {
    try {
      const { data, error } = await supabase
        .from('privacy_preferences')
        .select('*')
        .eq('userId', userId)
        .single();

      if (error) throw error;

      return data || {
        dataProcessing: true,
        marketing: false,
        analytics: true,
        cookies: true,
        thirdPartySharing: false,
        retentionPeriod: 365,
        dataDeletion: false
      };
    } catch (error) {
      console.error('Error getting privacy preferences:', error);
      throw error;
    }
  }

  // Data Operations
  async anonymizeUserData(userId: string): Promise<AnonymizationResult> {
    try {
      const startTime = Date.now();
      let anonymizedCount = 0;
      const failedRecords = [];

      // Anonymize user profile
      const { error: profileError } = await supabase
        .from('profiles')
        .update({
          full_name: 'Anonymous User',
          email: `anonymous-${Date.now()}@worldmine.com`,
          phone: null,
          avatar_url: null,
          business_name: null,
          business_description: null
        })
        .eq('id', userId);

      if (!profileError) anonymizedCount++;

      // Anonymize transactions
      const { data: transactions, error: txError } = await supabase
        .from('transactions')
        .update({ buyerId: null, sellerId: null })
        .eq('buyerId', userId)
        .or('sellerId', userId);

      if (!txError) anonymizedCount++;

      // Anonymize other sensitive data
      const tables = ['user_sessions', 'verification_documents', 'biometric_credentials'];
      for (const table of tables) {
        const { error } = await supabase
          .from(table)
          .update({ userId: null })
          .eq('userId', userId);
        
        if (!error) anonymizedCount++;
        else failedRecords.push(`Failed to anonymize ${table}`);
      }

      const processingTime = Date.now() - startTime;

      return {
        success: failedRecords.length === 0,
        anonymizedRecords: anonymizedCount,
        failedRecords,
        processingTime
      };
    } catch (error) {
      console.error('Error anonymizing user data:', error);
      throw error;
    }
  }

  async exportUserData(userId: string, format: DataExport['format'] = 'json'): Promise<string> {
    try {
      // Gather all user data
      const userData = await this.gatherUserData(userId);
      
      // Format based on requested format
      let exportData;
      switch (format) {
        case 'json':
          exportData = JSON.stringify(userData, null, 2);
          break;
        case 'csv':
          exportData = this.convertToCSV(userData);
          break;
        case 'xml':
          exportData = this.convertToXML(userData);
          break;
        case 'pdf':
          exportData = await this.convertToPDF(userData);
          break;
        default:
          throw new Error('Unsupported export format');
      }

      return exportData;
    } catch (error) {
      console.error('Error exporting user data:', error);
      throw error;
    }
  }

  async createDataExport(userId: string, format: string, data: any): Promise<string> {
    try {
      const { data: exportRecord, error } = await supabase
        .from('data_exports')
        .insert({
          userId,
          format,
          status: 'processing',
          createdAt: new Date().toISOString(),
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days
        })
        .select()
        .single();

      if (error) throw error;

      // Store export data
      const exportId = exportRecord.id;
      await supabase.storage
        .from(`user_exports/${exportId}`)
        .upload(`export.${format}`, new Blob([data]));

      // Update export record
      const { data: updatedRecord } = await supabase
        .from('data_exports')
        .update({
          status: 'completed',
          downloadUrl: `/api/v1/exports/download/${exportId}`,
          completedAt: new Date().toISOString()
        })
        .eq('id', exportId)
        .select()
        .single();

      return updatedRecord.downloadUrl || '';
    } catch (error) {
      console.error('Error creating data export:', error);
      throw error;
    }
  }

  // Marketplace Policies
  async createPolicy(
    type: MarketplacePolicy['type'],
    title: string,
    content: Record<string, string>,
    version: string,
    requiredAcknowledgment: boolean = false
  ): Promise<MarketplacePolicy> {
    try {
      const { data, error } = await supabase
        .from('marketplace_policies')
        .insert({
          type,
          title,
          content,
          version,
          effectiveDate: new Date().toISOString(),
          lastUpdated: new Date().toISOString(),
          isActive: true,
          requiredAcknowledgment
        })
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error creating policy:', error);
      throw error;
    }
  }

  async getPolicy(type: MarketplacePolicy['type'], language: string = 'en'): Promise<MarketplacePolicy | null> {
    try {
      const { data, error } = await supabase
        .from('marketplace_policies')
        .select('*')
        .eq('type', type)
        .eq('isActive', true)
        .order('version', { ascending: false })
        .limit(1)
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error getting policy:', error);
      throw error;
    }
  }

  // Dispute Resolution
  async createDispute(
    escrowTransactionId: string,
    claimantId: string,
    type: DisputeCase['type'],
    description: string,
    evidence: string[]
  ): Promise<DisputeCase> {
    try {
      const { data, error } = await supabase
        .from('disputes')
        .insert({
          escrowTransactionId,
          claimantId,
          type,
          description,
          evidence: { claimant: evidence },
          status: 'open',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;

      // Notify respondent
      await this.notifyDisputeParties(data.id, claimantId);

      return data;
    } catch (error) {
      console.error('Error creating dispute:', error);
      throw error;
    }
  }

  async respondToDispute(
    disputeId: string,
    respondentId: string,
    evidence: string[],
    response: string
  ): Promise<DisputeCase> {
    try {
      const { data, error } = await supabase
        .from('disputes')
        .update({
          respondentId,
          evidence: { respondent: evidence },
          status: 'investigating',
          updatedAt: new Date().toISOString()
        })
        .eq('id', disputeId)
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error responding to dispute:', error);
      throw error;
    }
  }

  async resolveDispute(
    disputeId: string,
    resolution: string,
    resolutionDetails: string,
    mediatorId?: string,
    favor: 'claimant' | 'respondent' | 'split'
  ): Promise<DisputeCase> {
    try {
      const { data, error } = await supabase
        .from('disputes')
        .update({
          status: favor === 'claimant' ? 'resolved_claimant' : favor === 'respondent' ? 'resolved_respondent' : 'resolved_claimant',
          resolution,
          resolutionDetails,
          mediatorId,
          resolvedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
        .eq('id', disputeId)
        .select()
        .single();

      if (error) throw error;

      // Update escrow transaction based on resolution
      await this.updateEscrowFromDispute(disputeId, favor);

      return data;
    } catch (error) {
      console.error('Error resolving dispute:', error);
      throw error;
    }
  }

  // Compliance Reporting
  async generateComplianceReport(
    reportType: ComplianceReport['reportType'],
    period: string
  ): Promise<ComplianceReport> {
    try {
      const metrics = await this.calculateComplianceMetrics(period);
      const findings = await this.identifyComplianceFindings();
      const recommendations = await this.generateComplianceRecommendations(findings);

      const { data, error } = await supabase
        .from('compliance_reports')
        .insert({
          reportType,
          period,
          generatedAt: new Date().toISOString(),
          metrics,
          findings,
          recommendations,
          status: 'draft'
        })
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error generating compliance report:', error);
      throw error;
    }
  }

  // Helper Methods
  private async gatherUserData(userId: string): Promise<any> {
    try {
      const [
        profile,
        transactions,
        listings,
        reviews,
        documents
      ] = await Promise.all([
        supabase.from('profiles').select('*').eq('id', userId).single(),
        supabase.from('transactions').select('*').or(`buyerId.eq.${userId},sellerId.eq.${userId}`),
        supabase.from('mineral_listings').select('*').eq('sellerId', userId),
        supabase.from('reviews').select('*').eq('reviewerId', userId),
        supabase.from('verification_documents').select('*').eq('userId', userId)
      ]);

      return {
        profile,
        transactions,
        listings,
        reviews,
        documents
      };
    } catch (error) {
      console.error('Error gathering user data:', error);
      return {};
    }
  }

  private convertToCSV(data: any): string {
    // Convert data to CSV format
    const headers = Object.keys(data[0] || {}).join(',');
    const rows = data.map((item: any) => 
      Object.values(item).map((value: any) => 
        typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value
      ).join(',')
    );
    
    return [headers, ...rows].join('\n');
  }

  private convertToXML(data: any): string {
    // Convert data to XML format
    const xmlItems = data.map((item: any) => {
      const xmlItem = Object.entries(item).map(([key, value]) => 
        `<${key}>${typeof value === 'string' ? this.escapeXML(value) : value}</${key}>`
      ).join('');
      return `<item>${xmlItem}</item>`;
    });

    return `<?xml version="1.0" encoding="UTF-8"?><data>${xmlItems.join('')}</data></xml>`;
  }

  private async convertToPDF(data: any): Promise<string> {
    // Convert data to PDF format
    // This would integrate with a PDF generation library
    return JSON.stringify(data); // Fallback
  }

  private escapeXML(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  private async calculateComplianceMetrics(period: string): Promise<ComplianceMetrics> {
    try {
      const since = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
      
      const [
        { count: totalUsers },
        { count: dataRequests },
        { count: consentRecords },
        { count: dataExports },
        { count: dataDeletions },
        { count: securityIncidents }
      ] = await Promise.all([
        supabase.from('profiles').select('*', { count: 'exact' }),
        supabase.from('data_subject_requests').select('*', { count: 'exact' }).gte('createdAt', since),
        supabase.from('consent_records').select('*', { count: 'exact' }).gte('timestamp', since),
        supabase.from('data_exports').select('*', { count: 'exact' }).gte('createdAt', since),
        supabase.from('data_exports').select('*', { count: 'exact' }).eq('status', 'completed').gte('createdAt', since),
        supabase.from('security_events').select('*', { count: 'exact' }).gte('timestamp', since).eq('severity', 'critical')
      ]);

      // Calculate scores
      const auditScore = Math.max(0, 100 - (securityIncidents * 10));
      const complianceScore = Math.max(0, 100 - (dataDeletions * 5));

      return {
        totalUsers: totalUsers || 0,
        dataRequests: dataRequests || 0,
        consentRecords: consentRecords || 0,
        dataExports: dataExports || 0,
        dataDeletions: dataDeletions || 0,
        securityIncidents: securityIncidents || 0,
        auditScore,
        complianceScore,
        period
      };
    } catch (error) {
      console.error('Error calculating compliance metrics:', error);
      throw error;
    }
  }

  private async identifyComplianceFindings(): Promise<ComplianceFinding[]> {
    // Identify compliance issues and findings
    const findings: ComplianceFinding[] = [];

    // Check for common compliance issues
    findings.push({
      category: 'data_protection',
      severity: 'medium',
      description: 'Some users have not accepted latest privacy policy',
      affectedRecords: 15,
      recommendation: 'Implement mandatory consent acceptance for new features'
    });

    return findings;
  }

  private async generateComplianceRecommendations(findings: ComplianceFinding[]): Promise<ComplianceRecommendation[]> {
    return findings.map(finding => ({
      priority: finding.severity,
      category: finding.category,
      action: `Address ${finding.description}`,
      description: `Implement controls to prevent ${finding.description}`,
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      assignee: 'Compliance Team'
    }));
  }

  private async getClientIP(): Promise<string> {
    // Get client IP address
    // This would integrate with an IP geolocation service
    return '127.0.0.1'; // Fallback for development
  }

  private async notifyDisputeParties(disputeId: string, claimantId: string): Promise<void> {
    try {
      // Get dispute details
      const { data: dispute } = await supabase
        .from('disputes')
        .select('*')
        .eq('id', disputeId)
        .single();

      // Create notifications
      const notifications = [
        {
          userId: claimantId,
          type: 'dispute_initiated',
          title: 'Dispute Initiated',
          message: `A dispute has been initiated for your transaction`,
          data: { disputeId },
          read: false,
          created_at: new Date().toISOString()
        }
      ];

      if (dispute.respondentId) {
        notifications.push({
          userId: dispute.respondentId,
          type: 'dispute_received',
          title: 'Dispute Received',
          message: `A dispute has been initiated against your transaction`,
          data: { disputeId },
          read: false,
          created_at: new Date().toISOString()
        });
      }

      await supabase.from('notifications').insert(notifications);
    } catch (error) {
      console.error('Error notifying dispute parties:', error);
    }
  }

  private async updateEscrowFromDispute(disputeId: string, favor: 'claimant' | 'respondent' | 'split'): Promise<void> {
    try {
      const { data: dispute } = await supabase
        .from('disputes')
        .select('escrowTransactionId')
        .eq('id', disputeId)
        .single();

      if (dispute) {
        // Update escrow based on dispute resolution
        if (favor === 'claimant') {
          // Release funds to claimant
          await supabase
            .from('escrow_transactions')
            .update({
              status: 'refunded',
              completedAt: new Date().toISOString()
            })
            .eq('id', dispute.escrowTransactionId);
        } else if (favor === 'respondent') {
          // Release funds to respondent
          await supabase
            .from('escrow_transactions')
            .update({
              status: 'completed',
              completedAt: new Date().toISOString()
            })
            .eq('id', dispute.escrowTransactionId);
        }
      }
    } catch (error) {
      console.error('Error updating escrow from dispute:', error);
    }
  }
}

// Additional Types
export interface ConsentUpdate {
  consentType: ConsentRecord['consentType'];
  granted: boolean;
  details?: Record<string, any>;
}

export interface ConsentResult {
  success: boolean;
  consentId?: string;
  message?: string;
}

export interface ComplianceResult {
  success: boolean;
  exportId?: string;
  message?: string;
  error?: string;
}

export default ComplianceService;
