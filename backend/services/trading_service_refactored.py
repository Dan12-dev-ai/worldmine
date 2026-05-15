"""
Refactored Trading Service for DEDAN 2.0
Split God functions into smaller, focused functions (<30 lines each)
Follows Single Responsibility Principle (SRP)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncpg
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """Order statuses"""
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class OrderRequest:
    """Order request data"""
    user_id: str
    mineral_id: str
    order_type: OrderType
    quantity: Decimal
    price: Decimal
    expiry_time: Optional[datetime] = None

@dataclass
class Order:
    """Order entity"""
    id: str
    user_id: str
    mineral_id: str
    order_type: OrderType
    quantity: Decimal
    remaining_quantity: Decimal
    price: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    expiry_time: Optional[datetime] = None

class TradingService:
    """Refactored trading service with focused functions"""
    
    def __init__(self, db_connection: asyncpg.Connection):
        self.db = db_connection
        self.order_book_manager = OrderBookManager(db_connection)
        self.price_calculator = PriceCalculator()
        self.fee_calculator = FeeCalculator()
        self.balance_manager = BalanceManager(db_connection)
        self.audit_logger = AuditLogger(db_connection)
    
    async def create_order(self, order_request: OrderRequest) -> Order:
        """Create a new trading order"""
        # Validate order request
        await self._validate_order_request(order_request)
        
        # Check user balance
        await self._check_user_balance(order_request)
        
        # Create order
        order = await self._create_order_entity(order_request)
        
        # Add to order book
        await self.order_book_manager.add_order(order)
        
        # Try to match order
        await self._try_match_order(order)
        
        # Log creation
        await self.audit_logger.log_order_creation(order)
        
        return order
    
    async def _validate_order_request(self, order_request: OrderRequest) -> None:
        """Validate order request parameters"""
        if not order_request.user_id:
            raise ValueError("User ID is required")
        
        if not order_request.mineral_id:
            raise ValueError("Mineral ID is required")
        
        if order_request.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if order_request.price <= 0:
            raise ValueError("Price must be positive")
        
        # Check expiry time
        if order_request.expiry_time and order_request.expiry_time <= datetime.utcnow():
            raise ValueError("Expiry time must be in the future")
    
    async def _check_user_balance(self, order_request: OrderRequest) -> None:
        """Check if user has sufficient balance"""
        if order_request.order_type == OrderType.BUY:
            required_balance = order_request.quantity * order_request.price
            await self.balance_manager.check_funds_balance(
                order_request.user_id, 
                required_balance
            )
        else:
            await self.balance_manager.check_mineral_balance(
                order_request.user_id,
                order_request.mineral_id,
                order_request.quantity
            )
    
    async def _create_order_entity(self, order_request: OrderRequest) -> Order:
        """Create order entity in database"""
        order_id = await self._generate_order_id()
        
        order = Order(
            id=order_id,
            user_id=order_request.user_id,
            mineral_id=order_request.mineral_id,
            order_type=order_request.order_type,
            quantity=order_request.quantity,
            remaining_quantity=order_request.quantity,
            price=order_request.price,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expiry_time=order_request.expiry_time
        )
        
        # Save to database
        await self._save_order_to_db(order)
        
        return order
    
    async def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def _save_order_to_db(self, order: Order) -> None:
        """Save order to database"""
        query = """
            INSERT INTO orders (
                id, user_id, mineral_id, order_type, quantity,
                remaining_quantity, price, status, created_at,
                updated_at, expiry_time
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        await self.db.execute(
            query,
            order.id,
            order.user_id,
            order.mineral_id,
            order.order_type.value,
            order.quantity,
            order.remaining_quantity,
            order.price,
            order.status.value,
            order.created_at,
            order.updated_at,
            order.expiry_time
        )
    
    async def _try_match_order(self, order: Order) -> None:
        """Try to match order with existing orders"""
        matches = await self.order_book_manager.find_matches(order)
        
        for match in matches:
            await self._execute_match(order, match)
            
            # Update order status
            if order.remaining_quantity <= 0:
                order.status = OrderStatus.FILLED
                await self._update_order_status(order)
                break
            else:
                order.status = OrderStatus.PARTIAL
                await self._update_order_status(order)
    
    async def _execute_match(self, order: Order, match: Order) -> None:
        """Execute a trade match"""
        # Calculate trade details
        trade_quantity = min(order.remaining_quantity, match.remaining_quantity)
        trade_price = match.price  # Use taker's price
        
        # Calculate fees
        buyer_fee = await self.fee_calculator.calculate_buy_fee(
            trade_quantity, trade_price
        )
        seller_fee = await self.fee_calculator.calculate_sell_fee(
            trade_quantity, trade_price
        )
        
        # Execute trade
        await self._execute_trade_execution(
            order, match, trade_quantity, trade_price, buyer_fee, seller_fee
        )
        
        # Update order quantities
        await self._update_order_quantities(order, match, trade_quantity)
    
    async def _execute_trade_execution(
        self, 
        order: Order, 
        match: Order, 
        quantity: Decimal, 
        price: Decimal,
        buyer_fee: Decimal,
        seller_fee: Decimal
    ) -> None:
        """Execute the trade"""
        # Determine buyer and seller
        if order.order_type == OrderType.BUY:
            buyer_order = order
            seller_order = match
        else:
            buyer_order = match
            seller_order = order
        
        # Transfer balances
        await self.balance_manager.transfer_funds(
            buyer_order.user_id,
            seller_order.user_id,
            quantity * price
        )
        
        await self.balance_manager.transfer_mineral(
            seller_order.user_id,
            buyer_order.user_id,
            order.mineral_id,
            quantity
        )
        
        # Deduct fees
        await self.balance_manager.deduct_fee(buyer_order.user_id, buyer_fee)
        await self.balance_manager.deduct_fee(seller_order.user_id, seller_fee)
        
        # Record trade
        await self._record_trade(
            buyer_order, seller_order, quantity, price, buyer_fee, seller_fee
        )
    
    async def _record_trade(
        self,
        buyer_order: Order,
        seller_order: Order,
        quantity: Decimal,
        price: Decimal,
        buyer_fee: Decimal,
        seller_fee: Decimal
    ) -> None:
        """Record trade in database"""
        trade_id = await self._generate_trade_id()
        
        query = """
            INSERT INTO trades (
                id, buyer_order_id, seller_order_id, mineral_id,
                quantity, price, buyer_fee, seller_fee, executed_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        await self.db.execute(
            query,
            trade_id,
            buyer_order.id,
            seller_order.id,
            buyer_order.mineral_id,
            quantity,
            price,
            buyer_fee,
            seller_fee,
            datetime.utcnow()
        )
    
    async def _generate_trade_id(self) -> str:
        """Generate unique trade ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def _update_order_quantities(
        self, 
        order: Order, 
        match: Order, 
        trade_quantity: Decimal
    ) -> None:
        """Update order remaining quantities"""
        order.remaining_quantity -= trade_quantity
        match.remaining_quantity -= trade_quantity
        
        # Update in database
        await self._update_order_quantity(order)
        await self._update_order_quantity(match)
    
    async def _update_order_quantity(self, order: Order) -> None:
        """Update order quantity in database"""
        query = """
            UPDATE orders 
            SET remaining_quantity = $1, updated_at = $2
            WHERE id = $3
        """
        
        await self.db.execute(
            query,
            order.remaining_quantity,
            datetime.utcnow(),
            order.id
        )
    
    async def _update_order_status(self, order: Order) -> None:
        """Update order status in database"""
        query = """
            UPDATE orders 
            SET status = $1, updated_at = $2
            WHERE id = $3
        """
        
        await self.db.execute(
            query,
            order.status.value,
            datetime.utcnow(),
            order.id
        )
    
    async def cancel_order(self, order_id: str, user_id: str) -> bool:
        """Cancel an order"""
        # Get order
        order = await self._get_order(order_id)
        
        if not order:
            return False
        
        if order.user_id != user_id:
            return False
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return False
        
        # Cancel order
        order.status = OrderStatus.CANCELLED
        await self._update_order_status(order)
        
        # Remove from order book
        await self.order_book_manager.remove_order(order)
        
        # Log cancellation
        await self.audit_logger.log_order_cancellation(order)
        
        return True
    
    async def _get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        query = """
            SELECT id, user_id, mineral_id, order_type, quantity,
                   remaining_quantity, price, status, created_at,
                   updated_at, expiry_time
            FROM orders
            WHERE id = $1
        """
        
        row = await self.db.fetchrow(query, order_id)
        
        if not row:
            return None
        
        return Order(
            id=row['id'],
            user_id=row['user_id'],
            mineral_id=row['mineral_id'],
            order_type=OrderType(row['order_type']),
            quantity=row['quantity'],
            remaining_quantity=row['remaining_quantity'],
            price=row['price'],
            status=OrderStatus(row['status']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            expiry_time=row['expiry_time']
        )
    
    async def get_user_orders(
        self, 
        user_id: str, 
        status: Optional[OrderStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Order]:
        """Get user's orders"""
        query = """
            SELECT id, user_id, mineral_id, order_type, quantity,
                   remaining_quantity, price, status, created_at,
                   updated_at, expiry_time
            FROM orders
            WHERE user_id = $1
        """
        
        params = [user_id]
        
        if status:
            query += " AND status = $2"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT $%d OFFSET $%d" % (len(params) + 1, len(params) + 2)
        params.extend([limit, offset])
        
        rows = await self.db.fetch(query, *params)
        
        return [
            Order(
                id=row['id'],
                user_id=row['user_id'],
                mineral_id=row['mineral_id'],
                order_type=OrderType(row['order_type']),
                quantity=row['quantity'],
                remaining_quantity=row['remaining_quantity'],
                price=row['price'],
                status=OrderStatus(row['status']),
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                expiry_time=row['expiry_time']
            )
            for row in rows
        ]

class OrderBookManager:
    """Manages order book operations"""
    
    def __init__(self, db_connection: asyncpg.Connection):
        self.db = db_connection
    
    async def add_order(self, order: Order) -> None:
        """Add order to order book"""
        query = """
            INSERT INTO order_book (
                order_id, mineral_id, order_type, price, quantity,
                remaining_quantity, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        await self.db.execute(
            query,
            order.id,
            order.mineral_id,
            order.order_type.value,
            order.price,
            order.quantity,
            order.remaining_quantity,
            order.created_at
        )
    
    async def remove_order(self, order: Order) -> None:
        """Remove order from order book"""
        query = """
            DELETE FROM order_book WHERE order_id = $1
        """
        
        await self.db.execute(query, order.id)
    
    async def find_matches(self, order: Order) -> List[Order]:
        """Find matching orders for the given order"""
        if order.order_type == OrderType.BUY:
            return await self._find_sell_matches(order)
        else:
            return await self._find_buy_matches(order)
    
    async def _find_sell_matches(self, buy_order: Order) -> List[Order]:
        """Find sell orders that match buy order"""
        query = """
            SELECT o.id, o.user_id, o.mineral_id, o.order_type,
                   o.quantity, o.remaining_quantity, o.price, o.status,
                   o.created_at, o.updated_at, o.expiry_time
            FROM orders o
            JOIN order_book ob ON o.id = ob.order_id
            WHERE o.mineral_id = $1
            AND o.order_type = 'sell'
            AND o.status IN ('pending', 'partial')
            AND o.price <= $2
            AND o.expiry_time > NOW()
            ORDER BY o.price ASC, o.created_at ASC
            LIMIT 10
        """
        
        rows = await self.db.fetch(
            query, buy_order.mineral_id, buy_order.price
        )
        
        return [self._row_to_order(row) for row in rows]
    
    async def _find_buy_matches(self, sell_order: Order) -> List[Order]:
        """Find buy orders that match sell order"""
        query = """
            SELECT o.id, o.user_id, o.mineral_id, o.order_type,
                   o.quantity, o.remaining_quantity, o.price, o.status,
                   o.created_at, o.updated_at, o.expiry_time
            FROM orders o
            JOIN order_book ob ON o.id = ob.order_id
            WHERE o.mineral_id = $1
            AND o.order_type = 'buy'
            AND o.status IN ('pending', 'partial')
            AND o.price >= $2
            AND o.expiry_time > NOW()
            ORDER BY o.price DESC, o.created_at ASC
            LIMIT 10
        """
        
        rows = await self.db.fetch(
            query, sell_order.mineral_id, sell_order.price
        )
        
        return [self._row_to_order(row) for row in rows]
    
    def _row_to_order(self, row) -> Order:
        """Convert database row to Order object"""
        return Order(
            id=row['id'],
            user_id=row['user_id'],
            mineral_id=row['mineral_id'],
            order_type=OrderType(row['order_type']),
            quantity=row['quantity'],
            remaining_quantity=row['remaining_quantity'],
            price=row['price'],
            status=OrderStatus(row['status']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            expiry_time=row['expiry_time']
        )

class PriceCalculator:
    """Calculates prices and price-related metrics"""
    
    def calculate_market_price(
        self, 
        buy_orders: List[Order], 
        sell_orders: List[Order]
    ) -> Decimal:
        """Calculate market price from order book"""
        if not buy_orders or not sell_orders:
            return Decimal('0')
        
        # Find best buy and sell prices
        best_buy = max(buy_orders, key=lambda x: x.price)
        best_sell = min(sell_orders, key=lambda x: x.price)
        
        # Market price is the midpoint
        return (best_buy.price + best_sell.price) / Decimal('2')
    
    def calculate_spread(
        self, 
        buy_orders: List[Order], 
        sell_orders: List[Order]
    ) -> Decimal:
        """Calculate bid-ask spread"""
        if not buy_orders or not sell_orders:
            return Decimal('0')
        
        best_buy = max(buy_orders, key=lambda x: x.price)
        best_sell = min(sell_orders, key=lambda x: x.price)
        
        return best_sell.price - best_buy.price

class FeeCalculator:
    """Calculates trading fees"""
    
    def __init__(self):
        self.buy_fee_rate = Decimal('0.001')  # 0.1%
        self.sell_fee_rate = Decimal('0.001')  # 0.1%
        self.min_fee = Decimal('0.01')  # Minimum fee
    
    async def calculate_buy_fee(
        self, 
        quantity: Decimal, 
        price: Decimal
    ) -> Decimal:
        """Calculate buy fee"""
        fee = quantity * price * self.buy_fee_rate
        return max(fee, self.min_fee)
    
    async def calculate_sell_fee(
        self, 
        quantity: Decimal, 
        price: Decimal
    ) -> Decimal:
        """Calculate sell fee"""
        fee = quantity * price * self.sell_fee_rate
        return max(fee, self.min_fee)

class BalanceManager:
    """Manages user balances"""
    
    def __init__(self, db_connection: asyncpg.Connection):
        self.db = db_connection
    
    async def check_funds_balance(
        self, 
        user_id: str, 
        required_amount: Decimal
    ) -> None:
        """Check if user has sufficient funds balance"""
        query = """
            SELECT balance FROM user_balances 
            WHERE user_id = $1 AND currency = 'USD'
        """
        
        row = await self.db.fetchrow(query, user_id)
        
        if not row or row['balance'] < required_amount:
            raise ValueError("Insufficient funds balance")
    
    async def check_mineral_balance(
        self, 
        user_id: str, 
        mineral_id: str, 
        required_quantity: Decimal
    ) -> None:
        """Check if user has sufficient mineral balance"""
        query = """
            SELECT balance FROM mineral_balances 
            WHERE user_id = $1 AND mineral_id = $2
        """
        
        row = await self.db.fetchrow(query, user_id, mineral_id)
        
        if not row or row['balance'] < required_quantity:
            raise ValueError("Insufficient mineral balance")
    
    async def transfer_funds(
        self, 
        from_user: str, 
        to_user: str, 
        amount: Decimal
    ) -> None:
        """Transfer funds between users"""
        await self.db.execute(
            "UPDATE user_balances SET balance = balance - $1 WHERE user_id = $2",
            amount, from_user
        )
        
        await self.db.execute(
            "UPDATE user_balances SET balance = balance + $1 WHERE user_id = $2",
            amount, to_user
        )
    
    async def transfer_mineral(
        self, 
        from_user: str, 
        to_user: str, 
        mineral_id: str, 
        quantity: Decimal
    ) -> None:
        """Transfer mineral between users"""
        await self.db.execute(
            "UPDATE mineral_balances SET balance = balance - $1 WHERE user_id = $2 AND mineral_id = $3",
            quantity, from_user, mineral_id
        )
        
        await self.db.execute(
            "UPDATE mineral_balances SET balance = balance + $1 WHERE user_id = $2 AND mineral_id = $3",
            quantity, to_user, mineral_id
        )
    
    async def deduct_fee(self, user_id: str, fee: Decimal) -> None:
        """Deduct fee from user balance"""
        await self.db.execute(
            "UPDATE user_balances SET balance = balance - $1 WHERE user_id = $2",
            fee, user_id
        )

class AuditLogger:
    """Logs trading activities for audit purposes"""
    
    def __init__(self, db_connection: asyncpg.Connection):
        self.db = db_connection
    
    async def log_order_creation(self, order: Order) -> None:
        """Log order creation"""
        query = """
            INSERT INTO audit_log (
                user_id, action, resource_id, resource_type,
                details, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        await self.db.execute(
            query,
            order.user_id,
            'CREATE_ORDER',
            order.id,
            'ORDER',
            f"Created {order.order_type.value} order for {order.quantity} at {order.price}",
            datetime.utcnow()
        )
    
    async def log_order_cancellation(self, order: Order) -> None:
        """Log order cancellation"""
        query = """
            INSERT INTO audit_log (
                user_id, action, resource_id, resource_type,
                details, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        await self.db.execute(
            query,
            order.user_id,
            'CANCEL_ORDER',
            order.id,
            'ORDER',
            f"Cancelled order with status {order.status.value}",
            datetime.utcnow()
        )
