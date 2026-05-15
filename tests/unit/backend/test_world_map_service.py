"""
Unit tests for world map service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

from services.world_map_service import WorldMapService, ContractStatus, TransportMode

class TestWorldMapService:
    """Test suite for WorldMapService class"""
    
    @pytest.fixture
    def world_map_service(self):
        """Create test world map service instance"""
        with patch('services.world_map_service.create_engine'), \
             patch('services.world_map_service.redis.Redis'), \
             patch('services.world_map_service.geopy.Nominatim'), \
             patch('services.world_map_service.Aer.get_backend'):
            return WorldMapService()
    
    def test_initialization(self, world_map_service):
        """Test service initialization"""
        assert world_map_service is not None
        assert hasattr(world_map_service, 'shipping_routes')
        assert hasattr(world_map_service, 'major_ports')
    
    def test_contract_status_enum(self, world_map_service):
        """Test contract status enum"""
        statuses = list(ContractStatus)
        assert len(statuses) >= 5
        assert ContractStatus.ACTIVE in statuses
        assert ContractStatus.COMPLETED in statuses
    
    def test_transport_mode_enum(self, world_map_service):
        """Test transport mode enum"""
        modes = list(TransportMode)
        assert len(modes) >= 5
        assert TransportMode.SEA_FREIGHT in modes
        assert TransportMode.AIR_FREIGHT in modes
    
    def test_calculate_shipping_route(self, world_map_service):
        """Test shipping route calculation"""
        # Mock locations
        origin = Mock(latitude=40.7128, longitude=-74.0060)  # New York
        destination = Mock(latitude=51.5074, longitude=-0.1278)  # London
        
        route = asyncio.run(world_map_service._calculate_shipping_route(
            origin, destination, TransportMode.SEA_FREIGHT
        ))
        
        assert route is not None
        assert route.transport_mode == TransportMode.SEA_FREIGHT
        assert route.distance_km > 0
        assert route.estimated_duration_days > 0
    
    def test_calculate_risk_score(self, world_map_service):
        """Test risk score calculation"""
        contract_data = {
            'quantity_tons': 1000,
            'price_per_ton': 50000,
            'origin_location': {'latitude': 40.7128, 'longitude': -74.0060},
            'destination_location': {'latitude': 51.5074, 'longitude': -0.1278},
            'buyer': {'reputation_score': 4.5},
            'seller': {'reputation_score': 4.2},
            'compliance_flags': []
        }
        
        risk_score = asyncio.run(world_map_service._calculate_risk_score(contract_data))
        
        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 1.0

if __name__ == "__main__":
    pytest.main([__file__])
