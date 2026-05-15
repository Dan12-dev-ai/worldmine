"""
Unit tests for mineral database service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

from database.mineral_database import MineralDatabase, MineralCategory, PurityGrade

class TestMineralDatabase:
    """Test suite for MineralDatabase class"""
    
    @pytest.fixture
    def mineral_db(self):
        """Create test mineral database instance"""
        with patch('database.mineral_database.create_engine'), \
             patch('database.mineral_database.redis.Redis'):
            return MineralDatabase()
    
    def test_initialization(self, mineral_db):
        """Test database initialization"""
        assert mineral_db is not None
        assert hasattr(mineral_db, 'minerals_data')
        assert hasattr(mineral_db, 'minerals_cache')
    
    def test_mineral_categories(self, mineral_db):
        """Test mineral categories enum"""
        categories = list(MineralCategory)
        assert len(categories) >= 10
        assert MineralCategory.PRECIOUS_METALS in categories
        assert MineralCategory.BATTERY_MINERALS in categories
    
    def test_purity_grades(self, mineral_db):
        """Test purity grades enum"""
        grades = list(PurityGrade)
        assert len(grades) >= 5
        assert PurityGrade.INDUSTRIAL in grades
        assert PurityGrade.INVESTMENT in grades
    
    @pytest.mark.asyncio
    async def test_get_mineral_statistics(self, mineral_db):
        """Test get mineral statistics"""
        # Mock the minerals data
        mineral_db.minerals_data = {
            'gold': Mock(annual_production=1000, price_usd_per_kg=50000),
            'silver': Mock(annual_production=2000, price_usd_per_kg=800),
            'copper': Mock(annual_production=5000, price_usd_per_kg=10)
        }
        
        with patch.object(mineral_db, 'SessionLocal'):
            stats = await mineral_db.get_mineral_statistics()
            
            assert 'total_minerals' in stats
            assert 'categories' in stats
            assert 'strategic_minerals' in stats
            assert stats['total_minerals'] == 3
    
    @pytest.mark.asyncio
    async def test_get_latest_news(self, mineral_db):
        """Test get latest news"""
        with patch.object(mineral_db, 'SessionLocal'):
            news = await mineral_db.get_latest_news(limit=10)
            
            assert isinstance(news, list)
            # Should return empty list since we're mocking
    
    def test_get_precious_metals(self, mineral_db):
        """Test get precious metals data"""
        precious_metals = mineral_db._get_precious_metals()
        
        assert isinstance(precious_metals, dict)
        # Should contain at least gold and silver
        assert 'Au' in precious_metals or 'gold' in str(precious_metals).lower()
    
    def test_get_battery_minerals(self, mineral_db):
        """Test get battery minerals data"""
        battery_minerals = mineral_db._get_battery_minerals()
        
        assert isinstance(battery_minerals, dict)
        # Should contain lithium
        assert 'Li' in battery_minals or 'lithium' in str(battery_minerals).lower()

if __name__ == "__main__":
    pytest.main([__file__])
