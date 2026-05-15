"""
AGENT ADVISORY SYSTEM
Agents generate SIGNALS ONLY (never orders)
Structured decision pipeline: Signal → Validation → Risk Check → Approval → Execution
================================================================================

Key constraint: Agents are completely isolated from execution layer.
All agent outputs are SIGNALS that must pass risk validation before execution.
Agents have ZERO authority to execute trades.
"""

import uuid
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import structlog

from core.production_foundation import (
    AgentSignal,
    AgentSignalType,
    OrderSide,
    RiskEngine,
    AuditLog,
    ValidatedOrder,
    OrderStatus,
    risk_engine,
    audit_log,
    logger,
)

# ============================================================================
# AGENT ADVISOR (SIGNALS ONLY)
# ============================================================================

class AIAgentAdvisor:
    """
    Pure advisory AI agent that ONLY generates signals.
    
    CONSTRAINTS:
    - Cannot execute trades
    - Cannot access execution layer
    - Cannot modify account state
    - Cannot access other users' data
    - All outputs are suggestions only
    - All signals must be validated before use
    """
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type  # 'price_predictor', 'anomaly_detector', etc.
        self.confidence_threshold = Decimal("0.65")  # Only emit signals > 65% confidence
        self.signal_history = []
        self.performance_metrics = {
            "signals_generated": 0,
            "signals_acted_upon": 0,
            "accuracy": Decimal("0"),
        }
    
    async def analyze_and_signal(
        self,
        asset: str,
        market_data: Dict[str, Any],
    ) -> Optional[AgentSignal]:
        """
        Analyze market and generate advisory signal (NOT AN ORDER).
        
        IMPORTANT: This only generates a SIGNAL for human/risk-engine review.
        This signal CANNOT directly cause trades.
        """
        
        # Run analysis
        signal_data = await self._run_analysis(asset, market_data)
        if not signal_data:
            return None
        
        # Check confidence threshold
        confidence = signal_data.get("confidence", Decimal("0"))
        if confidence < self.confidence_threshold:
            logger.info(
                "signal_below_confidence_threshold",
                agent_id=self.agent_id,
                asset=asset,
                confidence=float(confidence),
                threshold=float(self.confidence_threshold)
            )
            return None
        
        # Create advisory signal
        signal = AgentSignal(
            signal_id=f"SIG_{uuid.uuid4().hex[:12]}",
            agent_id=self.agent_id,
            signal_type=AgentSignalType[signal_data["signal_type"]],
            asset=asset,
            action=OrderSide[signal_data["action"]],
            confidence=confidence,
            magnitude=signal_data.get("magnitude", Decimal("1")),
            reasoning=signal_data.get("reasoning", ""),
            supporting_data=signal_data.get("supporting_data", {}),
            generate_at=datetime.now(timezone.utc),
        )
        
        # Audit the signal generation
        await audit_log.log_agent_signal(signal)
        
        logger.info(
            "advisory_signal_generated",
            agent_id=self.agent_id,
            signal_type=signal.signal_type.value,
            asset=asset,
            action=signal.action.value,
            confidence=float(confidence),
        )
        
        self.performance_metrics["signals_generated"] += 1
        self.signal_history.append(signal)
        
        return signal
    
    async def _run_analysis(
        self,
        asset: str,
        market_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Run analysis (overridden by specific agent types).
        
        Must return dict with:
        - signal_type: string
        - action: BUY or SELL
        - confidence: 0.0-1.0
        - reasoning: explanation
        - supporting_data: dict
        """
        # Override in subclasses
        raise NotImplementedError()
    
    def get_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return self.performance_metrics


# ============================================================================
# SPECIFIC AGENT IMPLEMENTATIONS
# ============================================================================

class PricePredictor(AIAgentAdvisor):
    """Price prediction agent - SIGNALS ONLY"""
    
    def __init__(self):
        super().__init__("PRICE_PREDICTOR", "price_predictor")
    
    async def _run_analysis(
        self,
        asset: str,
        market_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Predict price movement"""
        
        price = market_data.get("current_price", Decimal("0"))
        ma_20 = market_data.get("ma_20", Decimal("0"))
        momentum = market_data.get("momentum", Decimal("0"))
        
        # Simple logic: if price above MA20 and momentum positive, signal BUY
        if price > ma_20 and momentum > 0:
            return {
                "signal_type": "PRICE_PREDICTION",
                "action": "BUY",
                "confidence": Decimal("0.72"),
                "reasoning": "Price above 20-day MA with positive momentum",
                "supporting_data": {
                    "price": float(price),
                    "ma_20": float(ma_20),
                    "momentum": float(momentum),
                }
            }
        
        return None


class AnomalyDetector(AIAgentAdvisor):
    """Anomaly detection agent - SIGNALS ONLY"""
    
    def __init__(self):
        super().__init__("ANOMALY_DETECTOR", "anomaly_detector")
    
    async def _run_analysis(
        self,
        asset: str,
        market_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Detect market anomalies"""
        
        volume = market_data.get("volume", Decimal("0"))
        avg_volume = market_data.get("avg_volume", Decimal("0"))
        volume_ratio = volume / avg_volume if avg_volume > 0 else Decimal("1")
        
        # If volume significantly higher, signal opportunity
        if volume_ratio > Decimal("2.0"):
            return {
                "signal_type": "VOLUME_ANOMALY",
                "action": "BUY",
                "confidence": Decimal("0.68"),
                "reasoning": f"Volume {float(volume_ratio):.1f}x average - potential opportunity",
                "supporting_data": {
                    "volume": float(volume),
                    "avg_volume": float(avg_volume),
                    "ratio": float(volume_ratio),
                }
            }
        
        return None


class SentimentAnalyzer(AIAgentAdvisor):
    """Sentiment analysis agent - SIGNALS ONLY"""
    
    def __init__(self):
        super().__init__("SENTIMENT_ANALYZER", "sentiment_analyzer")
    
    async def _run_analysis(
        self,
        asset: str,
        market_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Analyze market sentiment"""
        
        sentiment_score = market_data.get("sentiment_score", Decimal("0"))  # -1 to +1
        
        # Positive sentiment above 0.6
        if sentiment_score > Decimal("0.6"):
            return {
                "signal_type": "SENTIMENT_ALERT",
                "action": "BUY",
                "confidence": Decimal("0.65"),
                "reasoning": f"Positive market sentiment ({float(sentiment_score):.2f})",
                "supporting_data": {
                    "sentiment_score": float(sentiment_score),
                }
            }
        
        return None

# ============================================================================
# SIGNAL VALIDATION PIPELINE
# ============================================================================

class SignalValidator:
    """
    Validates agent signals against business rules.
    
    Independent from risk engine - this checks signal quality,
    not position risk.
    """
    
    async def validate_signal(self, signal: AgentSignal) -> Tuple[bool, str]:
        """
        Validate signal quality.
        
        Returns: (is_valid, reason_if_invalid)
        """
        
        # Check signal freshness
        age = datetime.now(timezone.utc) - signal.generate_at
        if age.total_seconds() > signal.ttl_seconds:
            return False, "Signal expired"
        
        # Check confidence > threshold
        if signal.confidence < Decimal("0.5"):
            return False, "Confidence too low"
        
        # Check magnitude > 0
        if signal.magnitude <= 0:
            return False, "Invalid magnitude"
        
        # Check reasoning is present
        if not signal.reasoning:
            return False, "No reasoning provided"
        
        return True, ""


# ============================================================================
# DECISION PIPELINE
# ============================================================================

@dataclass
class DecisionPipelineInput:
    """Input to decision pipeline"""
    signal: AgentSignal
    user_id: str
    idempotency_key: str
    auto_execute: bool = False  # Allow automation if user enabled

@dataclass
class DecisionPipelineOutput:
    """Output from decision pipeline"""
    approved: bool
    order: Optional[ValidatedOrder] = None
    rejection_reason: str = ""
    risk_checks: Dict[str, bool] = field(default_factory=dict)
    signal_valid: bool = False

class StructuredDecisionPipeline:
    """
    Production decision pipeline:
    Signal → Validation → Risk Check → Approval → Ready for Execution
    
    Each stage is independent and can be audited.
    """
    
    def __init__(self):
        self.signal_validator = SignalValidator()
        self.risk_engine = risk_engine
    
    async def process(self, pipeline_input: DecisionPipelineInput) -> DecisionPipelineOutput:
        """
        Run signal through complete decision pipeline.
        
        Returns whether order is approved for execution.
        """
        
        output = DecisionPipelineOutput(approved=False)
        
        # STAGE 1: Signal Validation
        logger.info("pipeline_stage", stage="SIGNAL_VALIDATION", signal_id=pipeline_input.signal.signal_id)
        is_valid, reason = await self.signal_validator.validate_signal(pipeline_input.signal)
        output.signal_valid = is_valid
        
        if not is_valid:
            output.rejection_reason = f"Signal validation failed: {reason}"
            logger.warning("signal_validation_failed", reason=reason)
            return output
        
        # STAGE 2: Risk Validation
        logger.info("pipeline_stage", stage="RISK_VALIDATION", signal_id=pipeline_input.signal.signal_id)
        risk_approved, checks, risk_reason = await self.risk_engine.validate_order(pipeline_input.signal)
        output.risk_checks = checks
        
        if not risk_approved:
            output.rejection_reason = f"Risk validation failed: {risk_reason}"
            logger.warning("risk_validation_failed", reason=risk_reason)
            return output
        
        # STAGE 3: Create ValidatedOrder (ready for execution but NOT executed yet)
        logger.info("pipeline_stage", stage="ORDER_CREATION", signal_id=pipeline_input.signal.signal_id)
        order = ValidatedOrder(
            order_id=f"ORD_{uuid.uuid4().hex[:12]}",
            agent_signal_id=pipeline_input.signal.signal_id,
            asset=pipeline_input.signal.asset,
            side=pipeline_input.signal.action,
            quantity=Decimal("1"),  # Simplified - in production use optimal sizing
            price=await self._get_current_price(pipeline_input.signal.asset),
            order_type=pipeline_input.signal.signal_type.name.lower(),
            risk_checks=checks,
            approved_by_risk_engine=True,
        )
        
        output.order = order
        output.approved = True
        
        logger.info(
            "pipeline_decision_approved",
            order_id=order.order_id,
            signal_id=pipeline_input.signal.signal_id,
        )
        
        return output
    
    async def _get_current_price(self, asset: str) -> Decimal:
        """Get current price for asset"""
        # In production, fetch from real market data feed
        return Decimal("100")

# ============================================================================
# EXECUTION GATE (PREVENTS DIRECT AGENT EXECUTION)
# ============================================================================

class ExecutionGate:
    """
    Final safeguard: approved orders must be explicitly executed.
    Agents NEVER trigger execution.
    """
    
    async def submit_for_execution(
        self,
        order: ValidatedOrder,
        idempotency_key: str,
    ) -> bool:
        """
        Submit approved order for execution.
        
        This is the ONLY way trades can be executed.
        Agents cannot call this directly.
        """
        
        # Verify order is actually approved
        if not order.approved_by_risk_engine:
            logger.error("attempt_to_execute_unapproved_order", order_id=order.order_id)
            raise ValueError("Order not approved by risk engine")
        
        # Final sanity check
        if order.status != OrderStatus.RISK_VALIDATED:
            logger.error("order_not_in_valid_status", order_id=order.order_id, status=order.status)
            raise ValueError(f"Order must be RISK_VALIDATED, currently {order.status}")
        
        # Submit to execution
        logger.info("order_submitted_for_execution", order_id=order.order_id)
        
        return True

# ============================================================================
# ORCHESTRATED WORKFLOW
# ============================================================================

class AgentOrchestration:
    """Orchestrates the complete advisory → approval → execution pipeline"""
    
    def __init__(self):
        self.agents: Dict[str, AIAgentAdvisor] = {
            "price_predictor": PricePredictor(),
            "anomaly_detector": AnomalyDetector(),
            "sentiment_analyzer": SentimentAnalyzer(),
        }
        self.pipeline = StructuredDecisionPipeline()
        self.execution_gate = ExecutionGate()
    
    async def run_advisory_cycle(
        self,
        asset: str,
        market_data: Dict[str, Any],
    ) -> List[AgentSignal]:
        """Run all agents in advisory mode - generate signals only"""
        
        signals = []
        
        for agent_name, agent in self.agents.items():
            try:
                signal = await agent.analyze_and_signal(asset, market_data)
                if signal:
                    signals.append(signal)
                    logger.info(
                        "agent_signal_generated",
                        agent=agent_name,
                        asset=asset,
                        signal_id=signal.signal_id
                    )
            except Exception as e:
                logger.error("agent_analysis_failed", agent=agent_name, error=str(e))
        
        return signals
    
    async def process_signal_to_execution(
        self,
        signal: AgentSignal,
        user_id: str,
        idempotency_key: str,
        auto_execute: bool = False,
    ) -> bool:
        """
        Process signal through pipeline to potential execution.
        
        Flow:
        1. Signal generated by agent (advisory)
        2. Validate signal quality
        3. Risk engine validates (VETO power here)
        4. Create ValidatedOrder (ready but not executed)
        5. Execute only if approved AND explicitly submitted
        """
        
        # Step 1: Run through pipeline
        pipeline_input = DecisionPipelineInput(
            signal=signal,
            user_id=user_id,
            idempotency_key=idempotency_key,
            auto_execute=auto_execute,
        )
        
        decision = await self.pipeline.process(pipeline_input)
        
        # Step 2: If approved and auto_execute enabled, submit
        if decision.approved and auto_execute and decision.order:
            await self.execution_gate.submit_for_execution(
                decision.order,
                idempotency_key
            )
            return True
        
        # Otherwise, approved order is waiting for manual approval/execution
        return decision.approved

print("✅ Agent Advisory System loaded (Agents generate SIGNALS ONLY)")
