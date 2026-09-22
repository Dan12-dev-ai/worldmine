/**
 * World Mine — domain types.
 * Locked to backend serializers (docs/FRONTEND_MIGRATION_MAP.md).
 * These mirror — never reinterpret — the API contracts.
 */

/** Exact shape returned by GET /api/marketplace/listings (serialize_listing). */
export interface Listing {
  id: string;
  seller_id: string;
  title: string;
  description: string;
  mineral_type: string | null;
  quantity: number | null;
  unit_price: number | null;
  total_price: number | null;
  currency: string; // "USD"
  quality_grade: string | null;
  origin: string | null;
  country: string | null;
  city: string | null;
  latitude: number | null;
  longitude: number | null;
  status: 'active' | 'inactive';
  listing_type: string | null;
  created_at: string | null;
  updated_at: string | null;
  /** Optional projections — present only if the backend embeds them. */
  verification?: ListingVerification | null;
  seller?: ListingSeller | null;
}

/** EscrowStatus enum — backend/api/escrow.py */
export type EscrowStatus =
  | 'created' | 'funded' | 'locked' | 'pending_verification'
  | 'disputed' | 'resolved' | 'released' | 'cancelled' | 'refunded';

export type EscrowMilestone =
  | 'payment_received' | 'shipment_confirmed' | 'delivery_verified'
  | 'inspection_passed' | 'final_approval';

export interface Escrow {
  id: string;
  transaction_id: string | null;
  buyer_id: string;
  seller_id: string;
  amount: number;
  currency: string;
  status: EscrowStatus;
  release_conditions: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  dispute_details: Record<string, unknown> | null;
  milestones: EscrowMilestone[];
  auto_release_days: number;
  auto_release_date: string | null;
  payment_transaction_id: string | null;
}

/** User model — models.py User */
export type UserType = 'miner' | 'buyer' | 'institutional' | 'verifier' | 'admin';
export type VerificationLevel = 'none' | 'basic' | 'professional' | 'enterprise';
export type Tier = 'provisional' | 'standard' | 'premium' | 'enterprise';

export interface User {
  id: string;
  email: string;
  username: string;
  user_type: UserType;
  tier: Tier;
  verification_level: VerificationLevel;
  reputation_score: number;
  esg_score: number;
  total_transactions: number;
  total_volume: number;
  email_verified: boolean;
  is_active: boolean;
}

/**
 * ContractStatus / ContractType enums — backend/api/contracts.py (verified).
 */
export type ContractStatus =
  | 'draft' | 'pending_signature' | 'signed' | 'active' | 'expired' | 'terminated';

export type ContractType =
  | 'sales_agreement' | 'purchase_order' | 'service_agreement' | 'escrow_agreement';

/** Exact Contract model serialized by GET /api/contracts/contracts. */
export interface Contract {
  id: string;
  template_id: string;
  contract_type: ContractType | string;
  status: ContractStatus | string;
  /** `List[Dict[str, str]]` — e.g. {name, role, user_id}. */
  parties: Array<Record<string, string>>;
  content: string;
  signatures: Array<Record<string, unknown>>;
  created_at: string;
  audit_trail: Array<Record<string, unknown>>;
}

/** GET /api/contracts/templates */
export interface ContractTemplate {
  id: string;
  name: string;
  contract_type: ContractType | string;
  template_content: string;
  variables: string[];
}

/** Verification states — never color alone (§19). */
export type VerificationState =
  | 'UNVERIFIED' | 'PENDING' | 'PARTIALLY VERIFIED'
  | 'VERIFIED' | 'EXPIRED' | 'REQUIRES REVIEW';

/** Realtime event envelope (§39) — every event carries these. */
export interface RealtimeEvent<T = unknown> {
  id: string;
  type: string;
  timestamp: string;
  entity: string;
  payload: T;
  version: number;
}

/**
 * Verification panel data. The marketplace serializer does not embed this yet
 * (documented drift #1) — the detail page treats it as optional and renders
 * "not yet available" instead of inventing values (§38/§47).
 */
export interface ListingVerification {
  state: VerificationState | string;
  verified_by?: string | null;
  verified_at?: string | null;
  what?: string[] | null;
  evidence_count?: number | null;
  expires_at?: string | null;
}

/** Optional seller projection embedded by some serializers. */
export interface ListingSeller {
  username?: string | null;
  verification_level?: VerificationLevel | string | null;
}

/** Product lifecycle (§2) — the spine of the UI. */
export const LIFECYCLE_STAGES = [
  'DISCOVER', 'VERIFY', 'CONNECT', 'NEGOTIATE', 'CONTRACT',
  'ESCROW', 'PAY', 'SHIP', 'COMPLY', 'TRACE', 'COMPLETE',
] as const;
export type LifecycleStage = (typeof LIFECYCLE_STAGES)[number];

/* ==================================================================== *
 * Workspace module contracts — every shape below was read directly from
 * the backend serializers/Pydantic models (not guessed). Where a route
 * returns an untyped `Dict[str, Any]` that is stated explicitly.
 * ==================================================================== */

/** Envelope used by the escrow router: `{"data": ...}` — NOT a bare array. */
export interface DataEnvelope<T> {
  data: T;
}

/* ---------- Trading (backend/api/trading.py) ---------- */

/**
 * NOTE (drift): `GET /api/trading/orders` and `/trades` are typed
 * `List[Dict[str, Any]]` server-side and currently serve seeded/mock rows.
 * Fields are therefore optional and rendered only when actually present.
 */
export interface TradingOrder {
  id?: string;
  order_id?: string;
  user_id?: string;
  mineral_id?: string;
  side?: string;
  order_type?: string;
  quantity?: number;
  price?: number;
  filled_quantity?: number;
  status?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface Trade {
  trade_id?: string;
  order_id?: string;
  mineral_id?: string;
  side?: string;
  amount?: number;
  price?: number;
  total?: number;
  status?: string;
  executed_at?: string;
  [key: string]: unknown;
}

/** `GET /api/trading/performance` — `Dict[str, Any]`. */
export interface TradingPerformance {
  total_trades?: number;
  total_volume?: number;
  total_pnl?: number;
  win_rate?: number;
  [key: string]: unknown;
}

/* ---------- Logistics (backend/api/logistics.py) ---------- */

export type ShipmentStatus =
  | 'pending' | 'picked_up' | 'in_transit' | 'out_for_delivery'
  | 'delivered' | 'delayed' | 'cancelled' | 'returned';

export type TransportMode = 'truck' | 'ground' | 'ship' | 'air' | 'rail';

export interface GPSCoordinate {
  latitude: number;
  longitude: number;
  altitude?: number | null;
  accuracy?: number | null;
}

export interface Shipment {
  id: string;
  tracking_number: string;
  order_id: string;
  sender_id: string;
  recipient_id: string;
  /** `Union[Dict[str, Any], str]` server-side. */
  origin_address: Record<string, unknown> | string;
  destination_address: Record<string, unknown> | string;
  status: ShipmentStatus | string;
  transport_mode: TransportMode | string;
  weight: number | null;
  weight_kg: number | null;
  dimensions: Record<string, number>;
  estimated_delivery: string | null;
  actual_delivery: string | null;
  created_at: string;
  updated_at: string;
}

export interface TrackingEvent {
  id: string;
  shipment_id: string;
  status: ShipmentStatus | string;
  location: GPSCoordinate | null;
  description: string;
  timestamp: string;
}

/* ---------- Notifications (backend/api/notifications.py) ---------- */

export type NotificationType = 'info' | 'success' | 'warning' | 'error' | 'alert';
export type NotificationChannel = 'in_app' | 'email' | 'sms' | 'push' | 'webhook';
export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface NotificationItem {
  id: string;
  user_id: string;
  type: NotificationType | string;
  channel: NotificationChannel | string;
  priority: NotificationPriority | string;
  title: string;
  message: string;
  data: Record<string, unknown>;
  read: boolean;
  created_at: string;
  read_at: string | null;
}

/* ---------- Admin / governance (backend/api/admin.py) ---------- */

export type SystemModuleName =
  | 'marketplace' | 'trading' | 'wallet' | 'escrow' | 'contracts'
  | 'logistics' | 'payments' | 'notifications' | 'ai_agents';

export interface AdminSystemStats {
  total_users: number;
  active_users: number;
  total_transactions: number;
  total_escrow_amount: number;
  active_shipments: number;
  pending_notifications: number;
  ai_agents_active: number;
  timestamp: string;
}

export interface AdminModuleHealth {
  module: SystemModuleName | string;
  status: string;
  uptime_seconds: number;
  error_rate: number;
  last_check: string;
}

export interface AdminAuditEntry {
  id: string;
  admin_id: string;
  action: string;
  target_type: string;
  target_id: string;
  details: Record<string, unknown>;
  timestamp: string;
}

/* ---------- KYC (backend/api/kyc.py) ---------- */

/** `GET /api/kyc/documents` — `List[Dict[str, Any]]`. */
export interface KycDocument {
  id?: string;
  verification_id?: string;
  document_type?: string;
  status?: string;
  uploaded_at?: string;
  reviewed_at?: string | null;
  [key: string]: unknown;
}

/* ---------- Auth profile (backend/api/auth.py UserResponse) ---------- */

/** Exact shape returned by `GET /api/auth/me` (Bearer JWT required). */
export interface AccountProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  kyc_status: string;
  kyc_level: string;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

/**
 * Session identity.
 *
 * `/api/auth/me` currently serializes `UserResponse` (names, kyc_status,
 * kyc_level, is_verified, last_login) and exposes NO role field. `user_type` is
 * therefore optional and role gating fails CLOSED until the serializer adds it
 * (documented drift — never assume a role the server did not send, §37/§48).
 */
export type SessionUser = AccountProfile & { user_type?: UserType };

/* ---------- News (backend/api/mineral_news_api.py) ---------- */

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  category: string;
  author: string;
  published_at: string;
  sentiment: string;
  impact_level: string;
  mentioned_minerals: string[];
  mentioned_companies: string[];
  mentioned_countries: string[];
  price_impact: Record<string, number>;
  ai_analysis: string;
  relevance_score: number;
  verification_status: string;
  tags: string[];
}

