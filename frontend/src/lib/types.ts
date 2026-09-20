/**
 * World-Mine TypeScript Type Definitions
 * Production-ready type definitions for all API responses
 */

// User Types
export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone?: string;
  country?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  bio?: string;
  avatar_url?: string;
  company?: string;
  position?: string;
  website?: string;
  linkedin?: string;
  preferences: Record<string, unknown>;
  security_settings: Record<string, unknown>;
}

// Marketplace Types
export interface MineralListing {
  id: string;
  title: string;
  description: string;
  mineral_type: string;
  quantity: number;
  unit_price: number;
  currency: string;
  seller_id: string;
  quality_grade: string;
  origin: string;
  status: 'active' | 'sold' | 'pending' | 'cancelled';
  created_at: string;
  updated_at: string;
  images: string[];
  certifications?: {
    assay_report?: string;
    origin_document?: string;
    quality_certificate?: string;
    authenticity_report?: string;
  };
  country: string;
  city: string;
  latitude?: number;
  longitude?: number;
  shipping?: {
    available: boolean;
    cost: number;
    estimated_delivery: string;
    methods: string[];
  };
}

export interface Auction {
  id: string;
  listing_id: string;
  starting_bid: number;
  current_bid: number;
  end_time: string;
  status: 'active' | 'ended' | 'cancelled';
  bids: Bid[];
}

export interface Bid {
  id: string;
  auction_id: string;
  user_id: string;
  amount: number;
  created_at: string;
}

// Trading Types
export interface Order {
  id: string;
  user_id: string;
  mineral_id: string;
  side: 'buy' | 'sell';
  order_type: 'market' | 'limit' | 'stop_loss' | 'stop_limit' | 'iceberg';
  amount: number;
  price?: number;
  stop_price?: number;
  leverage: number;
  status: 'pending' | 'filled' | 'cancelled' | 'partial';
  filled_amount: number;
  filled_price?: number;
  created_at: string;
  updated_at: string;
}

export interface Trade {
  id: string;
  order_id: string;
  price: number;
  amount: number;
  side: 'buy' | 'sell';
  timestamp: string;
}

export interface OrderBookEntry {
  price: number;
  amount: number;
  total: number;
}

// Wallet Types
export interface Wallet {
  id: string;
  user_id: string;
  wallet_type: 'sovereign' | 'crypto' | 'bank';
  currency: string;
  balance: number;
  frozen_balance: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  wallet_id: string;
  type: 'deposit' | 'withdrawal' | 'transfer' | 'escrow' | 'refund';
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'cancelled';
  reference?: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

// Escrow Types
export interface Escrow {
  id: string;
  transaction_id: string;
  buyer_id: string;
  seller_id: string;
  amount: number;
  currency: string;
  status: 'created' | 'funded' | 'locked' | 'pending_verification' | 'released' | 'disputed' | 'resolved' | 'cancelled';
  created_at: string;
  updated_at: string;
  release_conditions: Record<string, unknown>;
  dispute_details?: {
    reason: string;
    raised_by: string;
    raised_at: string;
    resolution?: string;
  };
}

// Contract Types
export interface Contract {
  id: string;
  transaction_id: string;
  template_id: string;
  version: number;
  status: 'draft' | 'pending_signature' | 'signed' | 'active' | 'amended' | 'terminated';
  content: string;
  signatures: DigitalSignature[];
  created_at: string;
  updated_at: string;
  signed_at?: string;
}

export interface DigitalSignature {
  user_id: string;
  signature: string;
  signed_at: string;
  ip_address?: string;
}

// Logistics Types
export interface Shipment {
  id: string;
  transaction_id: string;
  tracking_number: string;
  carrier: string;
  status: 'pending' | 'picked_up' | 'in_transit' | 'out_for_delivery' | 'delivered' | 'exception';
  origin: {
    address: string;
    city: string;
    country: string;
    coordinates: { lat: number; lng: number };
  };
  destination: {
    address: string;
    city: string;
    country: string;
    coordinates: { lat: number; lng: number };
  };
  estimated_delivery: string;
  actual_delivery?: string;
  events: ShipmentEvent[];
  created_at: string;
  updated_at: string;
}

export interface ShipmentEvent {
  id: string;
  type: 'status_update' | 'location_update' | 'exception' | 'delivery';
  description: string;
  location?: {
    lat: number;
    lng: number;
    address: string;
  };
  timestamp: string;
}

// Notification Types
export interface Notification {
  id: string;
  user_id: string;
  type: 'system' | 'trade' | 'escrow' | 'logistics' | 'compliance' | 'ai_insight';
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  read: boolean;
  action_url?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

// AI Agent Types
export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
  capabilities: string[];
  metrics: {
    tasks_processed: number;
    success_rate: number;
    avg_response_time_ms: number;
  };
  last_active: string;
}

export interface AgentTask {
  id: string;
  agent_id: string;
  task_type: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
  created_at: string;
  completed_at?: string;
}

// Compliance Types
export interface ComplianceRecord {
  id: string;
  user_id: string;
  transaction_id?: string;
  type: 'kyc' | 'aml' | 'sanctions' | 'tax' | 'export_control';
  status: 'pending' | 'approved' | 'rejected' | 'requires_review';
  details: Record<string, unknown>;
  checked_at: string;
  checked_by: string;
}

// ESG Types
export interface ESGMetrics {
  id: string;
  entity_id: string;
  entity_type: 'user' | 'listing' | 'transaction';
  environmental_score: number;
  social_score: number;
  governance_score: number;
  overall_score: number;
  metrics: Record<string, unknown>;
  calculated_at: string;
}

// Video Session Types
export interface VideoSession {
  id: string;
  participants: string[];
  status: 'created' | 'active' | 'ended' | 'failed';
  created_at: string;
  started_at?: string;
  ended_at?: string;
  recording_url?: string;
}

// Trust Signal Types
export interface TrustSignal {
  id: string;
  user_id: string;
  reputation_score: number;
  feedback_count: number;
  verification_count: number;
  watchlist_count: number;
  last_updated: string;
}
