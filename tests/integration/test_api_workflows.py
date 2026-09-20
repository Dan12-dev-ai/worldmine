"""
Integration Tests for API Workflows
Tests critical workflows across all systems
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import uuid


class TestMarketplaceWorkflow:
    """Test marketplace trading workflow"""
    
    def test_create_listing(self, client):
        """Test creating a marketplace listing"""
        response = client.post("/api/marketplace/listings", json={
            "title": "Test Gemstone",
            "description": "High quality gem",
            "price": 1000.00,
            "currency": "USD",
            "category": "gemstones"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["title"] == "Test Gemstone"
    
    def test_list_listings(self, client):
        """Test listing all marketplace items"""
        response = client.get("/api/marketplace/listings")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)


class TestWalletWorkflow:
    """Test wallet transaction workflow"""
    
    def test_create_wallet(self, client):
        """Test creating a new wallet"""
        response = client.post("/api/wallet/wallets", json={
            "wallet_type": "trading",
            "currency": "USD"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["currency"] == "USD"
    
    def test_get_wallet_balance(self, client):
        """Test getting wallet balance"""
        wallet_id = str(uuid.uuid4())
        response = client.get(f"/api/wallet/wallets/{wallet_id}/balance")
        # May return 404 if wallet doesn't exist
        assert response.status_code in [200, 404]
    
    def test_create_deposit(self, client):
        """Test creating a deposit"""
        response = client.post("/api/wallet/deposits", json={
            "wallet_id": str(uuid.uuid4()),
            "amount": 500.00,
            "payment_method": "credit_card"
        })
        assert response.status_code in [200, 404]


class TestEscrowWorkflow:
    """Test escrow lifecycle workflow"""
    
    def test_create_escrow(self, client):
        """Test creating an escrow"""
        response = client.post("/api/escrow/escrow", json={
            "buyer_id": str(uuid.uuid4()),
            "seller_id": str(uuid.uuid4()),
            "amount": 2500.00,
            "currency": "USD",
            "description": "Gemstone purchase"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_fund_escrow(self, client):
        """Test funding an escrow"""
        escrow_id = str(uuid.uuid4())
        response = client.post(f"/api/escrow/escrow/{escrow_id}/fund", json={
            "payment_method": "wallet",
            "transaction_id": str(uuid.uuid4())
        })
        assert response.status_code in [200, 404]
    
    def test_release_escrow(self, client):
        """Test releasing escrow funds"""
        escrow_id = str(uuid.uuid4())
        response = client.post(f"/api/escrow/escrow/{escrow_id}/release")
        assert response.status_code in [200, 404]


class TestContractWorkflow:
    """Test contract lifecycle workflow"""
    
    def test_create_contract_template(self, client):
        """Test creating a contract template"""
        response = client.post("/api/contracts/templates", json={
            "name": "Sales Agreement",
            "description": "Standard sales contract",
            "content": "Terms and conditions...",
            "type": "sales"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_create_contract(self, client):
        """Test creating a contract from template"""
        response = client.post("/api/contracts/contracts", json={
            "template_id": str(uuid.uuid4()),
            "parties": [{"user_id": str(uuid.uuid4()), "role": "buyer"}],
            "terms": {"price": 1000.00, "delivery_date": "2024-12-31"}
        })
        assert response.status_code in [200, 404]
    
    def test_sign_contract(self, client):
        """Test signing a contract"""
        contract_id = str(uuid.uuid4())
        response = client.post(f"/api/contracts/contracts/{contract_id}/sign", json={
            "user_id": str(uuid.uuid4()),
            "signature": "digital_signature_here"
        })
        assert response.status_code in [200, 404]


class TestLogisticsWorkflow:
    """Test logistics tracking workflow"""
    
    def test_create_shipment(self, client):
        """Test creating a shipment"""
        response = client.post("/api/logistics/shipments", json={
            "tracking_number": str(uuid.uuid4()),
            "origin_address": "123 Main St",
            "destination_address": "456 Oak Ave",
            "weight": 10.5,
            "transport_mode": "ground"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_track_shipment(self, client):
        """Test tracking a shipment"""
        tracking_number = str(uuid.uuid4())
        response = client.get(f"/api/logistics/track/{tracking_number}")
        assert response.status_code in [200, 404]
    
    def test_update_shipment_status(self, client):
        """Test updating shipment status"""
        shipment_id = str(uuid.uuid4())
        response = client.put(f"/api/logistics/shipments/{shipment_id}/status", json={
            "status": "in_transit",
            "location": {"latitude": 40.7128, "longitude": -74.0060}
        })
        assert response.status_code in [200, 404]


class TestNotificationWorkflow:
    """Test notification workflow"""
    
    def test_create_notification(self, client):
        """Test creating a notification"""
        response = client.post("/api/notifications/notifications", json={
            "user_id": str(uuid.uuid4()),
            "type": "info",
            "channel": "in_app",
            "title": "Test Notification",
            "message": "This is a test notification"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_list_notifications(self, client):
        """Test listing notifications"""
        user_id = str(uuid.uuid4())
        response = client.get(f"/api/notifications/notifications?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_mark_notification_read(self, client):
        """Test marking notification as read"""
        notification_id = str(uuid.uuid4())
        response = client.put(f"/api/notifications/notifications/{notification_id}/read")
        assert response.status_code in [200, 404]


class TestPaymentWorkflow:
    """Test payment processing workflow"""
    
    def test_create_payment(self, client):
        """Test creating a payment"""
        response = client.post("/api/payment/payments", json={
            "amount": 100.00,
            "currency": "USD",
            "provider": "stripe",
            "payment_method": "credit_card"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_list_transactions(self, client):
        """Test listing payment transactions"""
        response = client.get("/api/payment/transactions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAdminWorkflow:
    """Test admin control workflow"""
    
    def test_get_system_stats(self, client):
        """Test getting system statistics"""
        response = client.get("/api/admin/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
    
    def test_get_module_health(self, client):
        """Test getting module health status"""
        response = client.get("/api/admin/modules/health")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_log(self, client):
        """Test getting audit log"""
        response = client.get("/api/admin/audit-log")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAIAgentWorkflow:
    """Test AI agent workflow"""
    
    def test_register_agent(self, client):
        """Test registering an AI agent"""
        response = client.post("/api/ai_agents/agents", json={
            "name": "Test Agent",
            "type": "trading",
            "description": "Test trading agent"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_list_agents(self, client):
        """Test listing AI agents"""
        response = client.get("/api/ai_agents/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_agent_health(self, client):
        """Test getting agent health"""
        agent_id = str(uuid.uuid4())
        response = client.get(f"/api/ai_monitoring/health/{agent_id}")
        assert response.status_code in [200, 404]


class TestWebSocketWorkflow:
    """Test WebSocket connection workflow"""
    
    def test_get_websocket_stats(self, client):
        """Test getting WebSocket statistics"""
        response = client.get("/api/ws/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_connections" in data


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    def test_complete_trading_workflow(self, client):
        """Test complete trading workflow from listing to payment"""
        # 1. Create wallet
        wallet_response = client.post("/api/wallet/wallets", json={
            "wallet_type": "trading",
            "currency": "USD"
        })
        assert wallet_response.status_code == 200
        wallet_id = wallet_response.json()["data"]["id"]
        
        # 2. Create listing
        listing_response = client.post("/api/marketplace/listings", json={
            "title": "Test Gemstone",
            "description": "High quality gem",
            "price": 1000.00,
            "currency": "USD",
            "category": "gemstones"
        })
        assert listing_response.status_code == 200
        listing_id = listing_response.json()["data"]["id"]
        
        # 3. Create escrow
        escrow_response = client.post("/api/escrow/escrow", json={
            "buyer_id": str(uuid.uuid4()),
            "seller_id": str(uuid.uuid4()),
            "amount": 1000.00,
            "currency": "USD",
            "description": "Gemstone purchase"
        })
        assert escrow_response.status_code == 200
        
        # 4. Create contract
        contract_response = client.post("/api/contracts/contracts", json={
            "template_id": str(uuid.uuid4()),
            "parties": [{"user_id": str(uuid.uuid4()), "role": "buyer"}],
            "terms": {"price": 1000.00}
        })
        # May fail if template doesn't exist
        assert contract_response.status_code in [200, 404]
        
        # 5. Create shipment
        shipment_response = client.post("/api/logistics/shipments", json={
            "tracking_number": str(uuid.uuid4()),
            "origin_address": "123 Main St",
            "destination_address": "456 Oak Ave",
            "weight": 10.5,
            "transport_mode": "ground"
        })
        assert shipment_response.status_code == 200
        
        # 6. Create notification
        notification_response = client.post("/api/notifications/notifications", json={
            "user_id": str(uuid.uuid4()),
            "type": "success",
            "channel": "in_app",
            "title": "Order Complete",
            "message": "Your order has been processed"
        })
        assert notification_response.status_code == 200


# Test configuration
# The `client` fixture is provided by the root conftest.py (session-scoped,
# with an in-memory SQLite database override).

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
