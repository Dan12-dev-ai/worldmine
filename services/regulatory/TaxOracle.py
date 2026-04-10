"""
DEDAN Mine - Tax Oracle Service
Automated tax calculation and compliance for Ethiopian mining operations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass

class MineralType(Enum):
    """Mineral types for tax calculation"""
    GOLD = "gold"
    DIAMOND = "diamond"
    PLATINUM = "platinum"
    TANTALUM = "tantalum"
    RARE_EARTH = "rare_earth"

class TaxJurisdiction(Enum):
    """Tax jurisdictions"""
    ETHIOPIA_LOCAL = "ethiopia_local"
    INTERNATIONAL_EXPORT = "international_export"
    USA_IMPORT = "usa_import"

@dataclass
class TaxRate:
    """Tax rate configuration"""
    jurisdiction: TaxJurisdiction
    mineral_type: MineralType
    rate_type: str  # percentage, fixed, tiered
    rate_value: float
    currency: str
    effective_from: datetime
    effective_to: Optional[datetime]
    conditions: Dict[str, Any]

@dataclass
class TaxCalculation:
    """Tax calculation result"""
    transaction_id: str
    mineral_type: MineralType
    amount: float
    jurisdiction: str
    tax_rate: float
    tax_amount: float
    net_amount: float
    calculated_at: datetime
    compliance_notes: List[str]

class TaxOracle:
    """Tax Oracle for automated tax calculation and compliance"""
    
    def __init__(self):
        self.tax_rates: Dict[str, TaxRate] = {}
        self.tax_calculations: Dict[str, TaxCalculation] = {}
        
        # Tax calculation parameters
        self.ethiopian_royalty_rates = {
            MineralType.GOLD: {"rate": 0.05, "type": "percentage", "min_threshold": 1000},  # 5% royalty
            MineralType.DIAMOND: {"rate": 0.08, "type": "percentage", "min_threshold": 100},   # 8% royalty
            MineralType.PLATINUM: {"rate": 0.06, "type": "percentage", "min_threshold": 500},  # 6% royalty
            MineralType.TANTALUM: {"rate": 0.04, "type": "percentage", "min_threshold": 2000}, # 4% royalty
            MineralType.RARE_EARTH: {"rate": 0.07, "type": "percentage", "min_threshold": 100}  # 7% royalty
        }
        
        self.export_duty_rates = {
            MineralType.GOLD: {"rate": 0.02, "type": "percentage", "destination": "international"},
            MineralType.DIAMOND: {"rate": 0.03, "type": "percentage", "destination": "international"},
            MineralType.PLATINUM: {"rate": 0.025, "type": "percentage", "destination": "international"},
            MineralType.RARE_EARTH: {"rate": 0.035, "type": "percentage", "destination": "international"}
        }
        
        # International tax treaties
        self.tax_treaties = {
            "US_ETHIOPIA": {"withholding_tax": 0.15, "tax_treaty": True},
            "EU_ETHIOPIA": {"withholding_tax": 0.10, "tax_treaty": True},
            "CHINA_ETHIOPIA": {"withholding_tax": 0.20, "tax_treaty": True}
        }
        
        # Initialize tax rates
        self._initialize_tax_rates()
    
    def _initialize_tax_rates(self):
        """Initialize all tax rates"""
        # Ethiopian royalty rates
        for mineral_type, config in self.ethiopian_royalty_rates.items():
            tax_rate = TaxRate(
                jurisdiction=TaxJurisdiction.ETHIOPIA_LOCAL,
                mineral_type=mineral_type,
                rate_type=config["type"],
                rate_value=config["rate"],
                currency="ETB",
                effective_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
                effective_to=None,
                conditions={"min_threshold": config["min_threshold"]}
            )
            self.tax_rates[f"ethiopia_{mineral_type.value}"] = tax_rate
        
        # International export duty rates
        for mineral_type, config in self.export_duty_rates.items():
            tax_rate = TaxRate(
                jurisdiction=TaxJurisdiction.INTERNATIONAL_EXPORT,
                mineral_type=mineral_type,
                rate_type=config["type"],
                rate_value=config["rate"],
                currency="USD",
                effective_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
                effective_to=None,
                conditions={"destination": config["destination"]}
            )
            self.tax_rates[f"export_{mineral_type.value}"] = tax_rate
    
    async def calculate_transaction_taxes(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all applicable taxes for a transaction"""
        try:
            mineral_type = MineralType(transaction_data.get("mineral_type", "gold"))
            amount = float(transaction_data.get("amount", 0))
            jurisdiction = transaction_data.get("jurisdiction", "ethiopia_local")
            
            # Get applicable tax rate
            tax_rate_key = f"{jurisdiction}_{mineral_type.value}"
            tax_rate = self.tax_rates.get(tax_rate_key)
            
            if not tax_rate:
                return {"error": f"No tax rate found for {tax_rate_key}"}
            
            # Calculate tax amount
            if tax_rate.rate_type == "percentage":
                tax_amount = amount * tax_rate.rate_value
            else:
                tax_amount = tax_rate.rate_value
            
            net_amount = amount - tax_amount
            
            # Store calculation
            calculation = TaxCalculation(
                transaction_id=transaction_data.get("transaction_id", ""),
                mineral_type=mineral_type,
                amount=amount,
                jurisdiction=jurisdiction,
                tax_rate=tax_rate.rate_value,
                tax_amount=tax_amount,
                net_amount=net_amount,
                calculated_at=datetime.now(timezone.utc),
                compliance_notes=[]
            )
            
            self.tax_calculations[transaction_data.get("transaction_id", "")] = calculation
            
            return {
                "success": True,
                "tax_amount": tax_amount,
                "net_amount": net_amount,
                "tax_rate": tax_rate.rate_value,
                "jurisdiction": jurisdiction
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global tax oracle instance
tax_oracle = TaxOracle()
