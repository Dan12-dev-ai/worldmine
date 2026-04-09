"""
Liquidity Provider Agent - DEDAN Mine Fractional Ownership System
Handles fractional-ownership logic for high-value minerals with institutional-grade liquidity
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
import json
import uuid
import asyncio
import math
from dataclasses import dataclass
from enum import Enum

class LiquidityTier(Enum):
    """Liquidity tier levels"""
    INSTITUTIONAL = "institutional"  # $10M+ minimum
    PREMIUM = "premium"          # $1M+ minimum
    STANDARD = "standard"        # $100K+ minimum
    RETAIL = "retail"           # $1K+ minimum

class FractionType(Enum):
    """Fraction ownership types"""
    DIRECT_OWNERSHIP = "direct_ownership"
    SYNTHETIC_EXPOSURE = "synthetic_exposure"
    YIELD_BEARING = "yield_bearing"
    GOVERNANCE_TOKEN = "governance_token"

@dataclass
class MineralAsset:
    """High-value mineral asset for fractional ownership"""
    asset_id: str
    mineral_type: str
    weight_carats: float
    purity: float
    origin_verified: bool
    market_value_usd: float
    liquidity_tier: LiquidityTier
    total_shares: int
    available_shares: int
    share_price_usd: float
    created_at: datetime
    metadata: Dict[str, Any]

@dataclass
class FractionalShare:
    """Fractional ownership share"""
    share_id: str
    asset_id: str
    owner_id: str
    share_count: int
    purchase_price_usd: float
    current_value_usd: float
    fraction_type: FractionType
    acquired_at: datetime
    yield_rate: float
    governance_weight: float
    metadata: Dict[str, Any]

@dataclass
class LiquidityPool:
    """Liquidity pool for fractional shares"""
    pool_id: str
    asset_id: str
    total_liquidity_usd: float
    available_liquidity_usd: float
    pool_size_shares: int
    apy_percentage: float
    fee_rate: float
    created_at: datetime
    last_updated: datetime
    providers: List[str]

class LiquidityProviderAgent:
    """Liquidity Provider Agent for fractional mineral ownership"""
    
    def __init__(self):
        self.mineral_assets: Dict[str, MineralAsset] = {}
        self.fractional_shares: Dict[str, List[FractionalShare]] = {}
        self.liquidity_pools: Dict[str, LiquidityPool] = {}
        
        # Liquidity tier configurations
        self.tier_configs = {
            LiquidityTier.INSTITUTIONAL: {
                "min_investment": 10000000,  # $10M
                "max_ownership_percentage": 0.4,  # 40% max
                "fee_rate": 0.001,  # 0.1%
                "apy_boost": 0.02  # +2% APY
            },
            LiquidityTier.PREMIUM: {
                "min_investment": 1000000,  # $1M
                "max_ownership_percentage": 0.15,  # 15% max
                "fee_rate": 0.002,  # 0.2%
                "apy_boost": 0.015  # +1.5% APY
            },
            LiquidityTier.STANDARD: {
                "min_investment": 100000,  # $100K
                "max_ownership_percentage": 0.05,  # 5% max
                "fee_rate": 0.003,  # 0.3%
                "apy_boost": 0.01  # +1% APY
            },
            LiquidityTier.RETAIL: {
                "min_investment": 1000,  # $1K
                "max_ownership_percentage": 0.01,  # 1% max
                "fee_rate": 0.005,  # 0.5%
                "apy_boost": 0.005  # +0.5% APY
            }
        }
        
        # Market making parameters
        self.spread_percentage = 0.02  # 2% spread
        self.depth_threshold = 0.1  # 10% of pool size
        self.rebalance_threshold = 0.05  # 5% imbalance threshold
        
        # Yield calculation parameters
        self.base_apy = 0.05  # 5% base APY
        self.risk_adjustment_factor = 0.02  # Risk adjustment
        self.liquidity_multiplier = 1.5  # Liquidity bonus multiplier
    
    async def create_fractional_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new fractional mineral asset"""
        try:
            # Validate asset data
            validation_result = await self._validate_asset_data(asset_data)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Determine liquidity tier
            market_value = asset_data["market_value_usd"]
            liquidity_tier = self._determine_liquidity_tier(market_value)
            
            # Calculate total shares
            total_shares = self._calculate_total_shares(market_value, liquidity_tier)
            share_price = market_value / total_shares
            
            # Create mineral asset
            asset = MineralAsset(
                asset_id=str(uuid.uuid4()),
                mineral_type=asset_data["mineral_type"],
                weight_carats=asset_data["weight_carats"],
                purity=asset_data["purity"],
                origin_verified=asset_data.get("origin_verified", False),
                market_value_usd=market_value,
                liquidity_tier=liquidity_tier,
                total_shares=total_shares,
                available_shares=total_shares,
                share_price_usd=share_price,
                created_at=datetime.now(timezone.utc),
                metadata=asset_data.get("metadata", {})
            )
            
            # Store asset
            self.mineral_assets[asset.asset_id] = asset
            
            # Create initial liquidity pool
            pool = await self._create_liquidity_pool(asset)
            self.liquidity_pools[pool.pool_id] = pool
            
            return {
                "success": True,
                "asset_id": asset.asset_id,
                "liquidity_tier": liquidity_tier.value,
                "total_shares": total_shares,
                "share_price_usd": share_price,
                "pool_id": pool.pool_id,
                "initial_apy": pool.apy_percentage
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def purchase_fractional_shares(self, purchase_request: Dict[str, Any]) -> Dict[str, Any]:
        """Purchase fractional shares of a mineral asset"""
        try:
            asset_id = purchase_request["asset_id"]
            buyer_id = purchase_request["buyer_id"]
            investment_amount = purchase_request["investment_amount_usd"]
            fraction_type = FractionType(purchase_request.get("fraction_type", "direct_ownership"))
            
            # Get asset
            asset = self.mineral_assets.get(asset_id)
            if not asset:
                return {"success": False, "error": "Asset not found"}
            
            # Validate investment amount
            tier_config = self.tier_configs[asset.liquidity_tier]
            if investment_amount < tier_config["min_investment"]:
                return {
                    "success": False,
                    "error": f"Minimum investment for {asset.liquidity_tier.value} tier is ${tier_config['min_investment']:,.2f}"
                }
            
            # Calculate shares to purchase
            shares_to_purchase = int(investment_amount / asset.share_price_usd)
            actual_investment = shares_to_purchase * asset.share_price_usd
            
            # Check availability
            if shares_to_purchase > asset.available_shares:
                return {"success": False, "error": "Insufficient shares available"}
            
            # Check ownership limits
            current_ownership = await self._get_user_ownership_percentage(asset_id, buyer_id)
            new_ownership = (current_ownership + shares_to_purchase) / asset.total_shares
            
            if new_ownership > tier_config["max_ownership_percentage"]:
                return {
                    "success": False,
                    "error": f"Ownership limit of {tier_config['max_ownership_percentage']*100:.1f}% exceeded"
                }
            
            # Calculate yield and governance
            yield_rate = await self._calculate_yield_rate(asset, fraction_type)
            governance_weight = await self._calculate_governance_weight(shares_to_purchase, asset.total_shares)
            
            # Create fractional share
            share = FractionalShare(
                share_id=str(uuid.uuid4()),
                asset_id=asset_id,
                owner_id=buyer_id,
                share_count=shares_to_purchase,
                purchase_price_usd=actual_investment,
                current_value_usd=actual_investment,
                fraction_type=fraction_type,
                acquired_at=datetime.now(timezone.utc),
                yield_rate=yield_rate,
                governance_weight=governance_weight,
                metadata=purchase_request.get("metadata", {})
            )
            
            # Update asset availability
            asset.available_shares -= shares_to_purchase
            
            # Store share
            if asset_id not in self.fractional_shares:
                self.fractional_shares[asset_id] = []
            self.fractional_shares[asset_id].append(share)
            
            # Update liquidity pool
            await self._update_liquidity_pool(asset_id, -actual_investment)
            
            return {
                "success": True,
                "share_id": share.share_id,
                "shares_purchased": shares_to_purchase,
                "investment_amount": actual_investment,
                "share_price": asset.share_price_usd,
                "ownership_percentage": new_ownership * 100,
                "yield_rate": yield_rate,
                "governance_weight": governance_weight,
                "fraction_type": fraction_type.value
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def provide_liquidity(self, liquidity_request: Dict[str, Any]) -> Dict[str, Any]:
        """Provide liquidity to a fractional asset pool"""
        try:
            asset_id = liquidity_request["asset_id"]
            provider_id = liquidity_request["provider_id"]
            liquidity_amount = liquidity_request["liquidity_amount_usd"]
            
            # Get asset and pool
            asset = self.mineral_assets.get(asset_id)
            pool = self.liquidity_pools.get(asset_id)
            
            if not asset or not pool:
                return {"success": False, "error": "Asset or pool not found"}
            
            # Calculate liquidity shares
            liquidity_shares = int(liquidity_amount / asset.share_price_usd)
            
            # Create liquidity share
            liquidity_share = FractionalShare(
                share_id=str(uuid.uuid4()),
                asset_id=asset_id,
                owner_id=provider_id,
                share_count=liquidity_shares,
                purchase_price_usd=liquidity_amount,
                current_value_usd=liquidity_amount,
                fraction_type=FractionType.YIELD_BEARING,
                acquired_at=datetime.now(timezone.utc),
                yield_rate=pool.apy_percentage,
                governance_weight=0.0,
                metadata={"liquidity_provider": True}
            )
            
            # Update pool
            pool.total_liquidity_usd += liquidity_amount
            pool.available_liquidity_usd += liquidity_amount
            pool.pool_size_shares += liquidity_shares
            
            if provider_id not in pool.providers:
                pool.providers.append(provider_id)
            
            # Store share
            if asset_id not in self.fractional_shares:
                self.fractional_shares[asset_id] = []
            self.fractional_shares[asset_id].append(liquidity_share)
            
            # Recalculate APY
            await self._recalculate_pool_apy(pool)
            
            return {
                "success": True,
                "share_id": liquidity_share.share_id,
                "liquidity_shares": liquidity_shares,
                "liquidity_amount": liquidity_amount,
                "current_apy": pool.apy_percentage,
                "pool_size": pool.total_liquidity_usd
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_market_depth(self, asset_id: str) -> Dict[str, Any]:
        """Get market depth for a fractional asset"""
        try:
            asset = self.mineral_assets.get(asset_id)
            pool = self.liquidity_pools.get(asset_id)
            
            if not asset or not pool:
                return {"success": False, "error": "Asset or pool not found"}
            
            # Calculate market depth
            depth_shares = int(pool.pool_size_shares * self.depth_threshold)
            depth_value = depth_shares * asset.share_price_usd
            
            # Calculate spread
            buy_price = asset.share_price_usd * (1 + self.spread_percentage / 2)
            sell_price = asset.share_price_usd * (1 - self.spread_percentage / 2)
            
            # Get order book (mock)
            order_book = await self._generate_order_book(asset, pool)
            
            return {
                "success": True,
                "asset_id": asset_id,
                "current_price": asset.share_price_usd,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "spread_percentage": self.spread_percentage,
                "depth_shares": depth_shares,
                "depth_value_usd": depth_value,
                "total_liquidity": pool.total_liquidity_usd,
                "available_liquidity": pool.available_liquidity_usd,
                "order_book": order_book
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def calculate_portfolio_value(self, user_id: str) -> Dict[str, Any]:
        """Calculate total portfolio value for a user"""
        try:
            total_value = 0.0
            portfolio_breakdown = {}
            yield_breakdown = {}
            governance_breakdown = {}
            
            # Iterate through all assets
            for asset_id, shares in self.fractional_shares.items():
                user_shares = [s for s in shares if s.owner_id == user_id]
                
                if user_shares:
                    asset = self.mineral_assets.get(asset_id)
                    if asset:
                        asset_value = sum(s.current_value_usd for s in user_shares)
                        total_value += asset_value
                        
                        portfolio_breakdown[asset_id] = {
                            "asset_type": asset.mineral_type,
                            "shares": sum(s.share_count for s in user_shares),
                            "value_usd": asset_value,
                            "ownership_percentage": (sum(s.share_count for s in user_shares) / asset.total_shares) * 100
                        }
                        
                        # Yield breakdown
                        total_yield = sum(s.current_value_usd * s.yield_rate for s in user_shares)
                        yield_breakdown[asset_id] = total_yield
                        
                        # Governance breakdown
                        total_governance = sum(s.governance_weight for s in user_shares)
                        governance_breakdown[asset_id] = total_governance
            
            return {
                "success": True,
                "user_id": user_id,
                "total_portfolio_value_usd": total_value,
                "portfolio_breakdown": portfolio_breakdown,
                "annual_yield_usd": sum(yield_breakdown.values()),
                "yield_breakdown": yield_breakdown,
                "total_governance_weight": sum(governance_breakdown.values()),
                "governance_breakdown": governance_breakdown
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def rebalance_liquidity_pools(self) -> Dict[str, Any]:
        """Rebalance liquidity pools to maintain optimal depth"""
        try:
            rebalanced_pools = []
            
            for pool_id, pool in self.liquidity_pools.items():
                asset = self.mineral_assets.get(pool_id)
                if not asset:
                    continue
                
                # Check if rebalancing is needed
                imbalance_ratio = abs(pool.available_liquidity_usd - pool.total_liquidity_usd * 0.5) / pool.total_liquidity_usd
                
                if imbalance_ratio > self.rebalance_threshold:
                    # Perform rebalancing
                    await self._perform_pool_rebalancing(pool, asset)
                    rebalanced_pools.append(pool_id)
            
            return {
                "success": True,
                "rebalanced_pools": rebalanced_pools,
                "total_pools": len(self.liquidity_pools)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Helper methods
    async def _validate_asset_data(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate asset data for fractional ownership"""
        required_fields = ["mineral_type", "weight_carats", "purity", "market_value_usd"]
        
        for field in required_fields:
            if field not in asset_data:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Validate values
        if asset_data["weight_carats"] <= 0:
            return {"valid": False, "error": "Weight must be positive"}
        
        if not (0 <= asset_data["purity"] <= 1):
            return {"valid": False, "error": "Purity must be between 0 and 1"}
        
        if asset_data["market_value_usd"] <= 0:
            return {"valid": False, "error": "Market value must be positive"}
        
        return {"valid": True}
    
    def _determine_liquidity_tier(self, market_value: float) -> LiquidityTier:
        """Determine liquidity tier based on market value"""
        if market_value >= 10000000:  # $10M+
            return LiquidityTier.INSTITUTIONAL
        elif market_value >= 1000000:  # $1M+
            return LiquidityTier.PREMIUM
        elif market_value >= 100000:  # $100K+
            return LiquidityTier.STANDARD
        else:
            return LiquidityTier.RETAIL
    
    def _calculate_total_shares(self, market_value: float, tier: LiquidityTier) -> int:
        """Calculate total shares based on market value and tier"""
        # Base share calculation: $1 per share for retail tier
        base_shares = int(market_value)
        
        # Adjust for tier (higher tiers get more shares for better granularity)
        tier_multiplier = {
            LiquidityTier.RETAIL: 1,
            LiquidityTier.STANDARD: 10,
            LiquidityTier.PREMIUM: 100,
            LiquidityTier.INSTITUTIONAL: 1000
        }
        
        return base_shares * tier_multiplier[tier]
    
    async def _create_liquidity_pool(self, asset: MineralAsset) -> LiquidityPool:
        """Create initial liquidity pool for asset"""
        tier_config = self.tier_configs[asset.liquidity_tier]
        
        # Calculate base APY
        base_apy = self.base_apy + tier_config["apy_boost"]
        
        # Adjust for asset risk
        risk_adjustment = await self._calculate_risk_adjustment(asset)
        final_apy = base_apy + risk_adjustment
        
        pool = LiquidityPool(
            pool_id=str(uuid.uuid4()),
            asset_id=asset.asset_id,
            total_liquidity_usd=0.0,
            available_liquidity_usd=0.0,
            pool_size_shares=0,
            apy_percentage=final_apy,
            fee_rate=tier_config["fee_rate"],
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            providers=[]
        )
        
        return pool
    
    async def _calculate_yield_rate(self, asset: MineralAsset, fraction_type: FractionType) -> float:
        """Calculate yield rate for fractional share"""
        pool = self.liquidity_pools.get(asset.asset_id)
        base_yield = pool.apy_percentage if pool else self.base_apy
        
        # Adjust for fraction type
        type_multiplier = {
            FractionType.DIRECT_OWNERSHIP: 1.0,
            FractionType.SYNTHETIC_EXPOSURE: 0.8,
            FractionType.YIELD_BEARING: 1.2,
            FractionType.GOVERNANCE_TOKEN: 0.6
        }
        
        return base_yield * type_multiplier[fraction_type]
    
    async def _calculate_governance_weight(self, shares: int, total_shares: int) -> float:
        """Calculate governance weight for shares"""
        # Basic governance weight based on ownership percentage
        ownership_percentage = shares / total_shares
        
        # Apply governance multiplier (1 vote per 1% ownership)
        return ownership_percentage * 100
    
    async def _get_user_ownership_percentage(self, asset_id: str, user_id: str) -> float:
        """Get current ownership percentage for user"""
        if asset_id not in self.fractional_shares:
            return 0.0
        
        user_shares = [s for s in self.fractional_shares[asset_id] if s.owner_id == user_id]
        total_user_shares = sum(s.share_count for s in user_shares)
        
        asset = self.mineral_assets.get(asset_id)
        return total_user_shares if asset else 0.0
    
    async def _update_liquidity_pool(self, asset_id: str, liquidity_change: float):
        """Update liquidity pool"""
        pool = self.liquidity_pools.get(asset_id)
        if pool:
            pool.available_liquidity_usd += liquidity_change
            pool.last_updated = datetime.now(timezone.utc)
    
    async def _recalculate_pool_apy(self, pool: LiquidityPool):
        """Recalculate pool APY based on liquidity depth"""
        # Higher liquidity = lower APY (supply and demand)
        liquidity_factor = min(1.0, pool.total_liquidity_usd / 1000000)  # Normalize to $1M
        
        # Adjust APY based on liquidity
        adjusted_apy = self.base_apy * (1 - liquidity_factor * 0.5)
        
        pool.apy_percentage = max(0.01, adjusted_apy)  # Minimum 1% APY
        pool.last_updated = datetime.now(timezone.utc)
    
    async def _generate_order_book(self, asset: MineralAsset, pool: LiquidityPool) -> Dict[str, Any]:
        """Generate mock order book"""
        # Mock order book generation
        spread = asset.share_price_usd * self.spread_percentage / 2
        
        orders = []
        for i in range(10):  # 10 levels on each side
            buy_price = asset.share_price_usd - spread * (i + 1)
            sell_price = asset.share_price_usd + spread * (i + 1)
            
            orders.append({
                "level": i + 1,
                "buy_price": buy_price,
                "buy_size": 100 * (10 - i),  # Larger sizes closer to market
                "sell_price": sell_price,
                "sell_size": 100 * (10 - i)
            })
        
        return {"orders": orders}
    
    async def _calculate_risk_adjustment(self, asset: MineralAsset) -> float:
        """Calculate risk adjustment for APY"""
        # Higher risk = higher yield
        risk_factors = {
            "origin_verified": -0.01 if asset.origin_verified else 0.02,
            "purity": (asset.purity - 0.9) * 0.05,  # Purity adjustment
            "mineral_type": {
                "gold": 0.0,
                "diamond": 0.01,
                "platinum": 0.005,
                "silver": 0.015,
                "rare_earth": 0.03
            }.get(asset.mineral_type.lower(), 0.02)
        }
        
        return sum(risk_factors.values())
    
    async def _perform_pool_rebalancing(self, pool: LiquidityPool, asset: MineralAsset):
        """Perform pool rebalancing"""
        # Mock rebalancing logic
        target_liquidity = pool.total_liquidity_usd * 0.5
        current_liquidity = pool.available_liquidity_usd
        
        if abs(current_liquidity - target_liquidity) > pool.total_liquidity_usd * self.rebalance_threshold:
            # Adjust available liquidity
            pool.available_liquidity_usd = target_liquidity
            pool.last_updated = datetime.now(timezone.utc)

# Singleton instance
liquidity_provider_agent = LiquidityProviderAgent()
