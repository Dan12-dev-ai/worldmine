"""
Evolving Agent Marketplace - DEDAN Mine
Market for renting and trading trained AI agents
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import json
import uuid
from dataclasses import dataclass

from ..database import get_db
from ..models import User, MarketAgent, AgentRental, Transaction

@dataclass
class AgentType:
    """Agent type configuration"""
    name: str
    description: str
    base_rental_price: float
    experience_multiplier: float
    required_experience: int

@dataclass
class RentalAgreement:
    """Rental agreement details"""
    agent_id: str
    renter_id: str
    rental_duration_hours: int
    total_cost: float
    payment_method: str
    terms_accepted: bool

class AgentMarketplace:
    """Marketplace for AI agent rentals and trading"""
    
    def __init__(self):
        self.agent_types = {
            "mineral_scout": AgentType(
                name="Mineral Scout Agent",
                description="Specializes in finding high-quality mineral opportunities",
                base_rental_price=50.0,
                experience_multiplier=1.5,
                required_experience=100
            ),
            "price_predictor": AgentType(
                name="Price Prediction Agent",
                description="Uses ML to predict optimal pricing strategies",
                base_rental_price=75.0,
                experience_multiplier=1.3,
                required_experience=150
            ),
            "risk_analyzer": AgentType(
                name="Risk Analysis Agent",
                description="Evaluates and mitigates trading risks",
                base_rental_price=60.0,
                experience_multiplier=1.4,
                required_experience=120
            ),
            "market_matcher": AgentType(
                name="Market Matcher Agent",
                description="Finds optimal buyer-seller matches",
                base_rental_price=40.0,
                experience_multiplier=1.2,
                required_experience=80
            )
        }
        
        self.payment_methods = ["tokens", "usdc", "usdt", "eth", "btc"]
    
    async def list_agent_for_rental(
        self,
        owner_id: str,
        agent_type: str,
        rental_price_per_hour: float,
        min_rental_hours: int = 1,
        max_rental_hours: int = 168,  # 1 week
        description: str = ""
    ) -> Dict[str, Any]:
        """List an agent for rental in the marketplace"""
        try:
            # Validate agent type
            if agent_type not in self.agent_types:
                return {
                    "success": False,
                    "error": f"Invalid agent type: {agent_type}"
                }
            
            # Check if user has sufficient experience
            owner_experience = await self._get_user_experience_points(owner_id)
            required_experience = self.agent_types[agent_type].required_experience
            
            if owner_experience < required_experience:
                return {
                    "success": False,
                    "error": f"Insufficient experience. Required: {required_experience}, Current: {owner_experience}"
                }
            
            # Create market agent listing
            market_agent = MarketAgent(
                id=str(uuid.uuid4()),
                owner_id=owner_id,
                agent_type=agent_type,
                rental_price_per_hour=rental_price_per_hour,
                min_rental_hours=min_rental_hours,
                max_rental_hours=max_rental_hours,
                description=description,
                experience_points=owner_experience,
                is_available=True,
                total_rentals=0,
                total_earnings=0.0,
                average_rating=0.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db = next(get_db())
            db.add(market_agent)
            db.commit()
            
            return {
                "success": True,
                "agent_id": market_agent.id,
                "agent_type": agent_type,
                "rental_price_per_hour": rental_price_per_hour,
                "experience_points": owner_experience,
                "listing_status": "active",
                "listed_at": market_agent.created_at.isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def rent_agent(
        self,
        renter_id: str,
        agent_id: str,
        rental_duration_hours: int,
        payment_method: str,
        terms_accepted: bool = False
    ) -> Dict[str, Any]:
        """Rent an agent from the marketplace"""
        try:
            # Validate payment method
            if payment_method not in self.payment_methods:
                return {
                    "success": False,
                    "error": f"Invalid payment method: {payment_method}"
                }
            
            # Get agent details
            agent = await self._get_market_agent(agent_id)
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            if not agent.is_available:
                return {"success": False, "error": "Agent is not available for rental"}
            
            # Validate rental duration
            if rental_duration_hours < agent.min_rental_hours:
                return {
                    "success": False,
                    "error": f"Minimum rental duration is {agent.min_rental_hours} hours"
                }
            
            if rental_duration_hours > agent.max_rental_hours:
                return {
                    "success": False,
                    "error": f"Maximum rental duration is {agent.max_rental_hours} hours"
                }
            
            # Calculate total cost
            total_cost = agent.rental_price_per_hour * rental_duration_hours
            
            # Check renter's balance (this would integrate with payment system)
            renter_balance = await self._get_user_balance(renter_id, payment_method)
            if renter_balance < total_cost:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Required: {total_cost}, Available: {renter_balance}"
                }
            
            if not terms_accepted:
                return {
                    "success": False,
                    "error": "Rental terms must be accepted"
                }
            
            # Create rental agreement
            rental = AgentRental(
                id=str(uuid.uuid4()),
                agent_id=agent_id,
                renter_id=renter_id,
                rental_duration_hours=rental_duration_hours,
                total_cost=total_cost,
                payment_method=payment_method,
                rental_start_time=datetime.now(timezone.utc),
                rental_end_time=datetime.now(timezone.utc) + timedelta(hours=rental_duration_hours),
                status="active",
                terms_accepted=terms_accepted,
                created_at=datetime.now(timezone.utc)
            )
            
            # Update agent availability
            agent.is_available = False
            agent.total_rentals += 1
            agent.updated_at = datetime.now(timezone.utc)
            
            # Process payment
            payment_result = await self._process_payment(
                renter_id=renter_id,
                owner_id=agent.owner_id,
                amount=total_cost,
                payment_method=payment_method,
                transaction_type="agent_rental"
            )
            
            if not payment_result["success"]:
                return {
                    "success": False,
                    "error": f"Payment failed: {payment_result['error']}"
                }
            
            db = next(get_db())
            db.add(rental)
            db.commit()
            
            return {
                "success": True,
                "rental_id": rental.id,
                "agent_id": agent_id,
                "rental_duration_hours": rental_duration_hours,
                "total_cost": total_cost,
                "payment_method": payment_method,
                "rental_start_time": rental.rental_start_time.isoformat(),
                "rental_end_time": rental.rental_end_time.isoformat(),
                "agent_access_token": await self._generate_agent_access_token(rental.id),
                "payment_transaction_id": payment_result.get("transaction_id")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_available_agents(
        self,
        agent_type: Optional[str] = None,
        max_price_per_hour: Optional[float] = None,
        min_experience_points: Optional[int] = None,
        sort_by: str = "experience_points",
        sort_order: str = "desc"
        ) -> Dict[str, Any]:
        """Get list of available agents for rental"""
        try:
            db = next(get_db())
            
            # Build query
            query = db.query(MarketAgent).filter(MarketAgent.is_available == True)
            
            if agent_type:
                query = query.filter(MarketAgent.agent_type == agent_type)
            
            if max_price_per_hour:
                query = query.filter(MarketAgent.rental_price_per_hour <= max_price_per_hour)
            
            if min_experience_points:
                query = query.filter(MarketAgent.experience_points >= min_experience_points)
            
            # Apply sorting
            if sort_by == "experience_points":
                query = query.order_by(
                    MarketAgent.experience_points.desc() if sort_order == "desc" 
                    else MarketAgent.experience_points.asc()
                )
            elif sort_by == "price":
                query = query.order_by(
                    MarketAgent.rental_price_per_hour.asc() if sort_order == "asc"
                    else MarketAgent.rental_price_per_hour.desc()
                )
            elif sort_by == "rating":
                query = query.order_by(
                    MarketAgent.average_rating.desc() if sort_order == "desc"
                    else MarketAgent.average_rating.asc()
                )
            
            agents = query.all()
            
            # Format response
            agent_list = []
            for agent in agents:
                agent_info = {
                    "id": agent.id,
                    "owner_id": agent.owner_id,
                    "agent_type": agent.agent_type,
                    "rental_price_per_hour": agent.rental_price_per_hour,
                    "min_rental_hours": agent.min_rental_hours,
                    "max_rental_hours": agent.max_rental_hours,
                    "description": agent.description,
                    "experience_points": agent.experience_points,
                    "total_rentals": agent.total_rentals,
                    "total_earnings": agent.total_earnings,
                    "average_rating": agent.average_rating,
                    "created_at": agent.created_at.isoformat()
                }
                
                # Add agent type details
                if agent.agent_type in self.agent_types:
                    agent_type_info = self.agent_types[agent.agent_type]
                    agent_info["agent_details"] = {
                        "name": agent_type_info.name,
                        "description": agent_type_info.description,
                        "base_price": agent_type_info.base_rental_price,
                        "experience_multiplier": agent_type_info.experience_multiplier
                    }
                
                agent_list.append(agent_info)
            
            return {
                "success": True,
                "agents": agent_list,
                "total_count": len(agent_list),
                "filters_applied": {
                    "agent_type": agent_type,
                    "max_price_per_hour": max_price_per_hour,
                    "min_experience_points": min_experience_points,
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_rented_agents(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get agents rented by a user"""
        try:
            db = next(get_db())
            
            # Build query
            query = db.query(AgentRental).filter(AgentRental.renter_id == user_id)
            
            if status:
                query = query.filter(AgentRental.status == status)
            
            rentals = query.order_by(AgentRental.created_at.desc()).all()
            
            rental_list = []
            for rental in rentals:
                # Get agent details
                agent = db.query(MarketAgent).filter(MarketAgent.id == rental.agent_id).first()
                
                rental_info = {
                    "rental_id": rental.id,
                    "agent_id": rental.agent_id,
                    "agent_type": agent.agent_type if agent else "unknown",
                    "rental_duration_hours": rental.rental_duration_hours,
                    "total_cost": rental.total_cost,
                    "payment_method": rental.payment_method,
                    "rental_start_time": rental.rental_start_time.isoformat(),
                    "rental_end_time": rental.rental_end_time.isoformat(),
                    "status": rental.status,
                    "created_at": rental.created_at.isoformat()
                }
                
                # Add time remaining if active
                if rental.status == "active":
                    time_remaining = rental.rental_end_time - datetime.now(timezone.utc)
                    rental_info["time_remaining_hours"] = max(0, time_remaining.total_seconds() / 3600)
                
                rental_list.append(rental_info)
            
            return {
                "success": True,
                "rentals": rental_list,
                "total_count": len(rental_list)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def end_rental(
        self,
        rental_id: str,
        renter_id: str,
        rating: Optional[int] = None,
        review: Optional[str] = None
    ) -> Dict[str, Any]:
        """End an active rental and update agent"""
        try:
            db = next(get_db())
            
            # Get rental
            rental = db.query(AgentRental).filter(
                AgentRental.id == rental_id,
                AgentRental.renter_id == renter_id
            ).first()
            
            if not rental:
                return {"success": False, "error": "Rental not found"}
            
            if rental.status != "active":
                return {"success": False, "error": "Rental is not active"}
            
            # Update rental status
            rental.status = "completed"
            rental.ended_at = datetime.now(timezone.utc)
            
            # Update agent availability and earnings
            agent = db.query(MarketAgent).filter(MarketAgent.id == rental.agent_id).first()
            if agent:
                agent.is_available = True
                agent.total_earnings += rental.total_cost
                
                # Update rating if provided
                if rating and 1 <= rating <= 5:
                    current_total_rating = agent.average_rating * agent.total_rentals
                    new_total_rating = current_total_rating + rating
                    agent.average_rating = new_total_rating / (agent.total_rentals + 1)
            
            db.commit()
            
            return {
                "success": True,
                "rental_id": rental_id,
                "agent_id": rental.agent_id,
                "final_cost": rental.total_cost,
                "rental_duration_actual_hours": (
                    rental.ended_at - rental.rental_start_time
                ).total_seconds() / 3600,
                "rating_submitted": rating is not None,
                "agent_updated": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_market_agent(self, agent_id: str) -> Optional[MarketAgent]:
        """Get market agent by ID"""
        try:
            db = next(get_db())
            return db.query(MarketAgent).filter(MarketAgent.id == agent_id).first()
        except Exception as e:
            print(f"Error getting market agent: {e}")
            return None
    
    async def _get_user_experience_points(self, user_id: str) -> int:
        """Get user's experience points"""
        # This would calculate based on user's activities
        # For now, return mock data
        return 250
    
    async def _get_user_balance(self, user_id: str, payment_method: str) -> float:
        """Get user's balance for specific payment method"""
        # This would integrate with payment system
        # For now, return mock data
        return 1000.0
    
    async def _process_payment(
        self,
        renter_id: str,
        owner_id: str,
        amount: float,
        payment_method: str,
        transaction_type: str
    ) -> Dict[str, Any]:
        """Process payment between users"""
        try:
            # This would integrate with actual payment processors
            # For now, simulate successful payment
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                from_user_id=renter_id,
                to_user_id=owner_id,
                amount=amount,
                payment_method=payment_method,
                transaction_type=transaction_type,
                status="completed",
                created_at=datetime.now(timezone.utc)
            )
            
            db = next(get_db())
            db.add(transaction)
            db.commit()
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "amount": amount,
                "payment_method": payment_method,
                "status": "completed"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_agent_access_token(self, rental_id: str) -> str:
        """Generate access token for rented agent"""
        import secrets
        return secrets.token_urlsafe(32)

# Singleton instance
agent_marketplace = AgentMarketplace()
