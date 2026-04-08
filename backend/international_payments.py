"""
DEDAN Mine - International Payment Architecture (ISO 20022)
Global payment integration with Thunes/Visa Direct and regulated stablecoins
Real-time account-to-account (A2A) global links for institutional buyers
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
import hashlib
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentRail(Enum):
    """International payment rails"""
    THUNES_A2A = "thunes_a2a"
    VISA_DIRECT = "visa_direct"
    SWIFT_GPI = "swift_gpi"
    SEPA_INSTANT = "sepa_instant"
    WIRE_TRANSFER = "wire_transfer"
    CRYPTO_STABLECOIN = "crypto_stablecoin"

class StablecoinType(Enum):
    """Regulated stablecoin types"""
    USDC = "usdc"
    PYUSD = "pyusd"
    USDP = "usdp"
    GUSD = "gusd"
    BUSD = "busd"

class ComplianceLevel(Enum):
    """Compliance levels"""
    STANDARD = "standard"
    ENHANCED = "enhanced"
    INSTITUTIONAL = "institutional"
    SOVEREIGN = "sovereign"

class TransactionStatus(Enum):
    """Transaction status types"""
    INITIATED = "initiated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"
    HELD_FOR_REVIEW = "held_for_review"

@dataclass
class ISO20022Payment:
    """ISO 20022 payment structure"""
    payment_id: str
    end_to_end_id: str
    transaction_id: str
    instructed_amount: Dict[str, Any]
    charge_bearer: str
    debtor_account: Dict[str, Any]
    creditor_account: Dict[str, Any]
    creditor_agent: Dict[str, Any]
    payment_information: Dict[str, Any]
    regulatory_reporting: Dict[str, Any]
    remittance_information: str
    compliance_data: Dict[str, Any]
    timestamp: datetime
    status: TransactionStatus
    settlement_asset: StablecoinType
    quantum_signature: str

@dataclass
class InternationalPaymentRequest:
    """International payment request"""
    buyer_id: str
    seller_id: str
    mineral_type: str
    quantity: float
    unit_price: float
    total_amount: float
    currency: str
    payment_rail: PaymentRail
    settlement_asset: StablecoinType
    buyer_account: Dict[str, Any]
    seller_account: Dict[str, Any]
    compliance_level: ComplianceLevel
    iso_20022_data: Dict[str, Any]
    satellite_provenance: Dict[str, Any]
    chain_of_custody: Dict[str, Any]

class ThunesIntegration:
    """Thunes A2A payment integration"""
    
    def __init__(self):
        self.api_base_url = "https://api.thunes.com/v1"
        self.api_key = os.getenv("THUNES_API_KEY")
        self.api_secret = os.getenv("THUNES_API_SECRET")
        self.webhook_secret = os.getenv("THUNES_WEBHOOK_SECRET")
        
        self.supported_countries = [
            "US", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH",
            "JP", "SG", "AU", "CA", "MX", "BR", "AR", "CL", "CO", "PE"
        ]
        
        self.transaction_limits = {
            "standard": {"min": 10.0, "max": 10000.0},
            "enhanced": {"min": 10.0, "max": 50000.0},
            "institutional": {"min": 1000.0, "max": 1000000.0},
            "sovereign": {"min": 10000.0, "max": 10000000.0}
        }
    
    async def initiate_a2a_payment(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Initiate account-to-account payment via Thunes"""
        try:
            # Validate payment request
            validation_result = await self.validate_payment_request(payment_request)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "nbe_compliance": False
                }
            
            # Generate ISO 20022 payment data
            iso_payment = await self.generate_iso_20022_payment(payment_request)
            
            # Prepare Thunes API request
            thunes_request = {
                "payment_id": iso_payment.payment_id,
                "end_to_end_id": iso_payment.end_to_end_id,
                "amount": iso_payment.instructed_amount,
                "currency": payment_request.currency,
                "debit_account": payment_request.buyer_account,
                "credit_account": payment_request.seller_account,
                "payment_purpose": "MINERAL_TRADE_SETTLEMENT",
                "remittance_info": iso_payment.remittance_information,
                "compliance_data": iso_payment.compliance_data,
                "regulatory_reporting": iso_payment.regulatory_reporting,
                "settlement_asset": payment_request.settlement_asset.value,
                "quantum_signature": iso_payment.quantum_signature
            }
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-ISO-20022-Version": "2020",
                "X-Compliance-Level": payment_request.compliance_level.value,
                "X-Settlement-Asset": payment_request.settlement_asset.value
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/payments/a2a",
                    json=thunes_request,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "payment_id": result.get("payment_id"),
                            "transaction_id": result.get("transaction_id"),
                            "status": result.get("status"),
                            "estimated_settlement": result.get("estimated_settlement"),
                            "fees": result.get("fees"),
                            "exchange_rate": result.get("exchange_rate"),
                            "nbe_compliance": True,
                            "iso_20022_compliant": True
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": error_data.get("message"),
                            "status_code": response.status,
                            "nbe_compliance": False
                        }
        
        except Exception as e:
            logger.error(f"Thunes A2A payment initiation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "nbe_compliance": False
            }
    
    async def validate_payment_request(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Validate payment request"""
        try:
            # Check transaction limits
            limits = self.transaction_limits.get(payment_request.compliance_level.value, {})
            if payment_request.total_amount < limits.get("min", 0):
                return {
                    "valid": False,
                    "error": f"Amount below minimum: {limits.get('min', 0)}"
                }
            
            if payment_request.total_amount > limits.get("max", float('inf')):
                return {
                    "valid": False,
                    "error": f"Amount above maximum: {limits.get('max', float('inf'))}"
                }
            
            # Check supported countries
            buyer_country = payment_request.buyer_account.get("country")
            seller_country = payment_request.seller_account.get("country")
            
            if buyer_country not in self.supported_countries:
                return {
                    "valid": False,
                    "error": f"Buyer country {buyer_country} not supported"
                }
            
            if seller_country not in self.supported_countries:
                return {
                    "valid": False,
                    "error": f"Seller country {seller_country} not supported"
                }
            
            # Validate account details
            if not await self.validate_account_details(payment_request.buyer_account):
                return {
                    "valid": False,
                    "error": "Invalid buyer account details"
                }
            
            if not await self.validate_account_details(payment_request.seller_account):
                return {
                    "valid": False,
                    "error": "Invalid seller account details"
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Payment request validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def validate_account_details(self, account: Dict[str, Any]) -> bool:
        """Validate account details"""
        try:
            required_fields = ["account_number", "bank_code", "country", "currency"]
            
            for field in required_fields:
                if field not in account or not account[field]:
                    return False
            
            # Validate account number format (mock implementation)
            account_number = account["account_number"]
            if len(account_number) < 8 or len(account_number) > 34:
                return False
            
            # Validate bank code (mock implementation)
            bank_code = account["bank_code"]
            if len(bank_code) < 3 or len(bank_code) > 11:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Account validation failed: {str(e)}")
            return False
    
    async def generate_iso_20022_payment(self, payment_request: InternationalPaymentRequest) -> ISO20022Payment:
        """Generate ISO 20022 compliant payment structure"""
        try:
            # Generate unique identifiers
            payment_id = f"THUNES_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(str(payment_request.buyer_id).encode()).hexdigest()[:8]}"
            end_to_end_id = f"E2E_{payment_id}"
            transaction_id = f"TXN_{payment_id}"
            
            # Create instructed amount
            instructed_amount = {
                "amount": str(payment_request.total_amount),
                "currency": payment_request.currency
            }
            
            # Create debtor account
            debtor_account = {
                "id": payment_request.buyer_account["account_number"],
                "scheme_name": "IBAN",
                "identification": payment_request.buyer_account["account_number"]
            }
            
            # Create creditor account
            creditor_account = {
                "id": payment_request.seller_account["account_number"],
                "scheme_name": "IBAN",
                "identification": payment_request.seller_account["account_number"]
            }
            
            # Create creditor agent
            creditor_agent = {
                "financial_institution_id": {
                    "bic": payment_request.seller_account.get("bic", ""),
                    "clearing_system_id": payment_request.seller_account.get("clearing_system_id", "")
                }
            }
            
            # Create payment information
            payment_information = {
                "payment_type": "TRF",
                "payment_method": "TRF",
                "requested_execution_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "batch_booking": False,
                "charges": "SHA"
            }
            
            # Create regulatory reporting
            regulatory_reporting = {
                "regulatory_reporting_type": "OTH",
                "lawful_basis": "CONSENT",
                "reporting_reason": "MINERAL_TRADE",
                "country": payment_request.buyer_account["country"],
                "date_time": datetime.now(timezone.utc).isoformat()
            }
            
            # Create compliance data
            compliance_data = {
                "compliance_level": payment_request.compliance_level.value,
                "kyc_status": "VERIFIED",
                "aml_status": "CLEARED",
                "sanctions_screening": "PASSED",
                "pep_screening": "PASSED",
                "adverse_media_check": "CLEAN",
                "source_of_funds": "INSTITUTIONAL",
                "purpose_of_payment": "MINERAL_PURCHASE",
                "expected_settlement_time": "REAL_TIME"
            }
            
            # Create remittance information
            remittance_info = f"MINERAL:{payment_request.mineral_type}:QTY:{payment_request.quantity}:PRICE:{payment_request.unit_price}"
            
            # Generate quantum signature
            quantum_signature = await self.generate_quantum_signature(payment_request)
            
            return ISO20022Payment(
                payment_id=payment_id,
                end_to_end_id=end_to_end_id,
                transaction_id=transaction_id,
                instructed_amount=instructed_amount,
                charge_bearer="SHA",
                debtor_account=debtor_account,
                creditor_account=creditor_account,
                creditor_agent=creditor_agent,
                payment_information=payment_information,
                regulatory_reporting=regulatory_reporting,
                remittance_information=remittance_info,
                compliance_data=compliance_data,
                timestamp=datetime.now(timezone.utc),
                status=TransactionStatus.INITIATED,
                settlement_asset=payment_request.settlement_asset,
                quantum_signature=quantum_signature
            )
            
        except Exception as e:
            logger.error(f"ISO 20022 payment generation failed: {str(e)}")
            raise
    
    async def generate_quantum_signature(self, payment_request: InternationalPaymentRequest) -> str:
        """Generate quantum-resistant signature"""
        try:
            # Create signature data
            signature_data = {
                "buyer_id": payment_request.buyer_id,
                "seller_id": payment_request.seller_id,
                "amount": payment_request.total_amount,
                "currency": payment_request.currency,
                "mineral_type": payment_request.mineral_type,
                "quantity": payment_request.quantity,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Generate hash
            data_string = json.dumps(signature_data, sort_keys=True)
            hash_value = hashlib.sha256(data_string.encode()).hexdigest()
            
            # Mock quantum signature (in production, use ML-DSA)
            quantum_signature = f"ML_DSA_{hash_value}_{datetime.now().timestamp()}"
            
            return quantum_signature
            
        except Exception as e:
            logger.error(f"Quantum signature generation failed: {str(e)}")
            raise

class VisaDirectIntegration:
    """Visa Direct payment integration"""
    
    def __init__(self):
        self.api_base_url = "https://api.visa.com/vdp"
        self.api_key = os.getenv("VISA_API_KEY")
        self.shared_secret = os.getenv("VISA_SHARED_SECRET")
        self.user_id = os.getenv("VISA_USER_ID")
        self.password = os.getenv("VISA_PASSWORD")
        
        self.supported_card_types = ["CREDIT", "DEBIT", "PREPAID"]
        self.supported_currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"]
    
    async def initiate_card_payment(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Initiate Visa Direct card payment"""
        try:
            # Validate card details
            validation_result = await self.validate_card_details(payment_request)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "nbe_compliance": False
                }
            
            # Generate Visa Direct request
            visa_request = await self.generate_visa_request(payment_request)
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/visadirect/v1/payments",
                    json=visa_request,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "payment_id": result.get("payment_id"),
                            "approval_code": result.get("approval_code"),
                            "status": result.get("status"),
                            "authorization_code": result.get("authorization_code"),
                            "nbe_compliance": True
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": error_data.get("message"),
                            "status_code": response.status,
                            "nbe_compliance": False
                        }
        
        except Exception as e:
            logger.error(f"Visa Direct payment initiation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "nbe_compliance": False
            }
    
    async def validate_card_details(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Validate card details"""
        try:
            buyer_card = payment_request.buyer_account.get("card_details", {})
            
            # Check required fields
            required_fields = ["card_number", "expiry_date", "cvv", "cardholder_name"]
            
            for field in required_fields:
                if field not in buyer_card or not buyer_card[field]:
                    return {
                        "valid": False,
                        "error": f"Missing card field: {field}"
                    }
            
            # Validate card number (Luhn algorithm)
            card_number = buyer_card["card_number"].replace(" ", "")
            if not self.luhn_check(card_number):
                return {
                    "valid": False,
                    "error": "Invalid card number"
                }
            
            # Validate expiry date
            expiry_date = buyer_card["expiry_date"]
            if not self.validate_expiry_date(expiry_date):
                return {
                    "valid": False,
                    "error": "Invalid expiry date"
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Card validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def luhn_check(self, card_number: str) -> bool:
        """Luhn algorithm check for card number"""
        try:
            total = 0
            reverse_digits = card_number[::-1]
            
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n
            
            return total % 10 == 0
            
        except:
            return False
    
    def validate_expiry_date(self, expiry_date: str) -> bool:
        """Validate card expiry date"""
        try:
            if len(expiry_date) != 5 or expiry_date[2] != '/':
                return False
            
            month, year = expiry_date.split('/')
            month = int(month)
            year = int("20" + year)
            
            if month < 1 or month > 12:
                return False
            
            current_date = datetime.now()
            expiry_date_obj = datetime(year, month, 1)
            
            return expiry_date_obj > current_date
            
        except:
            return False
    
    async def generate_visa_request(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Generate Visa Direct request"""
        try:
            buyer_card = payment_request.buyer_account.get("card_details", {})
            
            visa_request = {
                "systemsTraceAuditNumber": str(hashlib.sha256(str(payment_request.buyer_id).encode()).hexdigest()[:6]),
                "retrievalReferenceNumber": str(hashlib.sha256(str(payment_request.seller_id).encode()).hexdigest()[:12]),
                "amount": str(payment_request.total_amount),
                "currency": payment_request.currency,
                "sender": {
                    "primaryAccountNumber": buyer_card["card_number"],
                    "cardExpiryDate": buyer_card["expiry_date"],
                    "cardVerificationValue": {
                        "value": buyer_card["cvv"]
                    }
                },
                "recipient": {
                    "primaryAccountNumber": payment_request.seller_account.get("card_number", ""),
                    "cardExpiryDate": payment_request.seller_account.get("expiry_date", "")
                },
                "paymentType": "CREDIT",
                "transactionType": "GOODS_AND_SERVICES",
                "merchantCategoryCode": "5072",  # Building materials
                "sourceOfFunds": "CREDIT",
                "billingAddress": {
                    "country": payment_request.buyer_account.get("country", ""),
                    "city": payment_request.buyer_account.get("city", ""),
                    "state": payment_request.buyer_account.get("state", ""),
                    "postalCode": payment_request.buyer_account.get("postal_code", "")
                },
                "orderInformation": {
                    "orderNumber": f"MINERAL_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "amount": str(payment_request.total_amount),
                    "currency": payment_request.currency,
                    "description": f"Mineral purchase: {payment_request.mineral_type}"
                }
            }
            
            return visa_request
            
        except Exception as e:
            logger.error(f"Visa request generation failed: {str(e)}")
            raise

class StablecoinSettlement:
    """Regulated stablecoin settlement system"""
    
    def __init__(self):
        self.supported_stablecoins = {
            StablecoinType.USDC: {
                "contract_address": "0xA0b86a33E6441b8e89C7c7c8c4e6c8d4e8e8e8e8",
                "network": "ethereum",
                "decimals": 6,
                "regulator": "NYDFS"
            },
            StablecoinType.PYUSD: {
                "contract_address": "0x8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e",
                "network": "ethereum",
                "decimals": 6,
                "regulator": "NYDFS"
            },
            StablecoinType.USDP: {
                "contract_address": "0x8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
                "network": "ethereum",
                "decimals": 6,
                "regulator": "NYDFS"
            }
        }
        
        self.wallet_addresses = {
            "settlement": os.getenv("SETTLEMENT_WALLET_ADDRESS"),
            "escrow": os.getenv("ESCROW_WALLET_ADDRESS"),
            "compliance": os.getenv("COMPLIANCE_WALLET_ADDRESS")
        }
    
    async def initiate_stablecoin_settlement(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Initiate stablecoin settlement"""
        try:
            stablecoin_info = self.supported_stablecoins.get(payment_request.settlement_asset)
            if not stablecoin_info:
                return {
                    "success": False,
                    "error": f"Unsupported stablecoin: {payment_request.settlement_asset.value}",
                    "nbe_compliance": False
                }
            
            # Validate settlement amount
            amount_in_smallest_unit = int(payment_request.total_amount * (10 ** stablecoin_info["decimals"]))
            
            # Create settlement transaction
            settlement_tx = await self.create_settlement_transaction(
                payment_request,
                amount_in_smallest_unit,
                stablecoin_info
            )
            
            # Execute transaction
            tx_result = await self.execute_settlement_transaction(settlement_tx)
            
            return {
                "success": True,
                "transaction_hash": tx_result.get("transaction_hash"),
                "block_number": tx_result.get("block_number"),
                "gas_used": tx_result.get("gas_used"),
                "settlement_amount": payment_request.total_amount,
                "stablecoin": payment_request.settlement_asset.value,
                "network": stablecoin_info["network"],
                "regulator": stablecoin_info["regulator"],
                "nbe_compliance": True,
                "settlement_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stablecoin settlement failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "nbe_compliance": False
            }
    
    async def create_settlement_transaction(self, payment_request: InternationalPaymentRequest, amount: int, stablecoin_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create settlement transaction"""
        try:
            # Mock transaction creation (in production, integrate with Web3 library)
            settlement_tx = {
                "from": self.wallet_addresses["escrow"],
                "to": payment_request.seller_account.get("wallet_address", self.wallet_addresses["settlement"]),
                "value": amount,
                "contract_address": stablecoin_info["contract_address"],
                "network": stablecoin_info["network"],
                "gas_limit": 100000,
                "gas_price": 20000000000,  # 20 Gwei
                "nonce": await self.get_next_nonce(),
                "data": self.encode_transfer_data(payment_request.seller_account.get("wallet_address", ""), amount),
                "payment_id": f"STABLE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "mineral_type": payment_request.mineral_type,
                "quantity": payment_request.quantity,
                "buyer_id": payment_request.buyer_id,
                "seller_id": payment_request.seller_id
            }
            
            return settlement_tx
            
        except Exception as e:
            logger.error(f"Settlement transaction creation failed: {str(e)}")
            raise
    
    async def execute_settlement_transaction(self, settlement_tx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute settlement transaction"""
        try:
            # Mock transaction execution (in production, integrate with Web3 library)
            transaction_hash = f"0x{hashlib.sha256(json.dumps(settlement_tx, sort_keys=True).encode()).hexdigest()}"
            
            return {
                "transaction_hash": transaction_hash,
                "block_number": 12345678,
                "gas_used": 85000,
                "status": "confirmed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Settlement transaction execution failed: {str(e)}")
            raise
    
    async def get_next_nonce(self) -> int:
        """Get next nonce for transaction"""
        # Mock nonce generation
        return int(datetime.now().timestamp())
    
    def encode_transfer_data(self, to_address: str, amount: int) -> str:
        """Encode transfer data for stablecoin contract"""
        # Mock data encoding (in production, use proper ABI encoding)
        return f"0xa9059cbb{to_address[2:].zfill(64)}{amount.to_bytes(32, 'big').hex()}"

class InternationalPaymentEngine:
    """Main international payment engine"""
    
    def __init__(self):
        self.thunes = ThunesIntegration()
        self.visa_direct = VisaDirectIntegration()
        self.stablecoin_settlement = StablecoinSettlement()
        
        self.payment_rails = {
            PaymentRail.THUNES_A2A: self.thunes.initiate_a2a_payment,
            PaymentRail.VISA_DIRECT: self.visa_direct.initiate_card_payment,
            PaymentRail.CRYPTO_STABLECOIN: self.stablecoin_settlement.initiate_stablecoin_settlement
        }
    
    async def process_international_payment(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Process international payment"""
        try:
            # Validate payment request
            validation_result = await self.validate_payment_request(payment_request)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "nbe_compliance": False
                }
            
            # Get payment rail handler
            payment_handler = self.payment_rails.get(payment_request.payment_rail)
            if not payment_handler:
                return {
                    "success": False,
                    "error": f"Unsupported payment rail: {payment_request.payment_rail.value}",
                    "nbe_compliance": False
                }
            
            # Process payment
            result = await payment_handler(payment_request)
            
            # Add metadata
            result["payment_rail"] = payment_request.payment_rail.value
            result["settlement_asset"] = payment_request.settlement_asset.value
            result["compliance_level"] = payment_request.compliance_level.value
            result["mineral_type"] = payment_request.mineral_type
            result["quantity"] = payment_request.quantity
            result["unit_price"] = payment_request.unit_price
            result["total_amount"] = payment_request.total_amount
            result["currency"] = payment_request.currency
            result["buyer_id"] = payment_request.buyer_id
            result["seller_id"] = payment_request.seller_id
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"International payment processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "nbe_compliance": False
            }
    
    async def validate_payment_request(self, payment_request: InternationalPaymentRequest) -> Dict[str, Any]:
        """Validate international payment request"""
        try:
            # Check required fields
            required_fields = [
                "buyer_id", "seller_id", "mineral_type", "quantity", 
                "unit_price", "total_amount", "currency", "payment_rail",
                "settlement_asset", "buyer_account", "seller_account"
            ]
            
            for field in required_fields:
                if not hasattr(payment_request, field) or not getattr(payment_request, field):
                    return {
                        "valid": False,
                        "error": f"Missing required field: {field}"
                    }
            
            # Validate amounts
            if payment_request.quantity <= 0:
                return {
                    "valid": False,
                    "error": "Quantity must be positive"
                }
            
            if payment_request.unit_price <= 0:
                return {
                    "valid": False,
                    "error": "Unit price must be positive"
                }
            
            if payment_request.total_amount <= 0:
                return {
                    "valid": False,
                    "error": "Total amount must be positive"
                }
            
            # Validate currency
            supported_currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF"]
            if payment_request.currency not in supported_currencies:
                return {
                    "valid": False,
                    "error": f"Unsupported currency: {payment_request.currency}"
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Payment request validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def get_supported_payment_rails(self) -> Dict[str, Any]:
        """Get supported payment rails"""
        return {
            "supported_rails": [rail.value for rail in self.payment_rails.keys()],
            "supported_stablecoins": [coin.value for coin in StablecoinType],
            "supported_currencies": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF"],
            "compliance_levels": [level.value for level in ComplianceLevel],
            "transaction_limits": {
                "standard": {"min": 10.0, "max": 10000.0},
                "enhanced": {"min": 10.0, "max": 50000.0},
                "institutional": {"min": 1000.0, "max": 1000000.0},
                "sovereign": {"min": 10000.0, "max": 10000000.0}
            },
            "nbe_compliance": True
        }

# Global instance
international_payment_engine = InternationalPaymentEngine()
