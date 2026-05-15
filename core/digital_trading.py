# DIGITAL MINERAL TRADING PLATFORM (FINANCIAL LAYER)
# DEDAN Mine - Global Mineral Marketplace Platform
# Financial trading platform for mineral-backed instruments

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import numpy as np

from core.production_foundation import audit_log, risk_engine
from core.event_driven_architecture import event_bus, EventType, Event
from core.governance_orchestrator import governance_orchestrator

logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types for digital trading"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"

class InstrumentType(Enum):
    """Financial instrument types"""
    SPOT = "spot"  # Spot trading
    FUTURES = "futures"  # Futures contracts
    OPTIONS = "options"  # Options contracts
    ETF = "etf"  # Mineral ETF
    INDEX = "index"  # Price index

@dataclass
class TradingInstrument:
    """Digital trading instrument"""
    instrument_id: str
    symbol: str  # e.g., "GOLD.SPOT", "COPPER.FUTURES"
    instrument_type: InstrumentType
    underlying_asset: str  # Physical mineral
    contract_size: float
    tick_size: Decimal
    min_order_size: float
    max_order_size: float
    trading_hours: Dict[str, str]  # UTC trading hours
    settlement_currency: str
    is_active: bool = True

@dataclass
class Order:
    """Trading order"""
    order_id: str
    user_id: str
    instrument_id: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "GTC"  # Good Till Cancelled
    status: str = "pending"
    filled_quantity: float = 0.0
    remaining_quantity: float = field(init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        self.remaining_quantity = self.quantity

@dataclass
class Trade:
    """Executed trade"""
    trade_id: str
    buy_order_id: str
    sell_order_id: str
    instrument_id: str
    price: Decimal
    quantity: float
    executed_at: datetime
    buyer_id: str
    seller_id: str

@dataclass
class OrderBook:
    """Order book for an instrument"""
    instrument_id: str
    bids: List[Order] = field(default_factory=list)  # Buy orders, sorted by price desc
    asks: List[Order] = field(default_factory=list)  # Sell orders, sorted by price asc
    last_trade_price: Optional[Decimal] = None
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class DigitalTradingEngine:
    """
    Digital trading engine for mineral-backed financial instruments
    Handles order matching, risk management, and settlement
    """

    def __init__(self):
        self.instruments: Dict[str, TradingInstrument] = {}
        self.order_books: Dict[str, OrderBook] = {}
        self.pending_orders: Dict[str, Order] = {}
        self.completed_trades: List[Trade] = []
        self.user_positions: Dict[str, Dict[str, float]] = {}  # user_id -> instrument_id -> position

    async def initialize_instrument(self, instrument_data: Dict[str, Any]) -> TradingInstrument:
        """Initialize a new trading instrument"""
        instrument = TradingInstrument(
            instrument_id=str(uuid.uuid4()),
            symbol=instrument_data['symbol'],
            instrument_type=InstrumentType(instrument_data['type']),
            underlying_asset=instrument_data['underlying_asset'],
            contract_size=instrument_data['contract_size'],
            tick_size=Decimal(str(instrument_data['tick_size'])),
            min_order_size=instrument_data['min_order_size'],
            max_order_size=instrument_data['max_order_size'],
            trading_hours=instrument_data['trading_hours'],
            settlement_currency=instrument_data.get('settlement_currency', 'USD')
        )

        self.instruments[instrument.instrument_id] = instrument
        self.order_books[instrument.instrument_id] = OrderBook(instrument_id=instrument.instrument_id)

        # Publish instrument creation event
        event = Event(
            event_type=EventType.TRADING_INSTRUMENT_CREATED,
            payload={"instrument": instrument.__dict__},
            correlation_id=str(uuid.uuid4())
        )
        await event_bus.publish(event)

        logger.info(f"Trading instrument initialized: {instrument.symbol}")
        return instrument

    async def submit_order(self, user_id: str, order_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Order]]:
        """
        Submit trading order with risk validation
        """
        logger.info(f"Submitting order for user {user_id}")

        # Step 1: Validate user permissions and risk
        if not await self._validate_user_trading_permissions(user_id):
            return False, "User trading permissions denied", None

        # Step 2: Create order object
        order = Order(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            instrument_id=order_data['instrument_id'],
            order_type=OrderType(order_data['order_type']),
            side=OrderSide(order_data['side']),
            quantity=order_data['quantity'],
            price=Decimal(str(order_data['price'])) if 'price' in order_data else None,
            stop_price=Decimal(str(order_data['stop_price'])) if 'stop_price' in order_data else None,
            time_in_force=order_data.get('time_in_force', 'GTC')
        )

        # Step 3: Validate order parameters
        validation_result = await self._validate_order(order)
        if not validation_result[0]:
            return validation_result[0], validation_result[1], None

        # Step 4: Risk assessment
        risk_check = await self._assess_trading_risk(order)
        if not risk_check['approved']:
            return False, f"Risk check failed: {risk_check['reason']}", None

        # Step 5: Submit to order book
        success = await self._submit_to_order_book(order)

        if success:
            self.pending_orders[order.order_id] = order

            # Publish order submission event
            event = Event(
                event_type=EventType.TRADING_ORDER_SUBMITTED,
                payload={"order": order.__dict__, "risk_check": risk_check},
                correlation_id=str(uuid.uuid4())
            )
            await event_bus.publish(event)

            # Log order submission
            await audit_log.log_order_submission(order)

            logger.info(f"Order submitted: {order.order_id}")
            return True, "Order submitted successfully", order
        else:
            return False, "Order submission failed", None

    async def match_orders(self, instrument_id: str) -> List[Trade]:
        """
        Match buy and sell orders in the order book
        """
        order_book = self.order_books.get(instrument_id)
        if not order_book:
            return []

        trades = []
        instrument = self.instruments.get(instrument_id)

        # Simple price-time matching algorithm
        while order_book.bids and order_book.asks:
            best_bid = max(order_book.bids, key=lambda o: o.price or Decimal('0'))
            best_ask = min(order_book.asks, key=lambda o: o.price or Decimal('0'))

            # Check if orders can match
            if best_bid.price and best_ask.price and best_bid.price >= best_ask.price:
                # Execute trade
                trade_quantity = min(best_bid.remaining_quantity, best_ask.remaining_quantity)
                trade_price = best_ask.price if best_bid.order_type == OrderType.MARKET else best_bid.price

                trade = Trade(
                    trade_id=str(uuid.uuid4()),
                    buy_order_id=best_bid.order_id,
                    sell_order_id=best_ask.order_id,
                    instrument_id=instrument_id,
                    price=trade_price,
                    quantity=trade_quantity,
                    executed_at=datetime.now(timezone.utc),
                    buyer_id=best_bid.user_id,
                    seller_id=best_ask.user_id
                )

                # Update order quantities
                best_bid.filled_quantity += trade_quantity
                best_bid.remaining_quantity -= trade_quantity
                best_ask.filled_quantity += trade_quantity
                best_ask.remaining_quantity -= trade_quantity

                # Remove filled orders
                if best_bid.remaining_quantity == 0:
                    order_book.bids.remove(best_bid)
                    if best_bid.order_id in self.pending_orders:
                        del self.pending_orders[best_bid.order_id]
                if best_ask.remaining_quantity == 0:
                    order_book.asks.remove(best_ask)
                    if best_ask.order_id in self.pending_orders:
                        del self.pending_orders[best_ask.order_id]

                # Update positions
                await self._update_user_positions(trade)

                trades.append(trade)
                order_book.last_trade_price = trade_price
                order_book.last_update = datetime.now(timezone.utc)

                # Publish trade execution event
                event = Event(
                    event_type=EventType.TRADING_TRADE_EXECUTED,
                    payload={"trade": trade.__dict__},
                    correlation_id=str(uuid.uuid4())
                )
                await event_bus.publish(event)

                # Log trade execution
                await audit_log.log_trade_execution(trade)

            else:
                break  # No more matches possible

        logger.info(f"Executed {len(trades)} trades for instrument {instrument_id}")
        return trades

    async def get_order_book(self, instrument_id: str) -> Optional[OrderBook]:
        """Get current order book for instrument"""
        return self.order_books.get(instrument_id)

    async def get_user_positions(self, user_id: str) -> Dict[str, float]:
        """Get user's current positions"""
        return self.user_positions.get(user_id, {})

    async def _validate_order(self, order: Order) -> Tuple[bool, str]:
        """Validate order parameters"""
        instrument = self.instruments.get(order.instrument_id)
        if not instrument:
            return False, "Invalid instrument"

        # Check trading hours
        if not self._is_trading_hours(instrument):
            return False, "Outside trading hours"

        # Check order size limits
        if order.quantity < instrument.min_order_size:
            return False, f"Order size below minimum {instrument.min_order_size}"
        if order.quantity > instrument.max_order_size:
            return False, f"Order size above maximum {instrument.max_order_size}"

        # Validate price for limit orders
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and not order.price:
            return False, "Price required for limit orders"

        # Check tick size
        if order.price and order.price % instrument.tick_size != 0:
            return False, f"Price must be multiple of tick size {instrument.tick_size}"

        return True, "Order valid"

    async def _assess_trading_risk(self, order: Order) -> Dict[str, Any]:
        """Assess trading risk for order"""
        user_positions = self.user_positions.get(order.user_id, {})
        current_position = user_positions.get(order.instrument_id, 0)

        # Calculate potential new position
        position_change = order.quantity if order.side == OrderSide.BUY else -order.quantity
        new_position = current_position + position_change

        # Risk checks
        risk_checks = {
            "position_limit": abs(new_position) <= 1000,  # Max position size
            "daily_volume_limit": await self._check_daily_volume_limit(order.user_id),
            "concentration_limit": await self._check_concentration_limit(order.user_id, order.instrument_id),
            "volatility_check": await self._check_market_volatility(order.instrument_id)
        }

        approved = all(risk_checks.values())
        reason = "All risk checks passed" if approved else f"Failed checks: {[k for k, v in risk_checks.items() if not v]}"

        return {
            "approved": approved,
            "reason": reason,
            "checks": risk_checks,
            "new_position": new_position
        }

    async def _submit_to_order_book(self, order: Order) -> bool:
        """Submit order to appropriate order book"""
        order_book = self.order_books.get(order.instrument_id)
        if not order_book:
            return False

        if order.side == OrderSide.BUY:
            order_book.bids.append(order)
            order_book.bids.sort(key=lambda o: o.price or Decimal('0'), reverse=True)
        else:
            order_book.asks.append(order)
            order_book.asks.sort(key=lambda o: o.price or Decimal('0'))

        order_book.last_update = datetime.now(timezone.utc)
        return True

    async def _update_user_positions(self, trade: Trade):
        """Update user positions after trade execution"""
        # Update buyer position (long)
        if trade.buyer_id not in self.user_positions:
            self.user_positions[trade.buyer_id] = {}
        self.user_positions[trade.buyer_id][trade.instrument_id] = \
            self.user_positions[trade.buyer_id].get(trade.instrument_id, 0) + trade.quantity

        # Update seller position (short)
        if trade.seller_id not in self.user_positions:
            self.user_positions[trade.seller_id] = {}
        self.user_positions[trade.seller_id][trade.instrument_id] = \
            self.user_positions[trade.seller_id].get(trade.instrument_id, 0) - trade.quantity

    async def _validate_user_trading_permissions(self, user_id: str) -> bool:
        """Validate user has trading permissions"""
        # Placeholder - integrate with user service
        return True

    def _is_trading_hours(self, instrument: TradingInstrument) -> bool:
        """Check if current time is within trading hours"""
        # Placeholder - implement proper trading hours check
        return True

    async def _check_daily_volume_limit(self, user_id: str) -> bool:
        """Check user's daily volume limit"""
        # Placeholder - implement volume tracking
        return True

    async def _check_concentration_limit(self, user_id: str, instrument_id: str) -> bool:
        """Check position concentration limits"""
        # Placeholder - implement concentration checks
        return True

    async def _check_market_volatility(self, instrument_id: str) -> bool:
        """Check market volatility for trading restrictions"""
        # Placeholder - implement volatility checks
        return True

# Global digital trading engine instance
digital_trading_engine = DigitalTradingEngine()