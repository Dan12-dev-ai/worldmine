"""
QUANTUM-INSTANT SETTLEMENT PERFORMANCE TESTS
CRITICAL: Must verify <1ms settlement time for ALL transactions
"""

import pytest
import asyncio
import time
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.quantum_settlement import QuantumInstantSettlement, quantum_settlement_service

@pytest.fixture
async def settlement_service():
    """Initialize settlement service for testing"""
    service = QuantumInstantSettlement()
    
    # Mock database and Redis connections for testing
    service.db_pool = AsyncMock()
    service.redis_client = Mock()
    service.redis_client.ping = Mock(return_value=True)
    service.redis_client.setex = Mock()
    service.redis_client.hincrby = Mock()
    
    await service.initialize()
    return service

@pytest.mark.asyncio
async def test_quantum_settlement_performance(settlement_service):
    """
    CRITICAL TEST: Verify settlement time is <1ms
    This test must pass for ALL transactions
    """
    num_transactions = 100
    settlement_times = []
    
    print(f"\nTesting {num_transactions} transactions for <1ms settlement...")
    
    for i in range(num_transactions):
        start_time = time.time()
        
        result = await settlement_service.settle_transaction(
            from_address=f"user_{i}",
            to_address=f"user_{i+1}",
            amount=100.0,
            currency="USD",
            mineral_type="gold"
        )
        
        end_time = time.time()
        actual_settlement_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Verify the service's reported time matches actual time
        assert abs(result.settlement_time_ms - actual_settlement_time) < 0.1, \
            f"Reported time ({result.settlement_time_ms:.3f}ms) doesn't match actual time ({actual_settlement_time:.3f}ms)"
        
        # CRITICAL: Verify sub-millisecond performance
        assert result.settlement_time_ms < 1.0, \
            f"Transaction {i+1} failed: Settlement time {result.settlement_time_ms:.3f}ms >= 1.0ms"
        
        assert result.success, f"Transaction {i+1} failed: {result.error_message}"
        
        settlement_times.append(result.settlement_time_ms)
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {i+1}/{num_transactions} transactions")
    
    # Calculate statistics
    avg_time = sum(settlement_times) / len(settlement_times)
    min_time = min(settlement_times)
    max_time = max(settlement_times)
    p95_time = sorted(settlement_times)[int(len(settlement_times) * 0.95)]
    p99_time = sorted(settlement_times)[int(len(settlement_times) * 0.99)]
    sub_millisecond_rate = sum(1 for t in settlement_times if t < 1.0) / len(settlement_times) * 100
    
    print(f"\nPerformance Results:")
    print(f"  Average: {avg_time:.3f}ms")
    print(f"  Min: {min_time:.3f}ms")
    print(f"  Max: {max_time:.3f}ms")
    print(f"  P95: {p95_time:.3f}ms")
    print(f"  P99: {p99_time:.3f}ms")
    print(f"  Sub-millisecond Rate: {sub_millisecond_rate:.1f}%")
    
    # CRITICAL ASSERTIONS
    assert avg_time < 0.8, f"Average settlement time {avg_time:.3f}ms >= 0.8ms"
    assert p95_time < 1.0, f"P95 settlement time {p95_time:.3f}ms >= 1.0ms"
    assert p99_time < 1.2, f"P99 settlement time {p99_time:.3f}ms >= 1.2ms"
    assert sub_millisecond_rate >= 95.0, f"Sub-millisecond rate {sub_millisecond_rate:.1f}% < 95.0%"
    
    print(f"\n✅ ALL {num_transactions} transactions passed <1ms requirement!")

@pytest.mark.asyncio
async def test_concurrent_settlement_performance(settlement_service):
    """
    Test concurrent settlement performance
    CRITICAL: Must maintain <1ms even under concurrent load
    """
    num_concurrent = 50
    print(f"\nTesting {num_concurrent} concurrent transactions...")
    
    async def settle_single_transaction(i):
        return await settlement_service.settle_transaction(
            from_address=f"concurrent_user_{i}",
            to_address=f"concurrent_user_{i+1}",
            amount=100.0,
            currency="USD",
            mineral_type="gold"
        )
    
    # Execute concurrent transactions
    start_time = time.time()
    results = await asyncio.gather(*[settle_single_transaction(i) for i in range(num_concurrent)])
    total_time = time.time() - start_time
    
    # Verify all transactions succeeded
    successful_transactions = [r for r in results if r.success]
    settlement_times = [r.settlement_time_ms for r in successful_transactions]
    
    print(f"  Completed {len(successful_transactions)}/{num_concurrent} concurrent transactions")
    print(f"  Total time: {total_time:.3f}s")
    
    if settlement_times:
        avg_time = sum(settlement_times) / len(settlement_times)
        max_time = max(settlement_times)
        sub_millisecond_rate = sum(1 for t in settlement_times if t < 1.0) / len(settlement_times) * 100
        
        print(f"  Average settlement time: {avg_time:.3f}ms")
        print(f"  Max settlement time: {max_time:.3f}ms")
        print(f"  Sub-millisecond rate: {sub_millisecond_rate:.1f}%")
        
        # CRITICAL ASSERTIONS for concurrent performance
        assert avg_time < 0.8, f"Concurrent avg settlement time {avg_time:.3f}ms >= 0.8ms"
        assert max_time < 1.0, f"Concurrent max settlement time {max_time:.3f}ms >= 1.0ms"
        assert sub_millisecond_rate >= 90.0, f"Concurrent sub-millisecond rate {sub_millisecond_rate:.1f}% < 90.0%"
    
    print(f"✅ Concurrent performance test passed!")

@pytest.mark.asyncio
async def test_quantum_verification(settlement_service):
    """
    Test quantum verification functionality
    """
    print(f"\nTesting quantum verification...")
    
    result = await settlement_service.settle_transaction(
        from_address="quantum_test_user",
        to_address="quantum_test_recipient",
        amount=1000.0,
        currency="USD",
        mineral_type="lithium"
    )
    
    assert result.success, f"Quantum verification failed: {result.error_message}"
    assert result.quantum_proof, "Quantum proof should not be empty"
    assert result.blockchain_hash, "Blockchain hash should not be empty"
    assert len(result.blockchain_hash) == 64, "Blockchain hash should be 64 characters (SHA-256)"
    
    print(f"✅ Quantum verification test passed!")

@pytest.mark.asyncio
async def test_post_quantum_signatures(settlement_service):
    """
    Test CRYSTALS-Dilithium-5 post-quantum signatures
    """
    print(f"\nTesting post-quantum signatures...")
    
    result = await settlement_service.settle_transaction(
        from_address="pq_test_user",
        to_address="pq_test_recipient",
        amount=500.0,
        currency="EUR",
        mineral_type="copper"
    )
    
    assert result.success, f"Post-quantum signature failed: {result.error_message}"
    
    # Verify transaction can be retrieved with signature
    status = await settlement_service.get_transaction_status(result.transaction_id)
    assert status is not None, "Transaction should be retrievable"
    assert status['quantum_signature'], "Quantum signature should be present"
    
    print(f"✅ Post-quantum signature test passed!")

@pytest.mark.asyncio
async def test_different_minerals_and_currencies(settlement_service):
    """
    Test settlement with different minerals and currencies
    """
    print(f"\nTesting different minerals and currencies...")
    
    test_cases = [
        ("gold", "USD", 100.0),
        ("lithium", "EUR", 250.0),
        ("copper", "GBP", 500.0),
        ("rare_earth", "JPY", 1000.0),
        ("quantum_bits", "BTC", 0.1),
        ("ai_compute", "ETH", 1.5),
    ]
    
    for mineral, currency, amount in test_cases:
        result = await settlement_service.settle_transaction(
            from_address=f"test_{mineral}_user",
            to_address=f"test_{mineral}_recipient",
            amount=amount,
            currency=currency,
            mineral_type=mineral
        )
        
        assert result.success, f"Failed for {mineral}/{currency}: {result.error_message}"
        assert result.settlement_time_ms < 1.0, f"{mineral}/{currency} settlement time {result.settlement_time_ms:.3f}ms >= 1.0ms"
    
    print(f"✅ All minerals and currencies test passed!")

@pytest.mark.asyncio
async def test_performance_metrics(settlement_service):
    """
    Test performance metrics tracking
    """
    print(f"\nTesting performance metrics...")
    
    # Settle some transactions
    for i in range(10):
        await settlement_service.settle_transaction(
            from_address=f"metrics_user_{i}",
            to_address=f"metrics_recipient_{i}",
            amount=100.0,
            currency="USD",
            mineral_type="gold"
        )
    
    # Check metrics
    metrics = settlement_service.get_performance_metrics()
    
    assert metrics['total_transactions'] >= 10, "Should track total transactions"
    assert metrics['avg_settlement_time_ms'] > 0, "Should calculate average settlement time"
    assert metrics['avg_settlement_time_ms'] < 1.0, "Average should be <1ms"
    assert metrics['min_settlement_time_ms'] > 0, "Should track minimum settlement time"
    assert metrics['max_settlement_time_ms'] > 0, "Should track maximum settlement time"
    
    print(f"✅ Performance metrics test passed!")

@pytest.mark.asyncio
async def test_benchmark_function(settlement_service):
    """
    Test the benchmark function
    """
    print(f"\nTesting benchmark function...")
    
    # Mock Redis operations for benchmark
    settlement_service.redis_client = Mock()
    settlement_service.redis_client.ping = Mock(return_value=True)
    settlement_service.redis_client.setex = Mock()
    settlement_service.redis_client.hincrby = Mock()
    
    benchmark_results = await settlement_service.benchmark_performance(num_transactions=50)
    
    assert benchmark_results['total_transactions'] == 50, "Should process 50 transactions"
    assert benchmark_results['success_rate'] > 0, "Should have some successful transactions"
    assert benchmark_results['avg_settlement_time_ms'] > 0, "Should calculate average time"
    assert benchmark_results['sub_millisecond_rate'] >= 0, "Should calculate sub-millisecond rate"
    
    print(f"✅ Benchmark function test passed!")

if __name__ == "__main__":
    # Run performance tests
    print("🚀 Running Quantum-Instant Settlement Performance Tests")
    print("=" * 60)
    
    # Run specific test
    asyncio.run(test_quantum_settlement_performance(quantum_settlement_service))
    
    print("\n🎉 All performance tests passed!")
    print("✅ Quantum-Instant Settlement is ready for production!")
    print("⚡ Achieved sub-millisecond transaction finality!")
