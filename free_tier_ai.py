"""
DEDAN Mine - Free Tier AI Services (v3.1.0)
Groq + Gemini AI integration for zero-cost translation and processing
Local i18next JSON files for static translations
Dynamic AI translation with free tier limits
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import aiohttp
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Free tier AI providers"""
    GROQ = "groq"
    GEMINI = "gemini"
    LOCAL = "local"

class TranslationMode(Enum):
    """Translation modes"""
    STATIC = "static"  # Use local JSON files
    DYNAMIC = "dynamic"  # Use AI for dynamic translation
    HYBRID = "hybrid"  # Use static for common, AI for dynamic

@dataclass
class TranslationRequest:
    """Translation request structure"""
    text: str
    source_lang: str
    target_lang: str
    context: str = "general"
    mode: TranslationMode = TranslationMode.HYBRID
    priority: str = "normal"

@dataclass
class TranslationResponse:
    """Translation response structure"""
    success: bool
    translated_text: str
    provider: AIProvider
    mode: TranslationMode
    confidence: float
    cached: bool
    tokens_used: int = 0
    cost: float = 0.0

class LocalTranslationManager:
    """Local translation manager using i18next JSON files"""
    
    def __init__(self):
        self.translations_dir = Path("frontend/public/locales")
        self.supported_languages = ["en", "am", "ar", "zh", "es", "fr", "de", "ja", "ko"]
        self.static_translations = {}
        self.load_static_translations()
    
    def load_static_translations(self):
        """Load static translations from JSON files"""
        try:
            for lang in self.supported_languages:
                translation_file = self.translations_dir / f"{lang}/translation.json"
                if translation_file.exists():
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.static_translations[lang] = json.load(f)
                else:
                    # Create empty translation file
                    self.static_translations[lang] = {}
                    translation_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(translation_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Loaded static translations for {len(self.static_translations)} languages")
            
        except Exception as e:
            logger.error(f"Failed to load static translations: {str(e)}")
    
    def get_static_translation(self, key: str, lang: str, default: str = None) -> str:
        """Get static translation by key"""
        try:
            if lang not in self.static_translations:
                return default or key
            
            # Navigate nested keys (e.g., "common.buttons.save")
            keys = key.split('.')
            value = self.static_translations[lang]
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default or key
            
            return value if isinstance(value, str) else (default or key)
            
        except Exception as e:
            logger.error(f"Static translation failed: {str(e)}")
            return default or key
    
    def add_static_translation(self, lang: str, key: str, value: str):
        """Add static translation"""
        try:
            if lang not in self.static_translations:
                self.static_translations[lang] = {}
            
            # Navigate nested keys
            keys = key.split('.')
            current = self.static_translations[lang]
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
            # Save to file
            translation_file = self.translations_dir / f"{lang}/translation.json"
            translation_file.parent.mkdir(parents=True, exist_ok=True)
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(self.static_translations[lang], f, indent=2, ensure_ascii=False)
            
            logger.info(f"Added static translation: {lang}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to add static translation: {str(e)}")

class GroqAIManager:
    """Groq AI manager for free tier"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama3-8b-8192"
        self.limits = {
            "requests_per_day": 1440,
            "tokens_per_day": 100000,
            "concurrent_requests": 1
        }
        self.usage_today = {
            "requests": 0,
            "tokens": 0
        }
        self.session = None
    
    async def get_session(self):
        """Get HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self.session
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str, context: str = "general") -> Dict[str, Any]:
        """Translate text using Groq"""
        try:
            # Check limits
            if self.usage_today["requests"] >= self.limits["requests_per_day"]:
                return {
                    "success": False,
                    "error": "Daily request limit exceeded"
                }
            
            session = await self.get_session()
            
            # Create translation prompt
            prompt = f"""Translate the following text from {source_lang} to {target_lang}. 
Context: {context}
Text: {text}
Translation:"""
            
            # Make API request
            async with session.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional translator. Provide accurate, natural translations while preserving the original meaning and tone."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.3
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    translated_text = data["choices"][0]["message"]["content"].strip()
                    tokens_used = data.get("usage", {}).get("total_tokens", 0)
                    
                    # Update usage
                    self.usage_today["requests"] += 1
                    self.usage_today["tokens"] += tokens_used
                    
                    return {
                        "success": True,
                        "translated_text": translated_text,
                        "tokens_used": tokens_used,
                        "provider": "groq"
                    }
                else:
                    error_data = await response.text()
                    logger.error(f"Groq API error: {response.status} - {error_data}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Groq translation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

class GeminiAIManager:
    """Google Gemini AI manager for free tier"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-flash"
        self.limits = {
            "requests_per_minute": 15,
            "tokens_per_minute": 32000,
            "requests_per_day": 1500
        }
        self.usage_today = {
            "requests": 0,
            "tokens": 0
        }
        self.session = None
    
    async def get_session(self):
        """Get HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str, context: str = "general") -> Dict[str, Any]:
        """Translate text using Gemini"""
        try:
            # Check limits
            if self.usage_today["requests"] >= self.limits["requests_per_day"]:
                return {
                    "success": False,
                    "error": "Daily request limit exceeded"
                }
            
            session = await self.get_session()
            
            # Create translation prompt
            prompt = f"""Translate the following text from {source_lang} to {target_lang}. 
Context: {context}
Text: {text}
Translation:"""
            
            # Make API request
            async with session.post(
                f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "maxOutputTokens": 1000,
                        "temperature": 0.3
                    }
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    translated_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    tokens_used = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                    
                    # Update usage
                    self.usage_today["requests"] += 1
                    self.usage_today["tokens"] += tokens_used
                    
                    return {
                        "success": True,
                        "translated_text": translated_text,
                        "tokens_used": tokens_used,
                        "provider": "gemini"
                    }
                else:
                    error_data = await response.text()
                    logger.error(f"Gemini API error: {response.status} - {error_data}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Gemini translation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

class FreeTierAITranslator:
    """Free tier AI translator with fallback logic"""
    
    def __init__(self):
        self.local_manager = LocalTranslationManager()
        
        # Initialize AI managers
        groq_api_key = os.getenv("GROQ_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        self.groq_manager = GroqAIManager(groq_api_key) if groq_api_key else None
        self.gemini_manager = GeminiAIManager(gemini_api_key) if gemini_api_key else None
        
        # Translation cache
        self.translation_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Provider priority
        self.provider_priority = [AIProvider.LOCAL, AIProvider.GROQ, AIProvider.GEMINI]
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key"""
        import hashlib
        key_data = f"{source_lang}:{target_lang}:{text}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check translation cache"""
        try:
            if cache_key in self.translation_cache:
                cached = self.translation_cache[cache_key]
                import time
                if time.time() - cached["timestamp"] < self.cache_ttl:
                    return cached["translation"]
        except Exception as e:
            logger.error(f"Cache check failed: {str(e)}")
        return None
    
    def _store_cache(self, cache_key: str, translation: str):
        """Store translation in cache"""
        try:
            import time
            self.translation_cache[cache_key] = {
                "translation": translation,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Cache storage failed: {str(e)}")
    
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text with free tier AI"""
        try:
            # Check cache first
            cache_key = self._get_cache_key(request.text, request.source_lang, request.target_lang)
            cached_translation = self._check_cache(cache_key)
            
            if cached_translation:
                return TranslationResponse(
                    success=True,
                    translated_text=cached_translation,
                    provider=AIProvider.LOCAL,
                    mode=request.mode,
                    confidence=1.0,
                    cached=True
                )
            
            # Try static translation first for common phrases
            if request.mode in [TranslationMode.STATIC, TranslationMode.HYBRID]:
                static_translation = self.local_manager.get_static_translation(
                    request.text, request.target_lang, request.text
                )
                
                if static_translation != request.text:
                    self._store_cache(cache_key, static_translation)
                    return TranslationResponse(
                        success=True,
                        translated_text=static_translation,
                        provider=AIProvider.LOCAL,
                        mode=TranslationMode.STATIC,
                        confidence=0.95,
                        cached=False
                    )
            
            # Use AI for dynamic translation
            if request.mode in [TranslationMode.DYNAMIC, TranslationMode.HYBRID]:
                # Try Groq first
                if self.groq_manager:
                    result = await self.groq_manager.translate_text(
                        request.text, request.source_lang, request.target_lang, request.context
                    )
                    
                    if result["success"]:
                        self._store_cache(cache_key, result["translated_text"])
                        return TranslationResponse(
                            success=True,
                            translated_text=result["translated_text"],
                            provider=AIProvider.GROQ,
                            mode=TranslationMode.DYNAMIC,
                            confidence=0.85,
                            cached=False,
                            tokens_used=result["tokens_used"]
                        )
                
                # Try Gemini as fallback
                if self.gemini_manager:
                    result = await self.gemini_manager.translate_text(
                        request.text, request.source_lang, request.target_lang, request.context
                    )
                    
                    if result["success"]:
                        self._store_cache(cache_key, result["translated_text"])
                        return TranslationResponse(
                            success=True,
                            translated_text=result["translated_text"],
                            provider=AIProvider.GEMINI,
                            mode=TranslationMode.DYNAMIC,
                            confidence=0.80,
                            cached=False,
                            tokens_used=result["tokens_used"]
                        )
            
            # Fallback to original text
            return TranslationResponse(
                success=False,
                translated_text=request.text,
                provider=AIProvider.LOCAL,
                mode=request.mode,
                confidence=0.0,
                cached=False
            )
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return TranslationResponse(
                success=False,
                translated_text=request.text,
                provider=AIProvider.LOCAL,
                mode=request.mode,
                confidence=0.0,
                cached=False
            )
    
    async def batch_translate(self, requests: List[TranslationRequest]) -> List[TranslationResponse]:
        """Batch translate multiple requests"""
        results = []
        
        for request in requests:
            result = await self.translate(request)
            results.append(result)
            
            # Add small delay to respect rate limits
            await asyncio.sleep(0.1)
        
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        stats = {
            "cache_size": len(self.translation_cache),
            "static_languages": len(self.local_manager.static_translations),
            "providers": {}
        }
        
        if self.groq_manager:
            stats["providers"]["groq"] = {
                "available": True,
                "usage": self.groq_manager.usage_today,
                "limits": self.groq_manager.limits
            }
        
        if self.gemini_manager:
            stats["providers"]["gemini"] = {
                "available": True,
                "usage": self.gemini_manager.usage_today,
                "limits": self.gemini_manager.limits
            }
        
        return stats
    
    async def close(self):
        """Close all AI managers"""
        if self.groq_manager:
            await self.groq_manager.close()
        if self.gemini_manager:
            await self.gemini_manager.close()

# Global instance
free_tier_ai = FreeTierAITranslator()

# API endpoints
async def translate_text_api(text: str, source_lang: str, target_lang: str, 
                           context: str = "general", mode: str = "hybrid") -> Dict[str, Any]:
    """API endpoint for text translation"""
    try:
        request = TranslationRequest(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            context=context,
            mode=TranslationMode(mode)
        )
        
        result = await free_tier_ai.translate(request)
        
        return {
            "success": result.success,
            "translated_text": result.translated_text,
            "provider": result.provider.value,
            "mode": result.mode.value,
            "confidence": result.confidence,
            "cached": result.cached,
            "tokens_used": result.tokens_used
        }
        
    except Exception as e:
        logger.error(f"Translation API failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_ai_usage_stats_api() -> Dict[str, Any]:
    """API endpoint for AI usage statistics"""
    return free_tier_ai.get_usage_stats()

async def add_static_translation_api(lang: str, key: str, value: str) -> Dict[str, Any]:
    """API endpoint for adding static translations"""
    try:
        free_tier_ai.local_manager.add_static_translation(lang, key, value)
        
        return {
            "success": True,
            "message": f"Added static translation: {lang}.{key}"
        }
        
    except Exception as e:
        logger.error(f"Add static translation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
