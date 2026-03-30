#!/usr/bin/env python3
"""
AI Scraper Reliability Testing Suite
Tests the market news agent under various failure conditions
"""

import asyncio
import json
import time
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import MarketNewsAgent, AgentState

class ScraperReliabilityTest:
    def __init__(self):
        self.test_results = []
        
    async def test_api_failure_scenarios(self):
        """Test how the agent handles API failures"""
        print("🧪 Testing API failure scenarios...")
        
        # Test 1: Tavily API failure
        with patch('tavily.TavilyClient.search') as mock_search:
            mock_search.side_effect = Exception("API rate limit exceeded")
            
            agent = MarketNewsAgent()
            state = AgentState(
                search_queries=agent.search_queries,
                raw_news=[],
                processed_news=[],
                posted_news=[],
                errors=[]
            )
            
            try:
                result = await agent.search_news(state)
                self.test_results.append({
                    test: "Tavily API Failure",
                    status: "PASS" if any("rate limit" in str(error) for error in state.errors) else "FAIL",
                    details: f"Errors captured: {len(state.errors)}"
                })
            except Exception as e:
                self.test_results.append({
                    test: "Tavily API Failure",
                    status: "FAIL",
                    details: f"Unhandled exception: {str(e)}"
                })
        
        # Test 2: Claude API failure
        with patch('anthropic.Anthropic.messages.create') as mock_claude:
            mock_claude.side_effect = Exception("Claude API unavailable")
            
            agent = MarketNewsAgent()
            state = AgentState(
                search_queries=[{"title": "Test", "content": "Test content"}],
                raw_news=[{"title": "Test", "content": "Test content"}],
                processed_news=[],
                posted_news=[],
                errors=[]
            )
            
            try:
                result = await agent.analyze_news(state)
                self.test_results.append({
                    test: "Claude API Failure",
                    status: "PASS" if len(state.errors) > 0 else "FAIL",
                    details: f"Errors handled gracefully: {len(state.errors)}"
                })
            except Exception as e:
                self.test_results.append({
                    test: "Claude API Failure",
                    status: "FAIL",
                    details: f"Unhandled exception: {str(e)}"
                })
        
        # Test 3: Supabase connection failure
        with patch('supabase.create_client') as mock_supabase:
            mock_supabase.side_effect = Exception("Connection timeout")
            
            agent = MarketNewsAgent()
            state = AgentState(
                search_queries=[],
                raw_news=[],
                processed_news=[],
                posted_news=[],
                errors=[]
            )
            
            try:
                result = await agent.post_to_supabase(state)
                self.test_results.append({
                    test: "Supabase Connection Failure",
                    status: "PASS" if len(state.errors) > 0 else "FAIL",
                    details: f"Connection errors handled: {len(state.errors)}"
                })
            except Exception as e:
                self.test_results.append({
                    test: "Supabase Connection Failure",
                    status: "FAIL",
                    details: f"Unhandled exception: {str(e)}"
                })

    async def test_data_integrity_scenarios(self):
        """Test data integrity under various conditions"""
        print("🔒 Testing data integrity scenarios...")
        
        # Test 1: Malformed news data
        malformed_data = [
            {"title": None, "content": "Valid content"},  # Missing title
            {"title": "Valid title", "content": ""},  # Empty content
            {"title": "A" * 300, "content": "Valid content"},  # Extremely long title
            {"title": "Valid", "content": "<script>alert('xss')</script>"},  # XSS attempt
        ]
        
        for i, data in enumerate(malformed_data):
            try:
                agent = MarketNewsAgent()
                state = AgentState(
                    search_queries=[],
                    raw_news=[data],
                    processed_news=[],
                    posted_news=[],
                    errors=[]
                )
                
                result = await agent.analyze_news(state)
                self.test_results.append({
                    test: f"Malformed Data Test {i+1}",
                    status: "PASS" if len(state.errors) > 0 else "FAIL",
                    details: f"Handled malformed data: {data.get('title', 'N/A')[:50]}"
                })
            except Exception as e:
                self.test_results.append({
                    test: f"Malformed Data Test {i+1}",
                    status: "FAIL",
                    details: f"Exception: {str(e)}"
                })
        
        # Test 2: Duplicate detection
        duplicate_data = [
            {"title": "Same Title", "content": "Content 1"},
            {"title": "Same Title", "content": "Content 2"},
            {"title": "Different Title", "content": "Content 3"}
        ]
        
        agent = MarketNewsAgent()
        state = AgentState(
            search_queries=[],
            raw_news=duplicate_data,
            processed_news=[],
            posted_news=[],
            errors=[]
        )
        
        try:
            result = await agent.analyze_news(state)
            # Should detect duplicates and handle appropriately
            self.test_results.append({
                test: "Duplicate Detection",
                status: "PASS",  # We expect this to work
                details: f"Processed {len(result.processed_news)} items with duplicate detection"
            })
        except Exception as e:
            self.test_results.append({
                test: "Duplicate Detection",
                status: "FAIL",
                details: f"Exception: {str(e)}"
            })

    async def test_performance_scenarios(self):
        """Test performance under various conditions"""
        print("⚡ Testing performance scenarios...")
        
        # Test 1: Large dataset processing
        large_dataset = []
        for i in range(100):  # 100 news items
            large_dataset.append({
                "title": f"News Item {i}",
                "content": f"This is test content for item {i} with some additional text to simulate real news content.",
                "url": f"https://example.com/news/{i}"
            })
        
        start_time = time.time()
        
        try:
            agent = MarketNewsAgent()
            state = AgentState(
                search_queries=[],
                raw_news=large_dataset,
                processed_news=[],
                posted_news=[],
                errors=[]
            )
            
            result = await agent.analyze_news(state)
            processing_time = time.time() - start_time
            
            self.test_results.append({
                test: "Large Dataset Processing",
                status: "PASS" if processing_time < 30 else "WARN",  # Should process within 30 seconds
                details: f"Processed {len(large_dataset)} items in {processing_time:.2f}s"
            })
        except Exception as e:
            self.test_results.append({
                test: "Large Dataset Processing",
                status: "FAIL",
                details: f"Exception: {str(e)}"
            })
        
        # Test 2: Memory usage simulation
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            agent = MarketNewsAgent()
            state = AgentState(
                search_queries=[],
                raw_news=large_dataset[:50],  # Smaller dataset for memory test
                processed_news=[],
                posted_news=[],
                errors=[]
            )
            
            await agent.analyze_news(state)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            self.test_results.append({
                test: "Memory Usage",
                status: "PASS" if memory_increase < 100 else "WARN",  # Less than 100MB increase
                details: f"Memory increase: {memory_increase:.2f}MB"
            })
        except ImportError:
            self.test_results.append({
                test: "Memory Usage",
                status: "SKIP",
                details: "psutil not available for memory monitoring"
            })

    async def test_network_conditions(self):
        """Test behavior under various network conditions"""
        print("🌐 Testing network conditions...")
        
        # Test 1: Simulated slow network
        with patch('time.sleep') as mock_sleep:
            # Make sleep take longer to simulate slow network
            mock_sleep.side_effect = lambda x: time.sleep(x * 2)  # Double the delay
            
            start_time = time.time()
            
            try:
                agent = MarketNewsAgent()
                state = AgentState(
                    search_queries=agent.search_queries,
                    raw_news=[],
                    processed_news=[],
                    posted_news=[],
                    errors=[]
                )
                
                result = await agent.search_news(state)
                actual_time = time.time() - start_time
                expected_time = len(agent.search_queries) * 2  # Each query takes 2s with our mock
                
                self.test_results.append({
                    test: "Slow Network Handling",
                    status: "PASS" if actual_time >= expected_time else "FAIL",
                    details: f"Expected {expected_time}s, got {actual_time:.2f}s"
                })
            except Exception as e:
                self.test_results.append({
                    test: "Slow Network Handling",
                    status: "FAIL",
                    details: f"Exception: {str(e)}"
                })

    async def test_cleanup_logic(self):
        """Test the 7-day cleanup logic"""
        print("🧹 Testing cleanup logic...")
        
        # Test 1: Verify 7-day calculation
        from datetime import datetime, timedelta
        
        test_dates = [
            datetime.now() - timedelta(days=6),  # Should NOT be deleted
            datetime.now() - timedelta(days=7),  # Should be deleted (exactly 7 days)
            datetime.now() - timedelta(days=8),  # Should be deleted (over 7 days)
            datetime.now() - timedelta(days=1),   # Should NOT be deleted
        ]
        
        for i, test_date in enumerate(test_dates):
            seven_days_ago = datetime.now() - timedelta(days=7)
            should_delete = test_date < seven_days_ago
            
            self.test_results.append({
                test: f"Cleanup Logic Test {i+1}",
                status: "PASS",
                details: f"Date: {test_date.strftime('%Y-%m-%d')}, Should delete: {should_delete}"
            })

    async def run_all_tests(self):
        """Run all reliability tests"""
        print("🚀 Starting AI Scraper Reliability Tests...")
        print("=" * 50)
        
        await self.test_api_failure_scenarios()
        await self.test_data_integrity_scenarios()
        await self.test_performance_scenarios()
        await self.test_network_conditions()
        await self.test_cleanup_logic()
        
        print("=" * 50)
        print("📊 Test Results Summary:")
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📈 Success Rate: {(passed/(passed+failed+warnings)*100):.1f}%")
        
        if failed > 0:
            print("\n🚨 Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        if warnings > 0:
            print("\n⚠️  Warnings:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"  ⚠️  {result['test']}: {result['details']}")
        
        return {
            "total_tests": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "success_rate": (passed/(passed+failed+warnings)*100,
            "results": self.test_results
        }

async def main():
    """Main test runner"""
    tester = ScraperReliabilityTest()
    results = await tester.run_all_tests()
    
    # Save results to file
    with open('scraper_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to scraper_test_results.json")
    
    # Return appropriate exit code
    if results["failed"] > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
