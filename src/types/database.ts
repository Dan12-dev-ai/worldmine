/**
 * Database Type Definitions for Worldmine
 * Generated from Supabase schema
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      locations: never
    }
  }
}

// Mineral Types
export interface MineralType {
  id: string;
  name: string;
  code: string;
  category: 'precious_metals' | 'industrial_minerals' | 'rare_earths' | 'gemstones';
  unit: string;
  description: Record<string, string>;
  created_at: string;
}

// User Profiles
export interface Profile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  phone?: string;
  avatar_url?: string;
  business_name?: string;
  business_description?: Record<string, string>;
  verification_status: 'pending' | 'verified' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface SellerProfile extends Profile {
  mining_license?: Certification;
  geological_reports?: MediaFile[];
  rating?: SellerRating;
  capabilities?: SellerCapabilities;
  total_sales?: number;
  joined_at: string;
  last_active: string;
}

export interface BuyerProfile extends Profile {
  payment_methods?: PaymentMethod[];
  shipping_addresses?: Address[];
  purchase_history?: PurchaseHistory[];
  preferences?: BuyerPreferences;
  escrow_balance?: number;
}

// Listings
export interface MineralListing {
  id: string;
  seller_id: string;
  title: Record<string, string>;
  description: Record<string, string>;
  mineral_type_id: string;
  quantity: number;
  unit: string;
  price: number;
  currency: string;
  location: GeographicLocation;
  quality_assessment?: QualityAssessment;
  certifications?: Certification[];
  photos?: MediaFile[];
  documents?: MediaFile[];
  auction_settings?: AuctionSettings;
  negotiation_enabled: boolean;
  shipping_options?: ShippingOption[];
  status: 'draft' | 'active' | 'sold' | 'expired' | 'suspended';
  views: number;
  favorites: number;
  featured: boolean;
  created_at: string;
  updated_at: string;
}

// Transactions and Payments
export interface Transaction {
  id: string;
  buyer_id: string;
  seller_id: string;
  listing_id: string;
  amount: number;
  currency: string;
  type: 'direct_sale' | 'auction_sale' | 'milestone_release';
  status: 'pending_payment' | 'paid' | 'shipped' | 'delivered' | 'completed' | 'disputed' | 'refunded' | 'cancelled';
  escrow_id?: string;
  payment_method_id?: string;
  fees?: EscrowFees;
  created_at: string;
  updated_at: string;
}

export interface EscrowTransaction {
  id: string;
  buyer_id: string;
  seller_id: string;
  listing_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'funded' | 'shipped' | 'delivered' | 'completed' | 'disputed' | 'cancelled' | 'refunded';
  milestones?: Milestone[];
  documents?: TransactionDocument[];
  tracking?: ShippingTracking;
  fees?: EscrowFees;
  funded_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: string;
  escrow_id: string;
  title: string;
  description: string;
  amount: number;
  currency: string;
  due_date: string;
  status: 'pending' | 'completed' | 'approved' | 'rejected';
  completed_at?: string;
  evidence?: string[];
  created_at: string;
}

export interface PaymentMethod {
  id: string;
  user_id: string;
  type: 'card' | 'bank_transfer' | 'crypto' | 'escrow' | 'paypal' | 'wise' | 'flutterwave';
  provider: string;
  currency: string;
  is_default: boolean;
  metadata: Json;
  created_at: string;
  updated_at: string;
}

// Reviews and Ratings
export interface Review {
  id: string;
  reviewer_id: string;
  listing_id: string;
  rating: number;
  comment: Record<string, string>;
  verified: boolean;
  created_at: string;
}

export interface SellerRating {
  seller_id: string;
  overall: number;
  communication: number;
  quality: number;
  shipping: number;
  total_transactions: number;
  updated_at: string;
}

// Certifications
export interface Certification {
  id: string;
  type: 'mining_license' | 'environmental' | 'quality' | 'origin' | 'ethical';
  issuer: string;
  issue_date: string;
  expiry_date: string;
  document_url: string;
  verified: boolean;
  created_at: string;
}

// Media Files
export interface MediaFile {
  id: string;
  type: 'image' | 'video' | 'document';
  url: string;
  thumbnail?: string;
  size: number;
  metadata?: Json;
  uploaded_at: string;
}

// Geographic and Location
export interface GeographicLocation {
  country: string;
  region: string;
  coordinates: [number, number];
  timezone: string;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

// Quality and Specifications
export interface QualityAssessment {
  grade: string;
  purity: number;
  specifications: Json;
  certification_ids?: string[];
  assessment_date: string;
  assessed_by: string;
}

export interface SellerCapabilities {
  mineral_types: string[];
  shipping_methods: string[];
  payment_methods: string[];
  max_quantity: number;
  processing_time: number;
}

// Auction and Bidding
export interface AuctionSettings {
  enabled: boolean;
  start_date: string;
  end_date: string;
  starting_bid: number;
  reserve_price: number;
  bid_increment: number;
  current_bid?: number;
  current_bidder?: string;
}

export interface Bid {
  id: string;
  listing_id: string;
  bidder_id: string;
  amount: number;
  currency: string;
  is_auto_bid: boolean;
  max_auto_bid?: number;
  created_at: string;
}

// Shipping and Logistics
export interface ShippingOption {
  id: string;
  method: 'standard' | 'express' | 'freight' | 'air' | 'sea';
  cost: number;
  estimated_days: number;
  tracking_required: boolean;
  insurance_included: boolean;
  destinations: string[];
}

export interface ShippingTracking {
  carrier: string;
  tracking_number: string;
  status: 'pending' | 'in_transit' | 'out_for_delivery' | 'delivered' | 'exception';
  last_update: string;
  estimated_delivery?: string;
}

// Fees and Pricing
export interface EscrowFees {
  platform_fee: number;
  payment_processor_fee: number;
  currency_conversion_fee: number;
  total_fees: number;
  currency: string;
}

// Disputes and Resolution
export interface Dispute {
  id: string;
  escrow_id: string;
  claimant_id: string;
  respondent_id: string;
  reason: string;
  description: string;
  evidence?: string[];
  status: 'under_review' | 'investigating' | 'resolved_buyer' | 'resolved_seller' | 'cancelled';
  resolution_notes?: string;
  created_at: string;
  resolved_at?: string;
}

// Notifications
export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  data: Json;
  read: boolean;
  created_at: string;
}

// Favorites and Watchlist
export interface Favorite {
  id: string;
  user_id: string;
  listing_id: string;
  created_at: string;
}

// ISO 20022 Messages
export interface ISO20022Message {
  id: string;
  message_type: 'pacs.008.001.07' | 'pain.001.001.03' | 'camt.053.001.01';
  sender: PartyIdentification;
  receiver: PartyIdentification;
  amount: Amount;
  date: string;
  currency: string;
  raw: string;
  created_at: string;
}

export interface PartyIdentification {
  name: string;
  address: Address;
  account_number?: string;
  bank_code?: string;
  country: string;
}

export interface Amount {
  value: number;
  currency: string;
}

// Additional Helper Types
export interface PurchaseHistory {
  id: string;
  transaction_id: string;
  item: string;
  quantity: number;
  price: number;
  currency: string;
  purchased_at: string;
}

export interface BuyerPreferences {
  language: string;
  currency: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  shipping_preferences: {
    preferred_method: string;
    addresses: string[];
  };
}

export interface TransactionDocument {
  id: string;
  transaction_id: string;
  type: 'invoice' | 'receipt' | 'shipping_label' | 'customs_form' | 'certificate' | 'contract';
  url: string;
  uploaded_at: string;
  uploaded_by: string;
}

// Function Return Types
export interface IncrementFavoritesCountParams {
  listing_id: string;
}

export interface DecrementFavoritesCountParams {
  listing_id: string;
}
