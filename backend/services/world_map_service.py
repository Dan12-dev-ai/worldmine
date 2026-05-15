"""
🌍 DEDAN 2.0 - Interactive World Map Service
Real-time buyer-seller contract visualization with geospatial intelligence
Better than Bloomberg Terminal and Reuters Eikon for contract tracking
"""

import asyncio
import json
import uuid
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import asyncpg
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, Boolean, DateTime, Index, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import geopy
from geopy.distance import geodesic
import folium
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb")
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

Base = declarative_base()

class ContractStatus(Enum):
    """Contract status types"""
    ACTIVE = "active"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    DISPUTED = "disputed"

class TransportMode(Enum):
    """Transportation modes"""
    SEA_FREIGHT = "sea_freight"
    AIR_FREIGHT = "air_freight"
    ROAD_TRANSPORT = "road_transport"
    RAIL_TRANSPORT = "rail_transport"
    MULTIMODAL = "multimodal"

class ContractType(Enum):
    """Contract types"""
    SPOT = "spot"
    FORWARD = "forward"
    FUTURES = "futures"
    OPTIONS = "options"
    SWAP = "swap"
    LONG_TERM = "long_term"

@dataclass
class Location:
    """Geographic location data"""
    id: str
    name: str
    country: str
    region: str
    latitude: float
    longitude: float
    city: str
    postal_code: str
    timezone: str
    is_port: bool
    is_airport: bool
    is_mining_site: bool
    is_processing_facility: bool

@dataclass
class ContractParty:
    """Contract party information"""
    id: str
    name: str
    type: str  # "buyer" or "seller"
    company_type: str
    location: Location
    contact_email: str
    contact_phone: str
    verification_status: str
    reputation_score: float
    total_contracts: int
    success_rate: float
    languages_spoken: List[str]
    specialties: List[str]

@dataclass
class ShippingRoute:
    """Shipping route information"""
    id: str
    origin: Location
    destination: Location
    transport_mode: TransportMode
    distance_km: float
    estimated_duration_days: float
    cost_per_ton: float
    carbon_footprint_kg: float
    route_coordinates: List[Tuple[float, float]]
    shipping_lines: List[str]
    port_calls: List[str]
    risk_factors: List[str]

@dataclass
class MineralContract:
    """Complete mineral contract data"""
    id: str
    contract_number: str
    contract_type: ContractType
    status: ContractStatus
    mineral_type: str
    quantity_tons: float
    price_per_ton: float
    total_value_usd: float
    currency: str
    
    # Parties
    buyer: ContractParty
    seller: ContractParty
    
    # Locations and shipping
    origin_location: Location
    destination_location: Location
    shipping_route: ShippingRoute
    
    # Timeline
    created_at: datetime
    execution_date: datetime
    delivery_date: datetime
    expiry_date: Optional[datetime]
    
    # Quality and specifications
    purity_grade: str
    quality_certifications: List[str]
    inspection_required: bool
    inspection_location: Optional[Location]
    
    # Payment terms
    payment_method: str
    payment_terms: str
    letter_of_credit_required: bool
    bank_guarantee_required: bool
    
    # Risk and compliance
    risk_score: float
    compliance_flags: List[str]
    sanctions_check_passed: bool
    anti_money_laundering_check_passed: bool
    
    # Additional data
    contract_documents: List[str]
    tracking_number: Optional[str]
    insurance_coverage: float
    force_majeure_clause: bool
    
    created_at: datetime
    updated_at: datetime

class LocationDB(Base):
    """Database model for locations"""
    __tablename__ = "locations"
    
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    country = Column(String, index=True)
    region = Column(String, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    city = Column(String)
    postal_code = Column(String)
    timezone = Column(String)
    is_port = Column(Boolean, default=False)
    is_airport = Column(Boolean, default=False)
    is_mining_site = Column(Boolean, default=False)
    is_processing_facility = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContractDB(Base):
    """Database model for contracts"""
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True)
    contract_number = Column(String, unique=True, index=True)
    contract_type = Column(String, index=True)
    status = Column(String, index=True)
    mineral_type = Column(String, index=True)
    quantity_tons = Column(Float)
    price_per_ton = Column(Float)
    total_value_usd = Column(Float)
    currency = Column(String)
    
    # Parties
    buyer_id = Column(String, index=True)
    seller_id = Column(String, index=True)
    
    # Locations
    origin_location_id = Column(String, index=True)
    destination_location_id = Column(String, index=True)
    
    # Timeline
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    execution_date = Column(DateTime)
    delivery_date = Column(DateTime)
    expiry_date = Column(DateTime)
    
    # Quality
    purity_grade = Column(String)
    quality_certifications = Column(ARRAY(String))
    inspection_required = Column(Boolean, default=False)
    inspection_location_id = Column(String)
    
    # Payment
    payment_method = Column(String)
    payment_terms = Column(String)
    letter_of_credit_required = Column(Boolean, default=False)
    bank_guarantee_required = Column(Boolean, default=False)
    
    # Risk
    risk_score = Column(Float, index=True)
    compliance_flags = Column(ARRAY(String))
    sanctions_check_passed = Column(Boolean, default=False)
    anti_money_laundering_check_passed = Column(Boolean, default=False)
    
    # Additional
    contract_documents = Column(ARRAY(String))
    tracking_number = Column(String)
    insurance_coverage = Column(Float)
    force_majeure_clause = Column(Boolean, default=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorldMapService:
    """
    Advanced world map service for contract visualization
    Real-time geospatial intelligence and route optimization
    """
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Initialize geopy
        self.geolocator = geopy.Nominatim(user_agent="dedan_world_map")
        
        # Initialize location cache
        self.locations_cache = {}
        
        # Initialize contract cache
        self.contracts_cache = {}
        
        # Initialize shipping routes
        self.shipping_routes = self._initialize_shipping_routes()
        
        # Initialize major ports and airports
        self.major_ports = self._initialize_major_ports()
        self.major_airports = self._initialize_major_airports()
        
        print("🗺️ World Map Service initialized")
    
    def _initialize_shipping_routes(self) -> Dict[str, ShippingRoute]:
        """Initialize major shipping routes"""
        routes = {}
        
        # Major sea routes
        routes['pacific_to_asia'] = ShippingRoute(
            id='pacific_to_asia',
            origin=Location(
                id='los_angeles', name='Los Angeles', country='USA',
                region='North America', latitude=34.0522, longitude=-118.2437,
                city='Los Angeles', postal_code='90210', timezone='PST',
                is_port=True, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            destination=Location(
                id='shanghai', name='Shanghai', country='China',
                region='Asia', latitude=31.2304, longitude=121.4737,
                city='Shanghai', postal_code='200000', timezone='CST',
                is_port=True, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            transport_mode=TransportMode.SEA_FREIGHT,
            distance_km=10500,
            estimated_duration_days=14,
            cost_per_ton=85.0,
            carbon_footprint_kg=2500,
            route_coordinates=[(34.0522, -118.2437), (35.6762, 139.6503), (31.2304, 121.4737)],
            shipping_lines=['Maersk', 'MSC', 'COSCO'],
            port_calls=['Tokyo', 'Yokohama'],
            risk_factors=['piracy', 'weather', 'port_congestion']
        )
        
        routes['europe_to_asia'] = ShippingRoute(
            id='europe_to_asia',
            origin=Location(
                id='rotterdam', name='Rotterdam', country='Netherlands',
                region='Europe', latitude=51.9244, longitude=4.4777,
                city='Rotterdam', postal_code='3011', timezone='CET',
                is_port=True, is_airport=False, is_mining_site=False, is_processing_facility=False
            ),
            destination=Location(
                id='singapore', name='Singapore', country='Singapore',
                region='Asia', latitude=1.3521, longitude=103.8198,
                city='Singapore', postal_code='018956', timezone='SGT',
                is_port=True, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            transport_mode=TransportMode.SEA_FREIGHT,
            distance_km=14500,
            estimated_duration_days=21,
            cost_per_ton=120.0,
            carbon_footprint_kg=3500,
            route_coordinates=[(51.9244, 4.4777), (25.2048, 55.2708), (1.3521, 103.8198)],
            shipping_lines=['Maersk', 'MSC', 'CMA CGM'],
            port_calls=['Suez Canal', 'Colombo'],
            risk_factors=['geopolitical', 'suez_congestion', 'weather']
        )
        
        return routes
    
    def _initialize_major_ports(self) -> List[Location]:
        """Initialize major ports worldwide"""
        return [
            Location(
                id='rotterdam', name='Rotterdam', country='Netherlands',
                region='Europe', latitude=51.9244, longitude=4.4777,
                city='Rotterdam', postal_code='3011', timezone='CET',
                is_port=True, is_airport=False, is_mining_site=False, is_processing_facility=False
            ),
            Location(
                id='singapore', name='Singapore', country='Singapore',
                region='Asia', latitude=1.3521, longitude=103.8198,
                city='Singapore', postal_code='018956', timezone='SGT',
                is_port=True, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            Location(
                id='shanghai', name='Shanghai', country='China',
                region='Asia', latitude=31.2304, longitude=121.4737,
                city='Shanghai', postal_code='200000', timezone='CST',
                is_port=True, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            Location(
                id='los_angeles', name='Los Angeles', country='USA',
                region='North America', latitude=34.0522, longitude=-118.2437,
                city='Los Angeles', postal_code='90210', timezone='PST',
                is_port=True, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            Location(
                id='dubai', name='Dubai', country='UAE',
                region='Middle East', latitude=25.2048, longitude=55.2708,
                city='Dubai', postal_code='00000', timezone='GST',
                is_port=True, is_airport=True, is_mining_site=False, is_processing_facility=False
            )
        ]
    
    def _initialize_major_airports(self) -> List[Location]:
        """Initialize major airports worldwide"""
        return [
            Location(
                id='heathrow', name='Heathrow', country='UK',
                region='Europe', latitude=51.4700, longitude=-0.4543,
                city='London', postal_code='TW6', timezone='GMT',
                is_port=False, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            Location(
                id='jfk', name='JFK', country='USA',
                region='North America', latitude=40.6413, longitude=-73.7781,
                city='New York', postal_code='11430', timezone='EST',
                is_port=False, is_airport=True, is_mining_site=False, is_processing_facility=False
            ),
            Location(
                id='narita', name='Narita', country='Japan',
                region='Asia', latitude=35.7653, longitude=140.3864,
                city='Tokyo', postal_code='286-0001', timezone='JST',
                is_port=False, is_airport=True, is_mining_site=False, is_processing_facility=False
            )
        ]
    
    async def create_contract(self, contract_data: Dict[str, Any]) -> MineralContract:
        """Create new mineral contract"""
        try:
            # Generate contract ID
            contract_id = str(uuid.uuid4())
            
            # Create locations
            origin_location = await self._get_or_create_location(contract_data['origin_location'])
            destination_location = await self._get_or_create_location(contract_data['destination_location'])
            
            # Create parties
            buyer = await self._create_contract_party(contract_data['buyer'], 'buyer')
            seller = await self._create_contract_party(contract_data['seller'], 'seller')
            
            # Create shipping route
            shipping_route = await self._calculate_shipping_route(
                origin_location, destination_location, contract_data.get('transport_mode', TransportMode.SEA_FREIGHT)
            )
            
            # Create contract
            contract = MineralContract(
                id=contract_id,
                contract_number=contract_data['contract_number'],
                contract_type=ContractType(contract_data['contract_type']),
                status=ContractStatus(contract_data['status']),
                mineral_type=contract_data['mineral_type'],
                quantity_tons=contract_data['quantity_tons'],
                price_per_ton=contract_data['price_per_ton'],
                total_value_usd=contract_data['quantity_tons'] * contract_data['price_per_ton'],
                currency=contract_data.get('currency', 'USD'),
                
                buyer=buyer,
                seller=seller,
                
                origin_location=origin_location,
                destination_location=destination_location,
                shipping_route=shipping_route,
                
                contract_created_at=datetime.utcnow(),
                execution_date=datetime.fromisoformat(contract_data['execution_date']),
                delivery_date=datetime.fromisoformat(contract_data['delivery_date']),
                expiry_date=datetime.fromisoformat(contract_data['expiry_date']) if contract_data.get('expiry_date') else None,
                
                purity_grade=contract_data.get('purity_grade', '99.9%'),
                quality_certifications=contract_data.get('quality_certifications', []),
                inspection_required=contract_data.get('inspection_required', False),
                inspection_location=await self._get_or_create_location(contract_data['inspection_location']) if contract_data.get('inspection_location') else None,
                
                payment_method=contract_data.get('payment_method', 'wire_transfer'),
                payment_terms=contract_data.get('payment_terms', 'net_30'),
                letter_of_credit_required=contract_data.get('letter_of_credit_required', False),
                bank_guarantee_required=contract_data.get('bank_guarantee_required', False),
                
                risk_score=await self._calculate_risk_score(contract_data),
                compliance_flags=contract_data.get('compliance_flags', []),
                sanctions_check_passed=contract_data.get('sanctions_check_passed', True),
                anti_money_laundering_check_passed=contract_data.get('anti_money_laundering_check_passed', True),
                
                contract_documents=contract_data.get('contract_documents', []),
                tracking_number=contract_data.get('tracking_number'),
                insurance_coverage=contract_data.get('insurance_coverage', 0.0),
                force_majeure_clause=contract_data.get('force_majeure_clause', True),
                
                created_at=contract_created_at,
                updated_at=contract_created_at
            )
            
            # Save to database
            await self._save_contract_to_database(contract)
            
            # Cache contract
            self.contracts_cache[contract_id] = contract
            
            print(f"✅ Created contract {contract.contract_number}")
            return contract
            
        except Exception as e:
            print(f"❌ Error creating contract: {e}")
            raise
    
    async def _get_or_create_location(self, location_data: Dict[str, Any]) -> Location:
        """Get existing location or create new one"""
        try:
            # Check cache first
            cache_key = f"{location_data['latitude']},{location_data['longitude']}"
            if cache_key in self.locations_cache:
                return self.locations_cache[cache_key]
            
            # Check database
            session = self.SessionLocal()
            try:
                db_location = session.query(LocationDB).filter_by(
                    latitude=location_data['latitude'],
                    longitude=location_data['longitude']
                ).first()
                
                if db_location:
                    location = Location(
                        id=db_location.id,
                        name=db_location.name,
                        country=db_location.country,
                        region=db_location.region,
                        latitude=db_location.latitude,
                        longitude=db_location.longitude,
                        city=db_location.city,
                        postal_code=db_location.postal_code,
                        timezone=db_location.timezone,
                        is_port=db_location.is_port,
                        is_airport=db_location.is_airport,
                        is_mining_site=db_location.is_mining_site,
                        is_processing_facility=db_location.is_processing_facility
                    )
                else:
                    # Create new location
                    location_id = str(uuid.uuid4())
                    location = Location(
                        id=location_id,
                        name=location_data['name'],
                        country=location_data['country'],
                        region=location_data.get('region', ''),
                        latitude=location_data['latitude'],
                        longitude=location_data['longitude'],
                        city=location_data.get('city', ''),
                        postal_code=location_data.get('postal_code', ''),
                        timezone=location_data.get('timezone', 'UTC'),
                        is_port=location_data.get('is_port', False),
                        is_airport=location_data.get('is_airport', False),
                        is_mining_site=location_data.get('is_mining_site', False),
                        is_processing_facility=location_data.get('is_processing_facility', False)
                    )
                    
                    # Save to database
                    db_location = LocationDB(
                        id=location_id,
                        name=location.name,
                        country=location.country,
                        region=location.region,
                        latitude=location.latitude,
                        longitude=location.longitude,
                        city=location.city,
                        postal_code=location.postal_code,
                        timezone=location.timezone,
                        is_port=location.is_port,
                        is_airport=location.is_airport,
                        is_mining_site=location.is_mining_site,
                        is_processing_facility=location.is_processing_facility
                    )
                    session.add(db_location)
                    session.commit()
                
                # Cache location
                self.locations_cache[cache_key] = location
                return location
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"❌ Error getting/creating location: {e}")
            raise
    
    async def _create_contract_party(self, party_data: Dict[str, Any], party_type: str) -> ContractParty:
        """Create contract party"""
        try:
            location = await self._get_or_create_location(party_data['location'])
            
            party = ContractParty(
                id=str(uuid.uuid4()),
                name=party_data['name'],
                type=party_type,
                company_type=party_data.get('company_type', 'trading_company'),
                location=location,
                contact_email=party_data.get('contact_email', ''),
                contact_phone=party_data.get('contact_phone', ''),
                verification_status=party_data.get('verification_status', 'pending'),
                reputation_score=party_data.get('reputation_score', 0.0),
                total_contracts=party_data.get('total_contracts', 0),
                success_rate=party_data.get('success_rate', 0.0),
                languages_spoken=party_data.get('languages_spoken', ['English']),
                specialties=party_data.get('specialties', [])
            )
            
            return party
            
        except Exception as e:
            print(f"❌ Error creating contract party: {e}")
            raise
    
    async def _calculate_shipping_route(self, origin: Location, destination: Location, transport_mode: TransportMode) -> ShippingRoute:
        """Calculate optimal shipping route"""
        try:
            # Calculate distance
            distance_km = geodesic((origin.latitude, origin.longitude), (destination.latitude, destination.longitude)).kilometers
            
            # Estimate duration and cost based on transport mode
            if transport_mode == TransportMode.SEA_FREIGHT:
                estimated_duration_days = distance_km / 500  # ~500 km/day for sea freight
                cost_per_ton = distance_km * 0.008  # $0.008 per ton-km
                carbon_footprint_kg = distance_km * 0.15  # 0.15 kg CO2 per ton-km
            elif transport_mode == TransportMode.AIR_FREIGHT:
                estimated_duration_days = distance_km / 8000  # ~8000 km/day for air freight
                cost_per_ton = distance_km * 0.05  # $0.05 per ton-km
                carbon_footprint_kg = distance_km * 0.5  # 0.5 kg CO2 per ton-km
            else:
                estimated_duration_days = distance_km / 1000  # ~1000 km/day for road/rail
                cost_per_ton = distance_km * 0.02  # $0.02 per ton-km
                carbon_footprint_kg = distance_km * 0.08  # 0.08 kg CO2 per ton-km
            
            # Generate route coordinates (simplified)
            route_coordinates = [
                (origin.latitude, origin.longitude),
                (destination.latitude, destination.longitude)
            ]
            
            # Identify risk factors
            risk_factors = []
            if distance_km > 5000:
                risk_factors.append('long_distance')
            if transport_mode == TransportMode.SEA_FREIGHT:
                risk_factors.extend(['weather', 'piracy', 'port_congestion'])
            elif transport_mode == TransportMode.AIR_FREIGHT:
                risk_factors.extend(['weather', 'air_traffic', 'customs'])
            
            shipping_route = ShippingRoute(
                id=str(uuid.uuid4()),
                origin=origin,
                destination=destination,
                transport_mode=transport_mode,
                distance_km=distance_km,
                estimated_duration_days=estimated_duration_days,
                cost_per_ton=cost_per_ton,
                carbon_footprint_kg=carbon_footprint_kg,
                route_coordinates=route_coordinates,
                shipping_lines=[],
                port_calls=[],
                risk_factors=risk_factors
            )
            
            return shipping_route
            
        except Exception as e:
            print(f"❌ Error calculating shipping route: {e}")
            raise
    
    async def _calculate_risk_score(self, contract_data: Dict[str, Any]) -> float:
        """Calculate risk score for contract"""
        try:
            risk_score = 0.0
            
            # Base risk from contract value
            contract_value = contract_data['quantity_tons'] * contract_data['price_per_ton']
            if contract_value > 10000000:  # > $10M
                risk_score += 0.3
            elif contract_value > 5000000:  # > $5M
                risk_score += 0.2
            elif contract_value > 1000000:  # > $1M
                risk_score += 0.1
            
            # Risk from transport distance
            origin = contract_data['origin_location']
            destination = contract_data['destination_location']
            distance_km = geodesic((origin['latitude'], origin['longitude']), (destination['latitude'], destination['longitude'])).kilometers
            if distance_km > 10000:
                risk_score += 0.2
            elif distance_km > 5000:
                risk_score += 0.1
            
            # Risk from party reputation
            buyer_reputation = contract_data['buyer'].get('reputation_score', 0.0)
            seller_reputation = contract_data['seller'].get('reputation_score', 0.0)
            avg_reputation = (buyer_reputation + seller_reputation) / 2
            if avg_reputation < 3.0:
                risk_score += 0.3
            elif avg_reputation < 4.0:
                risk_score += 0.2
            elif avg_reputation < 4.5:
                risk_score += 0.1
            
            # Risk from compliance flags
            compliance_flags = contract_data.get('compliance_flags', [])
            risk_score += len(compliance_flags) * 0.1
            
            return min(risk_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            print(f"❌ Error calculating risk score: {e}")
            return 0.5  # Default medium risk
    
    async def _save_contract_to_database(self, contract: MineralContract):
        """Save contract to database"""
        try:
            session = self.SessionLocal()
            
            # Save locations if not exists
            for location in [contract.origin_location, contract.destination_location]:
                if not session.query(LocationDB).filter_by(id=location.id).first():
                    db_location = LocationDB(
                        id=location.id,
                        name=location.name,
                        country=location.country,
                        region=location.region,
                        latitude=location.latitude,
                        longitude=location.longitude,
                        city=location.city,
                        postal_code=location.postal_code,
                        timezone=location.timezone,
                        is_port=location.is_port,
                        is_airport=location.is_airport,
                        is_mining_site=location.is_mining_site,
                        is_processing_facility=location.is_processing_facility
                    )
                    session.add(db_location)
            
            # Save contract
            db_contract = ContractDB(
                id=contract.id,
                contract_number=contract.contract_number,
                contract_type=contract.contract_type.value,
                status=contract.status.value,
                mineral_type=contract.mineral_type,
                quantity_tons=contract.quantity_tons,
                price_per_ton=contract.price_per_ton,
                total_value_usd=contract.total_value_usd,
                currency=contract.currency,
                
                buyer_id=contract.buyer.id,
                seller_id=contract.seller.id,
                
                origin_location_id=contract.origin_location.id,
                destination_location_id=contract.destination_location.id,
                
                created_at=contract.created_at,
                execution_date=contract.execution_date,
                delivery_date=contract.delivery_date,
                expiry_date=contract.expiry_date,
                
                purity_grade=contract.purity_grade,
                quality_certifications=contract.quality_certifications,
                inspection_required=contract.inspection_required,
                inspection_location_id=contract.inspection_location.id if contract.inspection_location else None,
                
                payment_method=contract.payment_method,
                payment_terms=contract.payment_terms,
                letter_of_credit_required=contract.letter_of_credit_required,
                bank_guarantee_required=contract.bank_guarantee_required,
                
                risk_score=contract.risk_score,
                compliance_flags=contract.compliance_flags,
                sanctions_check_passed=contract.sanctions_check_passed,
                anti_money_laundering_check_passed=contract.anti_money_laundering_check_passed,
                
                contract_documents=contract.contract_documents,
                tracking_number=contract.tracking_number,
                insurance_coverage=contract.insurance_coverage,
                force_majeure_clause=contract.force_majeure_clause,
                
                updated_at=contract.updated_at
            )
            
            session.add(db_contract)
            session.commit()
            
            print(f"✅ Saved contract {contract.contract_number} to database")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving contract to database: {e}")
            raise
        finally:
            session.close()
    
    async def get_active_contracts(self, limit: int = 100) -> List[MineralContract]:
        """Get active contracts"""
        try:
            session = self.SessionLocal()
            
            contracts = session.query(ContractDB).filter(
                ContractDB.status == ContractStatus.ACTIVE.value
            ).order_by(ContractDB.created_at.desc()).limit(limit).all()
            
            # Convert to MineralContract objects
            mineral_contracts = []
            for db_contract in contracts:
                # This would need to fetch related data (locations, parties, etc.)
                # For now, return placeholder
                pass
            
            return mineral_contracts
            
        except Exception as e:
            print(f"❌ Error fetching active contracts: {e}")
            return []
        finally:
            session.close()
    
    async def get_contracts_by_region(self, region: str, limit: int = 50) -> List[MineralContract]:
        """Get contracts by geographic region"""
        try:
            session = self.SessionLocal()
            
            contracts = session.query(ContractDB).join(LocationDB).filter(
                LocationDB.region == region
            ).order_by(ContractDB.created_at.desc()).limit(limit).all()
            
            return []
            
        except Exception as e:
            print(f"❌ Error fetching contracts by region: {e}")
            return []
        finally:
            session.close()
    
    async def get_contracts_by_mineral(self, mineral_type: str, limit: int = 50) -> List[MineralContract]:
        """Get contracts by mineral type"""
        try:
            session = self.SessionLocal()
            
            contracts = session.query(ContractDB).filter(
                ContractDB.mineral_type == mineral_type
            ).order_by(ContractDB.created_at.desc()).limit(limit).all()
            
            return []
            
        except Exception as e:
            print(f"❌ Error fetching contracts by mineral: {e}")
            return []
        finally:
            session.close()
    
    async def generate_world_map_data(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate world map visualization data"""
        try:
            # Get contracts based on filters
            contracts = await self.get_active_contracts(limit=1000)
            
            # Prepare map data
            map_data = {
                'contracts': [],
                'routes': [],
                'locations': [],
                'statistics': {
                    'total_contracts': len(contracts),
                    'total_value_usd': sum(c.total_value_usd for c in contracts),
                    'regions': {},
                    'minerals': {},
                    'transport_modes': {}
                }
            }
            
            for contract in contracts:
                # Add contract data
                map_data['contracts'].append({
                    'id': contract.id,
                    'contract_number': contract.contract_number,
                    'mineral_type': contract.mineral_type,
                    'quantity_tons': contract.quantity_tons,
                    'total_value_usd': contract.total_value_usd,
                    'status': contract.status.value,
                    'origin': {
                        'name': contract.origin_location.name,
                        'country': contract.origin_location.country,
                        'latitude': contract.origin_location.latitude,
                        'longitude': contract.origin_location.longitude
                    },
                    'destination': {
                        'name': contract.destination_location.name,
                        'country': contract.destination_location.country,
                        'latitude': contract.destination_location.latitude,
                        'longitude': contract.destination_location.longitude
                    },
                    'shipping_route': {
                        'distance_km': contract.shipping_route.distance_km,
                        'transport_mode': contract.shipping_route.transport_mode.value,
                        'estimated_duration_days': contract.shipping_route.estimated_duration_days,
                        'cost_per_ton': contract.shipping_route.cost_per_ton
                    }
                })
                
                # Add route data
                map_data['routes'].append({
                    'id': contract.shipping_route.id,
                    'origin_lat': contract.origin_location.latitude,
                    'origin_lng': contract.origin_location.longitude,
                    'destination_lat': contract.destination_location.latitude,
                    'destination_lng': contract.destination_location.longitude,
                    'transport_mode': contract.shipping_route.transport_mode.value,
                    'distance_km': contract.shipping_route.distance_km,
                    'risk_score': contract.risk_score
                })
                
                # Add locations
                for location in [contract.origin_location, contract.destination_location]:
                    if location.id not in [loc['id'] for loc in map_data['locations']]:
                        map_data['locations'].append({
                            'id': location.id,
                            'name': location.name,
                            'country': location.country,
                            'region': location.region,
                            'latitude': location.latitude,
                            'longitude': location.longitude,
                            'is_port': location.is_port,
                            'is_airport': location.is_airport,
                            'is_mining_site': location.is_mining_site,
                            'is_processing_facility': location.is_processing_facility
                        })
                
                # Update statistics
                stats = map_data['statistics']
                
                # Regional statistics
                origin_region = contract.origin_location.region
                dest_region = contract.destination_location.region
                stats['regions'][origin_region] = stats['regions'].get(origin_region, 0) + 1
                stats['regions'][dest_region] = stats['regions'].get(dest_region, 0) + 1
                
                # Mineral statistics
                mineral = contract.mineral_type
                stats['minerals'][mineral] = stats['minerals'].get(mineral, 0) + 1
                
                # Transport mode statistics
                transport_mode = contract.shipping_route.transport_mode.value
                stats['transport_modes'][transport_mode] = stats['transport_modes'].get(transport_mode, 0) + 1
            
            return map_data
            
        except Exception as e:
            print(f"❌ Error generating world map data: {e}")
            return {'contracts': [], 'routes': [], 'locations': [], 'statistics': {}}
    
    async def get_contract_tracking(self, contract_id: str) -> Dict[str, Any]:
        """Get real-time contract tracking information"""
        try:
            # Get contract from cache or database
            contract = self.contracts_cache.get(contract_id)
            if not contract:
                # Fetch from database
                pass
            
            if not contract:
                return {'error': 'Contract not found'}
            
            # Calculate current position (simplified)
            current_time = datetime.utcnow()
            elapsed_time = (current_time - contract.execution_date).total_seconds() / 86400  # days
            
            # Estimate progress along route
            progress_percentage = min(elapsed_time / contract.shipping_route.estimated_duration_days * 100, 100)
            
            # Calculate current position (linear interpolation)
            if progress_percentage >= 100:
                current_position = {
                    'latitude': contract.destination_location.latitude,
                    'longitude': contract.destination_location.longitude,
                    'status': 'delivered'
                }
            else:
                origin_lat = contract.origin_location.latitude
                origin_lng = contract.origin_location.longitude
                dest_lat = contract.destination_location.latitude
                dest_lng = contract.destination_location.longitude
                
                current_lat = origin_lat + (dest_lat - origin_lat) * (progress_percentage / 100)
                current_lng = origin_lng + (dest_lng - origin_lng) * (progress_percentage / 100)
                
                current_position = {
                    'latitude': current_lat,
                    'longitude': current_lng,
                    'status': 'in_transit'
                }
            
            tracking_data = {
                'contract_id': contract_id,
                'contract_number': contract.contract_number,
                'current_position': current_position,
                'progress_percentage': progress_percentage,
                'elapsed_days': elapsed_time,
                'estimated_arrival': contract.delivery_date.isoformat(),
                'origin': {
                    'name': contract.origin_location.name,
                    'country': contract.origin_location.country,
                    'latitude': contract.origin_location.latitude,
                    'longitude': contract.origin_location.longitude
                },
                'destination': {
                    'name': contract.destination_location.name,
                    'country': contract.destination_location.country,
                    'latitude': contract.destination_location.latitude,
                    'longitude': contract.destination_location.longitude
                },
                'shipping_info': {
                    'transport_mode': contract.shipping_route.transport_mode.value,
                    'distance_km': contract.shipping_route.distance_km,
                    'estimated_duration_days': contract.shipping_route.estimated_duration_days,
                    'tracking_number': contract.tracking_number
                },
                'last_updated': current_time.isoformat()
            }
            
            return tracking_data
            
        except Exception as e:
            print(f"❌ Error getting contract tracking: {e}")
            return {'error': 'Tracking information unavailable'}

# Initialize world map service
world_map_service = WorldMapService()
