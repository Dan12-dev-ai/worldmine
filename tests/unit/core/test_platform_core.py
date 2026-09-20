import pytest
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from core.governance_orchestrator import governance_orchestrator, AgentSignal, AgentType, GovernanceDecision
from core.physical_marketplace import physical_marketplace_engine, AssetCategory
from core.digital_trading import digital_trading_engine, OrderType, OrderSide, InstrumentType
from core.ethiopian_sovereign_hub import ethiopian_sovereign_hub, EthiopianPayoutRequest, PayoutRail

@pytest.mark.asyncio
async def test_governance_authorization():
    """Test that only authorized agents and signals are approved"""
    # Authorized signal
    valid_signal = AgentSignal(
        agent_id="market_intelligence_agent",
        agent_type=AgentType.MARKET_INTELLIGENCE,
        signal_type="market_analysis",
        confidence=0.9,
        timestamp=datetime.now(timezone.utc),
        data={"trend": "bullish"}
    )
    decision = await governance_orchestrator.validate_agent_signal(valid_signal)
    assert decision.approved is True

    # Unauthorized agent
    invalid_agent_signal = AgentSignal(
        agent_id="rogue_agent",
        agent_type=AgentType.MARKET_INTELLIGENCE,
        signal_type="market_analysis",
        confidence=1.0,
        timestamp=datetime.now(timezone.utc),
        data={}
    )
    decision = await governance_orchestrator.validate_agent_signal(invalid_agent_signal)
    assert decision.approved is False
    assert "Agent not authorized" in decision.reason

    # Unauthorized signal type for agent
    invalid_signal_type = AgentSignal(
        agent_id="market_intelligence_agent",
        agent_type=AgentType.MARKET_INTELLIGENCE,
        signal_type="fraud_alert", # Should be under FRAUD_TRUST agent
        confidence=0.9,
        timestamp=datetime.now(timezone.utc),
        data={}
    )
    decision = await governance_orchestrator.validate_agent_signal(invalid_signal_type)
    assert decision.approved is False

@pytest.mark.asyncio
async def test_physical_marketplace_listing_flow():
    """Test the verified listing creation flow in physical marketplace"""
    seller_data = {"seller_id": "seller_123"}
    asset_data = {
        "category": "gold",
        "quantity": 10.0,
        "unit": "kg",
        "location": {"latitude": 9.0, "longitude": 38.0},
        "certifications": [{"id": "cert_001", "issuer": "Global Lab"}],
        "asking_price": 650000.0,
        "seller_id": "seller_123"
    }

    success, message, listing = await physical_marketplace_engine.create_verified_listing(seller_data, asset_data)
    
    assert success is True
    assert listing is not None
    assert listing.asset.category == AssetCategory.GOLD
    assert listing.escrow_required is True

@pytest.mark.asyncio
async def test_ethiopian_sovereign_hub_compliance():
    """Test NBE compliance logic in Ethiopian Sovereign Hub"""
    # Test illegal Birr to Crypto conversion (P2P prohibition)
    illegal_request = EthiopianPayoutRequest(
        user_id="user_eth_001",
        amount=1000.0,
        currency="ETB",
        rail=PayoutRail.WEB3_CRYPTO,
        destination={"crypto": {"symbol": "USDT", "wallet_address": "0x123"}}
    )
    
    result = await ethiopian_sovereign_hub.process_ethiopian_payout(illegal_request)
    assert result["success"] is False
    assert "NBE Compliance: Direct ETB to crypto conversion is prohibited" in result["error"]

    # Test legal Local Birr payout
    legal_request = EthiopianPayoutRequest(
        user_id="user_eth_001",
        amount=1000.0,
        currency="ETB",
        rail=PayoutRail.LOCAL_BIRR,
        destination={"chapa_phone": "0911223344"}
    )
    # Mocking verify_biometric to pass
    with mock.patch.object(ethiopian_sovereign_hub.chapa_integration, 'verify_biometric', return_value={"verified": True}):
        # Mocking the actual Chapa API call
        with mock.patch('aiohttp.ClientSession.post') as mocked_post:
            mock_resp = mock.AsyncMock()
            mock_resp.status = 200
            mock_resp.json = mock.AsyncMock(return_value={"transaction_id": "chapa_tx_123"})
            mocked_post.return_value.__aenter__.return_value = mock_resp
            
            result = await ethiopian_sovereign_hub.process_ethiopian_payout(legal_request)
            assert result["success"] is True
            assert result["nbe_status"] == "nbe_compliant"

@pytest.mark.asyncio
async def test_digital_trading_order_matching():
    """Test basic order matching in digital trading engine"""
    instrument_data = {
        "symbol": "GOLD.SPOT",
        "type": "spot",
        "underlying_asset": "gold",
        "contract_size": 1.0,
        "tick_size": 0.01,
        "min_order_size": 0.1,
        "max_order_size": 100.0,
        "trading_hours": {"mon-fri": "00:00-24:00"}
    }
    
    instrument = await digital_trading_engine.initialize_instrument(instrument_data)
    
    # Submit BUY limit order
    buy_order_data = {
        "instrument_id": instrument.instrument_id,
        "order_type": "limit",
        "side": "buy",
        "quantity": 1.0,
        "price": 2000.0
    }
    await digital_trading_engine.submit_order("buyer_1", buy_order_data)

    # Submit SELL limit order that matches
    sell_order_data = {
        "instrument_id": instrument.instrument_id,
        "order_type": "limit",
        "side": "sell",
        "quantity": 1.0,
        "price": 1990.0
    }
    await digital_trading_engine.submit_order("seller_1", sell_order_data)

    # Match orders
    trades = await digital_trading_engine.match_orders(instrument.instrument_id)
    
    assert len(trades) == 1
    assert trades[0].price == Decimal('2000.0') # Match at the resting order price
    assert trades[0].quantity == 1.0
    
    # Check positions
    buyer_pos = await digital_trading_engine.get_user_positions("buyer_1")
    seller_pos = await digital_trading_engine.get_user_positions("seller_1")
    
    assert buyer_pos[instrument.instrument_id] == 1.0
    assert seller_pos[instrument.instrument_id] == -1.0

import unittest.mock as mock
