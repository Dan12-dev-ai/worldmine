"""
DEDAN Mine - Agentic Orchestrator (v3.0.0)
LLM-powered agent for multilingual translation and dispute resolution
MCP-compatible integration for OECD 2026 compliance
Real-time translation to 100+ languages with dialect support
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import base64
import aiohttp
import openai
from openai import AsyncOpenAI
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Agent capabilities"""
    TRANSLATION = "translation"
    DISPUTE_RESOLUTION = "dispute_resolution"
    COMPLIANCE_CHECK = "compliance_check"
    MARKET_ANALYSIS = "market_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    DOCUMENT_GENERATION = "document_generation"

class LanguageCode(Enum):
    """Supported language codes"""
    AMHARIC = "am"
    ENGLISH = "en"
    ARABIC = "ar"
    MANDARIN = "zh"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    HINDI = "hi"
    BENGALI = "bn"
    URDU = "ur"
    INDONESIAN = "id"
    MALAY = "ms"
    THAI = "th"
    VIETNAMESE = "vi"
    SWAHILI = "sw"
    HAUSA = "ha"
    YORUBA = "yo"
    IGBO = "ig"
    ZULU = "zu"
    AFRIKAANS = "af"
    DUTCH = "nl"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    POLISH = "pl"
    CZECH = "cs"
    SLOVAK = "sk"
    HUNGARIAN = "hu"
    ROMANIAN = "ro"
    BULGARIAN = "bg"
    CROATIAN = "hr"
    SERBIAN = "sr"
    SLOVENIAN = "sl"
    ESTONIAN = "et"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    GREEK = "el"
    HEBREW = "he"
    TURKISH = "tr"
    PERSIAN = "fa"
    KURDISH = "ku"
    ARMENIAN = "hy"
    AZERBAIJANI = "az"
    GEORGIAN = "ka"
    KAZAKH = "kk"
    UZBEK = "uz"
    TAJIK = "tg"
    KYRGYZ = "ky"
    MONGOLIAN = "mn"
    NEPALI = "ne"
    SINHALA = "si"
    TAMIL = "ta"
    TELUGU = "te"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    BURMESE = "my"
    KHMER = "km"
    LAO = "lo"
    TAGALOG = "tl"
    INDONESIAN_JAVANESE = "jv"
    SUNDANESE = "su"
    BALINESE = "ban"
    MADURESE = "mad"
    ACEHNESE = "ace"
    MINANGKABAU = "min"
    BUGINESE = "bug"
    MAKASARESE = "mak"
    TOLAI = "ksl"
    FIJIAN = "fj"
    SAMOAN = "sm"
    TONGAN = "to"
    MAORI = "mi"
    HAWAIIAN = "haw"
    CHAMORRO = "ch"
    PALAUAN = "pau"
    MARSHALLESE = "mh"
    KIRIBATI = "gil"
    TUVALUAN = "tvl"
    NAURUAN = "na"
    MICRONESIAN = "chk"
    PALAUAN = "pau"

class ComplianceStandard(Enum):
    """Compliance standards"""
    OECD_2026 = "oecd_2026"
    ISO_20400 = "iso_20400"
    RMI_STANDARD = "rmi_standard"
    LME_RESPONSIBLE = "lme_responsible"
    EU_CONFLICT_MINERALS = "eu_conflict_minerals"
    US_CONFLICT_MINERALS = "us_conflict_minerals"

@dataclass
class TranslationRequest:
    """Translation request structure"""
    request_id: str
    source_text: str
    source_language: LanguageCode
    target_language: LanguageCode
    target_dialect: Optional[str]
    context: str
    priority: str
    user_id: str
    timestamp: datetime

@dataclass
class TranslationResponse:
    """Translation response structure"""
    request_id: str
    translated_text: str
    source_language: LanguageCode
    target_language: LanguageCode
    target_dialect: Optional[str]
    confidence_score: float
    translation_method: str
    processing_time: float
    timestamp: datetime

@dataclass
class DisputeRequest:
    """Dispute resolution request"""
    dispute_id: str
    parties: List[str]
    dispute_type: str
    description: str
    evidence: List[Dict[str, Any]]
    compliance_standard: ComplianceStandard
    priority: str
    user_id: str
    timestamp: datetime

@dataclass
class DisputeResponse:
    """Dispute resolution response"""
    dispute_id: str
    resolution: str
    reasoning: str
    compliance_analysis: Dict[str, Any]
    recommended_actions: List[str]
    confidence_score: float
    processing_time: float
    timestamp: datetime

@dataclass
class AgentTask:
    """Agent task structure"""
    task_id: str
    capability: AgentCapability
    request_data: Dict[str, Any]
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

class MultilingualTranslationAgent:
    """Multilingual translation agent with LLM support"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.getenv("OPENAI_ORG_ID")
        )
        
        self.supported_languages = {lang.value: lang for lang in LanguageCode}
        self.translation_cache = {}
        self.dialect_mappings = self._initialize_dialect_mappings()
        self.context_templates = self._initialize_context_templates()
        
        # Language priority mapping
        self.priority_languages = {
            "am": "Amharic",
            "en": "English", 
            "ar": "Arabic",
            "zh": "Mandarin"
        }
        
        self.translation_models = {
            "high_priority": "gpt-4-turbo-preview",
            "standard": "gpt-3.5-turbo",
            "batch": "gpt-3.5-turbo"
        }
    
    def _initialize_dialect_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize dialect mappings for languages"""
        return {
            "am": {
                "addis_ababa": "Addis Ababa dialect",
                "gondar": "Gondar dialect",
                "bahir_dar": "Bahir Dar dialect",
                "hawassa": "Hawassa dialect",
                "mekelle": "Mekelle dialect"
            },
            "ar": {
                "egyptian": "Egyptian Arabic",
                "levantine": "Levantine Arabic",
                "gulf": "Gulf Arabic",
                "maghrebi": "Maghrebi Arabic",
                "standard": "Modern Standard Arabic"
            },
            "zh": {
                "mandarin": "Mandarin Chinese",
                "cantonese": "Cantonese Chinese",
                "shanghainese": "Shanghainese Chinese",
                "taiwanese": "Taiwanese Mandarin",
                "simplified": "Simplified Chinese",
                "traditional": "Traditional Chinese"
            },
            "en": {
                "american": "American English",
                "british": "British English",
                "australian": "Australian English",
                "canadian": "Canadian English",
                "indian": "Indian English"
            }
        }
    
    def _initialize_context_templates(self) -> Dict[str, str]:
        """Initialize context templates for different domains"""
        return {
            "mineral_trading": "Translate this mineral trading document with accurate technical terminology and market-specific language.",
            "legal_compliance": "Translate this legal/compliance document maintaining precise legal terminology and formal tone.",
            "financial_transactions": "Translate this financial transaction information with accurate monetary and banking terminology.",
            "technical_specifications": "Translate these technical specifications maintaining precision and technical accuracy.",
            "customer_support": "Translate this customer support communication in a natural, helpful tone appropriate for the target culture.",
            "marketing": "Translate this marketing content adapting cultural references and maintaining persuasive impact.",
            "news": "Translate this news article maintaining journalistic style and factual accuracy.",
            "general": "Translate this general text maintaining natural flow and appropriate tone."
        }
    
    async def translate_text(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using LLM with cultural adaptation"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.translation_cache:
                cached_result = self.translation_cache[cache_key]
                return TranslationResponse(
                    request_id=request.request_id,
                    translated_text=cached_result["text"],
                    source_language=request.source_language,
                    target_language=request.target_language,
                    target_dialect=request.target_dialect,
                    confidence_score=cached_result["confidence"],
                    translation_method="cache",
                    processing_time=0.001,
                    timestamp=datetime.now(timezone.utc)
                )
            
            # Determine model based on priority
            model = self._determine_model(request.priority, request.source_language, request.target_language)
            
            # Create translation prompt
            prompt = self._create_translation_prompt(request)
            
            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a professional translator specializing in {request.target_language.value} with expertise in {self.context_templates.get(request.context, 'general')}. 
                        
                        Translation requirements:
                        1. Maintain accuracy and natural flow
                        2. Adapt cultural references appropriately
                        3. Use correct terminology for the context
                        4. Preserve the original meaning and tone
                        5. If dialect is specified, use appropriate regional variations
                        
                        Target language: {request.target_language.value}
                        Target dialect: {request.target_dialect or 'Standard'}
                        Context: {request.context}
                        """
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                request.source_text, translated_text, model
            )
            
            # Cache result
            self.translation_cache[cache_key] = {
                "text": translated_text,
                "confidence": confidence_score,
                "timestamp": datetime.now(timezone.utc)
            }
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return TranslationResponse(
                request_id=request.request_id,
                translated_text=translated_text,
                source_language=request.source_language,
                target_language=request.target_language,
                target_dialect=request.target_dialect,
                confidence_score=confidence_score,
                translation_method="llm",
                processing_time=processing_time,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return TranslationResponse(
                request_id=request.request_id,
                translated_text="",
                source_language=request.source_language,
                target_language=request.target_language,
                target_dialect=request.target_dialect,
                confidence_score=0.0,
                translation_method="error",
                processing_time=0.0,
                timestamp=datetime.now(timezone.utc)
            )
    
    def _determine_model(self, priority: str, source_lang: LanguageCode, target_lang: LanguageCode) -> str:
        """Determine which model to use based on priority and languages"""
        # Check if either language is a priority language
        priority_check = (
            source_lang.value in self.priority_languages or
            target_lang.value in self.priority_languages
        )
        
        if priority == "high" or priority_check:
            return self.translation_models["high_priority"]
        elif priority == "batch":
            return self.translation_models["batch"]
        else:
            return self.translation_models["standard"]
    
    def _create_translation_prompt(self, request: TranslationRequest) -> str:
        """Create translation prompt for LLM"""
        source_lang_name = self._get_language_name(request.source_language)
        target_lang_name = self._get_language_name(request.target_language)
        
        dialect_info = ""
        if request.target_dialect:
            dialect_mapping = self.dialect_mappings.get(request.target_language.value, {})
            dialect_info = f"\nTarget dialect: {dialect_mapping.get(request.target_dialect, request.target_dialect)}"
        
        context_info = self.context_templates.get(request.context, self.context_templates["general"])
        
        prompt = f"""Please translate the following text from {source_lang_name} to {target_lang_name}{dialect_info}.

Context: {context_info}

Source text:
{request.source_text}

Translation:"""
        
        return prompt
    
    def _get_language_name(self, language: LanguageCode) -> str:
        """Get full language name"""
        language_names = {
            LanguageCode.AMHARIC: "Amharic",
            LanguageCode.ENGLISH: "English",
            LanguageCode.ARABIC: "Arabic",
            LanguageCode.MANDARIN: "Mandarin Chinese",
            LanguageCode.SPANISH: "Spanish",
            LanguageCode.FRENCH: "French",
            LanguageCode.GERMAN: "German",
            LanguageCode.JAPANESE: "Japanese",
            LanguageCode.KOREAN: "Korean",
            LanguageCode.RUSSIAN: "Russian",
            LanguageCode.PORTUGUESE: "Portuguese",
            LanguageCode.ITALIAN: "Italian",
            LanguageCode.HINDI: "Hindi",
            LanguageCode.BENGALI: "Bengali",
            LanguageCode.URDU: "Urdu",
            LanguageCode.INDONESIAN: "Indonesian",
            LanguageCode.MALAY: "Malay",
            LanguageCode.THAI: "Thai",
            LanguageCode.VIETNAMESE: "Vietnamese",
            LanguageCode.SWAHILI: "Swahili",
            LanguageCode.HAUSA: "Hausa",
            LanguageCode.YORUBA: "Yoruba",
            LanguageCode.IGBO: "Igbo",
            LanguageCode.ZULU: "Zulu",
            LanguageCode.AFRIKAANS: "Afrikaans",
            LanguageCode.DUTCH: "Dutch",
            LanguageCode.SWEDISH: "Swedish",
            LanguageCode.NORWEGIAN: "Norwegian",
            LanguageCode.DANISH: "Danish",
            LanguageCode.FINNISH: "Finnish",
            LanguageCode.POLISH: "Polish",
            LanguageCode.CZECH: "Czech",
            LanguageCode.SLOVAK: "Slovak",
            LanguageCode.HUNGARIAN: "Hungarian",
            LanguageCode.ROMANIAN: "Romanian",
            LanguageCode.BULGARIAN: "Bulgarian",
            LanguageCode.CROATIAN: "Croatian",
            LanguageCode.SERBIAN: "Serbian",
            LanguageCode.SLOVENIAN: "Slovenian",
            LanguageCode.ESTONIAN: "Estonian",
            LanguageCode.LATVIAN: "Latvian",
            LanguageCode.LITHUANIAN: "Lithuanian",
            LanguageCode.GREEK: "Greek",
            LanguageCode.HEBREW: "Hebrew",
            LanguageCode.TURKISH: "Turkish",
            LanguageCode.PERSIAN: "Persian",
            LanguageCode.KURDISH: "Kurdish",
            LanguageCode.ARMENIAN: "Armenian",
            LanguageCode.AZERBAIJANI: "Azerbaijani",
            LanguageCode.GEORGIAN: "Georgian",
            LanguageCode.KAZAKH: "Kazakh",
            LanguageCode.UZBEK: "Uzbek",
            LanguageCode.TAJIK: "Tajik",
            LanguageCode.KYRGYZ: "Kyrgyz",
            LanguageCode.MONGOLIAN: "Mongolian",
            LanguageCode.NEPALI: "Nepali",
            LanguageCode.SINHALA: "Sinhala",
            LanguageCode.TAMIL: "Tamil",
            LanguageCode.TELUGU: "Telugu",
            LanguageCode.MARATHI: "Marathi",
            LanguageCode.GUJARATI: "Gujarati",
            LanguageCode.KANNADA: "Kannada",
            LanguageCode.MALAYALAM: "Malayalam",
            LanguageCode.PUNJABI: "Punjabi",
            LanguageCode.BURMESE: "Burmese",
            LanguageCode.KHMER: "Khmer",
            LanguageCode.LAO: "Lao",
            LanguageCode.TAGALOG: "Tagalog",
            LanguageCode.INDONESIAN_JAVANESE: "Javanese",
            LanguageCode.SUNDANESE: "Sundanese",
            LanguageCode.BALINESE: "Balinese",
            LanguageCode.MADURESE: "Madurese",
            LanguageCode.ACEHNESE: "Acehnese",
            LanguageCode.MINANGKABAU: "Minangkabau",
            LanguageCode.BUGINESE: "Buginese",
            LanguageCode.MAKASARESE: "Makasarese",
            LanguageCode.TOLAI: "Tolai",
            LanguageCode.FIJIAN: "Fijian",
            LanguageCode.SAMOAN: "Samoan",
            LanguageCode.TONGAN: "Tongan",
            LanguageCode.MAORI: "Maori",
            LanguageCode.HAWAIIAN: "Hawaiian",
            LanguageCode.CHAMORRO: "Chamorro",
            LanguageCode.PALAUAN: "Palauan",
            LanguageCode.MARSHALLESE: "Marshallese",
            LanguageCode.KIRIBATI: "Kiribati",
            LanguageCode.TUVALUAN: "Tuvaluan",
            LanguageCode.NAURUAN: "Nauruan",
            LanguageCode.MICRONESIAN: "Micronesian"
        }
        
        return language_names.get(language, language.value)
    
    def _calculate_confidence_score(self, source_text: str, translated_text: str, model: str) -> float:
        """Calculate confidence score for translation"""
        try:
            # Base confidence based on model
            model_confidence = {
                "gpt-4-turbo-preview": 0.95,
                "gpt-3.5-turbo": 0.85,
                "gpt-3.5-turbo": 0.85
            }
            
            base_confidence = model_confidence.get(model, 0.8)
            
            # Adjust based on text length
            if len(source_text) < 10:
                base_confidence -= 0.1
            elif len(source_text) > 1000:
                base_confidence -= 0.05
            
            # Adjust based on complexity (simple heuristic)
            complexity_indicators = ["technical", "legal", "financial", "specification"]
            for indicator in complexity_indicators:
                if indicator in source_text.lower():
                    base_confidence -= 0.02
            
            return max(0.5, min(1.0, base_confidence))
            
        except Exception as e:
            logger.error(f"Confidence score calculation failed: {str(e)}")
            return 0.8
    
    def _generate_cache_key(self, request: TranslationRequest) -> str:
        """Generate cache key for translation"""
        key_data = f"{request.source_language.value}_{request.target_language.value}_{request.target_dialect}_{request.context}_{hashlib.sha256(request.source_text.encode()).hexdigest()}"
        return hashlib.sha256(key_data.encode()).hexdigest()

class DisputeResolutionAgent:
    """Dispute resolution agent with OECD 2026 compliance"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.getenv("OPENAI_ORG_ID")
        )
        
        self.compliance_standards = {
            ComplianceStandard.OECD_2026: self._get_oecd_2026_rules(),
            ComplianceStandard.ISO_20400: self._get_iso_20400_rules(),
            ComplianceStandard.RMI_STANDARD: self._get_rmi_rules(),
            ComplianceStandard.LME_RESPONSIBLE: self._get_lme_rules(),
            ComplianceStandard.EU_CONFLICT_MINERALS: self._get_eu_conflict_rules(),
            ComplianceStandard.US_CONFLICT_MINERALS: self._get_us_conflict_rules()
        }
        
        self.resolution_strategies = {
            "negotiation": "Facilitate direct negotiation between parties",
            "mediation": "Provide neutral third-party mediation",
            "arbitration": "Implement binding arbitration process",
            "compliance_enforcement": "Apply compliance standards for resolution",
            "escalation": "Escalate to higher authority if needed"
        }
    
    def _get_oecd_2026_rules(self) -> Dict[str, Any]:
        """Get OECD 2026 due diligence rules"""
        return {
            "name": "OECD Due Diligence Guidance 2026",
            "principles": [
                "Establish strong company management systems",
                "Identify and assess risks in supply chain",
                "Design and implement strategy to respond to risks",
                "Carry out independent third-party audit",
                "Report annually on supply chain due diligence"
            ],
            "requirements": [
                "Risk assessment procedures",
                "Supply chain transparency",
                "Stakeholder engagement",
                "Continuous monitoring",
                "Remediation processes"
            ]
        }
    
    def _get_iso_20400_rules(self) -> Dict[str, Any]:
        """Get ISO 20400 sustainable procurement rules"""
        return {
            "name": "ISO 20400 Sustainable Procurement",
            "principles": [
                "Accountability",
                "Transparency",
                "Ethical behavior",
                "Respect for human rights",
                "Environmental protection"
            ],
            "requirements": [
                "Sustainable procurement policy",
                "Supplier assessment",
                "Life cycle thinking",
                "Continuous improvement"
            ]
        }
    
    def _get_rmi_rules(self) -> Dict[str, Any]:
        """Get Responsible Minerals Initiative rules"""
        return {
            "name": "RMI Standard",
            "principles": [
                "Conflict-free sourcing",
                "Supply chain due diligence",
                "Responsible mining practices",
                "Community engagement"
            ],
            "requirements": [
                "Chain of custody verification",
                "Smelter/refiner due diligence",
                "Risk management",
                "Transparency reporting"
            ]
        }
    
    def _get_lme_rules(self) -> Dict[str, Any]:
        """Get LME responsible sourcing rules"""
        return {
            "name": "LME Responsible Sourcing",
            "principles": [
                "Responsible sourcing",
                "Environmental stewardship",
                "Social responsibility",
                "Governance"
            ],
            "requirements": [
                "Due diligence processes",
                "Risk assessment",
                "Stakeholder engagement",
                "Continuous improvement"
            ]
        }
    
    def _get_eu_conflict_rules(self) -> Dict[str, Any]:
        """Get EU Conflict Minerals Regulation rules"""
        return {
            "name": "EU Conflict Minerals Regulation",
            "principles": [
                "Due diligence obligation",
                "Supply chain transparency",
                "Risk management",
                "Stakeholder engagement"
            ],
            "requirements": [
                "Supply chain due diligence",
                "Risk assessment",
                "Mitigation measures",
                "Reporting obligations"
            ]
        }
    
    def _get_us_conflict_rules(self) -> Dict[str, Any]:
        """Get US Conflict Minerals Rule rules"""
        return {
            "name": "US Conflict Minerals Rule (Section 1502)",
            "principles": [
                "Due diligence requirement",
                "Supply chain transparency",
                "Conflict-free sourcing",
                "Reporting obligation"
            ],
            "requirements": [
                "Due diligence processes",
                "Chain of custody verification",
                "Risk assessment",
                "Annual reporting"
            ]
        }
    
    async def resolve_dispute(self, request: DisputeRequest) -> DisputeResponse:
        """Resolve dispute using LLM with compliance analysis"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get compliance standard rules
            compliance_rules = self.compliance_standards.get(request.compliance_standard)
            
            # Create resolution prompt
            prompt = self._create_resolution_prompt(request, compliance_rules)
            
            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert dispute resolution specialist with deep knowledge of {compliance_rules['name']} and international trade law.
                        
                        Your task is to analyze the dispute and provide a fair, compliant resolution that:
                        1. Follows the applicable compliance standard
                        2. Protects all parties' interests
                        3. Maintains business relationships where possible
                        4. Provides clear, actionable recommendations
                        5. Ensures regulatory compliance
                        
                        Compliance Standard: {compliance_rules['name']}
                        Principles: {', '.join(compliance_rules['principles'])}
                        Requirements: {', '.join(compliance_rules['requirements'])}
                        """
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            resolution_text = response.choices[0].message.content.strip()
            
            # Parse resolution components
            resolution_components = self._parse_resolution_response(resolution_text)
            
            # Calculate confidence score
            confidence_score = self._calculate_dispute_confidence(request, resolution_components)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return DisputeResponse(
                dispute_id=request.dispute_id,
                resolution=resolution_components.get("resolution", ""),
                reasoning=resolution_components.get("reasoning", ""),
                compliance_analysis=resolution_components.get("compliance_analysis", {}),
                recommended_actions=resolution_components.get("recommended_actions", []),
                confidence_score=confidence_score,
                processing_time=processing_time,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Dispute resolution failed: {str(e)}")
            return DisputeResponse(
                dispute_id=request.dispute_id,
                resolution="",
                reasoning="",
                compliance_analysis={},
                recommended_actions=[],
                confidence_score=0.0,
                processing_time=0.0,
                timestamp=datetime.now(timezone.utc)
            )
    
    def _create_resolution_prompt(self, request: DisputeRequest, compliance_rules: Dict[str, Any]) -> str:
        """Create dispute resolution prompt"""
        parties_str = ", ".join(request.parties)
        evidence_str = "\n".join([f"- {e.get('type', 'Unknown')}: {e.get('content', 'No content')}" for e in request.evidence])
        
        prompt = f"""Please analyze and resolve the following dispute according to {compliance_rules['name']}. 

Dispute Details:
- Dispute ID: {request.dispute_id}
- Parties: {parties_str}
- Dispute Type: {request.dispute_type}
- Description: {request.description}
- Evidence: {evidence_str}
- Priority: {request.priority}

Please provide:
1. A fair and balanced resolution
2. Detailed reasoning for your decision
3. Compliance analysis based on the applicable standard
4. Recommended actions for each party
5. Risk assessment and mitigation strategies

Format your response as follows:

RESOLUTION:
[Your resolution here]

REASONING:
[Your detailed reasoning here]

COMPLIANCE_ANALYSIS:
[Analysis of how the resolution complies with the standard]

RECOMMENDED_ACTIONS:
- [Action 1]
- [Action 2]
- [Action 3]

RISK_ASSESSMENT:
[Risk assessment and mitigation]"""
        
        return prompt
    
    def _parse_resolution_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        components = {
            "resolution": "",
            "reasoning": "",
            "compliance_analysis": {},
            "recommended_actions": []
        }
        
        try:
            sections = response_text.split("\n\n")
            
            for section in sections:
                if section.startswith("RESOLUTION:"):
                    components["resolution"] = section.replace("RESOLUTION:", "").strip()
                elif section.startswith("REASONING:"):
                    components["reasoning"] = section.replace("REASONING:", "").strip()
                elif section.startswith("COMPLIANCE_ANALYSIS:"):
                    components["compliance_analysis"] = {
                        "analysis": section.replace("COMPLIANCE_ANALYSIS:", "").strip()
                    }
                elif section.startswith("RECOMMENDED_ACTIONS:"):
                    actions = section.replace("RECOMMENDED_ACTIONS:", "").strip()
                    components["recommended_actions"] = [
                        action.strip().replace("- ", "") 
                        for action in actions.split("\n") 
                        if action.strip()
                    ]
        except Exception as e:
            logger.error(f"Response parsing failed: {str(e)}")
            # Fallback to full text as resolution
            components["resolution"] = response_text
        
        return components
    
    def _calculate_dispute_confidence(self, request: DisputeRequest, components: Dict[str, Any]) -> float:
        """Calculate confidence score for dispute resolution"""
        try:
            base_confidence = 0.85
            
            # Adjust based on completeness
            if components["resolution"]:
                base_confidence += 0.05
            if components["reasoning"]:
                base_confidence += 0.05
            if components["compliance_analysis"]:
                base_confidence += 0.03
            if components["recommended_actions"]:
                base_confidence += 0.02
            
            # Adjust based on evidence quality
            if len(request.evidence) >= 3:
                base_confidence += 0.05
            elif len(request.evidence) >= 1:
                base_confidence += 0.02
            
            # Adjust based on dispute complexity
            if request.dispute_type in ["payment_dispute", "quality_issue", "delivery_delay"]:
                base_confidence += 0.05
            elif request.dispute_type in ["contract_breach", "regulatory_violation"]:
                base_confidence -= 0.05
            
            return max(0.5, min(1.0, base_confidence))
            
        except Exception as e:
            logger.error(f"Dispute confidence calculation failed: {str(e)}")
            return 0.8

class AgenticOrchestrator:
    """Main agentic orchestrator for translation and dispute resolution"""
    
    def __init__(self):
        self.translation_agent = MultilingualTranslationAgent()
        self.dispute_agent = DisputeResolutionAgent()
        
        self.active_tasks = {}
        self.task_queue = asyncio.Queue()
        self.max_concurrent_tasks = 10
        self.orchestrator_active = True
        
        # MCP compatibility
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "https://api.mcp.dedanmine.io")
        self.mcp_api_key = os.getenv("MCP_API_KEY")
        
        # Start task processor
        asyncio.create_task(self._process_tasks())
    
    async def _process_tasks(self):
        """Process tasks from queue"""
        while self.orchestrator_active:
            try:
                task = await self.task_queue.get()
                
                # Update task status
                task.started_at = datetime.now(timezone.utc)
                task.status = "processing"
                
                # Process task based on capability
                if task.capability == AgentCapability.TRANSLATION:
                    result = await self._process_translation_task(task)
                elif task.capability == AgentCapability.DISPUTE_RESOLUTION:
                    result = await self._process_dispute_task(task)
                else:
                    result = {"success": False, "error": f"Unsupported capability: {task.capability.value}"}
                
                # Update task result
                task.completed_at = datetime.now(timezone.utc)
                task.result = result
                task.status = "completed" if result.get("success", False) else "failed"
                
                # Clean up old tasks
                await self._cleanup_old_tasks()
                
            except Exception as e:
                logger.error(f"Task processing failed: {str(e)}")
    
    async def _process_translation_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process translation task"""
        try:
            request_data = task.request_data
            translation_request = TranslationRequest(
                request_id=task.task_id,
                source_text=request_data["source_text"],
                source_language=LanguageCode(request_data["source_language"]),
                target_language=LanguageCode(request_data["target_language"]),
                target_dialect=request_data.get("target_dialect"),
                context=request_data.get("context", "general"),
                priority=request_data.get("priority", "standard"),
                user_id=request_data["user_id"],
                timestamp=datetime.now(timezone.utc)
            )
            
            result = await self.translation_agent.translate_text(translation_request)
            
            return {
                "success": True,
                "translation": {
                    "request_id": result.request_id,
                    "translated_text": result.translated_text,
                    "source_language": result.source_language.value,
                    "target_language": result.target_language.value,
                    "target_dialect": result.target_dialect,
                    "confidence_score": result.confidence_score,
                    "translation_method": result.translation_method,
                    "processing_time": result.processing_time
                }
            }
            
        except Exception as e:
            logger.error(f"Translation task processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _process_dispute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process dispute resolution task"""
        try:
            request_data = task.request_data
            dispute_request = DisputeRequest(
                dispute_id=task.task_id,
                parties=request_data["parties"],
                dispute_type=request_data["dispute_type"],
                description=request_data["description"],
                evidence=request_data.get("evidence", []),
                compliance_standard=ComplianceStandard(request_data["compliance_standard"]),
                priority=request_data.get("priority", "standard"),
                user_id=request_data["user_id"],
                timestamp=datetime.now(timezone.utc)
            )
            
            result = await self.dispute_agent.resolve_dispute(dispute_request)
            
            return {
                "success": True,
                "dispute_resolution": {
                    "dispute_id": result.dispute_id,
                    "resolution": result.resolution,
                    "reasoning": result.reasoning,
                    "compliance_analysis": result.compliance_analysis,
                    "recommended_actions": result.recommended_actions,
                    "confidence_score": result.confidence_score,
                    "processing_time": result.processing_time
                }
            }
            
        except Exception as e:
            logger.error(f"Dispute task processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def submit_translation_task(self, source_text: str, source_language: str, target_language: str, 
                                    target_dialect: Optional[str] = None, context: str = "general",
                                    priority: str = "standard", user_id: str = "anonymous") -> Dict[str, Any]:
        """Submit translation task"""
        try:
            task_id = f"TRANS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(source_text.encode()).hexdigest()[:8]}"
            
            task = AgentTask(
                task_id=task_id,
                capability=AgentCapability.TRANSLATION,
                request_data={
                    "source_text": source_text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "target_dialect": target_dialect,
                    "context": context,
                    "priority": priority,
                    "user_id": user_id
                },
                status="queued",
                created_at=datetime.now(timezone.utc),
                started_at=None,
                completed_at=None,
                result=None,
                error=None
            )
            
            self.active_tasks[task_id] = task
            await self.task_queue.put(task)
            
            return {
                "success": True,
                "task_id": task_id,
                "status": "queued",
                "estimated_completion": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Translation task submission failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def submit_dispute_task(self, parties: List[str], dispute_type: str, description: str,
                                evidence: List[Dict[str, Any]], compliance_standard: str,
                                priority: str = "standard", user_id: str = "anonymous") -> Dict[str, Any]:
        """Submit dispute resolution task"""
        try:
            task_id = f"DISPUTE_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(description.encode()).hexdigest()[:8]}"
            
            task = AgentTask(
                task_id=task_id,
                capability=AgentCapability.DISPUTE_RESOLUTION,
                request_data={
                    "parties": parties,
                    "dispute_type": dispute_type,
                    "description": description,
                    "evidence": evidence,
                    "compliance_standard": compliance_standard,
                    "priority": priority,
                    "user_id": user_id
                },
                status="queued",
                created_at=datetime.now(timezone.utc),
                started_at=None,
                completed_at=None,
                result=None,
                error=None
            )
            
            self.active_tasks[task_id] = task
            await self.task_queue.put(task)
            
            return {
                "success": True,
                "task_id": task_id,
                "status": "queued",
                "estimated_completion": (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dispute task submission failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        try:
            task = self.active_tasks.get(task_id)
            
            if not task:
                return {
                    "success": False,
                    "error": f"Task not found: {task_id}"
                }
            
            response = {
                "success": True,
                "task_id": task_id,
                "capability": task.capability.value,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "result": task.result,
                "error": task.error
            }
            
            if task.status == "completed" and task.result:
                response["processing_time"] = (
                    task.completed_at - task.started_at
                ).total_seconds() if task.started_at and task.completed_at else 0
            
            return response
            
        except Exception as e:
            logger.error(f"Task status retrieval failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _cleanup_old_tasks(self):
        """Clean up old completed tasks"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            
            tasks_to_remove = [
                task_id for task_id, task in self.active_tasks.items()
                if task.status == "completed" and task.completed_at and task.completed_at < cutoff_time
            ]
            
            for task_id in tasks_to_remove:
                del self.active_tasks[task_id]
                
        except Exception as e:
            logger.error(f"Task cleanup failed: {str(e)}")
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        try:
            active_tasks = len(self.active_tasks)
            queued_tasks = sum(1 for task in self.active_tasks.values() if task.status == "queued")
            processing_tasks = sum(1 for task in self.active_tasks.values() if task.status == "processing")
            completed_tasks = sum(1 for task in self.active_tasks.values() if task.status == "completed")
            
            return {
                "orchestrator_active": self.orchestrator_active,
                "active_tasks": active_tasks,
                "queued_tasks": queued_tasks,
                "processing_tasks": processing_tasks,
                "completed_tasks": completed_tasks,
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "supported_languages": len(LanguageCode),
                "priority_languages": list(self.translation_agent.priority_languages.keys()),
                "compliance_standards": [standard.value for standard in ComplianceStandard],
                "mcp_compatible": True,
                "mcp_server_url": self.mcp_server_url,
                "status_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Orchestrator status retrieval failed: {str(e)}")
            return {"error": str(e)}

# Global instance
agentic_orchestrator = AgenticOrchestrator()

# API endpoints
async def translate_text_api(source_text: str, source_language: str, target_language: str,
                           target_dialect: Optional[str] = None, context: str = "general",
                           priority: str = "standard", user_id: str = "anonymous") -> Dict[str, Any]:
    """API endpoint for text translation"""
    return await agentic_orchestrator.submit_translation_task(
        source_text, source_language, target_language, target_dialect, context, priority, user_id
    )

async def resolve_dispute_api(parties: List[str], dispute_type: str, description: str,
                            evidence: List[Dict[str, Any]], compliance_standard: str,
                            priority: str = "standard", user_id: str = "anonymous") -> Dict[str, Any]:
    """API endpoint for dispute resolution"""
    return await agentic_orchestrator.submit_dispute_task(
        parties, dispute_type, description, evidence, compliance_standard, priority, user_id
    )

async def get_task_status_api(task_id: str) -> Dict[str, Any]:
    """API endpoint for task status"""
    return await agentic_orchestrator.get_task_status(task_id)

async def get_orchestrator_status_api() -> Dict[str, Any]:
    """API endpoint for orchestrator status"""
    return await agentic_orchestrator.get_orchestrator_status()
