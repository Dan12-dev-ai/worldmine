"""
API Integration Tests for DEDAN 2.0
"""

import pytest
import requests
import json
import time
from datetime import datetime

class TestAPIIntegration:
    """Test API endpoints integration"""
    
    BASE_URL = "https://staging.dedan.ai/api/v1"
    
    def test_health_check(self):
        """Test API health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_user_registration_flow(self):
        """Test user registration API flow"""
        # Register new user
        user_data = {
            'email': 'testuser@example.com',
            'password': 'SecurePassword123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'company': 'Test Corp'
        }
        
        response = requests.post(f"{self.BASE_URL}/auth/register", json=user_data, timeout=10)
        assert response.status_code == 201
        
        data = response.json()
        assert 'user_id' in data
        assert 'message' in data
    
    def test_mineral_marketplace_api(self):
        """Test mineral marketplace API endpoints"""
        # Get minerals list
        response = requests.get(f"{self.BASE_URL}/minerals", timeout=10)
        assert response.status_code == 200
        
        minerals = response.json()
        assert isinstance(minerals, list)
        assert len(minerals) > 0
        
        # Get specific mineral
        if minerals:
            mineral_id = minerals[0]['id']
            response = requests.get(f"{self.BASE_URL}/minerals/{mineral_id}", timeout=10)
            assert response.status_code == 200
            
            mineral = response.json()
            assert mineral['id'] == mineral_id
            assert 'name' in mineral
            assert 'price' in mineral
    
    def test_news_api(self):
        """Test news API endpoints"""
        # Get latest news
        response = requests.get(f"{self.BASE_URL}/news/latest", timeout=10)
        assert response.status_code == 200
        
        news = response.json()
        assert isinstance(news, list)
        
        if news:
            article = news[0]
            assert 'title' in article
            assert 'summary' in article
            assert 'source' in article
    
    def test_trading_api(self):
        """Test trading API endpoints"""
        # Get market data
        response = requests.get(f"{self.BASE_URL}/trading/market-data", timeout=10)
        assert response.status_code == 200
        
        market_data = response.json()
        assert 'pairs' in market_data
        assert 'prices' in market_data
        
        # Get order book
        response = requests.get(f"{self.BASE_URL}/trading/orderbook/GOLD-USD", timeout=10)
        assert response.status_code == 200
        
        orderbook = response.json()
        assert 'bids' in orderbook
        assert 'asks' in orderbook
    
    def test_world_map_api(self):
        """Test world map API endpoints"""
        # Get contracts
        response = requests.get(f"{self.BASE_URL}/world-map/contracts", timeout=10)
        assert response.status_code == 200
        
        contracts = response.json()
        assert isinstance(contracts, list)
        
        if contracts:
            contract = contracts[0]
            assert 'id' in contract
            assert 'mineral_type' in contract
            assert 'origin' in contract
            assert 'destination' in contract
    
    def test_quantum_predictions_api(self):
        """Test quantum predictions API"""
        # Get quantum predictions
        response = requests.get(f"{self.BASE_URL}/quantum/predictions", timeout=10)
        assert response.status_code == 200
        
        predictions = response.json()
        assert isinstance(predictions, list)
        
        if predictions:
            prediction = predictions[0]
            assert 'mineral_type' in prediction
            assert 'predicted_price' in prediction
            assert 'confidence_score' in prediction
            assert 'quantum_advantage' in prediction
    
    def test_api_response_times(self):
        """Test API response times"""
        endpoints = [
            '/health',
            '/minerals',
            '/news/latest',
            '/trading/market-data',
            '/world-map/contracts'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            assert response.status_code == 200
            assert response_time < 500, f"{endpoint} took {response_time}ms, expected <500ms"
    
    def test_api_error_handling(self):
        """Test API error handling"""
        # Test 404 error
        response = requests.get(f"{self.BASE_URL}/nonexistent", timeout=10)
        assert response.status_code == 404
        
        # Test 400 error for invalid data
        invalid_data = {'invalid': 'data'}
        response = requests.post(f"{self.BASE_URL}/auth/register", json=invalid_data, timeout=10)
        assert response.status_code == 400
        
        # Test 401 error for unauthorized access
        response = requests.get(f"{self.BASE_URL}/user/profile", timeout=10)
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__])
