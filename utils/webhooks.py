"""
🪝 DEDAN 2.0 - UNIFIED WEBHOOK UTILITIES
Consolidated webhook handling and signature verification
Eliminates all duplicate webhook code across the codebase
"""

import os
import json
import hashlib
import hmac
import time
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
from enum import Enum
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class WebhookProvider(Enum):
    """Supported webhook providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    CHAPA = "chapa"
    WISE = "wise"
    SQUARE = "square"
    RAZORPAY = "razorpay"

class WebhookType(Enum):
    """Webhook event types"""
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_PENDING = "payment_pending"
    REFUND = "refund"
    DISPUTE = "dispute"
    SUBSCRIPTION = "subscription"
    ACCOUNT_UPDATE = "account_update"
    UNKNOWN = "unknown"

@dataclass
class WebhookEvent:
    """Webhook event structure"""
    provider: WebhookProvider
    event_type: WebhookType
    event_id: str
    data: Dict[str, Any]
    timestamp: datetime
    signature: str
    processed: bool = False
    retry_count: int = 0

class WebhookConfig:
    """Webhook configuration"""
    
    def __init__(self):
        self.secrets = {
            WebhookProvider.STRIPE: os.getenv("STRIPE_WEBHOOK_SECRET"),
            WebhookProvider.PAYPAL: os.getenv("PAYPAL_WEBHOOK_SECRET"),
            WebhookProvider.CHAPA: os.getenv("CHAPA_WEBHOOK_SECRET"),
            WebhookProvider.WISE: os.getenv("WISE_WEBHOOK_SECRET"),
            WebhookProvider.SQUARE: os.getenv("SQUARE_WEBHOOK_SECRET"),
            WebhookProvider.RAZORPAY: os.getenv("RAZORPAY_WEBHOOK_SECRET"),
        }
        
        self.retry_limits = {
            WebhookProvider.STRIPE: 3,
            WebhookProvider.PAYPAL: 5,
            WebhookProvider.CHAPA: 3,
            WebhookProvider.WISE: 3,
            WebhookProvider.SQUARE: 5,
            WebhookProvider.RAZORPAY: 3,
        }
        
        self.timeout_seconds = 30

class WebhookSignature:
    """Unified webhook signature verification"""
    
    def __init__(self, config: WebhookConfig = None):
        self.config = config or WebhookConfig()
    
    def verify_signature(self, payload: bytes, signature: str, provider: WebhookProvider) -> bool:
        """
        Verify webhook signature
        Consolidates duplicate implementations from:
        - edge_payment_webhooks.py
        - universal_payment_nexus.py
        """
        try:
            secret = self.config.secrets.get(provider)
            if not secret:
                logger.warning(f"No secret configured for provider {provider.value}")
                return False
            
            # Handle different signature formats
            if provider == WebhookProvider.STRIPE:
                return self._verify_stripe_signature(payload, signature, secret)
            elif provider == WebhookProvider.PAYPAL:
                return self._verify_paypal_signature(payload, signature, secret)
            elif provider == WebhookProvider.CHAPA:
                return self._verify_chapa_signature(payload, signature, secret)
            else:
                # Generic HMAC verification
                return self._verify_generic_signature(payload, signature, secret)
                
        except Exception as e:
            logger.error(f"Signature verification failed for {provider.value}: {e}")
            return False
    
    def _verify_stripe_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            # Stripe signatures are in format: t=timestamp,v1=signature
            if not signature.startswith('t='):
                return False
            
            elements = signature.split(',')
            timestamp = None
            expected_signature = None
            
            for element in elements:
                if element.startswith('t='):
                    timestamp = element[2:]
                elif element.startswith('v1='):
                    expected_signature = element[3:]
            
            if not timestamp or not expected_signature:
                return False
            
            # Verify timestamp is within tolerance (5 minutes)
            try:
                ts_int = int(timestamp)
                if abs(time.time() - ts_int) > 300:  # 5 minutes
                    return False
            except ValueError:
                return False
            
            # Construct signed payload
            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
            
            # Generate expected signature
            expected = hmac.new(
                secret.encode(),
                signed_payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, expected)
            
        except Exception as e:
            logger.error(f"Stripe signature verification failed: {e}")
            return False
    
    def _verify_paypal_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify PayPal webhook signature"""
        try:
            # PayPal uses different signature format
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"PayPal signature verification failed: {e}")
            return False
    
    def _verify_chapa_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Chapa webhook signature"""
        try:
            # Chapa uses SHA-256 HMAC
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Chapa signature verification failed: {e}")
            return False
    
    def _verify_generic_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Generic HMAC signature verification"""
        try:
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Allow for different signature formats
            return signature in [expected_signature, f"sha256={expected_signature}"]
            
        except Exception as e:
            logger.error(f"Generic signature verification failed: {e}")
            return False

class WebhookProcessor:
    """Unified webhook processing"""
    
    def __init__(self, config: WebhookConfig = None):
        self.config = config or WebboxConfig()
        self.signature_verifier = WebhookSignature(config)
        self.event_handlers: Dict[WebhookType, List[Callable]] = {}
    
    def register_handler(self, event_type: WebhookType, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def process_webhook(self, webhook_data: Dict[str, Any], provider: str, signature: str) -> Dict[str, Any]:
        """
        Process webhook at edge
        Consolidates duplicate implementations from multiple files
        """
        try:
            # Parse provider
            try:
                webhook_provider = WebhookProvider(provider.lower())
            except ValueError:
                logger.error(f"Unsupported webhook provider: {provider}")
                return {
                    "success": False,
                    "error": f"Unsupported provider: {provider}",
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Verify signature
            payload = json.dumps(webhook_data).encode()
            if not self.signature_verifier.verify_signature(payload, signature, webhook_provider):
                logger.warning(f"Invalid signature for provider {provider}")
                return {
                    "success": False,
                    "error": "Invalid signature",
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Parse webhook event
            event = self._parse_webhook_event(webhook_data, webhook_provider, signature)
            
            # Process event
            result = await self._process_event(event)
            
            return {
                "success": True,
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "provider": provider,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
    
    def _parse_webhook_event(self, webhook_data: Dict[str, Any], provider: WebhookProvider, signature: str) -> WebhookEvent:
        """Parse webhook event data"""
        try:
            # Extract event type based on provider
            event_type = self._determine_event_type(webhook_data, provider)
            
            # Extract event ID
            event_id = webhook_data.get('id') or webhook_data.get('event_id') or str(uuid.uuid4())
            
            return WebhookEvent(
                provider=provider,
                event_type=event_type,
                event_id=event_id,
                data=webhook_data,
                timestamp=datetime.now(timezone.utc),
                signature=signature
            )
            
        except Exception as e:
            logger.error(f"Failed to parse webhook event: {e}")
            # Return default event
            return WebhookEvent(
                provider=provider,
                event_type=WebhookType.UNKNOWN,
                event_id=str(uuid.uuid4()),
                data=webhook_data,
                timestamp=datetime.now(timezone.utc),
                signature=signature
            )
    
    def _determine_event_type(self, webhook_data: Dict[str, Any], provider: WebhookProvider) -> WebhookType:
        """
        Determine webhook event type
        Consolidates duplicate implementations from multiple files
        """
        try:
            if provider == WebhookProvider.STRIPE:
                event_type = webhook_data.get('type', '').lower()
                if 'payment_succeeded' in event_type:
                    return WebhookType.PAYMENT_SUCCESS
                elif 'payment_failed' in event_type:
                    return WebhookType.PAYMENT_FAILED
                elif 'payment_intent.payment_failed' in event_type:
                    return WebhookType.PAYMENT_FAILED
                elif 'payment_intent.succeeded' in event_type:
                    return WebhookType.PAYMENT_SUCCESS
                elif 'charge.succeeded' in event_type:
                    return WebhookType.PAYMENT_SUCCESS
                elif 'charge.failed' in event_type:
                    return WebhookType.PAYMENT_FAILED
                elif 'invoice.payment_succeeded' in event_type:
                    return WebhookType.PAYMENT_SUCCESS
                elif 'customer.subscription' in event_type:
                    return WebhookType.SUBSCRIPTION
                elif 'account.updated' in event_type:
                    return WebhookType.ACCOUNT_UPDATE
                elif 'charge.dispute' in event_type:
                    return WebhookType.DISPUTE
            
            elif provider == WebhookProvider.PAYPAL:
                event_type = webhook_data.get('event_type', '').lower()
                if 'payment_completed' in event_type:
                    return WebhookType.PAYMENT_SUCCESS
                elif 'payment_failed' in event_type:
                    return WebhookType.PAYMENT_FAILED
                elif 'payment_sale_completed' in event_type:
                    return WebhookType.PAYMENT_SUCCESS
                elif 'billing_subscription' in event_type:
                    return WebhookType.SUBSCRIPTION
            
            elif provider == WebhookProvider.CHAPA:
                status = webhook_data.get('status', '').lower()
                if status == 'success':
                    return WebhookType.PAYMENT_SUCCESS
                elif status == 'failed':
                    return WebhookType.PAYMENT_FAILED
                elif status == 'pending':
                    return WebhookType.PAYMENT_PENDING
            
            # Generic fallback
            if 'payment' in str(webhook_data).lower():
                if 'success' in str(webhook_data).lower() or 'complete' in str(webhook_data).lower():
                    return WebhookType.PAYMENT_SUCCESS
                elif 'fail' in str(webhook_data).lower() or 'error' in str(webhook_data).lower():
                    return WebhookType.PAYMENT_FAILED
            
            return WebhookType.UNKNOWN
            
        except Exception as e:
            logger.error(f"Failed to determine event type: {e}")
            return WebhookType.UNKNOWN
    
    async def _process_event(self, event: WebhookEvent) -> Dict[str, Any]:
        """Process webhook event"""
        try:
            handlers = self.event_handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"No handlers registered for event type {event.event_type.value}")
                return {"message": "No handlers registered"}
            
            results = []
            for handler in handlers:
                try:
                    result = await handler(event)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Handler failed for event {event.event_id}: {e}")
                    results.append({"error": str(e)})
            
            return {
                "handlers_executed": len(handlers),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Event processing failed: {e}")
            return {"error": str(e)}

class WebhookRetryManager:
    """Webhook retry management"""
    
    def __init__(self, config: WebhookConfig = None):
        self.config = config or WebhookConfig()
        self.retry_queue: List[WebhookEvent] = []
    
    async def schedule_retry(self, event: WebhookEvent, delay_seconds: int = 60):
        """Schedule webhook retry"""
        if event.retry_count >= self.config.retry_limits.get(event.provider, 3):
            logger.error(f"Max retries exceeded for event {event.event_id}")
            return False
        
        # Add delay and reschedule
        await asyncio.sleep(delay_seconds)
        event.retry_count += 1
        
        # Re-process event
        processor = WebhookProcessor(self.config)
        result = await processor.process_webhook(event.data, event.provider.value, event.signature)
        
        return result.get("success", False)

class UnifiedWebhooks:
    """Single interface for all webhook operations"""
    
    def __init__(self, config: WebhookConfig = None):
        self.config = config or WebhookConfig()
        self.signature_verifier = WebhookSignature(config)
        self.processor = WebhookProcessor(config)
        self.retry_manager = WebhookRetryManager(config)
    
    def verify_signature(self, payload: bytes, signature: str, provider: str) -> bool:
        """Verify webhook signature"""
        try:
            webhook_provider = WebhookProvider(provider.lower())
            return self.signature_verifier.verify_signature(payload, signature, webhook_provider)
        except ValueError:
            return False
    
    async def process_webhook(self, webhook_data: Dict[str, Any], provider: str, signature: str) -> Dict[str, Any]:
        """Process webhook"""
        return await self.processor.process_webhook(webhook_data, provider, signature)
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        try:
            webhook_event_type = WebhookType(event_type.lower())
            self.processor.register_handler(webhook_event_type, handler)
        except ValueError:
            logger.error(f"Unsupported event type: {event_type}")
    
    async def schedule_retry(self, event_data: Dict[str, Any], provider: str, signature: str, retry_count: int = 0):
        """Schedule webhook retry"""
        try:
            webhook_provider = WebhookProvider(provider.lower())
            event = WebhookEvent(
                provider=webhook_provider,
                event_type=WebhookType.UNKNOWN,
                event_id=str(uuid.uuid4()),
                data=event_data,
                timestamp=datetime.now(timezone.utc),
                signature=signature,
                retry_count=retry_count
            )
            return await self.retry_manager.schedule_retry(event)
        except ValueError:
            return False

# Global instance for easy access
unified_webhooks = UnifiedWebhooks()

# Backward compatibility functions (to ease migration)
def verify_webhook_signature(payload: bytes, signature: str, provider: str) -> bool:
    """Backward compatibility wrapper"""
    return unified_webhooks.verify_signature(payload, signature, provider)

async def process_webhook(webhook_data: Dict[str, Any], provider: str, signature: str) -> Dict[str, Any]:
    """Backward compatibility wrapper"""
    return await unified_webhooks.process_webhook(webhook_data, provider, signature)

# Import required for UUID generation
import uuid
