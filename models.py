"""
Database Models - DEDAN Mine Backend
SQLAlchemy models for all database tables
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(50), nullable=False)  # miner, buyer, institutional, verifier, admin
    tier = Column(String(20), nullable=False, default='provisional')  # provisional, standard, premium, enterprise
    verification_level = Column(String(20), nullable=False, default='none')  # none, basic, professional, enterprise
    esg_score = Column(Integer, nullable=False, default=0)
    carbon_credits = Column(Float, nullable=False, default=0.0)
    reputation_score = Column(Float, nullable=False, default=0.0)
    total_transactions = Column(Integer, nullable=False, default=0)
    total_volume = Column(Float, nullable=False, default=0.0)
    location = Column(JSON, nullable=False)
    profile_data = Column(JSON, nullable=False)
    quantum_public_key = Column(String(1024), nullable=True)
    
    # NEW: Reputation and verification fields
    reputation_score = Column(Float, nullable=False, default=0.0)
    verification_data = Column(JSON, nullable=True)  # GPS/Satellite metadata
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    last_active = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    is_active = Column(Boolean, nullable=False, default=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    phone_verified = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    listings = relationship("Listing", back_populates="seller")
    bids = relationship("Bid", back_populates="bidder")
    buy_it_now_transactions_buyer = relationship("BuyItNowTransaction", foreign_keys="BuyItNowTransaction.buyer_id", back_populates="buyer")
    buy_it_now_transactions_seller = relationship("BuyItNowTransaction", foreign_keys="BuyItNowTransaction.seller_id", back_populates="seller")
    guardian_patterns = relationship("GuardianPattern", back_populates="user")
    market_agents = relationship("MarketAgent", back_populates="owner")
    agent_rentals = relationship("AgentRental", back_populates="renter")

class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    gem_type = Column(String(100), nullable=False, index=True)
    weight = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # carat, gram, kilogram, lot
    price = Column(Float, nullable=False, index=True)
    price_per_unit = Column(Float, nullable=False)  # Generated column
    listing_type = Column(String(20), nullable=False, index=True)  # auction, buy_it_now, make_offer, quick_match
    
    # Auction-specific fields
    auction_end_time = Column(DateTime(timezone=True), nullable=True)
    reserve_price = Column(Float, nullable=True)
    current_bid = Column(Float, nullable=False, default=0.0)
    current_bidder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    bid_count = Column(Integer, nullable=False, default=0)
    auto_extend = Column(Boolean, nullable=False, default=True)
    extend_time_minutes = Column(Integer, nullable=False, default=10)
    
    # Buy-It-Now specific fields
    buy_it_now_price = Column(Float, nullable=True)
    bulk_discount_available = Column(Boolean, nullable=False, default=False)
    bulk_tiers = Column(JSON, nullable=False, default=[])
    
    # Media and verification
    images = Column(JSON, nullable=False, default=[])
    video_url = Column(String(500), nullable=True)
    video_360_url = Column(String(500), nullable=True)
    authenticity_scan = Column(JSON, nullable=True)
    
    # Quality and trust
    quality_grade = Column(String(20), nullable=True)  # A, AA, AAA, investment, collector
    certification = Column(JSON, nullable=False, default=[])
    seller_notes = Column(Text, nullable=True)
    condition = Column(String(100), nullable=False, default='natural')
    
    # Future features
    traceability_enabled = Column(Boolean, nullable=False, default=False)
    video_negotiation_enabled = Column(Boolean, nullable=False, default=False)
    ai_agent_managed = Column(Boolean, nullable=False, default=False)
    esg_monitored = Column(Boolean, nullable=False, default=False)
    
    # Location and compliance
    mine_location = Column(JSON, nullable=False)
    extraction_date = Column(DateTime(timezone=True), nullable=True)
    origin_certificate = Column(String(100), nullable=True)
    compliance_status = Column(String(20), nullable=False, default='pending', index=True)
    ecx_compliance_data = Column(JSON, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=False, default=[])
    view_count = Column(Integer, nullable=False, default=0)
    watch_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    seller = relationship("User", back_populates="listings")
    auction = relationship("Auction", back_populates="listing", uselist=False)
    bids = relationship("Bid", back_populates="listing")
    buy_it_now_transactions = relationship("BuyItNowTransaction", back_populates="listing")
    traceability = relationship("TraceabilityRecord", back_populates="listing")
    esg_metrics = relationship("ESGMetrics", back_populates="listing")
    compliance_records = relationship("ComplianceRecord", back_populates="listing")
    video_sessions = relationship("VideoSession", back_populates="listing")

class Auction(Base):
    __tablename__ = "auctions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, unique=True, index=True)
    current_bid = Column(Float, nullable=False, default=0.0)
    current_bidder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    bid_count = Column(Integer, nullable=False, default=0)
    starting_price = Column(Float, nullable=False)
    reserve_price = Column(Float, nullable=True)
    auction_status = Column(String(20), nullable=False, default='active', index=True)
    auto_extend = Column(Boolean, nullable=False, default=True)
    extend_count = Column(Integer, nullable=False, default=0)
    max_extensions = Column(Integer, nullable=False, default=3)
    extend_time_minutes = Column(Integer, nullable=False, default=10)
    auction_type = Column(String(20), nullable=False, default='standard')  # standard, live_video, sealed_bid
    live_video_url = Column(String(500), nullable=True)
    scheduled_start_time = Column(DateTime(timezone=True), nullable=True)
    actual_start_time = Column(DateTime(timezone=True), nullable=True)
    actual_end_time = Column(DateTime(timezone=True), nullable=True)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    final_price = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    listing = relationship("Listing", back_populates="auction")
    current_bidder = relationship("User", foreign_keys=[current_bidder_id])
    winner = relationship("User", foreign_keys=[winner_id])

class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), ForeignKey("auctions.id"), nullable=False, index=True)
    bidder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False, index=True)
    bid_time = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    is_winning = Column(Boolean, nullable=False, default=False)
    is_proxy = Column(Boolean, nullable=False, default=False)
    max_proxy_amount = Column(Float, nullable=True)
    quantum_signature = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    auction = relationship("Auction", back_populates="bids")
    bidder = relationship("User", back_populates="bids")

class BuyItNowTransaction(Base):
    __tablename__ = "buy_it_now_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, index=True)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=False)
    commission_rate = Column(Float, nullable=False, default=5.0)
    commission_amount = Column(Float, nullable=False)
    seller_payout = Column(Float, nullable=False)
    
    # Transaction status
    transaction_status = Column(String(20), nullable=False, default='pending', index=True)
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(20), nullable=False, default='pending')
    payment_processor = Column(String(50), nullable=True)
    
    # Blockchain integration
    blockchain_tx_hash = Column(String(128), nullable=True)
    smart_contract_address = Column(String(128), nullable=True)
    escrow_released = Column(Boolean, nullable=False, default=False)
    
    # Timeline
    payment_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Relationships
    listing = relationship("Listing", back_populates="buy_it_now_transactions")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="buy_it_now_transactions_buyer")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="buy_it_now_transactions_seller")

class TraceabilityRecord(Base):
    __tablename__ = "traceability_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, index=True)
    mine_location = Column(JSON, nullable=False)
    extraction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    extraction_method = Column(String(100), nullable=False)
    miner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # IoT sensor data
    iot_sensors = Column(JSON, nullable=False, default=[])
    environmental_conditions = Column(JSON, nullable=False, default={})
    
    # ESG metrics
    carbon_footprint = Column(Float, nullable=False, default=0.0)
    water_usage = Column(Float, nullable=False, default=0.0)
    energy_source = Column(String(100), nullable=False)
    energy_consumption = Column(Float, nullable=False, default=0.0)
    
    # Blockchain integration
    verification_blockchain_hash = Column(String(128), nullable=False, index=True)
    previous_hash = Column(String(128), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    nonce = Column(String(64), nullable=True)
    
    # Compliance
    export_license_number = Column(String(100), nullable=True)
    compliance_officer_signature = Column(String(500), nullable=True)
    anti_smuggling_score = Column(Integer, nullable=False, default=0)
    manual_review = Column(Boolean, nullable=False, default=False)
    manual_reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    manual_review_notes = Column(Text, nullable=True)
    manual_review_date = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    listing = relationship("Listing", back_populates="traceability")
    miner = relationship("User", foreign_keys=[miner_id])
    manual_reviewer = relationship("User", foreign_keys=[manual_reviewer_id])
    approver = relationship("User", foreign_keys=[approved_by])

class ESGMetrics(Base):
    __tablename__ = "esg_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=True, index=True)
    
    # ESG scores (0-100)
    overall_score = Column(Integer, nullable=False)
    environmental_score = Column(Integer, nullable=False)
    social_score = Column(Integer, nullable=False)
    governance_score = Column(Integer, nullable=False)
    
    # Carbon credits
    carbon_credits_earned = Column(Float, nullable=False, default=0.0)
    carbon_credits_used = Column(Float, nullable=False, default=0.0)
    
    # Social impact
    community_investment = Column(Float, nullable=False, default=0.0)
    local_jobs_created = Column(Integer, nullable=False, default=0)
    training_programs_supported = Column(Integer, nullable=False, default=0)
    fair_labor_practices = Column(Boolean, nullable=False, default=False)
    health_safety_standards = Column(Boolean, nullable=False, default=False)
    community_engagement = Column(Integer, nullable=False, default=0)
    
    # AI explanation
    ai_explanation = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.00)
    model_version = Column(String(50), nullable=True)
    
    assessment_date = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc).date(), index=True)
    assessor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="esg_metrics")
    listing = relationship("Listing", back_populates="esg_metrics")
    assessor = relationship("User", foreign_keys=[assessor_id])

class ComplianceRecord(Base):
    __tablename__ = "compliance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=True, index=True)
    
    # Compliance information
    compliance_type = Column(String(50), nullable=False, index=True)  # export_license, import_permit, authenticity_certificate, origin_verification, anti_smuggling_check
    jurisdiction = Column(String(100), nullable=False, index=True)  # Ethiopia, Kenya, Tanzania, etc.
    
    # Document management
    documents = Column(JSON, nullable=False, default=[])
    document_hashes = Column(JSON, nullable=False, default=[])
    
    # Automated compliance
    ai_risk_score = Column(Integer, nullable=False, default=0)
    compliance_score = Column(Integer, nullable=False, default=0)
    automated_checks = Column(JSON, nullable=False, default={})
    
    # Human review
    manual_review_required = Column(Boolean, nullable=False, default=False)
    manual_reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    manual_review_notes = Column(Text, nullable=True)
    manual_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status and timeline
    status = Column(String(20), nullable=False, default='pending', index=True)  # pending, under_review, approved, rejected, requires_additional_info
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # ECX integration
    ecx_reference_number = Column(String(100), nullable=True, index=True)
    ecx_submission_date = Column(DateTime(timezone=True), nullable=True)
    ecx_approval_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="compliance_records")
    listing = relationship("Listing", back_populates="compliance_records")
    manual_reviewer = relationship("User", foreign_keys=[manual_reviewer_id])
    approver = relationship("User", foreign_keys=[approved_by])

class AIAgent(Base):
    __tablename__ = "ai_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    agent_name = Column(String(200), nullable=False)
    agent_type = Column(String(50), nullable=False, index=True)  # trading, analysis, verification, compliance, portfolio_management
    
    # Agent configuration
    strategy = Column(JSON, nullable=False)
    risk_tolerance = Column(String(20), nullable=False, default='moderate')  # conservative, moderate, aggressive
    target_markets = Column(JSON, nullable=False, default=[])
    budget_limits = Column(JSON, nullable=False, default={})
    profit_margin_target = Column(Float, nullable=False, default=0.0)
    max_position_size = Column(Float, nullable=False, default=0.0)
    stop_loss_percentage = Column(Float, nullable=False, default=0.0)
    take_profit_percentage = Column(Float, nullable=False, default=0.0)
    
    # AI model information
    model_type = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    federated_learning_participant = Column(Boolean, nullable=False, default=True)
    
    # Performance metrics
    performance_metrics = Column(JSON, nullable=False, default={})
    learning_data = Column(JSON, nullable=False, default=[])
    reinforcement_learning_rewards = Column(JSON, nullable=False, default=[])
    
    # Agent status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    last_active = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    total_actions = Column(Integer, nullable=False, default=0)
    successful_actions = Column(Integer, nullable=False, default=0)
    
    # Relationships
    owner = relationship("User")
    agent_actions = relationship("AgentAction", back_populates="agent")

class AgentAction(Base):
    __tablename__ = "agent_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # place_bid, make_offer, analyze_market, verify_authenticity, compliance_check, portfolio_rebalance
    
    # Action details
    action_data = Column(JSON, nullable=False)
    target_listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=True, index=True)
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # AI decision making
    confidence_score = Column(Float, nullable=False, default=0.00)
    reasoning = Column(Text, nullable=True)
    alternative_actions_considered = Column(JSON, nullable=False, default=[])
    
    # Outcome
    outcome = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=False, default=False)
    profit_impact = Column(Float, nullable=False, default=0.00)
    
    # Federated learning
    learning_contribution = Column(JSON, nullable=False, default={})
    privacy_preserved = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Relationships
    agent = relationship("AIAgent", back_populates="agent_actions")
    target_listing = relationship("Listing")
    target_user = relationship("User")

class VideoSession(Base):
    __tablename__ = "video_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, index=True)
    host_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session configuration
    session_type = Column(String(50), nullable=False)  # negotiation, live_auction, verification_inspection, expert_consultation
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    max_participants = Column(Integer, nullable=False, default=10)
    
    # Video infrastructure
    video_url = Column(String(500), nullable=True)
    recording_url = Column(String(500), nullable=True)
    stream_key = Column(String(500), nullable=True)
    bandwidth_requirements = Column(JSON, nullable=False, default={})
    
    # Participants
    participant_ids = Column(JSON, nullable=False, default=[])
    waiting_room = Column(JSON, nullable=False, default=[])
    active_participants = Column(JSON, nullable=False, default=[])
    
    # Session data
    chat_messages = Column(JSON, nullable=False, default=[])
    shared_documents = Column(JSON, nullable=False, default=[])
    screen_shares = Column(JSON, nullable=False, default=[])
    
    # Session status
    session_status = Column(String(20), nullable=False, default='scheduled', index=True)  # scheduled, waiting, active, paused, ended, cancelled
    actual_start_time = Column(DateTime(timezone=True), nullable=True)
    actual_end_time = Column(DateTime(timezone=True), nullable=True)
    end_reason = Column(String(100), nullable=True)  # completed, technical_issue, mutual_agreement, etc.
    
    # Security and recording
    encryption_enabled = Column(Boolean, nullable=False, default=True)
    quantum_encryption_key = Column(String(1024), nullable=True)
    recording_enabled = Column(Boolean, nullable=False, default=True)
    auto_transcription = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    listing = relationship("Listing", back_populates="video_sessions")
    host = relationship("User")

class TrustSignal(Base):
    __tablename__ = "trust_signals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    signal_type = Column(String(50), nullable=False, index=True)  # positive_feedback, watch_list_add, watch_list_remove, verified_purchase, quick_response, professional_verification, bulk_trader, long_term_member
    
    # Signal data
    signal_data = Column(JSON, nullable=False)
    source_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    context = Column(String(100), nullable=True)  # auction, purchase, verification, etc.
    
    # Signal strength
    signal_strength = Column(Float, nullable=False, default=1.00)
    decay_rate = Column(Float, nullable=False, default=0.95)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Verification
    is_verified = Column(Boolean, nullable=False, default=False)
    verification_method = Column(String(50), nullable=True)  # blockchain, multi_sig, manual_review
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    source_user = relationship("User", foreign_keys=[source_user_id])

class BulkOrder(Base):
    __tablename__ = "bulk_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, index=True)
    
    # Bulk order details
    quantity_requested = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    
    # Tiered pricing
    pricing_tier = Column(JSON, nullable=False)  # {min_qty: 10, max_qty: 100, discount_percent: 5}
    volume_discount = Column(Float, nullable=False, default=0.00)
    
    # Order status
    order_status = Column(String(20), nullable=False, default='requested', index=True)  # requested, negotiating, confirmed, partial_shipment, shipped, delivered, cancelled
    partial_deliveries = Column(JSON, nullable=False, default=[])
    
    # Logistics
    shipping_address = Column(JSON, nullable=False)
    preferred_shipping_method = Column(String(100), nullable=True)
    special_requirements = Column(Text, nullable=True)
    
    # Timeline
    negotiation_deadline = Column(DateTime(timezone=True), nullable=True)
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    buyer = relationship("User")
    listing = relationship("Listing")

# Add indexes for performance
Index('idx_users_email', User.email)
Index('idx_users_username', User.username)
Index('idx_users_tier', User.tier)
Index('idx_users_reputation', User.reputation_score.desc())

Index('idx_listings_seller', Listing.seller_id)
Index('idx_listings_category', Listing.category)
Index('idx_listings_gem_type', Listing.gem_type)
Index('idx_listings_listing_type', Listing.listing_type)
Index('idx_listings_price', Listing.price)
Index('idx_listings_created', Listing.created_at.desc())

Index('idx_auctions_listing', Auction.listing_id)
Index('idx_auctions_current_bidder', Auction.current_bidder_id)
Index('idx_auctions_status', Auction.auction_status)
Index('idx_auctions_end_time', Auction.actual_end_time)

Index('idx_bids_auction', Bid.auction_id)
Index('idx_bids_bidder', Bid.bidder_id)
Index('idx_bids_amount', Bid.amount.desc())
Index('idx_bids_time', Bid.bid_time.desc())

Index('idx_buy_it_now_transactions_listing', BuyItNowTransaction.listing_id)
Index('idx_buy_it_now_transactions_buyer', BuyItNowTransaction.buyer_id)
Index('idx_buy_it_now_transactions_seller', BuyItNowTransaction.seller_id)
Index('idx_buy_it_now_transactions_status', BuyItNowTransaction.transaction_status)
Index('idx_buy_it_now_transactions_created', BuyItNowTransaction.created_at.desc())

Index('idx_traceability_listing', TraceabilityRecord.listing_id)
Index('idx_traceability_mine_location', TraceabilityRecord.mine_location)
Index('idx_traceability_extraction_date', TraceabilityRecord.extraction_date)
Index('idx_traceability_blockchain_hash', TraceabilityRecord.verification_blockchain_hash)

Index('idx_esg_user', ESGMetrics.user_id)
Index('idx_esg_listing', ESGMetrics.listing_id)
Index('idx_esg_overall_score', ESGMetrics.overall_score.desc())
Index('idx_esg_assessment_date', ESGMetrics.assessment_date.desc())

Index('idx_compliance_user', ComplianceRecord.user_id)
Index('idx_compliance_listing', ComplianceRecord.listing_id)
Index('idx_compliance_status', ComplianceRecord.status)
Index('idx_compliance_type', ComplianceRecord.compliance_type)
Index('idx_compliance_jurisdiction', ComplianceRecord.jurisdiction)
Index('idx_compliance_ecx_reference', ComplianceRecord.ecx_reference_number)

Index('idx_ai_agents_owner', AIAgent.owner_id)
Index('idx_ai_agents_type', AIAgent.agent_type)
Index('idx_ai_agents_active', AIAgent.is_active)

Index('idx_agent_actions_agent', AgentAction.agent_id)
Index('idx_agent_actions_type', AgentAction.action_type)
Index('idx_agent_actions_target_listing', AgentAction.target_listing_id)
Index('idx_agent_actions_created', AgentAction.created_at.desc())

Index('idx_video_sessions_listing', VideoSession.listing_id)
Index('idx_video_sessions_host', VideoSession.host_id)
Index('idx_video_sessions_scheduled_time', VideoSession.scheduled_time)
Index('idx_video_sessions_status', VideoSession.session_status)

Index('idx_trust_signals_user', TrustSignal.user_id)
Index('idx_trust_signals_type', TrustSignal.signal_type)
Index('idx_trust_signals_source_user', TrustSignal.source_user_id)
Index('idx_trust_signals_strength', TrustSignal.signal_strength.desc())
Index('idx_trust_signals_expires', TrustSignal.expires_at)

# Add new tables at the end of the file

class GuardianPattern(Base):
    __tablename__ = "user_guardians"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    behavior_patterns = Column(JSON, nullable=False)  # login_times, typical_trade_sizes
    risk_history = Column(JSON, nullable=False)  # Historical risk scores
    last_analysis = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="guardian_patterns")

class MarketAgent(Base):
    __tablename__ = "market_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False, index=True)  # mineral_scout, price_predictor, risk_analyzer, market_matcher
    rental_price_per_hour = Column(Float, nullable=False)
    min_rental_hours = Column(Integer, nullable=False, default=1)
    max_rental_hours = Column(Integer, nullable=False, default=168)  # 1 week
    description = Column(Text, nullable=True)
    experience_points = Column(Integer, nullable=False, default=0)
    is_available = Column(Boolean, nullable=False, default=True, index=True)
    total_rentals = Column(Integer, nullable=False, default=0)
    total_earnings = Column(Float, nullable=False, default=0.0)
    average_rating = Column(Float, nullable=False, default=0.0)
    agent_config = Column(JSON, nullable=True)  # Agent configuration and training data
    performance_metrics = Column(JSON, nullable=False)  # Historical performance data
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="market_agents")
    rentals = relationship("AgentRental", back_populates="agent")

class AgentRental(Base):
    __tablename__ = "agent_rentals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("market_agents.id"), nullable=False, index=True)
    renter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    rental_duration_hours = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # tokens, usdc, usdt, eth, btc
    rental_start_time = Column(DateTime(timezone=True), nullable=False)
    rental_end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default='active', index=True)  # active, completed, cancelled
    terms_accepted = Column(Boolean, nullable=False, default=False)
    access_token = Column(String(255), nullable=True)  # Temporary access token for agent
    usage_logs = Column(JSON, nullable=False)  # Agent usage during rental
    rating = Column(Integer, nullable=True)  # 1-5 rating from renter
    review = Column(Text, nullable=True)  # Review comments
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Relationships
    agent = relationship("MarketAgent", back_populates="rentals")
    renter = relationship("User", back_populates="agent_rentals")

# Add indexes for new tables
Index('idx_guardian_patterns_user', GuardianPattern.user_id)
Index('idx_guardian_patterns_updated', GuardianPattern.updated_at.desc())

Index('idx_market_agents_owner', MarketAgent.owner_id)
Index('idx_market_agents_type', MarketAgent.agent_type)
Index('idx_market_agents_available', MarketAgent.is_available)
Index('idx_market_agents_experience', MarketAgent.experience_points.desc())
Index('idx_market_agents_created', MarketAgent.created_at.desc())

# Add unified tables at the end of the file

class UnifiedUserSession(Base):
    __tablename__ = "unified_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Core user data (protected by Zero-Knowledge Shield)
    user_profile = Column(JSON, nullable=False)
    verification_data = Column(JSON, nullable=False)
    
    # Guardian AI Security State
    security_level = Column(String(50), nullable=False, default='standard')
    risk_score = Column(Float, nullable=False, default=0.0)
    behavior_patterns = Column(JSON, nullable=False)
    security_flags = Column(JSON, nullable=False)
    is_frozen = Column(Boolean, nullable=False, default=False)
    freeze_reason = Column(String(500), nullable=True)
    
    # Reputation Oracle State
    trust_score = Column(Float, nullable=False, default=50.0)
    fee_discount = Column(Float, nullable=False, default=0.0)
    trade_history = Column(JSON, nullable=False)
    reputation_factors = Column(JSON, nullable=False)
    
    # Satellite Verification State
    location_verified = Column(Boolean, nullable=False, default=False)
    satellite_coordinates = Column(JSON, nullable=True)
    space_verified = Column(Boolean, nullable=False, default=False)
    sentinel_provenance = Column(String(255), nullable=True)
    
    # Micro-Insurance State
    insurance_active = Column(Boolean, nullable=False, default=False)
    risk_premium = Column(Float, nullable=False, default=0.0)
    coverage_amount = Column(Float, nullable=False, default=0.0)
    insurance_claims = Column(JSON, nullable=False)
    
    # Agent Marketplace State
    owned_agents = Column(JSON, nullable=False)
    rented_agents = Column(JSON, nullable=False)
    agent_permissions = Column(JSON, nullable=False)
    
    # Legacy Chain State
    inheritance_configured = Column(Boolean, nullable=False, default=False)
    heir_addresses = Column(JSON, nullable=False)
    legacy_triggers = Column(JSON, nullable=False)
    
    # Co-Ownership State
    owned_shares = Column(JSON, nullable=False)
    dao_tokens = Column(Float, nullable=False, default=0.0)
    governance_votes = Column(JSON, nullable=False)
    
    # ESG Impact State
    esg_score = Column(Float, nullable=False, default=0.0)
    ethical_impact_credits = Column(Float, nullable=False, default=0.0)
    sustainability_metrics = Column(JSON, nullable=False)
    
    # Community Oracle State
    verification_requests = Column(JSON, nullable=False)
    peer_validations = Column(JSON, nullable=False)
    community_reputation = Column(Float, nullable=False, default=0.0)
    
    # Privacy and security flags
    pii_protected = Column(Boolean, nullable=False, default=True)
    encryption_enabled = Column(Boolean, nullable=False, default=True)
    zk_proof_verified = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="unified_sessions")

class FeatureExecutionLog(Base):
    __tablename__ = "feature_execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Feature execution details
    feature_name = Column(String(100), nullable=False, index=True)
    priority = Column(Integer, nullable=False)  # FeaturePriority enum value
    status = Column(String(20), nullable=False, index=True)  # FeatureStatus enum value
    
    # Request and response data
    request_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=True)
    error_message = Column(String(1000), nullable=True)
    
    # Execution metrics
    execution_time_ms = Column(Integer, nullable=False)
    dependencies_satisfied = Column(Boolean, nullable=False, default=True)
    blocked_by = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="feature_executions")

class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Policy details
    coverage_amount = Column(Float, nullable=False)
    premium_rate = Column(Float, nullable=False)
    total_premium = Column(Float, nullable=False)
    policy_type = Column(String(50), nullable=False, default='standard')
    
    # Risk assessment
    risk_factors = Column(JSON, nullable=False)
    total_risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    
    # Verification status
    satellite_verified = Column(Boolean, nullable=False, default=False)
    location_risk = Column(Float, nullable=False, default=0.0)
    
    # Policy status
    active = Column(Boolean, nullable=False, default=True)
    paid = Column(Boolean, nullable=False, default=False)
    claims_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="insurance_policies")

class SatelliteVerification(Base):
    __tablename__ = "satellite_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    transaction_id = Column(String(100), nullable=True, index=True)
    
    # Coordinate data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=False)
    
    # Sentinel API data
    satellite_id = Column(String(100), nullable=False)
    provenance_hash = Column(String(64), nullable=False, index=True)
    capture_time = Column(DateTime(timezone=True), nullable=False)
    image_resolution = Column(String(20), nullable=True)
    cloud_cover = Column(String(10), nullable=True)
    
    # Verification results
    verified = Column(Boolean, nullable=False, default=False)
    confidence_score = Column(Float, nullable=False)
    verification_method = Column(String(50), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="satellite_verifications")

# Add indexes for unified tables
Index('idx_unified_sessions_user', UnifiedUserSession.user_id)
Index('idx_unified_sessions_session', UnifiedUserSession.session_id)
Index('idx_unified_sessions_frozen', UnifiedUserSession.is_frozen)
Index('idx_unified_sessions_trust_score', UnifiedUserSession.trust_score)
Index('idx_unified_sessions_space_verified', UnifiedUserSession.space_verified)
Index('idx_unified_sessions_insurance_active', UnifiedUserSession.insurance_active)
Index('idx_unified_sessions_created', UnifiedUserSession.created_at.desc())
Index('idx_unified_sessions_updated', UnifiedUserSession.updated_at.desc())

Index('idx_feature_executions_session', FeatureExecutionLog.session_id)
Index('idx_feature_executions_user', FeatureExecutionLog.user_id)
Index('idx_feature_executions_feature', FeatureExecutionLog.feature_name)
Index('idx_feature_executions_status', FeatureExecutionLog.status)
Index('idx_feature_executions_priority', FeatureExecutionLog.priority)
Index('idx_feature_executions_created', FeatureExecutionLog.created_at.desc())

Index('idx_insurance_policies_user', InsurancePolicy.user_id)
Index('idx_insurance_policies_session', InsurancePolicy.session_id)
Index('idx_insurance_policies_policy_id', InsurancePolicy.policy_id)
Index('idx_insurance_policies_active', InsurancePolicy.active)
Index('idx_insurance_policies_paid', InsurancePolicy.paid)
Index('idx_insurance_policies_expires', InsurancePolicy.expires_at)

Index('idx_satellite_verifications_user', SatelliteVerification.user_id)
Index('idx_satellite_verifications_session', SatelliteVerification.session_id)
Index('idx_satellite_verifications_transaction', SatelliteVerification.transaction_id)
Index('idx_satellite_verifications_provenance', SatelliteVerification.provenance_hash)
Index('idx_satellite_verifications_verified', SatelliteVerification.verified)
Index('idx_satellite_verifications_created', SatelliteVerification.created_at.desc())
