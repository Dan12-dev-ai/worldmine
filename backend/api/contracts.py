"""
Contract System API
Contract engine with templates, signatures, and audit trails
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import hashlib

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])


class ContractStatus(str, Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class ContractType(str, Enum):
    SALES_AGREEMENT = "sales_agreement"
    PURCHASE_ORDER = "purchase_order"
    SERVICE_AGREEMENT = "service_agreement"
    ESCROW_AGREEMENT = "escrow_agreement"


class ContractTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contract_type: ContractType
    template_content: str
    variables: List[str] = Field(default_factory=list)


class Contract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    contract_type: ContractType
    status: ContractStatus = Field(default=ContractStatus.DRAFT)
    parties: List[Dict[str, str]] = Field(default_factory=list)
    content: str
    signatures: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)


class ContractTemplateCreate(BaseModel):
    """Request body for creating a contract template"""
    name: str
    description: Optional[str] = None
    content: Optional[str] = None
    template_content: Optional[str] = None
    type: Optional[str] = None
    contract_type: Optional[str] = None
    variables: List[str] = Field(default_factory=list)


class ContractCreate(BaseModel):
    """Request body for creating a contract from a template"""
    template_id: str
    parties: List[Dict[str, Any]] = Field(default_factory=list)
    terms: Dict[str, Any] = Field(default_factory=dict)
    variables: Optional[Dict[str, Any]] = None


class ContractSign(BaseModel):
    """Request body for signing a contract"""
    user_id: Optional[str] = None
    signer_id: Optional[str] = None
    signature: Optional[str] = None
    signature_data: Optional[str] = None


# Storage
contract_templates: Dict[str, ContractTemplate] = {}
contracts: Dict[str, Contract] = {}


@router.post("/templates")
async def create_template(body: ContractTemplateCreate):
    valid_types = [t.value for t in ContractType]
    contract_type = body.contract_type or body.type or "sales_agreement"
    if contract_type not in valid_types:
        contract_type = "sales_agreement"
    template = ContractTemplate(
        name=body.name,
        contract_type=ContractType(contract_type),
        template_content=body.content or body.template_content or "",
        variables=body.variables
    )
    contract_templates[template.id] = template
    return {"data": jsonable_encoder(template)}


@router.get("/templates", response_model=List[ContractTemplate])
async def list_templates(skip: int = 0, limit: int = 100):
    return list(contract_templates.values())[skip:skip + limit]


@router.post("/contracts", response_model=Contract, status_code=status.HTTP_201_CREATED)
async def create_contract(body: ContractCreate):
    if body.template_id not in contract_templates:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

    template = contract_templates[body.template_id]
    content = template.template_content
    variables = body.variables or body.terms or {}
    for key, value in variables.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))

    contract = Contract(
        template_id=body.template_id,
        contract_type=template.contract_type,
        parties=[{str(k): str(v) for k, v in party.items()} for party in body.parties],
        content=content
    )
    contracts[contract.id] = contract
    return contract


@router.get("/contracts", response_model=List[Contract])
async def list_contracts(skip: int = 0, limit: int = 100):
    return list(contracts.values())[skip:skip + limit]


@router.get("/contracts/{contract_id}", response_model=Contract)
async def get_contract(contract_id: str):
    if contract_id not in contracts:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contract not found")
    return contracts[contract_id]


@router.post("/contracts/{contract_id}/sign")
async def sign_contract(contract_id: str, body: Optional[ContractSign] = None):
    if contract_id not in contracts:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contract not found")

    contract = contracts[contract_id]
    signer_id = (body.user_id or body.signer_id) if body else None
    signer_id = signer_id or "system"
    signature_data = (body.signature or body.signature_data or "") if body else ""
    signature_hash = hashlib.sha256((contract.content + signer_id + signature_data).encode()).hexdigest()

    contract.signatures.append({
        "signer_id": signer_id,
        "signature_hash": signature_hash,
        "signed_at": datetime.utcnow().isoformat()
    })

    if len(contract.signatures) >= max(len(contract.parties), 1):
        contract.status = ContractStatus.SIGNED

    contract.audit_trail.append({
        "action": "signed",
        "actor": signer_id,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"message": "Contract signed", "status": contract.status}


@router.post("/contracts/{contract_id}/activate")
async def activate_contract(contract_id: str):
    if contract_id not in contracts:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contract not found")

    contract = contracts[contract_id]
    if contract.status != ContractStatus.SIGNED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Contract must be signed")

    contract.status = ContractStatus.ACTIVE
    return {"message": "Contract activated"}
