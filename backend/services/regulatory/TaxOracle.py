"""
Tax Oracle Service - DEDAN Mine Regulatory Compliance
Automatically calculates local Ethiopian royalties and international export duties
Integrates with global tax compliance frameworks for institutional trading
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import json
import uuid
import asyncio
import math
from dataclasses import dataclass
from enum import Enum

class TaxJurisdiction(Enum):
    """Tax jurisdiction types"""
    ETHIOPIA_LOCAL = "ethiopia_local"
    INTERNATIONAL_EXPORT = "international_export"
    IMPORT_COUNTRY = "import_country"
    TRANSIT_COUNTRY = "transit_country"
    SPECIAL_ECONOMIC_ZONE = "special_economic_zone"

class MineralType(Enum):
    """Mineral types for tax calculation"""
    GOLD = "gold"
    DIAMOND = "diamond"
    PLATINUM = "platinum"
    SILVER = "silver"
    RARE_EARTH = "rare_earth"
    COPPER = "copper"
    IRON_ORE = "iron_ore"
    TANTALUM = "tantalum"

@dataclass
class TaxRate:
    """Tax rate configuration"""
    jurisdiction: TaxJurisdiction
    mineral_type: MineralType
    rate_type: str  # "percentage", "per_ounce", "per_carat", "fixed"
    rate_value: float
    currency: str
    effective_from: datetime
    effective_to: Optional[datetime]
    conditions: Dict[str, Any]

@dataclass
class TaxCalculation:
    """Tax calculation result"""
    calculation_id: str
    transaction_id: str
    jurisdiction: TaxJurisdiction
    mineral_type: MineralType
    quantity: float
    unit_price: float
    total_value: float
    tax_amount: float
    tax_rate: float
    currency: str
    calculated_at: datetime
    compliance_notes: List[str]

class TaxOracle:
    """Tax Oracle for automated tax calculation and compliance"""
    
    def __init__(self):
        self.tax_rates: Dict[str, TaxRate] = {}
        self.tax_calculations: Dict[str, TaxCalculation] = {}
        
        # Initialize tax rates
        self._initialize_tax_rates()
        
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
            MineralType.TANTALUM: {"rate": 0.015, "type": "percentage", "destination": "international"},
            MineralType.RARE_EARTH: {"rate": 0.035, "type": "percentage", "destination": "international"}
        }
        
        # International tax treaties
        self.tax_treaties = {
            "USA": {"withholding_rate": 0.15, "treaty_benefits": True},
            "UK": {"withholding_rate": 0.12, "treaty_benefits": True},
            "CHINA": {"withholding_rate": 0.10, "treaty_benefits": True},
            "GERMANY": {"withholding_rate": 0.12, "treaty_benefits": True},
            "UAE": {"withholding_rate": 0.05, "treaty_benefits": True},
            "SINGAPORE": {"withholding_rate": 0.08, "treaty_benefits": True}
        }
        
        # Special economic zones
        self.sez_benefits = {
            "ETHIOPIA_SEZ": {"tax_holiday": 10, "reduced_rate": 0.01},
            "Djibouti_SEZ": {"tax_holiday": 15, "reduced_rate": 0.005},
            "Kenya_SEZ": {"tax_holiday": 8, "reduced_rate": 0.015}
        }
    
    def _initialize_tax_rates(self):
        """Initialize tax rate database"""
        # Ethiopian local tax rates
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
            transaction_id = transaction_data["transaction_id"]
            mineral_type = MineralType(transaction_data["mineral_type"])
            quantity = transaction_data["quantity"]
            unit_price = transaction_data["unit_price"]
            total_value = quantity * unit_price
            
            # Origin and destination
            origin_country = transaction_data.get("origin_country", "Ethiopia")
            destination_country = transaction_data.get("destination_country")
            transit_countries = transaction_data.get("transit_countries", [])
            
            # Special conditions
            is_sez = transaction_data.get("special_economic_zone", False)
            sez_type = transaction_data.get("sez_type")
            
            tax_calculations = []
            total_tax_amount = 0.0
            compliance_notes = []
            
            # Step 1: Ethiopian local royalties
            if origin_country.lower() == "ethiopia":
                ethiopian_tax = await self._calculate_ethiopian_royalty(
                    transaction_id, mineral_type, quantity, unit_price, total_value
                )
                tax_calculations.append(ethiopian_tax)
                total_tax_amount += ethiopian_tax.tax_amount
                compliance_notes.extend(ethiopian_tax.compliance_notes)
            
            # Step 2: Export duties
            export_tax = await self._calculate_export_duty(
                transaction_id, mineral_type, quantity, unit_price, total_value, destination_country
            )
            tax_calculations.append(export_tax)
            total_tax_amount += export_tax.tax_amount
            compliance_notes.extend(export_tax.compliance_notes)
            
            # Step 3: Transit country taxes
            for transit_country in transit_countries:
                transit_tax = await self._calculate_transit_tax(
                    transaction_id, mineral_type, quantity, unit_price, total_value, transit_country
                )
                tax_calculations.append(transit_tax)
                total_tax_amount += transit_tax.tax_amount
                compliance_notes.extend(transit_tax.compliance_notes)
            
            # Step 4: Import country taxes
            if destination_country:
                import_tax = await self._calculate_import_tax(
                    transaction_id, mineral_type, quantity, unit_price, total_value, destination_country
                )
                tax_calculations.append(import_tax)
                total_tax_amount += import_tax.tax_amount
                compliance_notes.extend(import_tax.compliance_notes)
            
            # Step 5: Apply SEZ benefits if applicable
            if is_sez and sez_type:
                sez_adjustment = await self._apply_sez_benefits(
                    tax_calculations, sez_type, origin_country
                )
                total_tax_amount = sez_adjustment["adjusted_total"]
                compliance_notes.append(f"SEZ benefits applied: {sez_type}")
            
            # Step 6: Generate tax compliance report
            compliance_report = await self._generate_compliance_report(
                transaction_data, tax_calculations, total_tax_amount
            )
            
            # Store calculations
            for calc in tax_calculations:
                self.tax_calculations[calc.calculation_id] = calc
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "total_tax_amount": total_tax_amount,
                "tax_calculations": [
                    {
                        "calculation_id": calc.calculation_id,
                        "jurisdiction": calc.jurisdiction.value,
                        "mineral_type": calc.mineral_type.value,
                        "tax_amount": calc.tax_amount,
                        "tax_rate": calc.tax_rate,
                        "currency": calc.currency,
                        "compliance_notes": calc.compliance_notes
                    }
                    for calc in tax_calculations
                ],
                "compliance_report": compliance_report,
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_ethiopian_royalty(self, transaction_id: str, mineral_type: MineralType, 
                                         quantity: float, unit_price: float, total_value: float) -> TaxCalculation:
        """Calculate Ethiopian royalty taxes"""
        royalty_config = self.ethiopian_royalty_rates[mineral_type]
        tax_rate = royalty_config["rate"]
        
        # Check minimum threshold
        if total_value < royalty_config["min_threshold"]:
            tax_amount = 0.0
            compliance_notes = [f"Below minimum threshold of ${royalty_config['min_threshold']}"]
        else:
            tax_amount = total_value * tax_rate
            compliance_notes = [f"Ethiopian royalty applied at {tax_rate*100:.1f}%"]
        
        return TaxCalculation(
            calculation_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            jurisdiction=TaxJurisdiction.ETHIOPIA_LOCAL,
            mineral_type=mineral_type,
            quantity=quantity,
            unit_price=unit_price,
            total_value=total_value,
            tax_amount=tax_amount,
            tax_rate=tax_rate,
            currency="ETB",
            calculated_at=datetime.now(timezone.utc),
            compliance_notes=compliance_notes
        )
    
    async def _calculate_export_duty(self, transaction_id: str, mineral_type: MineralType,
                                   quantity: float, unit_price: float, total_value: float,
                                   destination_country: str) -> TaxCalculation:
        """Calculate export duties"""
        export_config = self.export_duty_rates[mineral_type]
        tax_rate = export_config["rate"]
        
        # Check for treaty benefits
        treaty_benefits = self.tax_treaties.get(destination_country, {})
        if treaty_benefits.get("treaty_benefits", False):
            # Apply reduced rate for treaty countries
            tax_rate = min(tax_rate, treaty_benefits["withholding_rate"])
            compliance_notes = [f"Export duty with treaty benefits for {destination_country} at {tax_rate*100:.1f}%"]
        else:
            compliance_notes = [f"Standard export duty at {tax_rate*100:.1f}%"]
        
        tax_amount = total_value * tax_rate
        
        return TaxCalculation(
            calculation_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            jurisdiction=TaxJurisdiction.INTERNATIONAL_EXPORT,
            mineral_type=mineral_type,
            quantity=quantity,
            unit_price=unit_price,
            total_value=total_value,
            tax_amount=tax_amount,
            tax_rate=tax_rate,
            currency="USD",
            calculated_at=datetime.now(timezone.utc),
            compliance_notes=compliance_notes
        )
    
    async def _calculate_transit_tax(self, transaction_id: str, mineral_type: MineralType,
                                    quantity: float, unit_price: float, total_value: float,
                                    transit_country: str) -> TaxCalculation:
        """Calculate transit country taxes"""
        # Mock transit tax calculation
        transit_tax_rates = {
            "Djibouti": 0.005,  # 0.5%
            "Kenya": 0.008,     # 0.8%
            "Sudan": 0.01,      # 1.0%
            "Eritrea": 0.012    # 1.2%
        }
        
        tax_rate = transit_tax_rates.get(transit_country, 0.01)  # Default 1%
        tax_amount = total_value * tax_rate
        
        return TaxCalculation(
            calculation_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            jurisdiction=TaxJurisdiction.TRANSIT_COUNTRY,
            mineral_type=mineral_type,
            quantity=quantity,
            unit_price=unit_price,
            total_value=total_value,
            tax_amount=tax_amount,
            tax_rate=tax_rate,
            currency="USD",
            calculated_at=datetime.now(timezone.utc),
            compliance_notes=[f"Transit tax for {transit_country} at {tax_rate*100:.1f}%"]
        )
    
    async def _calculate_import_tax(self, transaction_id: str, mineral_type: MineralType,
                                   quantity: float, unit_price: float, total_value: float,
                                   destination_country: str) -> TaxCalculation:
        """Calculate import country taxes"""
        # Mock import tax calculation
        import_tax_rates = {
            "USA": 0.05,       # 5%
            "UK": 0.20,        # 20% VAT
            "Germany": 0.19,    # 19% VAT
            "China": 0.13,     # 13% VAT
            "UAE": 0.05,       # 5%
            "Singapore": 0.07   # 7% GST
        }
        
        tax_rate = import_tax_rates.get(destination_country, 0.15)  # Default 15%
        tax_amount = total_value * tax_rate
        
        return TaxCalculation(
            calculation_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            jurisdiction=TaxJurisdiction.IMPORT_COUNTRY,
            mineral_type=mineral_type,
            quantity=quantity,
            unit_price=unit_price,
            total_value=total_value,
            tax_amount=tax_amount,
            tax_rate=tax_rate,
            currency="USD",
            calculated_at=datetime.now(timezone.utc),
            compliance_notes=[f"Import tax for {destination_country} at {tax_rate*100:.1f}%"]
        )
    
    async def _apply_sez_benefits(self, tax_calculations: List[TaxCalculation], 
                                sez_type: str, origin_country: str) -> Dict[str, Any]:
        """Apply Special Economic Zone benefits"""
        sez_config = self.sez_benefits.get(sez_type, {})
        
        if not sez_config:
            return {"adjusted_total": sum(calc.tax_amount for calc in tax_calculations)}
        
        # Apply tax holiday or reduced rate
        if sez_config.get("tax_holiday", 0) > 0:
            # Full tax holiday
            adjusted_total = 0.0
            for calc in tax_calculations:
                calc.tax_amount = 0.0
                calc.compliance_notes.append(f"Tax holiday applied for {sez_type}")
        else:
            # Reduced rate
            reduced_rate = sez_config.get("reduced_rate", 0.01)
            adjusted_total = 0.0
            for calc in tax_calculations:
                if calc.jurisdiction == TaxJurisdiction.ETHIOPIA_LOCAL:
                    calc.tax_amount = calc.total_value * reduced_rate
                    calc.compliance_notes.append(f"Reduced rate {reduced_rate*100:.1f}% for {sez_type}")
                adjusted_total += calc.tax_amount
        
        return {"adjusted_total": adjusted_total, "sez_benefits_applied": True}
    
    async def _generate_compliance_report(self, transaction_data: Dict[str, Any],
                                         tax_calculations: List[TaxCalculation],
                                         total_tax_amount: float) -> Dict[str, Any]:
        """Generate comprehensive tax compliance report"""
        return {
            "transaction_id": transaction_data["transaction_id"],
            "total_transaction_value": transaction_data["quantity"] * transaction_data["unit_price"],
            "total_tax_amount": total_tax_amount,
            "effective_tax_rate": total_tax_amount / (transaction_data["quantity"] * transaction_data["unit_price"]),
            "tax_breakdown": [
                {
                    "jurisdiction": calc.jurisdiction.value,
                    "tax_amount": calc.tax_amount,
                    "tax_rate": calc.tax_rate,
                    "currency": calc.currency
                }
                for calc in tax_calculations
            ],
            "compliance_status": "compliant",
            "compliance_notes": [note for calc in tax_calculations for note in calc.compliance_notes],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_tax_rates(self, jurisdiction: Optional[str] = None, 
                          mineral_type: Optional[str] = None) -> Dict[str, Any]:
        """Get current tax rates"""
        rates = []
        
        for rate_id, tax_rate in self.tax_rates.items():
            if jurisdiction and tax_rate.jurisdiction.value != jurisdiction:
                continue
            if mineral_type and tax_rate.mineral_type.value != mineral_type:
                continue
            
            rates.append({
                "rate_id": rate_id,
                "jurisdiction": tax_rate.jurisdiction.value,
                "mineral_type": tax_rate.mineral_type.value,
                "rate_type": tax_rate.rate_type,
                "rate_value": tax_rate.rate_value,
                "currency": tax_rate.currency,
                "effective_from": tax_rate.effective_from.isoformat(),
                "effective_to": tax_rate.effective_to.isoformat() if tax_rate.effective_to else None,
                "conditions": tax_rate.conditions
            })
        
        return {
            "success": True,
            "tax_rates": rates,
            "total_rates": len(rates)
        }
    
    async def update_tax_rate(self, rate_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update tax rate (admin function)"""
        try:
            rate_id = rate_update["rate_id"]
            new_rate_value = rate_update["new_rate_value"]
            effective_from = datetime.fromisoformat(rate_update["effective_from"])
            
            if rate_id in self.tax_rates:
                tax_rate = self.tax_rates[rate_id]
                tax_rate.rate_value = new_rate_value
                tax_rate.effective_from = effective_from
                
                return {
                    "success": True,
                    "message": f"Tax rate {rate_id} updated to {new_rate_value}",
                    "effective_from": effective_from.isoformat()
                }
            else:
                return {"success": False, "error": "Tax rate not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_tax_calculation_history(self, transaction_id: str) -> Dict[str, Any]:
        """Get tax calculation history for a transaction"""
        calculations = [
            calc for calc in self.tax_calculations.values()
            if calc.transaction_id == transaction_id
        ]
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "calculations": [
                {
                    "calculation_id": calc.calculation_id,
                    "jurisdiction": calc.jurisdiction.value,
                    "mineral_type": calc.mineral_type.value,
                    "tax_amount": calc.tax_amount,
                    "tax_rate": calc.tax_rate,
                    "currency": calc.currency,
                    "calculated_at": calc.calculated_at.isoformat(),
                    "compliance_notes": calc.compliance_notes
                }
                for calc in calculations
            ],
            "total_calculations": len(calculations)
        }

# Singleton instance
tax_oracle = TaxOracle()
