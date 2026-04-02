/**
 * Enterprise Payment Service with Escrow Support
 * Handles multi-currency payments, escrow transactions, and international banking
 */

import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database';

const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

// Types
export interface PaymentMethod {
  id: string;
  type: 'card' | 'bank_transfer' | 'crypto' | 'escrow' | 'paypal' | 'wise' | 'flutterwave';
  provider: string;
  currency: string;
  isDefault: boolean;
  metadata: Record<string, any>;
}

export interface Currency {
  code: string;
  name: string;
  symbol: string;
  rate: number;
  lastUpdated: string;
}

export interface ExchangeRates {
  base: string;
  rates: Record<string, number>;
  timestamp: string;
}

export interface EscrowTransaction {
  id: string;
  buyerId: string;
  sellerId: string;
  listingId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'funded' | 'shipped' | 'delivered' | 'completed' | 'disputed' | 'cancelled' | 'refunded';
  milestones: Milestone[];
  documents: TransactionDocument[];
  tracking: ShippingTracking;
  fees: EscrowFees;
  createdAt: string;
  updatedAt: string;
  fundedAt?: string;
  completedAt?: string;
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  amount: number;
  currency: string;
  dueDate: string;
  status: 'pending' | 'completed' | 'approved' | 'rejected';
  completedAt?: string;
  evidence?: string[];
}

export interface TransactionDocument {
  id: string;
  type: 'invoice' | 'receipt' | 'shipping_label' | 'customs_form' | 'certificate' | 'contract';
  url: string;
  uploadedAt: string;
  uploadedBy: string;
}

export interface ShippingTracking {
  carrier: string;
  trackingNumber: string;
  status: 'pending' | 'in_transit' | 'out_for_delivery' | 'delivered' | 'exception';
  lastUpdate: string;
  estimatedDelivery?: string;
}

export interface EscrowFees {
  platformFee: number;
  paymentProcessorFee: number;
  currencyConversionFee: number;
  totalFees: number;
  currency: string;
}

export interface PaymentRequest {
  amount: number;
  currency: string;
  method: PaymentMethod;
  description: string;
  metadata?: Record<string, any>;
  returnUrl?: string;
  cancelUrl?: string;
}

export interface PaymentResult {
  success: boolean;
  transactionId?: string;
  paymentId?: string;
  status: string;
  message?: string;
  fees?: EscrowFees;
}

export interface RefundRequest {
  transactionId: string;
  amount?: number;
  reason: string;
  evidence?: string[];
}

export interface RefundResult {
  success: boolean;
  refundId?: string;
  amount: number;
  currency: string;
  status: string;
  estimatedArrival?: string;
}

export interface ISO20022Message {
  messageId: string;
  messageType: 'pacs.008.001.07' | 'pain.001.001.03' | 'camt.053.001.01';
  sender: PartyIdentification;
  receiver: PartyIdentification;
  amount: Amount;
  date: string;
  currency: string;
  raw: string;
}

export interface PartyIdentification {
  name: string;
  address: Address;
  accountNumber?: string;
  bankCode?: string;
  country: string;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

export interface Amount {
  value: number;
  currency: string;
}

// Payment Provider Interfaces
export interface PaymentProvider {
  name: string;
  processPayment(request: PaymentRequest): Promise<PaymentResult>;
  processRefund(request: RefundRequest): Promise<RefundResult>;
  getPaymentStatus(paymentId: string): Promise<any>;
  supportedCurrencies: string[];
}

// Stripe Provider
export class StripeProvider implements PaymentProvider {
  name = 'stripe';
  private stripe: any;

  constructor() {
    // Initialize Stripe with public key
    this.stripe = null; // Will be initialized with actual Stripe SDK
  }

  async processPayment(request: PaymentRequest): Promise<PaymentResult> {
    try {
      // Process payment through Stripe
      const paymentIntent = await this.stripe.paymentIntents.create({
        amount: Math.round(request.amount * 100), // Convert to cents
        currency: request.currency.toLowerCase(),
        payment_method: request.method.metadata?.stripePaymentMethodId,
        description: request.description,
        metadata: request.metadata,
        confirmation_method: 'manual',
        return_url: request.returnUrl,
        cancel_url: request.cancelUrl
      });

      return {
        success: true,
        transactionId: paymentIntent.id,
        paymentId: paymentIntent.id,
        status: paymentIntent.status,
        fees: {
          platformFee: request.amount * 0.025, // 2.5% platform fee
          paymentProcessorFee: (request.amount * 0.029) + 0.30, // Stripe fees
          currencyConversionFee: 0,
          totalFees: (request.amount * 0.025) + (request.amount * 0.029) + 0.30,
          currency: request.currency
        }
      };
    } catch (error) {
      return {
        success: false,
        message: error.message,
        status: 'failed'
      };
    }
  }

  async processRefund(request: RefundRequest): Promise<RefundResult> {
    try {
      const refund = await this.stripe.refunds.create({
        payment_intent: request.transactionId,
        amount: request.amount ? Math.round(request.amount * 100) : undefined,
        reason: 'requested_by_customer',
        metadata: {
          reason: request.reason
        }
      });

      return {
        success: true,
        refundId: refund.id,
        amount: refund.amount / 100,
        currency: refund.currency,
        status: refund.status,
        estimatedArrival: '5-7 business days'
      };
    } catch (error) {
      return {
        success: false,
        amount: 0,
        currency: 'USD',
        status: 'failed'
      };
    }
  }

  async getPaymentStatus(paymentId: string): Promise<any> {
    try {
      const paymentIntent = await this.stripe.paymentIntents.retrieve(paymentId);
      return {
        status: paymentIntent.status,
        amount: paymentIntent.amount / 100,
        currency: paymentIntent.currency.toUpperCase()
      };
    } catch (error) {
      return { status: 'error', error: error.message };
    }
  }

  supportedCurrencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD'];
}

// Wise Provider
export class WiseProvider implements PaymentProvider {
  name = 'wise';
  private wise: any;

  constructor() {
    // Initialize Wise API
    this.wise = null; // Will be initialized with Wise SDK
  }

  async processPayment(request: PaymentRequest): Promise<PaymentResult> {
    try {
      // Process payment through Wise
      const transfer = await this.wise.transfers.create({
        targetAccount: request.method.metadata?.wiseAccountId,
        sourceAmount: {
          value: request.amount,
          currency: request.currency
        },
        reference: request.description,
        details: {
          reference: request.metadata?.reference
        }
      });

      return {
        success: true,
        transactionId: transfer.id,
        status: transfer.status,
        fees: {
          platformFee: request.amount * 0.015, // 1.5% platform fee
          paymentProcessorFee: transfer.fees?.total || 0,
          currencyConversionFee: transfer.fees?.exchangeRate || 0,
          totalFees: (request.amount * 0.015) + (transfer.fees?.total || 0) + (transfer.fees?.exchangeRate || 0),
          currency: request.currency
        }
      };
    } catch (error) {
      return {
        success: false,
        message: error.message,
        status: 'failed'
      };
    }
  }

  async processRefund(request: RefundRequest): Promise<RefundResult> {
    try {
      const refund = await this.wise.transfers.refund(request.transactionId, {
        amount: request.amount,
        reason: request.reason
      });

      return {
        success: true,
        refundId: refund.id,
        amount: refund.amount,
        currency: refund.sourceCurrency,
        status: refund.status,
        estimatedArrival: '3-5 business days'
      };
    } catch (error) {
      return {
        success: false,
        amount: 0,
        currency: 'USD',
        status: 'failed'
      };
    }
  }

  async getPaymentStatus(paymentId: string): Promise<any> {
    try {
      const transfer = await this.wise.transfers.get(paymentId);
      return {
        status: transfer.status,
        amount: transfer.sourceAmount,
        currency: transfer.sourceCurrency
      };
    } catch (error) {
      return { status: 'error', error: error.message };
    }
  }

  supportedCurrencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'NGN', 'KES', 'ETB'];
}

// Main Payment Service
export class PaymentService {
  private static instance: PaymentService;
  private providers: Map<string, PaymentProvider> = new Map();

  private constructor() {
    // Initialize payment providers
    this.providers.set('stripe', new StripeProvider());
    this.providers.set('wise', new WiseProvider());
  }

  static getInstance(): PaymentService {
    if (!PaymentService.instance) {
      PaymentService.instance = new PaymentService();
    }
    return PaymentService.instance;
  }

  // Escrow Management
  async createEscrow(
    buyerId: string,
    sellerId: string,
    listingId: string,
    amount: number,
    currency: string,
    milestones: Omit<Milestone[], 'id' | 'status' | 'completedAt'>[]
  ): Promise<EscrowTransaction> {
    try {
      // Calculate fees
      const platformFee = amount * 0.025; // 2.5% platform fee
      const totalFees = platformFee;

      const escrowData: Omit<EscrowTransaction, 'id' | 'createdAt' | 'updatedAt'> = {
        buyerId,
        sellerId,
        listingId,
        amount,
        currency,
        status: 'pending',
        milestones: milestones.map(m => ({
          ...m,
          id: crypto.randomUUID(),
          status: 'pending'
        })),
        documents: [],
        tracking: {
          carrier: '',
          trackingNumber: '',
          status: 'pending',
          lastUpdate: new Date().toISOString()
        },
        fees: {
          platformFee,
          paymentProcessorFee: 0,
          currencyConversionFee: 0,
          totalFees,
          currency
        }
      };

      const { data, error } = await supabase
        .from('escrow_transactions')
        .insert(escrowData)
        .select()
        .single();

      if (error) throw error;

      // Generate ISO 20022 payment message
      await this.generateISO20022Message(data.id, 'pacs.008.001.07');

      return data;
    } catch (error) {
      console.error('Error creating escrow:', error);
      throw error;
    }
  }

  async fundEscrow(escrowId: string, paymentMethod: PaymentMethod): Promise<EscrowTransaction> {
    try {
      const escrow = await this.getEscrow(escrowId);
      if (!escrow || escrow.status !== 'pending') {
        throw new Error('Escrow not found or not in pending status');
      }

      // Process payment
      const provider = this.providers.get(paymentMethod.provider);
      if (!provider) {
        throw new Error('Payment provider not supported');
      }

      const paymentResult = await provider.processPayment({
        amount: escrow.amount,
        currency: escrow.currency,
        method: paymentMethod,
        description: `Escrow funding for transaction ${escrowId}`,
        metadata: {
          escrowId,
          type: 'escrow_funding'
        }
      });

      if (!paymentResult.success) {
        throw new Error(paymentResult.message || 'Payment failed');
      }

      // Update escrow status
      const { data, error } = await supabase
        .from('escrow_transactions')
        .update({
          status: 'funded',
          fundedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
        .eq('id', escrowId)
        .select()
        .single();

      if (error) throw error;

      // Notify seller
      await this.notifySeller(escrow.sellerId, {
        type: 'escrow_funded',
        escrowId,
        amount: escrow.amount,
        currency: escrow.currency
      });

      return data;
    } catch (error) {
      console.error('Error funding escrow:', error);
      throw error;
    }
  }

  async releaseMilestone(
    escrowId: string,
    milestoneId: string,
    confirmation: MilestoneConfirmation
  ): Promise<Milestone> {
    try {
      const escrow = await this.getEscrow(escrowId);
      if (!escrow) {
        throw new Error('Escrow not found');
      }

      const milestone = escrow.milestones.find(m => m.id === milestoneId);
      if (!milestone) {
        throw new Error('Milestone not found');
      }

      // Update milestone status
      const { data, error } = await supabase
        .from('milestones')
        .update({
          status: 'completed',
          completedAt: new Date().toISOString(),
          evidence: confirmation.evidence || []
        })
        .eq('id', milestoneId)
        .select()
        .single();

      if (error) throw error;

      // Release funds for this milestone
      const releaseAmount = milestone.amount;
      await this.releaseFunds(escrow.sellerId, releaseAmount, escrow.currency, milestoneId);

      // Check if all milestones are completed
      const allCompleted = escrow.milestones.every(m => m.status === 'completed');
      if (allCompleted) {
        await this.completeEscrow(escrowId);
      }

      return data;
    } catch (error) {
      console.error('Error releasing milestone:', error);
      throw error;
    }
  }

  async completeEscrow(escrowId: string): Promise<EscrowTransaction> {
    try {
      const { data, error } = await supabase
        .from('escrow_transactions')
        .update({
          status: 'completed',
          completedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
        .eq('id', escrowId)
        .select()
        .single();

      if (error) throw error;

      // Release remaining funds to seller
      const escrow = await this.getEscrow(escrowId);
      if (escrow) {
        const completedMilestones = escrow.milestones.filter(m => m.status === 'completed');
        const releasedAmount = completedMilestones.reduce((sum, m) => sum + m.amount, 0);
        const remainingAmount = escrow.amount - releasedAmount - escrow.fees.platformFee;

        if (remainingAmount > 0) {
          await this.releaseFunds(escrow.sellerId, remainingAmount, escrow.currency);
        }
      }

      return data;
    } catch (error) {
      console.error('Error completing escrow:', error);
      throw error;
    }
  }

  async handleDispute(
    escrowId: string,
    dispute: DisputeClaim
  ): Promise<DisputeResolution> {
    try {
      const escrow = await this.getEscrow(escrowId);
      if (!escrow) {
        throw new Error('Escrow not found');
      }

      // Freeze remaining funds
      const { data, error } = await supabase
        .from('escrow_transactions')
        .update({
          status: 'disputed',
          updatedAt: new Date().toISOString()
        })
        .eq('id', escrowId)
        .select()
        .single();

      if (error) throw error;

      // Create dispute case
      const disputeData = {
        escrowId,
        claimantId: dispute.claimantId,
        respondentId: escrow.sellerId,
        reason: dispute.reason,
        description: dispute.description,
        evidence: dispute.evidence || [],
        status: 'under_review',
        createdAt: new Date().toISOString()
      };

      const { data: disputeCase, error: disputeError } = await supabase
        .from('disputes')
        .insert(disputeData)
        .select()
        .single();

      if (disputeError) throw disputeError;

      // Notify both parties
      await this.notifyDisputeParties(escrow, disputeCase);

      return {
        disputeId: disputeCase.id,
        status: 'under_review',
        estimatedResolution: '7-14 business days'
      };
    } catch (error) {
      console.error('Error handling dispute:', error);
      throw error;
    }
  }

  // Currency Exchange
  async getExchangeRates(baseCurrency: string = 'USD'): Promise<ExchangeRates> {
    try {
      // In production, integrate with real exchange rate API
      const mockRates = {
        USD: { EUR: 0.85, GBP: 0.73, CAD: 1.25, AUD: 1.35 },
        EUR: { USD: 1.18, GBP: 0.86, CAD: 1.47, AUD: 1.59 },
        GBP: { USD: 1.37, EUR: 1.16, CAD: 1.71, AUD: 1.85 }
      };

      const rates = mockRates[baseCurrency] || mockRates.USD;

      return {
        base: baseCurrency,
        rates,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error getting exchange rates:', error);
      throw error;
    }
  }

  async convertAmount(
    amount: number,
    fromCurrency: string,
    toCurrency: string
  ): Promise<{ amount: number; rate: number }> {
    try {
      const exchangeRates = await this.getExchangeRates(fromCurrency);
      const rate = exchangeRates.rates[toCurrency];

      if (!rate) {
        throw new Error('Exchange rate not available');
      }

      return {
        amount: amount * rate,
        rate
      };
    } catch (error) {
      console.error('Error converting amount:', error);
      throw error;
    }
  }

  // ISO 20022 Messaging
  async generateISO20022Message(
    transactionId: string,
    messageType: string
  ): Promise<ISO20022Message> {
    try {
      const escrow = await this.getEscrow(transactionId);
      if (!escrow) {
        throw new Error('Transaction not found');
      }

      const message: ISO20022Message = {
        messageId: `MSG-${Date.now()}-${transactionId}`,
        messageType: messageType as any,
        sender: {
          name: 'Worldmine Buyer',
          accountNumber: escrow.buyerId,
          country: 'US'
        },
        receiver: {
          name: 'Worldmine Seller',
          accountNumber: escrow.sellerId,
          country: 'US'
        },
        amount: {
          value: escrow.amount,
          currency: escrow.currency
        },
        date: new Date().toISOString().split('T')[0],
        currency: escrow.currency,
        raw: JSON.stringify({ transactionId, messageType })
      };

      // Store ISO 20022 message
      await supabase
        .from('iso20022_messages')
        .insert(message);

      return message;
    } catch (error) {
      console.error('Error generating ISO 20022 message:', error);
      throw error;
    }
  }

  // Helper Methods
  private async getEscrow(escrowId: string): Promise<EscrowTransaction | null> {
    try {
      const { data, error } = await supabase
        .from('escrow_transactions')
        .select(`
          *,
          buyer:profiles(*),
          seller:profiles(*),
          listing:mineral_listings(*)
        `)
        .eq('id', escrowId)
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error getting escrow:', error);
      throw error;
    }
  }

  private async releaseFunds(
    sellerId: string,
    amount: number,
    currency: string,
    milestoneId?: string
  ): Promise<void> {
    try {
      // In production, integrate with actual payment provider
      console.log(`Releasing ${amount} ${currency} to seller ${sellerId}`);
      
      // Record the release
      await supabase
        .from('fund_releases')
        .insert({
          sellerId,
          amount,
          currency,
          milestoneId,
          releasedAt: new Date().toISOString(),
          status: 'completed'
        });
    } catch (error) {
      console.error('Error releasing funds:', error);
      throw error;
    }
  }

  private async notifySeller(
    sellerId: string,
    notification: any
  ): Promise<void> {
    try {
      await supabase
        .from('notifications')
        .insert({
          userId: sellerId,
          type: notification.type,
          title: notification.type === 'escrow_funded' ? 'Escrow Funded' : 'Payment Received',
          message: `Your escrow has been funded with ${notification.amount} ${notification.currency}`,
          data: notification,
          read: false,
          createdAt: new Date().toISOString()
        });
    } catch (error) {
      console.error('Error notifying seller:', error);
    }
  }

  private async notifyDisputeParties(
    escrow: EscrowTransaction,
    dispute: any
  ): Promise<void> {
    try {
      const notifications = [
        {
          userId: escrow.buyerId,
          type: 'dispute_initiated',
          title: 'Dispute Initiated',
          message: `A dispute has been initiated for transaction ${escrow.id}`,
          data: { escrowId: escrow.id, disputeId: dispute.id },
          read: false,
          createdAt: new Date().toISOString()
        },
        {
          userId: escrow.sellerId,
          type: 'dispute_received',
          title: 'Dispute Received',
          message: `A dispute has been initiated against your transaction ${escrow.id}`,
          data: { escrowId: escrow.id, disputeId: dispute.id },
          read: false,
          createdAt: new Date().toISOString()
        }
      ];

      await supabase.from('notifications').insert(notifications);
    } catch (error) {
      console.error('Error notifying dispute parties:', error);
    }
  }

  // Payment Methods Management
  async addPaymentMethod(
    userId: string,
    paymentMethod: Omit<PaymentMethod, 'id'>
  ): Promise<PaymentMethod> {
    try {
      const { data, error } = await supabase
        .from('payment_methods')
        .insert({
          ...paymentMethod,
          isDefault: false
        })
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error adding payment method:', error);
      throw error;
    }
  }

  async getUserPaymentMethods(userId: string): Promise<PaymentMethod[]> {
    try {
      const { data, error } = await supabase
        .from('payment_methods')
        .select('*')
        .eq('userId', userId)
        .order('isDefault', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error getting user payment methods:', error);
      throw error;
    }
  }

  async setDefaultPaymentMethod(
    userId: string,
    paymentMethodId: string
  ): Promise<void> {
    try {
      // Remove default from all methods
      await supabase
        .from('payment_methods')
        .update({ isDefault: false })
        .eq('userId', userId);

      // Set new default
      const { error } = await supabase
        .from('payment_methods')
        .update({ isDefault: true })
        .eq('id', paymentMethodId)
        .eq('userId', userId);

      if (error) throw error;
    } catch (error) {
      console.error('Error setting default payment method:', error);
      throw error;
    }
  }
}

// Additional Types
export interface DisputeClaim {
  claimantId: string;
  reason: string;
  description: string;
  evidence?: string[];
}

export interface DisputeResolution {
  disputeId: string;
  status: string;
  estimatedResolution: string;
}

export interface MilestoneConfirmation {
  evidence?: string[];
  approvedBy?: string;
  notes?: string;
}

export default PaymentService;
