"""
Zero-Knowledge User Shield - DEDAN Mine
Pydantic schemas with SecretStr for PII protection
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, SecretStr, EmailStr, validator
from datetime import datetime
import re

class SecureUserRegistration(BaseModel):
    """Secure user registration schema with PII protection"""
    email: EmailStr
    username: str
    password: SecretStr
    phone: Optional[SecretStr] = None
    full_name: Optional[SecretStr] = None
    address: Optional[Dict[str, Any]] = None
    id_document: Optional[SecretStr] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        # Password validation without logging the actual password
        password_str = v.get_secret_value() if hasattr(v, 'get_secret_value') else str(v)
        
        if len(password_str) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password_str):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password_str):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password_str):
            raise ValueError('Password must contain at least one digit')
        
        return v

class SecureUserLogin(BaseModel):
    """Secure user login schema with PII protection"""
    email: EmailStr
    password: SecretStr
    remember_me: bool = False
    login_method: str = "password"
    device_info: Optional[Dict[str, Any]] = None

class SecureUserProfile(BaseModel):
    """Secure user profile update schema with PII protection"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone: Optional[SecretStr] = None
    full_name: Optional[SecretStr] = None
    address: Optional[Dict[str, Any]] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v and (len(v) < 3 or len(v) > 50):
            raise ValueError('Username must be between 3 and 50 characters long')
        return v

class SecureTransaction(BaseModel):
    """Secure transaction schema with PII protection"""
    amount: float
    recipient_id: str
    description: Optional[str] = None
    payment_method: str
    billing_address: Optional[Dict[str, Any]] = None
    card_number: Optional[SecretStr] = None
    bank_account: Optional[SecretStr] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 1000000:  # $1M limit
            raise ValueError('Amount exceeds maximum limit')
        return v

class SecureListing(BaseModel):
    """Secure listing schema with PII protection"""
    title: str
    description: str
    category: str
    gem_type: str
    weight: float
    unit: str
    price: float
    listing_type: str
    images: List[str]
    seller_location: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    extraction_location: Optional[Dict[str, Any]] = None
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        if v > 10000000:  # $10M limit
            raise ValueError('Price exceeds maximum limit')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v <= 0:
            raise ValueError('Weight must be greater than 0')
        return v

class SecureKYCDocument(BaseModel):
    """Secure KYC document schema with PII protection"""
    document_type: str
    document_number: SecretStr
    issuing_country: str
    expiry_date: Optional[datetime] = None
    front_image: Optional[str] = None
    back_image: Optional[str] = None
    selfie_image: Optional[str] = None
    address_proof: Optional[SecretStr] = None
    
    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = ['passport', 'national_id', 'driving_license', 'mining_license']
        if v not in allowed_types:
            raise ValueError(f'Document type must be one of: {allowed_types}')
        return v

class SecureBankAccount(BaseModel):
    """Secure bank account schema with PII protection"""
    account_holder_name: SecretStr
    account_number: SecretStr
    routing_number: Optional[SecretStr] = None
    bank_name: Optional[str] = None
    bank_address: Optional[Dict[str, Any]] = None
    swift_code: Optional[str] = None
    
    @validator('account_number')
    def validate_account_number(cls, v):
        # Basic validation without logging the account number
        account_str = v.get_secret_value() if hasattr(v, 'get_secret_value') else str(v)
        
        if len(account_str) < 8:
            raise ValueError('Account number must be at least 8 digits long')
        
        if not account_str.isdigit():
            raise ValueError('Account number must contain only digits')
        
        return v

class SecureVerificationData(BaseModel):
    """Secure verification data schema with PII protection"""
    gps_coordinates: Optional[Dict[str, float]] = None
    satellite_metadata: Optional[Dict[str, Any]] = None
    biometric_hash: Optional[SecretStr] = None
    device_fingerprint: Optional[SecretStr] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    
    @validator('gps_coordinates')
    def validate_gps_coordinates(cls, v):
        if v:
            lat = v.get('latitude')
            lng = v.get('longitude')
            
            if lat is None or lng is None:
                raise ValueError('GPS coordinates must include both latitude and longitude')
            
            if not (-90 <= lat <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            
            if not (-180 <= lng <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        
        return v

class SecureAgentRental(BaseModel):
    """Secure agent rental schema with PII protection"""
    agent_id: str
    rental_duration_hours: int
    payment_method: str
    rental_purpose: Optional[str] = None
    access_credentials: Optional[SecretStr] = None
    usage_constraints: Optional[Dict[str, Any]] = None
    
    @validator('rental_duration_hours')
    def validate_rental_duration(cls, v):
        if v < 1:
            raise ValueError('Rental duration must be at least 1 hour')
        if v > 168:  # 1 week
            raise ValueError('Rental duration cannot exceed 168 hours')
        return v

class SecureComplianceReport(BaseModel):
    """Secure compliance report schema with PII protection"""
    report_type: str
    reporter_id: str
    subject_id: str
    description: str
    evidence_files: Optional[List[str]] = None
    anonymous_report: bool = False
    contact_info: Optional[SecretStr] = None
    
    @validator('description')
    def validate_description(cls, v):
        if len(v) < 10:
            raise ValueError('Description must be at least 10 characters long')
        if len(v) > 2000:
            raise ValueError('Description cannot exceed 2000 characters')
        return v

class ZeroKnowledgeShield:
    """Zero-knowledge protection utilities"""
    
    @staticmethod
    def mask_pii(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """Mask PII data while keeping some characters visible"""
        if len(data) <= visible_chars:
            return data
        
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)
    
    @staticmethod
    def safe_log(data: Any, field_name: str = "data") -> str:
        """Safely log data without exposing PII"""
        if isinstance(data, SecretStr):
            return f"{field_name}: [REDACTED_SECRET]"
        elif isinstance(data, str):
            # Check if it looks like PII
            pii_patterns = [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
                r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',          # SSN
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
            ]
            
            for pattern in pii_patterns:
                if re.search(pattern, data):
                    return f"{field_name}: [REDACTED_PII]"
            
            return f"{field_name}: {data}"
        else:
            return f"{field_name}: {str(data)}"
    
    @staticmethod
    def sanitize_for_logging(model: BaseModel) -> Dict[str, Any]:
        """Sanitize pydantic model for safe logging"""
        safe_dict = {}
        
        for field_name, field_value in model.dict().items():
            if isinstance(field_value, SecretStr):
                safe_dict[field_name] = "[REDACTED_SECRET]"
            elif isinstance(field_value, str):
                # Check for PII patterns
                if ZeroKnowledgeShield._contains_pii(field_value):
                    safe_dict[field_name] = "[REDACTED_PII]"
                else:
                    safe_dict[field_name] = field_value
            else:
                safe_dict[field_name] = field_value
        
        return safe_dict
    
    @staticmethod
    def _contains_pii(text: str) -> bool:
        """Check if text contains PII patterns"""
        pii_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',          # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
        
        return any(re.search(pattern, text) for pattern in pii_patterns)
