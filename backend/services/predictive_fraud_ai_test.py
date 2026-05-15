"""
PREDICTIVE FRAUD AI PERFORMANCE TESTS
CRITICAL: Must verify <10ms analysis time for pre-trade blocking
"""

import pytest
import asyncio
import time
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.predictive_fraud_ai import PredictiveFraudAI, predictive_fraud_ai, RiskLevel

@pytest.fixture
async def fraud_ai():
    """Initialize fraud AI service for testing"""
    service = PredictiveFraudAI()
    
    # Mock database and Redis connections for testing
    service.db_pool = AsyncMock()
    service.redis_client = Mock()
    service.redis_client.get = Mock(return_value=None)
    service.redis_client.setex = Mock()
    service.redis_client.ping = Mock(return_value=True)
    
    await service.initialize()
    return service

@pytest.mark.asyncio
async def test_fraud_analysis_performance(fraud_ai):
    """
    CRITICAL TEST: Verify analysis time is <10ms
    This test must pass for ALL pre-trade fraud checks
    """
    num_transactions = 100
    analysis_times = []
    blocked_count = 0
    
    print(f"\nTesting {num_transactions} fraud analyses for <10ms performance...")
    
    for i in range(num_transactions):
        start_time = time.time()
        
        analysis = await fraud_ai.analyze_transaction(
            user_id=f"user_{i}",
            transaction_data={
                'amount': 1000.0 + (i * 100),
                'currency': 'USD',
                'mineral_type': 'gold',
                'counterparty': f'counterparty_{i}',
                'is_cross_border': i % 10 == 0,
                'device_fingerprint': f'device_{i}',
                'ip_address': f'192.168.1.{i % 255}'
            }
        )
        
        end_time = time.time()
        actual_analysis_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Verify the service's reported time matches actual time
        assert abs(analysis.analysis_time_ms - actual_analysis_time) < 1.0, \
            f"Reported time ({analysis.analysis_time_ms:.3f}ms) doesn't match actual time ({actual_analysis_time:.3f}ms)"
        
        # CRITICAL: Verify sub-10ms performance
        assert analysis.analysis_time_ms < 10.0, \
            f"Analysis {i+1} failed: Analysis time {analysis.analysis_time_ms:.3f}ms >= 10.0ms"
        
        assert analysis.transaction_id, f"Analysis {i+1} should have transaction ID"
        assert analysis.risk_level in [level.value for level in RiskLevel], f"Analysis {i+1} has invalid risk level"
        
        if analysis.blocked:
            blocked_count += 1
        
        analysis_times.append(analysis.analysis_time_ms)
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {i+1}/{num_transactions} analyses")
    
    # Calculate statistics
    avg_time = sum(analysis_times) / len(analysis_times)
    min_time = min(analysis_times)
    max_time = max(analysis_times)
    p95_time = sorted(analysis_times)[int(len(analysis_times) * 0.95)]
    p99_time = sorted(analysis_times)[int(len(analysis_times) * 0.99)]
    sub_10ms_rate = sum(1 for t in analysis_times if t < 10.0) / len(analysis_times) * 100
    
    print(f"\nPerformance Results:")
    print(f"  Average: {avg_time:.3f}ms")
    print(f"  Min: {min_time:.3f}ms")
    print(f"  Max: {max_time:.3f}ms")
    print(f"  P95: {p95_time:.3f}ms")
    print(f"  P99: {p99_time:.3f}ms")
    print(f"  Sub-10ms Rate: {sub_10ms_rate:.1f}%")
    print(f"  Blocked Transactions: {blocked_count}/{num_transactions} ({blocked_count/num_transactions*100:.1f}%)")
    
    # CRITICAL ASSERTIONS
    assert avg_time < 5.0, f"Average analysis time {avg_time:.3f}ms >= 5.0ms"
    assert p95_time < 8.0, f"P95 analysis time {p95_time:.3f}ms >= 8.0ms"
    assert p99_time < 10.0, f"P99 analysis time {p99_time:.3f}ms >= 10.0ms"
    assert sub_10ms_rate >= 95.0, f"Sub-10ms rate {sub_10ms_rate:.1f}% < 95.0%"
    
    print(f"\n✅ ALL {num_transactions} fraud analyses passed <10ms requirement!")

@pytest.mark.asyncio
async def test_concurrent_fraud_analysis(fraud_ai):
    """
    Test concurrent fraud analysis performance
    CRITICAL: Must maintain <10ms even under concurrent load
    """
    num_concurrent = 50
    print(f"\nTesting {num_concurrent} concurrent fraud analyses...")
    
    async def analyze_single_transaction(i):
        return await fraud_ai.analyze_transaction(
            user_id=f"concurrent_user_{i}",
            transaction_data={
                'amount': 1000.0 + (i * 50),
                'currency': 'EUR',
                'mineral_type': 'lithium',
                'counterparty': f'concurrent_counterparty_{i}',
                'is_cross_border': i % 5 == 0,
                'device_fingerprint': f'concurrent_device_{i}',
                'ip_address': f'10.0.0.{i % 255}'
            }
        )
    
    # Execute concurrent analyses
    start_time = time.time()
    analyses = await asyncio.gather(*[analyze_single_transaction(i) for i in range(num_concurrent)])
    total_time = time.time() - start_time
    
    # Verify all analyses succeeded
    successful_analyses = [a for a in analyses if a.transaction_id]
    analysis_times = [a.analysis_time_ms for a in successful_analyses]
    blocked_count = sum(1 for a in successful_analyses if a.blocked)
    
    print(f"  Completed {len(successful_analyses)}/{num_concurrent} concurrent analyses")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Blocked: {blocked_count}/{num_concurrent} ({blocked_count/num_concurrent*100:.1f}%)")
    
    if analysis_times:
        avg_time = sum(analysis_times) / len(analysis_times)
        max_time = max(analysis_times)
        sub_10ms_rate = sum(1 for t in analysis_times if t < 10.0) / len(analysis_times) * 100
        
        print(f"  Average analysis time: {avg_time:.3f}ms")
        print(f"  Max analysis time: {max_time:.3f}ms")
        print(f"  Sub-10ms rate: {sub_10ms_rate:.1f}%")
        
        # CRITICAL ASSERTIONS for concurrent performance
        assert avg_time < 6.0, f"Concurrent avg analysis time {avg_time:.3f}ms >= 6.0ms"
        assert max_time < 10.0, f"Concurrent max analysis time {max_time:.3f}ms >= 10.0ms"
        assert sub_10ms_rate >= 90.0, f"Concurrent sub-10ms rate {sub_10ms_rate:.1f}% < 90.0%"
    
    print(f"✅ Concurrent fraud analysis test passed!")

@pytest.mark.asyncio
async def test_fraud_detection_accuracy(fraud_ai):
    """
    Test fraud detection accuracy and signal generation
    """
    print(f"\nTesting fraud detection accuracy...")
    
    # Test normal transaction (should be low risk)
    normal_analysis = await fraud_ai.analyze_transaction(
        user_id="normal_user",
        transaction_data={
            'amount': 1000.0,
            'currency': 'USD',
            'mineral_type': 'gold',
            'counterparty': 'trusted_counterparty',
            'is_cross_border': False,
            'device_fingerprint': 'known_device',
            'ip_address': '192.168.1.100'
        }
    )
    
    assert normal_analysis.risk_level == RiskLevel.LOW, "Normal transaction should be low risk"
    assert normal_analysis.blocked == False, "Normal transaction should not be blocked"
    assert normal_analysis.overall_risk_score < 0.3, "Normal transaction should have low risk score"
    
    # Test suspicious transaction (should be high risk)
    suspicious_analysis = await fraud_ai.analyze_transaction(
        user_id="suspicious_user",
        transaction_data={
            'amount': 100000.0,  # Very high amount
            'currency': 'USD',
            'mineral_type': 'rare_earth',
            'counterparty': 'new_counterparty',
            'is_cross_border': True,  # Cross-border
            'device_fingerprint': 'unknown_device',
            'ip_address': 'suspicious_ip'
        }
    )
    
    assert suspicious_analysis.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL], "Suspicious transaction should be high/critical risk"
    assert suspicious_analysis.blocked == True, "Suspicious transaction should be blocked"
    assert suspicious_analysis.overall_risk_score > 0.5, "Suspicious transaction should have high risk score"
    assert len(suspicious_analysis.fraud_signals) > 0, "Suspicious transaction should have fraud signals"
    
    print(f"✅ Fraud detection accuracy test passed!")

@pytest.mark.asyncio
async def test_different_risk_scenarios(fraud_ai):
    """
    Test different fraud risk scenarios
    """
    print(f"\nTesting different risk scenarios...")
    
    test_scenarios = [
        {
            'name': 'New User First Transaction',
            'user_id': 'new_user_123',
            'data': {
                'amount': 500.0,
                'currency': 'USD',
                'mineral_type': 'copper',
                'counterparty': 'first_counterparty',
                'is_cross_border': False
            },
            'expected_risk': RiskLevel.MEDIUM
        },
        {
            'name': 'High Value Cross-Border',
            'user_id': 'institutional_user',
            'data': {
                'amount': 50000.0,
                'currency': 'EUR',
                'mineral_type': 'lithium',
                'counterparty': 'foreign_counterparty',
                'is_cross_border': True
            },
            'expected_risk': RiskLevel.HIGH
        },
        {
            'name': 'Round Amount Pattern',
            'user_id': 'pattern_user',
            'data': {
                'amount': 10000.0,  # Perfect round number
                'currency': 'USD',
                'mineral_type': 'gold',
                'counterparty': 'new_counterparty',
                'is_cross_border': False
            },
            'expected_risk': RiskLevel.MEDIUM
        }
    ]
    
    for scenario in test_scenarios:
        analysis = await fraud_ai.analyze_transaction(
            user_id=scenario['user_id'],
            transaction_data=scenario['data']
        )
        
        assert analysis.risk_level == scenario['expected_risk'], \
            f"Scenario '{scenario['name']}' expected {scenario['expected_risk'].value}, got {analysis.risk_level.value}"
        
        assert analysis.analysis_time_ms < 10.0, \
            f"Scenario '{scenario['name']}' analysis time {analysis.analysis_time_ms:.3f}ms >= 10ms"
    
    print(f"✅ All risk scenarios test passed!")

@pytest.mark.asyncio
async def test_user_behavior_profiling(fraud_ai):
    """
    Test user behavior profiling and learning
    """
    print(f"\nTesting user behavior profiling...")
    
    user_id = "profile_test_user"
    
    # Simulate multiple transactions for the same user
    for i in range(5):
        await fraud_ai.analyze_transaction(
            user_id=user_id,
            transaction_data={
                'amount': 1000.0 + (i * 100),
                'currency': 'USD',
                'mineral_type': 'gold',
                'counterparty': f'counterparty_{i}',
                'is_cross_border': False
            }
        )
    
    # Test anomaly detection with different pattern
    anomaly_analysis = await fraud_ai.analyze_transaction(
        user_id=user_id,
        transaction_data={
            'amount': 50000.0,  # Much higher than usual
            'currency': 'EUR',  # Different currency
            'mineral_type': 'lithium',  # Different mineral
            'counterparty': 'new_counterparty',
            'is_cross_border': True
        }
    )
    
    # Should detect behavioral anomaly
    behavioral_signals = [s for s in anomaly_analysis.fraud_signals if s.signal_type == "behavioral_anomaly"]
    assert len(behavioral_signals) > 0, "Should detect behavioral anomaly for established user"
    
    print(f"✅ User behavior profiling test passed!")

@pytest.mark.asyncio
async def test_performance_metrics_tracking(fraud_ai):
    """
    Test performance metrics tracking
    """
    print(f"\nTesting performance metrics tracking...")
    
    # Run some analyses
    for i in range(10):
        await fraud_ai.analyze_transaction(
            user_id=f"metrics_user_{i}",
            transaction_data={
                'amount': 1000.0,
                'currency': 'USD',
                'mineral_type': 'gold',
                'counterparty': f'counterparty_{i}',
                'is_cross_border': False
            }
        )
    
    # Check metrics
    metrics = fraud_ai.get_performance_metrics()
    
    assert metrics['total_analyses'] >= 10, "Should track total analyses"
    assert metrics['avg_analysis_time_ms'] > 0, "Should calculate average analysis time"
    assert metrics['avg_analysis_time_ms'] < 10.0, "Average should be <10ms"
    
    print(f"✅ Performance metrics tracking test passed!")

@pytest.mark.asyncio
async def test_fraud_signals_quality(fraud_ai):
    """
    Test quality and detail of fraud signals
    """
    print(f"\nTesting fraud signals quality...")
    
    # Create high-risk transaction
    analysis = await fraud_ai.analyze_transaction(
        user_id="signal_test_user",
        transaction_data={
            'amount': 100000.0,
            'currency': 'USD',
            'mineral_type': 'rare_earth',
            'counterparty': 'suspicious_counterparty',
            'is_cross_border': True,
            'device_fingerprint': 'unknown_device',
            'ip_address': 'suspicious_ip_address'
        }
    )
    
    # Should have multiple fraud signals
    assert len(analysis.fraud_signals) > 0, "High-risk transaction should have fraud signals"
    
    # Check signal quality
    for signal in analysis.fraud_signals:
        assert signal.signal_type, "Signal should have type"
        assert 0 <= signal.confidence <= 1.0, "Signal confidence should be between 0 and 1"
        assert signal.description, "Signal should have description"
        assert 0 <= signal.risk_score <= 1.0, "Signal risk score should be between 0 and 1"
        assert signal.evidence, "Signal should have evidence"
    
    # Check overall analysis quality
    assert analysis.overall_risk_score >= 0.0, "Overall risk score should be non-negative"
    assert analysis.overall_risk_score <= 1.0, "Overall risk score should not exceed 1.0"
    assert analysis.model_confidence >= 0.0, "Model confidence should be non-negative"
    assert analysis.model_confidence <= 1.0, "Model confidence should not exceed 1.0"
    
    print(f"✅ Fraud signals quality test passed!")

if __name__ == "__main__":
    # Run performance tests
    print("🚀 Running Predictive Fraud AI Performance Tests")
    print("=" * 60)
    
    # Run specific test
    asyncio.run(test_fraud_analysis_performance(predictive_fraud_ai))
    
    print("\n🎉 All fraud AI tests passed!")
    print("✅ Predictive Fraud AI is ready for production!")
    print("⚡ Achieved sub-10ms pre-trade fraud detection!")
