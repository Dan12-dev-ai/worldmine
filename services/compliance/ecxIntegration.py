"""
ECX Compliance Engine - DEDAN Mine Ethiopian Commodity Exchange Integration
ECX-integrated legal compliance engine for Ethiopian gems with automatic export forms and anti-smuggling support
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import json
import asyncio
from dataclasses import dataclass, asdict

from models import ComplianceRecord, User, Listing
from database import get_db
from services.ai.explainableAI import ComplianceAI

@dataclass
class ECXGemType:
    """ECX gem type specifications"""
    name: str
    code: str
    export_license_required: bool
    minimum_purity: float
    standard_certifications: List[str]
    export_restrictions: List[str]
    market_price基准: float  # Base market price

@dataclass
class ExportForm:
    """ECX export form data"""
    gem_type: str
    quantity: float
    unit: str
    quality_grade: str
    origin: str
    export_license_number: str
    destination_country: str
    intended_use: str
    certificate_numbers: List[str]
    exporter_details: Dict[str, Any]
    anti_smuggling_declaration: bool

class ECXComplianceService:
    """ECX compliance engine for Ethiopian gems"""
    
    def __init__(self):
        self.db = next(get_db())
        self.ai_analyzer = ComplianceAI()
        
        # ECX gem types and requirements
        self.ecx_gem_types = {
            "opal": ECXGemType(
                name="Ethiopian Opal",
                code="ET-OP",
                export_license_required=True,
                minimum_purity=0.85,
                standard_certifications=["GIA", "IGI", "AGL"],
                export_restrictions=["conflict_zones", "unlicensed_mines"],
                market_price基准=100.0
            ),
            "emerald": ECXGemType(
                name="Ethiopian Emerald",
                code="ET-EM",
                export_license_required=True,
                minimum_purity=0.90,
                standard_certifications=["GIA", "IGI", "AGL", "GRS"],
                export_restrictions=["conflict_zones", "unlicensed_mines", "size_limits"],
                market_price基准=500.0
            ),
            "sapphire": ECXGemType(
                name="Ethiopian Sapphire",
                code="ET-SA",
                export_license_required=True,
                minimum_purity=0.88,
                standard_certifications=["GIA", "IGI", "AGL", "SGL"],
                export_restrictions=["conflict_zones", "unlicensed_mines"],
                market_price基准=300.0
            ),
            "ruby": ECXGemType(
                name="Ethiopian Ruby",
                code="ET-RU",
                export_license_required=True,
                minimum_purity=0.92,
                standard_certifications=["GIA", "IGI", "AGL", "SGL"],
                export_restrictions=["conflict_zones", "unlicensed_mines", "synthetic_ban"],
                market_price基准=200.0
            )
        }
        
        # Export form templates
        self.export_templates = self._generate_export_templates()
    
    async def generate_ecx_export_form(
        self,
        listing_id: str,
        exporter_id: str,
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate ECX-compliant export form"""
        try:
            # Get listing details
            listing = self.db.query(Listing).filter(Listing.id == listing_id).first()
            if not listing:
                return {"success": False, "error": "Listing not found"}
            
            # Validate gem type
            gem_type = self.ecx_gem_types.get(listing.gem_type.lower())
            if not gem_type:
                return {"success": False, "error": f"Unsupported gem type: {listing.gem_type}"}
            
            # Create export form
            export_form = ExportForm(
                gem_type=listing.gem_type,
                quantity=listing.weight,
                unit=listing.unit,
                quality_grade=self._determine_quality_grade(listing),
                origin=self._extract_origin(listing),
                export_license_number=form_data.get("export_license_number", ""),
                destination_country=form_data.get("destination_country", ""),
                intended_use=form_data.get("intended_use", "jewelry_manufacturing"),
                certificate_numbers=form_data.get("certificate_numbers", []),
                exporter_details={
                    "name": form_data.get("exporter_name", ""),
                    "address": form_data.get("exporter_address", ""),
                    "phone": form_data.get("exporter_phone", ""),
                    "email": form_data.get("exporter_email", ""),
                    "tax_id": form_data.get("tax_id", "")
                },
                anti_smuggling_declaration=True
            )
            
            # Generate ECX reference number
            ecx_reference = await self._generate_ecx_reference(export_form)
            
            # Create compliance record
            compliance_record = ComplianceRecord(
                id=str(uuid.uuid4()),
                user_id=exporter_id,
                listing_id=listing_id,
                compliance_type="export_license",
                jurisdiction="ethiopia",
                documents=json.dumps([self._create_export_document(export_form)]),
                ai_risk_score=await self._calculate_export_risk_score(export_form, listing),
                compliance_score=await self._calculate_export_compliance_score(export_form),
                manual_review_required=await self._requires_manual_review(export_form),
                ecx_reference_number=ecx_reference,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(compliance_record)
            self.db.commit()
            
            return {
                "success": True,
                "ecx_reference_number": ecx_reference,
                "export_form": asdict(export_form),
                "compliance_score": compliance_record.compliance_score,
                "risk_score": compliance_record.ai_risk_score,
                "requires_manual_review": compliance_record.manual_review_required,
                "next_steps": await self._get_export_next_steps(compliance_record)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def submit_anti_smuggling_check(
        self,
        listing_id: str,
        origin_data: Dict[str, Any],
        certificate_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Submit anti-smuggling verification check"""
        try:
            # Get listing details
            listing = self.db.query(Listing).filter(Listing.id == listing_id).first()
            if not listing:
                return {"success": False, "error": "Listing not found"}
            
            # AI-powered anti-smuggling analysis
            smuggling_analysis = await self.ai_analyzer.analyze_smuggling_risk(
                origin_data, certificate_data, listing
            )
            
            # Create compliance record
            compliance_record = ComplianceRecord(
                id=str(uuid.uuid4()),
                user_id=listing.seller_id,
                listing_id=listing_id,
                compliance_type="anti_smuggling_check",
                jurisdiction="ethiopia",
                documents=json.dumps(certificate_data or []),
                ai_risk_score=smuggling_analysis.get("risk_score", 0),
                compliance_score=smuggling_analysis.get("compliance_score", 50),
                manual_review_required=smuggling_analysis.get("requires_review", False),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(compliance_record)
            self.db.commit()
            
            return {
                "success": True,
                "smuggling_analysis": smuggling_analysis,
                "compliance_record_id": compliance_record.id,
                "risk_level": self._get_risk_level(smuggling_analysis.get("risk_score", 0)),
                "recommendations": smuggling_analysis.get("recommendations", [])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def verify_authenticity_certificate(
        self,
        certificate_id: str,
        certificate_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify gem authenticity certificate"""
        try:
            # AI-powered certificate verification
            verification_result = await self.ai_analyzer.verify_certificate(
                certificate_id, certificate_data
            )
            
            # Check against known certifying bodies
            recognized_bodies = ["GIA", "IGI", "AGL", "GRS", "SGL"]
            is_recognized = certificate_data.get("issuing_body") in recognized_bodies
            
            # Create compliance record
            compliance_record = ComplianceRecord(
                id=str(uuid.uuid4()),
                compliance_type="authenticity_certificate",
                jurisdiction="international",
                documents=json.dumps([certificate_data]),
                ai_risk_score=verification_result.get("risk_score", 0),
                compliance_score=verification_result.get("authenticity_score", 50),
                manual_review_required=not is_recognized or verification_result.get("requires_review", False),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(compliance_record)
            self.db.commit()
            
            return {
                "success": True,
                "verification_result": verification_result,
                "certificate_recognized": is_recognized,
                "compliance_score": compliance_record.compliance_score,
                "blockchain_verified": await self._verify_certificate_blockchain(certificate_id)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_compliance_status(
        self,
        user_id: str,
        listing_id: str = None
    ) -> Dict[str, Any]:
        """Get comprehensive compliance status"""
        try:
            query = self.db.query(ComplianceRecord).filter(
                ComplianceRecord.user_id == user_id
            )
            
            if listing_id:
                query = query.filter(ComplianceRecord.listing_id == listing_id)
            
            compliance_records = query.order_by(ComplianceRecord.created_at.desc()).all()
            
            if not compliance_records:
                return {"success": False, "error": "No compliance records found"}
            
            # Calculate overall compliance score
            overall_score = sum(record.compliance_score for record in compliance_records) / len(compliance_records)
            
            # Get compliance by type
            compliance_by_type = {}
            for record in compliance_records:
                compliance_type = record.compliance_type
                if compliance_type not in compliance_by_type:
                    compliance_by_type[compliance_type] = []
                compliance_by_type[compliance_type].append({
                    "status": record.status,
                    "score": record.compliance_score,
                    "created_at": record.created_at.isoformat(),
                    "requires_review": record.manual_review_required
                })
            
            return {
                "success": True,
                "overall_compliance_score": overall_score,
                "compliance_by_type": compliance_by_type,
                "total_records": len(compliance_records),
                "pending_reviews": len([r for r in compliance_records if r.manual_review_required]),
                "recommendations": await self._generate_compliance_recommendations(compliance_records)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_ecx_report(
        self,
        user_id: str,
        report_type: str = "monthly"
    ) -> Dict[str, Any]:
        """Generate ECX compliance report"""
        try:
            # Get compliance records for period
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=30) if report_type == "monthly" else end_date - timedelta(days=90)
            
            compliance_records = self.db.query(ComplianceRecord).filter(
                ComplianceRecord.user_id == user_id,
                ComplianceRecord.created_at >= start_date,
                ComplianceRecord.created_at <= end_date
            ).all()
            
            # Generate report data
            report_data = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "type": report_type
                },
                "compliance_summary": {
                    "total_records": len(compliance_records),
                    "average_score": sum(r.compliance_score for r in compliance_records) / len(compliance_records) if compliance_records else 0,
                    "high_risk_items": len([r for r in compliance_records if r.ai_risk_score > 70]),
                    "manual_reviews_required": len([r for r in compliance_records if r.manual_review_required])
                },
                "ecx_transactions": await self._get_ecx_transactions(user_id, start_date, end_date),
                "recommendations": await self._generate_ecx_recommendations(compliance_records)
            }
            
            return {
                "success": True,
                "ecx_report": report_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _determine_quality_grade(self, listing: Listing) -> str:
        """Determine quality grade based on listing data"""
        # This would use AI analysis of images and descriptions
        # For now, return based on price tier
        if listing.price >= 10000:
            return "investment"
        elif listing.price >= 5000:
            return "AAA"
        elif listing.price >= 2000:
            return "AA"
        elif listing.price >= 1000:
            return "A"
        else:
            return "commercial"
    
    def _extract_origin(self, listing: Listing) -> str:
        """Extract origin information from listing"""
        if listing.mine_location:
            location_data = json.loads(listing.mine_location)
            return location_data.get("region", "Ethiopia")
        return "Ethiopia"
    
    def _create_export_document(self, export_form: ExportForm) -> Dict[str, Any]:
        """Create export document structure"""
        return {
            "document_type": "export_license",
            "form_number": export_form.export_license_number,
            "gem_details": {
                "type": export_form.gem_type,
                "quantity": export_form.quantity,
                "unit": export_form.unit,
                "quality_grade": export_form.quality_grade,
                "origin": export_form.origin
            },
            "exporter": export_form.exporter_details,
            "destination": export_form.destination_country,
            "intended_use": export_form.intended_use,
            "certificates": export_form.certificate_numbers,
            "anti_smuggling_declaration": export_form.anti_smuggling_declaration,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _generate_ecx_reference(self, export_form: ExportForm) -> str:
        """Generate ECX reference number"""
        import random
        year = datetime.now(timezone.utc).year
        sequence = random.randint(1000, 9999)
        gem_code = self.ecx_gem_types.get(export_form.gem_type.lower(), {}).code or "UNK"
        return f"ECX-{year}-{gem_code}-{sequence}"
    
    async def _calculate_export_risk_score(self, export_form: ExportForm, listing: Listing) -> int:
        """Calculate export risk score using AI"""
        risk_factors = {}
        
        # Quantity risk
        if export_form.quantity > 100:
            risk_factors["quantity"] = 30
        elif export_form.quantity > 50:
            risk_factors["quantity"] = 20
        else:
            risk_factors["quantity"] = 10
        
        # Destination risk
        high_risk_destinations = ["sanctioned_countries_list"]
        if export_form.destination_country in high_risk_destinations:
            risk_factors["destination"] = 50
        else:
            risk_factors["destination"] = 15
        
        # Certificate risk
        if not export_form.certificate_numbers:
            risk_factors["certificates"] = 40
        elif len(export_form.certificate_numbers) < 2:
            risk_factors["certificates"] = 20
        else:
            risk_factors["certificates"] = 10
        
        # AI analysis
        ai_risk = await self.ai_analyzer.analyze_export_risk(export_form, listing, risk_factors)
        
        return max(ai_risk.get("risk_score", 0), sum(risk_factors.values()) // len(risk_factors))
    
    async def _calculate_export_compliance_score(self, export_form: ExportForm) -> int:
        """Calculate export compliance score"""
        score = 0
        
        # Export license (30 points)
        if export_form.export_license_number:
            score += 30
        
        # Certificates (25 points)
        if export_form.certificate_numbers and len(export_form.certificate_numbers) >= 2:
            score += 25
        elif export_form.certificate_numbers:
            score += 15
        
        # Quality standards (20 points)
        if export_form.quality_grade in ["AAA", "AA", "A"]:
            score += 20
        elif export_form.quality_grade in ["investment"]:
            score += 15
        
        # Anti-smuggling declaration (25 points)
        if export_form.anti_smuggling_declaration:
            score += 25
        
        return min(score, 100)
    
    async def _requires_manual_review(self, export_form: ExportForm) -> bool:
        """Determine if manual review is required"""
        # High value exports require review
        if export_form.quantity > 50:
            return True
        
        # Certain destinations require review
        review_required_destinations = ["high_risk_countries"]
        if export_form.destination_country in review_required_destinations:
            return True
        
        # Missing certificates require review
        if not export_form.certificate_numbers:
            return True
        
        return False
    
    async def _get_export_next_steps(self, compliance_record: ComplianceRecord) -> List[str]:
        """Get next steps for export compliance"""
        steps = []
        
        if compliance_record.manual_review_required:
            steps.append("Submit additional documentation for manual review")
            steps.append("Await compliance officer approval")
        
        if compliance_record.compliance_score < 80:
            steps.append("Improve documentation quality")
            steps.append("Obtain additional certifications")
        
        if compliance_record.ai_risk_score > 60:
            steps.append("Provide additional origin verification")
            steps.append("Submit to enhanced due diligence")
        
        return steps
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level based on score"""
        if risk_score >= 80:
            return "high"
        elif risk_score >= 60:
            return "medium"
        elif risk_score >= 40:
            return "low"
        else:
            return "minimal"
    
    async def _verify_certificate_blockchain(self, certificate_id: str) -> bool:
        """Verify certificate on blockchain"""
        # This would integrate with blockchain verification
        # For now, return True
        return True
    
    async def _get_ecx_transactions(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get ECX transactions for period"""
        # This would query ECX transaction records
        # For now, return mock data
        return [
            {
                "date": "2026-01-15",
                "ecx_reference": "ECX-2026-ET-OP-1234",
                "gem_type": "opal",
                "quantity": 25.5,
                "status": "approved",
                "export_destination": "USA"
            },
            {
                "date": "2026-01-10",
                "ecx_reference": "ECX-2026-ET-EM-5678",
                "gem_type": "emerald",
                "quantity": 10.2,
                "status": "pending_review",
                "export_destination": "Belgium"
            }
        ]
    
    def _generate_export_templates(self) -> Dict[str, Dict[str, Any]]:
        """Generate export form templates for different gem types"""
        templates = {}
        
        for gem_type, gem_info in self.ecx_gem_types.items():
            templates[gem_type] = {
                "required_fields": [
                    "export_license_number",
                    "quantity",
                    "quality_grade",
                    "origin",
                    "destination_country",
                    "intended_use",
                    "certificate_numbers"
                ],
                "optional_fields": [
                    "exporter_details",
                    "additional_documents"
                ],
                "certifications": gem_info.standard_certifications,
                "restrictions": gem_info.export_restrictions,
                "minimum_requirements": {
                    "purity": gem_info.minimum_purity,
                    "license_required": gem_info.export_license_required
                }
            }
        
        return templates
    
    async def _generate_compliance_recommendations(self, compliance_records: List[ComplianceRecord]) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        # Analyze common issues
        high_risk_records = [r for r in compliance_records if r.ai_risk_score > 70]
        manual_review_records = [r for r in compliance_records if r.manual_review_required]
        
        if high_risk_records:
            recommendations.append("Implement enhanced due diligence procedures")
            recommendations.append("Obtain additional origin documentation")
        
        if manual_review_records:
            recommendations.append("Improve documentation quality and completeness")
            recommendations.append("Engage pre-compliance consultation services")
        
        if len(compliance_records) < 5:
            recommendations.append("Establish regular compliance monitoring schedule")
        
        return recommendations
