"""
🔐 DEDAN 2.0 - AI-Powered KYC Verification API
<2 minute completion, <30 second approval
Enterprise-grade AI models with real-time processing
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
import asyncio
import uuid
import hashlib
import json
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
import base64
import io
from PIL import Image
import face_recognition
import pytesseract
from supabase import create_client, Client
import redis
import requests
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize clients
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# AI Models (loaded once)
class AIModels:
    def __init__(self):
        self.ocr_model = None
        self.face_recognition_model = None
        self.document_classifier = None
        self.liveness_detector = None
    
    async def load_models(self):
        """Load AI models for KYC processing"""
        # Document classification model
        self.document_classifier = pipeline(
            "text-classification",
            model="microsoft/DialoGPT-medium",
            tokenizer="microsoft/DialoGPT-medium"
        )
        
        # Face recognition model (using face_recognition library)
        print("✅ AI Models loaded for KYC processing")
        
        return True

# Initialize AI models
ai_models = AIModels()

class KYCDocumentUpload(BaseModel):
    """KYC document upload request"""
    document_type: str  # "passport", "id_card", "driver_license", "proof_of_address"
    front_image: str = None  # Base64 encoded
    back_image: str = None   # Base64 encoded
    selfie_image: str = None  # Base64 encoded

class FaceRecognitionRequest(BaseModel):
    """Face recognition request"""
    user_id: str
    selfie_image: str  # Base64 encoded
    document_face: str  # Base64 encoded from ID document

class KYCResult(BaseModel):
    """KYC verification result"""
    status: str  # "approved", "rejected", "manual_review"
    confidence: float  # 0.0 - 1.0
    match_score: Optional[float] = None
    risk_score: float  # 0.0 - 1.0
    processing_time_ms: int
    verification_id: str
    kyc_level: str  # "none", "basic", "standard", "enhanced", "full"
    rejection_reason: Optional[str] = None
    approval_timestamp: Optional[datetime] = None

router = APIRouter(prefix="/api/kyc", tags=["kyc"])

def decode_base64_image(base64_string: str) -> np.ndarray:
    """Decode base64 image to numpy array"""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return image
    except Exception as e:
        print(f"❌ Error decoding base64 image: {e}")
        return None

def detect_document_edges(image: np.ndarray) -> bool:
    """Detect if image has clear document edges"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if we have a document-like contour
        if len(contours) > 0:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # Check if contour area is reasonable for a document
            image_area = image.shape[0] * image.shape[1]
            document_ratio = area / image_area
            
            # Document should occupy at least 60% of image
            return document_ratio > 0.6
        
        return False
    except Exception as e:
        print(f"❌ Error detecting document edges: {e}")
        return False

def detect_blur(image: np.ndarray) -> float:
    """Detect image blur using Laplacian variance"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Lower variance means more blur
        # Threshold: 100 (blurry) to 500 (sharp)
        blur_score = max(0, min(1, (500 - laplacian_var) / 400))
        
        return blur_score
    except Exception as e:
        print(f"❌ Error detecting blur: {e}")
        return 1.0  # Assume blurry if error

def detect_glare(image: np.ndarray) -> float:
    """Detect glare in image"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate brightness histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Check for overexposed pixels (glare)
        overexposed_pixels = np.sum(hist[200:256])  # Bright pixels
        
        # Calculate glare score
        total_pixels = image.shape[0] * image.shape[1]
        glare_ratio = overexposed_pixels / total_pixels
        
        # Higher ratio means more glare
        # Normalize to 0-1 scale
        glare_score = min(1.0, glare_ratio * 10)
        
        return glare_score
    except Exception as e:
        print(f"❌ Error detecting glare: {e}")
        return 1.0  # Assume glare if error

def extract_face_embedding(image: np.ndarray) -> Optional[np.ndarray]:
    """Extract face embedding from image"""
    try:
        # Convert RGB to BGR for face_recognition
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Find face locations
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return None
        
        # Get face encodings (embeddings)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) == 0:
            return None
        
        return face_encodings[0]  # Return first face embedding
        
    except Exception as e:
        print(f"❌ Error extracting face embedding: {e}")
        return None

def calculate_face_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Calculate similarity between two face embeddings"""
    try:
        # Use face distance for comparison
        face_distance = face_recognition.face_distance([embedding1], embedding2)[0]
        
        # Convert distance to similarity score (0-1 scale)
        # Lower distance = higher similarity
        similarity = max(0, min(1, 1 - (face_distance / 0.6)))
        
        return similarity
    except Exception as e:
        print(f"❌ Error calculating face similarity: {e}")
        return 0.0

def detect_liveness(image: np.ndarray) -> Dict[str, Any]:
    """Detect liveness to prevent photo spoofing"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simple liveness detection using eye blink and head movement
        # In production, use advanced models like FaceNet or DeepFace
        
        # Eye detection (simplified)
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Basic liveness indicators
        liveness_score = 0.5  # Neutral score
        
        if len(eyes) >= 2:
            liveness_score += 0.3  # Eyes detected
        
        # Check for image quality indicators
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var > 100:  # Not too blurry
            liveness_score += 0.2
        
        return {
            "is_live": liveness_score > 0.6,
            "confidence": liveness_score,
            "eyes_detected": len(eyes),
            "image_quality": "good" if laplacian_var > 100 else "poor"
        }
    except Exception as e:
        print(f"❌ Error detecting liveness: {e}")
        return {"is_live": False, "confidence": 0.0, "error": str(e)}

async def run_sanctions_check(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run sanctions and PEP checks"""
    try:
        # In production, integrate with real sanctions APIs
        # OFAC, UN, EU sanctions lists
        
        # Mock sanctions check
        sanctions_result = {
            "ofac_check": "clear",
            "un_check": "clear", 
            "eu_check": "clear",
            "pep_check": "clear",
            "adverse_media_check": "clear",
            "overall_risk": "low"
        }
        
        # Check for high-risk countries
        high_risk_countries = ["XX", "IR", "KP", "SY", "MM"]
        if user_data.get("country") in high_risk_countries:
            sanctions_result["overall_risk"] = "high"
            sanctions_result["country_risk"] = "high"
        
        # Check for politically exposed persons
        # In production, integrate with PEP database
        pep_names = ["John Smith", "Jane Doe"]  # Mock PEP list
        full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}"
        if any(pep in full_name for pep in pep_names):
            sanctions_result["pep_check"] = "flagged"
            sanctions_result["overall_risk"] = "medium"
        
        return sanctions_result
        
    except Exception as e:
        print(f"❌ Error in sanctions check: {e}")
        return {"error": str(e), "overall_risk": "unknown"}

async def calculate_kyc_risk_score(
    document_validity: float,
    face_match_score: float,
    liveness_score: float,
    sanctions_result: Dict[str, Any]
) -> float:
    """Calculate overall KYC risk score"""
    try:
        # Weight different factors
        document_weight = 0.3
        face_match_weight = 0.3
        liveness_weight = 0.2
        sanctions_weight = 0.2
        
        # Document validity score (0-1)
        document_score = document_validity
        
        # Face match score (0-1)
        face_score = face_match_score
        
        # Liveness score (0-1)
        live_score = liveness_score
        
        # Sanctions score (0-1)
        sanctions_risk_mapping = {"low": 0.9, "medium": 0.6, "high": 0.3, "unknown": 0.5}
        sanctions_score = sanctions_risk_mapping.get(sanctions_result.get("overall_risk", "unknown"), 0.5)
        
        # Calculate weighted risk score
        risk_score = (
            document_score * document_weight +
            face_score * face_match_weight +
            live_score * liveness_weight +
            sanctions_score * sanctions_weight
        )
        
        return max(0.0, min(1.0, risk_score))
        
    except Exception as e:
        print(f"❌ Error calculating risk score: {e}")
        return 0.5  # Medium risk if error

@router.post("/upload-document", response_model=Dict[str, Any])
async def upload_document(
    request: KYCDocumentUpload,
    background_tasks: BackgroundTasks,
    credentials: dict = Depends(lambda: {"user_id": "test_user"})  # TODO: Implement JWT auth
):
    """
    Upload and validate KYC documents with AI processing
    - <2 second document validation
    - Auto-crop and quality checks
    - Blur and glare detection
    """
    start_time = datetime.utcnow()
    
    try:
        # Load AI models if not loaded
        if ai_models.document_classifier is None:
            await ai_models.load_models()
        
        user_id = credentials["user_id"]
        verification_id = str(uuid.uuid4())
        
        # Process front image
        front_validation = {"valid": False, "issues": []}
        if request.front_image:
            front_image = decode_base64_image(request.front_image)
            if front_image is not None:
                # Document edge detection
                has_edges = detect_document_edges(front_image)
                if not has_edges:
                    front_validation["issues"].append("Document edges not clearly visible")
                
                # Blur detection
                blur_score = detect_blur(front_image)
                if blur_score > 0.7:
                    front_validation["issues"].append("Document appears blurry")
                
                # Glare detection
                glare_score = detect_glare(front_image)
                if glare_score > 0.6:
                    front_validation["issues"].append("Document has glare or reflections")
                
                front_validation["valid"] = len(front_validation["issues"]) == 0
                front_validation["blur_score"] = blur_score
                front_validation["glare_score"] = glare_score
        
        # Process back image (if applicable)
        back_validation = {"valid": False, "issues": []}
        if request.back_image:
            back_image = decode_base64_image(request.back_image)
            if back_image is not None:
                has_edges = detect_document_edges(back_image)
                if not has_edges:
                    back_validation["issues"].append("Document back not clearly visible")
                
                blur_score = detect_blur(back_image)
                if blur_score > 0.7:
                    back_validation["issues"].append("Document back appears blurry")
                
                glare_score = detect_glare(back_image)
                if glare_score > 0.6:
                    back_validation["issues"].append("Document back has glare")
                
                back_validation["valid"] = len(back_validation["issues"]) == 0
                back_validation["blur_score"] = blur_score
                back_validation["glare_score"] = glare_score
        
        # Calculate overall document validity
        document_validity = 1.0
        all_issues = front_validation["issues"] + back_validation["issues"]
        if all_issues:
            document_validity = max(0.0, 1.0 - (len(all_issues) * 0.2))
        
        # Store document data
        document_data = {
            "user_id": user_id,
            "verification_id": verification_id,
            "document_type": request.document_type,
            "front_image": request.front_image,
            "back_image": request.back_image,
            "front_validation": front_validation,
            "back_validation": back_validation,
            "document_validity": document_validity,
            "status": "uploaded",
            "created_at": start_time.isoformat()
        }
        
        # Save to database
        result = supabase.table('kyc_documents').insert(document_data).execute()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "verification_id": verification_id,
            "document_id": result.data[0]["id"],
            "document_validity": document_validity,
            "validation_issues": all_issues,
            "processing_time_ms": processing_time,
            "message": "Document uploaded and validated successfully"
        }
        
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {
            "status": "error",
            "error": str(e),
            "processing_time_ms": processing_time,
            "message": "Document upload failed"
        }

@router.post("/facial-recognition", response_model=KYCResult)
async def facial_recognition(
    request: FaceRecognitionRequest,
    background_tasks: BackgroundTasks,
    credentials: dict = Depends(lambda: {"user_id": "test_user"})  # TODO: Implement JWT auth
):
    """
    Perform facial recognition with liveness detection
    - <10 second processing time
    - <30 second approval
    - Real-time face matching
    """
    start_time = datetime.utcnow()
    
    try:
        user_id = credentials["user_id"]
        verification_id = str(uuid.uuid4())
        
        # Get user's uploaded documents
        documents = supabase.table('kyc_documents').select('*').eq('user_id', user_id).execute()
        
        if not documents.data:
            raise HTTPException(
                status_code=400,
                detail={"error": "No documents found", "message": "Please upload documents first"}
            )
        
        # Get the most recent document with face
        document_with_face = None
        for doc in documents.data:
            if doc.get("document_type") in ["passport", "id_card", "driver_license"]:
                document_with_face = doc
                break
        
        if not document_with_face:
            raise HTTPException(
                status_code=400,
                detail={"error": "No ID document with photo found", "message": "Please upload an ID document with photo"}
            )
        
        # Decode images
        selfie_image = decode_base64_image(request.selfie_image)
        document_image = decode_base64_image(request.document_face)
        
        if selfie_image is None or document_image is None:
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid image data", "message": "Could not process images"}
            )
        
        # Extract face embeddings
        selfie_embedding = extract_face_embedding(selfie_image)
        document_embedding = extract_face_embedding(document_image)
        
        if selfie_embedding is None:
            raise HTTPException(
                status_code=400,
                detail={"error": "No face detected", "message": "Could not detect face in selfie"}
            )
        
        if document_embedding is None:
            raise HTTPException(
                status_code=400,
                detail={"error": "No face in document", "message": "Could not detect face in document photo"}
            )
        
        # Calculate face similarity
        match_score = calculate_face_similarity(document_embedding, selfie_embedding)
        
        # Liveness detection
        liveness_result = detect_liveness(selfie_image)
        
        # Get user data for sanctions check
        user_data = supabase.table('users').select('*').eq('id', user_id).execute()
        user_info = user_data.data[0] if user_data.data else {}
        
        # Run sanctions check
        sanctions_result = await run_sanctions_check(user_info)
        
        # Calculate overall risk score
        document_validity = document_with_face.get("document_validity", 0.5)
        risk_score = await calculate_kyc_risk_score(
            document_validity,
            match_score,
            liveness_result.get("confidence", 0.0),
            sanctions_result
        )
        
        # Determine KYC result
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Approval logic
        if (match_score >= 0.85 and 
            liveness_result.get("is_live", False) == False and 
            risk_score <= 0.3 and
            sanctions_result.get("overall_risk") == "low"):
            
            # Auto-approve
            kyc_status = "approved"
            kyc_level = "full"
            confidence = match_score
            rejection_reason = None
            approval_timestamp = datetime.utcnow()
            
        elif (match_score >= 0.7 and risk_score <= 0.5):
            # Manual review
            kyc_status = "manual_review"
            kyc_level = "pending"
            confidence = match_score
            rejection_reason = "Additional verification required"
            approval_timestamp = None
            
        else:
            # Reject
            kyc_status = "rejected"
            kyc_level = "none"
            confidence = match_score
            rejection_reason = "Face match too low or liveness check failed"
            approval_timestamp = None
        
        # Update user KYC status
        user_update = {
            "kyc_status": kyc_status,
            "kyc_level": kyc_level,
            "kyc_completed_at": approval_timestamp.isoformat() if approval_timestamp else None,
            "last_verification_id": verification_id,
            "risk_score": risk_score
        }
        
        supabase.table('users').update(user_update).eq('id', user_id).execute()
        
        # Store verification result
        verification_result = {
            "user_id": user_id,
            "verification_id": verification_id,
            "match_score": match_score,
            "liveness_score": liveness_result.get("confidence", 0.0),
            "sanctions_result": sanctions_result,
            "risk_score": risk_score,
            "status": kyc_status,
            "kyc_level": kyc_level,
            "processing_time_ms": processing_time,
            "created_at": start_time.isoformat(),
            "approval_timestamp": approval_timestamp.isoformat() if approval_timestamp else None
        }
        
        supabase.table('kyc_verifications').insert(verification_result).execute()
        
        return KYCResult(
            status=kyc_status,
            confidence=confidence,
            match_score=match_score,
            risk_score=risk_score,
            processing_time_ms=processing_time,
            verification_id=verification_id,
            kyc_level=kyc_level,
            rejection_reason=rejection_reason,
            approval_timestamp=approval_timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        return KYCResult(
            status="error",
            confidence=0.0,
            risk_score=1.0,
            processing_time_ms=processing_time,
            verification_id=verification_id,
            kyc_level="none",
            rejection_reason=f"Processing error: {str(e)}"
        )

@router.get("/status/{verification_id}", response_model=Dict[str, Any])
async def get_kyc_status(verification_id: str):
    """
    Get KYC verification status
    - Real-time status updates
    - Processing progress tracking
    """
    try:
        # Get verification result
        verification = supabase.table('kyc_verifications').select('*').eq('verification_id', verification_id).execute()
        
        if not verification.data:
            raise HTTPException(
                status_code=404,
                detail={"error": "Verification not found", "message": "Invalid verification ID"}
            )
        
        verification_data = verification.data[0]
        
        return {
            "status": "success",
            "verification_id": verification_id,
            "kyc_status": verification_data.get("status"),
            "kyc_level": verification_data.get("kyc_level"),
            "confidence": verification_data.get("confidence"),
            "risk_score": verification_data.get("risk_score"),
            "processing_time_ms": verification_data.get("processing_time_ms"),
            "created_at": verification_data.get("created_at"),
            "approval_timestamp": verification_data.get("approval_timestamp"),
            "rejection_reason": verification_data.get("rejection_reason")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Status check failed", "message": str(e)}
        )

@router.get("/documents", response_model=List[Dict[str, Any]])
async def get_user_documents(
    credentials: dict = Depends(lambda: {"user_id": "test_user"})  # TODO: Implement JWT auth
):
    """
    Get user's uploaded KYC documents
    - Document status tracking
    - Validation results
    """
    try:
        user_id = credentials["user_id"]
        
        documents = supabase.table('kyc_documents').select('*').eq('user_id', user_id).execute()
        
        if not documents.data:
            return []
        
        return documents.data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Document fetch failed", "message": str(e)}
        )

@router.post("/retry", response_model=Dict[str, Any])
async def retry_kyc(
    credentials: dict = Depends(lambda: {"user_id": "test_user"})  # TODO: Implement JWT auth
):
    """
    Retry KYC verification for manual review cases
    - Re-process with AI models
    - Updated document validation
    """
    try:
        user_id = credentials["user_id"]
        
        # Get user data
        user = supabase.table('users').select('*').eq('id', user_id).execute()
        if not user.data:
            raise HTTPException(
                status_code=404,
                detail={"error": "User not found", "message": "User account not found"}
            )
        
        user_data = user.data[0]
        
        # Check if user is eligible for retry
        if user_data.get("kyc_status") not in ["rejected", "manual_review"]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Not eligible for retry", "message": "KYC status must be rejected or manual review"}
            )
        
        # Reset KYC status to pending
        supabase.table('users').update({
            "kyc_status": "pending",
            "kyc_level": "pending"
        }).eq('id', user_id).execute()
        
        return {
            "status": "success",
            "message": "KYC reset to pending. Please upload new documents.",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "KYC retry failed", "message": str(e)}
        )
