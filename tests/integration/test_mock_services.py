"""
Mock Services for Integration Testing
Mock Stripe, DHL, blockchain explorers for isolated testing
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging
from unittest.mock import Mock, AsyncMock
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockStripeAPI:
    """Mock Stripe API for payment testing"""
    
    def __init__(self):
        self.payments = {}
        self.customers = {}
        self.refunds = {}
        self.webhooks = []
    
    async def create_payment_intent(self, amount: int, currency: str = "usd") -> Dict[str, Any]:
        """Create mock payment intent"""
        payment_id = f"pi_test_{uuid.uuid4().hex[:8]}"
        
        payment_intent = {
            "id": payment_id,
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "created": int(time.time()),
            "charges": [{
                "id": f"ch_test_{uuid.uuid4().hex[:8]}",
                "amount": amount,
                "currency": currency,
                "status": "succeeded",
                "paid": True
            }]
        }
        
        self.payments[payment_id] = payment_intent
        logger.info(f"Created mock payment intent: {payment_id}")
        
        return payment_intent
    
    async def confirm_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm mock payment intent"""
        if payment_intent_id in self.payments:
            payment = self.payments[payment_intent_id]
            payment["status"] = "succeeded"
            logger.info(f"Confirmed payment intent: {payment_intent_id}")
            return payment
        
        raise ValueError(f"Payment intent not found: {payment_intent_id}")
    
    async def create_refund(self, charge_id: str, amount: int) -> Dict[str, Any]:
        """Create mock refund"""
        refund_id = f"re_test_{uuid.uuid4().hex[:8]}"
        
        refund = {
            "id": refund_id,
            "charge": charge_id,
            "amount": amount,
            "status": "succeeded",
            "created": int(time.time())
        }
        
        self.refunds[refund_id] = refund
        logger.info(f"Created mock refund: {refund_id}")
        
        return refund
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get mock customer"""
        if customer_id in self.customers:
            return self.customers[customer_id]
        
        return {
            "id": customer_id,
            "email": f"customer_{customer_id}@example.com",
            "name": f"Test Customer {customer_id}",
            "created": int(time.time())
        }
    
    async def create_customer(self, email: str, name: str) -> Dict[str, Any]:
        """Create mock customer"""
        customer_id = f"cus_test_{uuid.uuid4().hex[:8]}"
        
        customer = {
            "id": customer_id,
            "email": email,
            "name": name,
            "created": int(time.time())
        }
        
        self.customers[customer_id] = customer
        logger.info(f"Created mock customer: {customer_id}")
        
        return customer

class MockDHLAPI:
    """Mock DHL API for shipping testing"""
    
    def __init__(self):
        self.shipments = {}
        self.tracking = {}
    
    async def create_shipment(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock shipment"""
        shipment_id = f"dhlt_test_{uuid.uuid4().hex[:8]}"
        tracking_number = f"1234567890{uuid.uuid4().hex[:4]}"
        
        shipment = {
            "id": shipment_id,
            "tracking_number": tracking_number,
            "status": "created",
            "created": int(time.time()),
            "origin": shipment_data.get("origin", {}),
            "destination": shipment_data.get("destination", {}),
            "packages": shipment_data.get("packages", []),
            "weight": shipment_data.get("weight", 0),
            "service": shipment_data.get("service", "express")
        }
        
        self.shipments[shipment_id] = shipment
        self.tracking[tracking_number] = shipment
        
        logger.info(f"Created mock shipment: {shipment_id}")
        
        return shipment
    
    async def get_tracking(self, tracking_number: str) -> Dict[str, Any]:
        """Get mock tracking information"""
        if tracking_number in self.tracking:
            tracking = self.tracking[tracking_number]
            
            # Simulate tracking progression
            created_time = tracking["created"]
            current_time = int(time.time())
            elapsed = current_time - created_time
            
            if elapsed < 3600:  # Less than 1 hour
                tracking["status"] = "picked_up"
                tracking["location"] = "Origin Facility"
            elif elapsed < 7200:  # Less than 2 hours
                tracking["status"] = "in_transit"
                tracking["location"] = "Transit Hub"
            elif elapsed < 10800:  # Less than 3 hours
                tracking["status"] = "out_for_delivery"
                tracking["location"] = "Local Facility"
            else:
                tracking["status"] = "delivered"
                tracking["location"] = "Destination"
                tracking["delivered_at"] = current_time
            
            return tracking
        
        raise ValueError(f"Tracking number not found: {tracking_number}")
    
    async def cancel_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Cancel mock shipment"""
        if shipment_id in self.shipments:
            shipment = self.shipments[shipment_id]
            shipment["status"] = "cancelled"
            shipment["cancelled_at"] = int(time.time())
            
            logger.info(f"Cancelled mock shipment: {shipment_id}")
            return shipment
        
        raise ValueError(f"Shipment not found: {shipment_id}")

class MockBlockchainExplorer:
    """Mock blockchain explorer for testing"""
    
    def __init__(self):
        self.transactions = {}
        self.blocks = {}
        self.addresses = {}
    
    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get mock transaction"""
        if tx_hash in self.transactions:
            return self.transactions[tx_hash]
        
        # Generate mock transaction
        transaction = {
            "hash": tx_hash,
            "block_number": 12345 + len(self.transactions),
            "transaction_index": 0,
            "from": f"0x{uuid.uuid4().hex[:40]}",
            "to": f"0x{uuid.uuid4().hex[:40]}",
            "value": str(1000000000000000000),  # 1 ETH
            "gas": "21000",
            "gas_price": "20000000000",
            "status": "confirmed",
            "timestamp": int(time.time()),
            "input": "0x" + "0" * 68,  # Mock input data
            "output": "0x" + "0" * 64  # Mock output data
        }
        
        self.transactions[tx_hash] = transaction
        logger.info(f"Generated mock transaction: {tx_hash}")
        
        return transaction
    
    async def get_block(self, block_number: int) -> Dict[str, Any]:
        """Get mock block"""
        if block_number in self.blocks:
            return self.blocks[block_number]
        
        # Generate mock block
        block = {
            "number": block_number,
            "hash": f"0x{uuid.uuid4().hex[:64]}",
            "parent_hash": f"0x{uuid.uuid4().hex[:64]}",
            "timestamp": int(time.time()),
            "miner": f"0x{uuid.uuid4().hex[:40]}",
            "difficulty": "1234567890",
            "gas_limit": "30000000",
            "gas_used": "21000000",
            "transactions": [],
            "size": "12345"
        }
        
        self.blocks[block_number] = block
        logger.info(f"Generated mock block: {block_number}")
        
        return block
    
    async def get_address_balance(self, address: str) -> Dict[str, Any]:
        """Get mock address balance"""
        if address in self.addresses:
            return self.addresses[address]
        
        # Generate mock balance
        balance = {
            "address": address,
            "balance": str(1000000000000000000),  # 1 ETH
            "usd_balance": "2000.00",
            "token_balances": {
                "DAI": "1000.00",
                "USDC": "500.00"
            }
        }
        
        self.addresses[address] = balance
        logger.info(f"Generated mock balance for address: {address}")
        
        return balance
    
    async def get_contract_info(self, contract_address: str) -> Dict[str, Any]:
        """Get mock contract info"""
        return {
            "address": contract_address,
            "name": f"Contract {contract_address[:8]}",
            "symbol": f"TKN{contract_address[:4]}",
            "decimals": 18,
            "total_supply": str(1000000000000000000),
            "holders": 1000,
            "verified": True
        }

class MockExternalAPIs:
    """Mock external APIs for integration testing"""
    
    def __init__(self):
        self.stripe = MockStripeAPI()
        self.dhl = MockDHLAPI()
        self.blockchain = MockBlockchainExplorer()
        self.webhooks = []
    
    async def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through mock Stripe"""
        try:
            # Create customer if not exists
            customer = await self.stripe.create_customer(
                payment_data.get("email", "test@example.com"),
                payment_data.get("name", "Test User")
            )
            
            # Create payment intent
            payment_intent = await self.stripe.create_payment_intent(
                payment_data.get("amount", 5000),
                payment_data.get("currency", "usd")
            )
            
            # Confirm payment
            confirmed_payment = await self.stripe.confirm_payment_intent(
                payment_intent["id"]
            )
            
            # Store webhook event
            webhook_event = {
                "id": f"evt_{uuid.uuid4().hex[:8]}",
                "type": "payment_intent.succeeded",
                "created": int(time.time()),
                "data": {
                    "object": "payment_intent",
                    "id": payment_intent["id"]
                }
            }
            self.webhooks.append(webhook_event)
            
            logger.info(f"Processed mock payment: {payment_intent['id']}")
            
            return {
                "success": True,
                "payment": confirmed_payment,
                "customer": customer,
                "webhook_id": webhook_event["id"]
            }
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_shipment(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create shipment through mock DHL"""
        try:
            shipment = await self.dhl.create_shipment(shipment_data)
            
            logger.info(f"Created mock shipment: {shipment['id']}")
            
            return {
                "success": True,
                "shipment": shipment
            }
            
        except Exception as e:
            logger.error(f"Error creating shipment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def track_shipment(self, tracking_number: str) -> Dict[str, Any]:
        """Track shipment through mock DHL"""
        try:
            tracking = await self.dhl.get_tracking(tracking_number)
            
            logger.info(f"Tracked mock shipment: {tracking_number}")
            
            return {
                "success": True,
                "tracking": tracking
            }
            
        except Exception as e:
            logger.error(f"Error tracking shipment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_blockchain_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Verify transaction through mock blockchain explorer"""
        try:
            transaction = await self.blockchain.get_transaction(tx_hash)
            
            # Verify transaction is valid
            is_valid = (
                transaction["status"] == "confirmed" and
                transaction["block_number"] > 0 and
                int(transaction["value"]) > 0 and
                len(transaction["from"]) == 42 and
                len(transaction["to"]) == 42
            )
            
            logger.info(f"Verified mock transaction: {tx_hash}")
            
            return {
                "success": True,
                "transaction": transaction,
                "is_valid": is_valid
            }
            
        except Exception as e:
            logger.error(f"Error verifying transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_blockchain_balance(self, address: str) -> Dict[str, Any]:
        """Get balance through mock blockchain explorer"""
        try:
            balance = await self.blockchain.get_address_balance(address)
            
            logger.info(f"Got mock blockchain balance for address: {address}")
            
            return {
                "success": True,
                "balance": balance
            }
            
        except Exception as e:
            logger.error(f"Error getting blockchain balance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_webhook_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get webhook events"""
        return self.webhooks[-limit:] if self.webhooks else []
    
    async def simulate_payment_failure(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate payment failure"""
        try:
            # Simulate declined payment
            payment_intent = await self.stripe.create_payment_intent(
                payment_data.get("amount", 5000),
                payment_data.get("currency", "usd")
            )
            
            # Mock failure
            payment_intent["status"] = "requires_payment_method"
            payment_intent["last_payment_error"] = {
                "code": "card_declined",
                "message": "Your card has been declined."
            }
            
            logger.info(f"Simulated payment failure: {payment_intent['id']}")
            
            return {
                "success": False,
                "error": "Card declined",
                "payment_intent": payment_intent
            }
            
        except Exception as e:
            logger.error(f"Error simulating payment failure: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def simulate_shipping_delay(self, tracking_number: str, delay_hours: int = 2) -> Dict[str, Any]:
        """Simulate shipping delay"""
        try:
            tracking = await self.dhl.get_tracking(tracking_number)
            
            # Simulate delay
            tracking["status"] = "delayed"
            tracking["estimated_delivery"] = int(time.time()) + (delay_hours * 3600)
            tracking["delay_reason"] = "Weather conditions"
            
            logger.info(f"Simulated shipping delay: {tracking_number}")
            
            return {
                "success": True,
                "tracking": tracking
            }
            
        except Exception as e:
            logger.error(f"Error simulating shipping delay: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def simulate_blockchain_network_congestion(self) -> Dict[str, Any]:
        """Simulate blockchain network congestion"""
        try:
            # Get latest block
            latest_block = await self.blockchain.get_block(12345 + len(self.blocks))
            
            # Simulate congestion
            latest_block["gas_price"] = "50000000000"  # High gas price
            latest_block["network_congestion"] = True
            latest_block["confirmation_time"] = 600  # 10 minutes
            
            logger.info("Simulated blockchain network congestion")
            
            return {
                "success": True,
                "block": latest_block,
                "congestion_level": "high"
            }
            
        except Exception as e:
            logger.error(f"Error simulating blockchain congestion: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Mock HTTP server for external API testing
class MockAPIServer:
    """Mock API server for testing external integrations"""
    
    def __init__(self, port: int = 8888):
        self.port = port
        self.app = None
        self.external_apis = MockExternalAPIs()
        self.site = None
    
    async def start(self):
        """Start mock API server"""
        from aiohttp import web
        
        app = web.Application()
        
        # Payment endpoints
        app.router.add_post('/stripe/payment-intent', self.handle_payment_intent)
        app.router.add_post('/stripe/confirm', self.handle_payment_confirm)
        app.router.add_post('/stripe/refund', self.handle_refund)
        
        # Shipping endpoints
        app.router.add_post('/dhl/shipment', self.handle_shipment)
        app.router.add_get('/dhl/tracking/{tracking}', self.handle_tracking)
        
        # Blockchain endpoints
        app.router.add_get('/blockchain/tx/{tx_hash}', self.handle_transaction)
        app.router.add_get('/blockchain/block/{block_number}', self.handle_block)
        app.router.add_get('/blockchain/balance/{address}', self.handle_balance)
        app.router.add_get('/blockchain/contract/{address}', self.handle_contract)
        
        # Webhook endpoints
        app.router.add_post('/webhook/stripe', self.handle_webhook)
        app.router.add_get('/webhook/events', self.handle_webhook_events)
        
        # Health check
        app.router.add_get('/health', self.handle_health)
        
        runner = web.AppRunner(app)
        self.site = web.TCPSite(runner, 'localhost', self.port)
        
        logger.info(f"Starting mock API server on port {self.port}")
        await self.site.start()
    
    async def stop(self):
        """Stop mock API server"""
        if self.site:
            await self.site.stop()
            logger.info("Stopped mock API server")
    
    async def handle_payment_intent(self, request):
        """Handle payment intent creation"""
        data = await request.json()
        result = await self.external_apis.process_payment(data)
        return web.json_response(result)
    
    async def handle_payment_confirm(self, request):
        """Handle payment confirmation"""
        data = await request.json()
        payment_intent = await self.external_apis.stripe.confirm_payment_intent(
            data.get("payment_intent_id")
        )
        return web.json_response({"success": True, "payment_intent": payment_intent})
    
    async def handle_refund(self, request):
        """Handle refund creation"""
        data = await request.json()
        refund = await self.external_apis.stripe.create_refund(
            data.get("charge_id"),
            data.get("amount")
        )
        return web.json_response({"success": True, "refund": refund})
    
    async def handle_shipment(self, request):
        """Handle shipment creation"""
        data = await request.json()
        result = await self.external_apis.create_shipment(data)
        return web.json_response(result)
    
    async def handle_tracking(self, request):
        """Handle shipment tracking"""
        tracking_number = request.match_info['tracking']
        result = await self.external_apis.track_shipment(tracking_number)
        return web.json_response(result)
    
    async def handle_transaction(self, request):
        """Handle transaction verification"""
        tx_hash = request.match_info['tx_hash']
        result = await self.external_apis.verify_blockchain_transaction(tx_hash)
        return web.json_response(result)
    
    async def handle_block(self, request):
        """Handle block retrieval"""
        block_number = int(request.match_info['block_number'])
        result = await self.external_apis.blockchain.get_block(block_number)
        return web.json_response(result)
    
    async def handle_balance(self, request):
        """Handle balance retrieval"""
        address = request.match_info['address']
        result = await self.external_apis.get_blockchain_balance(address)
        return web.json_response(result)
    
    async def handle_contract(self, request):
        """Handle contract info retrieval"""
        address = request.match_info['address']
        result = await self.external_apis.blockchain.get_contract_info(address)
        return web.json_response(result)
    
    async def handle_webhook(self, request):
        """Handle webhook events"""
        data = await request.json()
        webhook_event = {
            "id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": data.get("type", "payment_intent.succeeded"),
            "created": int(time.time()),
            "data": data
        }
        self.external_apis.webhooks.append(webhook_event)
        return web.json_response({"success": True, "event": webhook_event})
    
    async def handle_webhook_events(self, request):
        """Handle webhook event retrieval"""
        limit = int(request.query.get("limit", 10))
        events = await self.external_apis.get_webhook_events(limit)
        return web.json_response({"events": events})
    
    async def handle_health(self, request):
        """Handle health check"""
        return web.json_response({
            "status": "healthy",
            "timestamp": int(time.time()),
            "services": {
                "stripe": "mock",
                "dhl": "mock",
                "blockchain": "mock"
            }
        })

# Test runner for mock services
async def test_mock_services():
    """Test mock services functionality"""
    logger.info("Testing mock services...")
    
    # Test payment processing
    apis = MockExternalAPIs()
    
    payment_data = {
        "email": "test@example.com",
        "name": "Test User",
        "amount": 5000,
        "currency": "usd"
    }
    
    payment_result = await apis.process_payment(payment_data)
    assert payment_result["success"], "Payment processing failed"
    
    # Test shipment creation
    shipment_data = {
        "origin": {"address": "123 Test St", "city": "Test City", "country": "US"},
        "destination": {"address": "456 Test Ave", "city": "Test City", "country": "US"},
        "packages": [{"weight": 1.0, "dimensions": "10x10x5"}],
        "service": "express"
    }
    
    shipment_result = await apis.create_shipment(shipment_data)
    assert shipment_result["success"], "Shipment creation failed"
    
    # Test blockchain verification
    tx_hash = "0x" + "0" * 64
    tx_result = await apis.verify_blockchain_transaction(tx_hash)
    assert tx_result["success"], "Transaction verification failed"
    
    logger.info("All mock service tests passed")

if __name__ == "__main__":
    asyncio.run(test_mock_services())
