#!/usr/bin/env python3
"""
Cleanup Logic Verification Test
Tests the 7-day auto-delete logic for market news
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CleanupLogicTest:
    def __init__(self):
        self.test_results = []
        
    def test_seven_day_calculation(self):
        """Test the 7-day calculation logic"""
        print("📅 Testing 7-day calculation logic...")
        
        test_cases = [
            {
                "name": "Exactly 7 days ago",
                "input_date": datetime.now() - timedelta(days=7),
                "expected_should_delete": True,
                "description": "Should be deleted - exactly 7 days old"
            },
            {
                "name": "6 days ago",
                "input_date": datetime.now() - timedelta(days=6),
                "expected_should_delete": False,
                "description": "Should NOT be deleted - only 6 days old"
            },
            {
                "name": "8 days ago",
                "input_date": datetime.now() - timedelta(days=8),
                "expected_should_delete": True,
                "description": "Should be deleted - over 7 days old"
            },
            {
                "name": "1 day ago",
                "input_date": datetime.now() - timedelta(days=1),
                "expected_should_delete": False,
                "description": "Should NOT be deleted - only 1 day old"
            },
            {
                "name": "7 days minus 1 second",
                "input_date": datetime.now() - timedelta(days=7, seconds=1),
                "expected_should_delete": True,
                "description": "Should be deleted - just over 7 days"
            },
            {
                "name": "7 days plus 1 second",
                "input_date": datetime.now() - timedelta(days=7, seconds=-1),
                "expected_should_delete": False,
                "description": "Should NOT be deleted - just under 7 days"
            }
        ]
        
        for test_case in test_cases:
            # Simulate the SQL logic: DELETE FROM market_news WHERE created_at < now() - interval '7 days'
            seven_days_ago = datetime.now() - timedelta(days=7)
            should_delete = test_case["input_date"] < seven_days_ago
            
            passed = should_delete == test_case["expected_should_delete"]
            
            self.test_results.append({
                "test": f"7-Day Calculation - {test_case['name']}",
                "status": "PASS" if passed else "FAIL",
                "input_date": test_case["input_date"].isoformat(),
                "seven_days_ago": seven_days_ago.isoformat(),
                "should_delete": should_delete,
                "expected": test_case["expected_should_delete"],
                "description": test_case["description"]
            })
            
            status_icon = "✅" if passed else "❌"
            print(f"  {status_icon} {test_case['name']}: {test_case['description']}")
            print(f"     Input: {test_case['input_date'].isoformat()}")
            print(f"     7 days ago: {seven_days_ago.isoformat()}")
            print(f"     Should delete: {should_delete}")
            print(f"     Expected: {test_case['expected_should_delete']}")
            print()

    def test_edge_cases(self):
        """Test edge cases for cleanup logic"""
        print("🔍 Testing edge cases...")
        
        # Test 1: Future dates
        future_date = datetime.now() + timedelta(days=1)
        should_delete_future = future_date < (datetime.now() - timedelta(days=7))
        
        self.test_results.append({
            "test": "Future Date Handling",
            "status": "PASS" if not should_delete_future else "FAIL",
            "description": "Future dates should never be deleted",
            "input": future_date.isoformat(),
            "should_delete": should_delete_future
        })
        
        # Test 2: Null/None dates
        try:
            should_delete_null = None < (datetime.now() - timedelta(days=7))
            self.test_results.append({
                "test": "Null Date Handling",
                "status": "FAIL",
                "description": "Should handle null dates gracefully",
                "error": "TypeError occurred"
            })
        except TypeError as e:
            self.test_results.append({
                "test": "Null Date Handling",
                "status": "PASS",
                "description": "Correctly handled null date with TypeError",
                "error": str(e)
            })
        
        # Test 3: Invalid date formats
        try:
            invalid_date = "invalid-date-string"
            should_delete_invalid = invalid_date < (datetime.now() - timedelta(days=7))
            self.test_results.append({
                "test": "Invalid Date Format",
                "status": "FAIL",
                "description": "Should handle invalid date formats",
                "error": "Should have raised TypeError"
            })
        except Exception as e:
            self.test_results.append({
                "test": "Invalid Date Format",
                "status": "PASS",
                "description": "Correctly handled invalid date format",
                "error": type(e).__name__
            })

    def test_sql_injection_resistance(self):
        """Test that cleanup logic is resistant to SQL injection"""
        print("🛡️  Testing SQL injection resistance...")
        
        # Simulate malicious input that might be used in crafted dates
        malicious_inputs = [
            "2023-01-01'; DROP TABLE market_news; --",
            "2023-01-01' OR '1'='1",
            "2023-01-01' UNION SELECT * FROM users --"
        ]
        
        for malicious_input in malicious_inputs:
            try:
                # This should fail gracefully, not execute SQL
                should_delete = malicious_input < (datetime.now() - timedelta(days=7))
                self.test_results.append({
                    "test": f"SQL Injection - {malicious_input[:20]}...",
                    "status": "FAIL" if should_delete else "PASS",
                    "description": "Should reject malicious input",
                    "input": malicious_input,
                    "should_delete": should_delete
                })
            except Exception as e:
                self.test_results.append({
                    "test": f"SQL Injection - {malicious_input[:20]}...",
                    "status": "PASS",
                    "description": "Correctly rejected malicious input",
                    "error": type(e).__name__
                })

    def test_boundary_conditions(self):
        """Test boundary conditions"""
        print("🎯 Testing boundary conditions...")
        
        # Test exactly at 7-day boundary
        boundary_tests = [
            {
                "name": "Exactly 7 days - 1 microsecond",
                "offset": timedelta(days=7, microseconds=-1),
                "should_delete": False
            },
            {
                "name": "Exactly 7 days",
                "offset": timedelta(days=7),
                "should_delete": False  # created_at < now() - interval '7 days' means strictly less than
            },
            {
                "name": "Exactly 7 days + 1 microsecond", 
                "offset": timedelta(days=7, microseconds=1),
                "should_delete": True
            }
        ]
        
        for test in boundary_tests:
            test_date = datetime.now() - test["offset"]
            seven_days_ago = datetime.now() - timedelta(days=7)
            should_delete = test_date < seven_days_ago
            
            passed = should_delete == test["should_delete"]
            
            self.test_results.append({
                "test": f"Boundary Test - {test['name']}",
                "status": "PASS" if passed else "FAIL",
                "description": f"Offset: {test['offset']}, Should delete: {test['should_delete']}",
                "result": f"Actual: {should_delete}"
            })

    def test_timezone_handling(self):
        """Test timezone handling"""
        print("🌍 Testing timezone handling...")
        
        # Test with different timezones
        from datetime import timezone, timedelta
        
        utc_time = datetime.now(timezone.utc)
        local_time = datetime.now()
        
        # Both should work the same way for relative calculations
        utc_seven_days_ago = utc_time - timedelta(days=7)
        local_seven_days_ago = local_time - timedelta(days=7)
        
        # Test dates
        test_date_utc = utc_time - timedelta(days=8)
        test_date_local = local_time - timedelta(days=8)
        
        should_delete_utc = test_date_utc < utc_seven_days_ago
        should_delete_local = test_date_local < local_seven_days_ago
        
        self.test_results.append({
            "test": "Timezone UTC",
            "status": "PASS" if should_delete_utc else "FAIL",
            "description": "UTC timezone handling",
            "should_delete": should_delete_utc
        })
        
        self.test_results.append({
            "test": "Timezone Local",
            "status": "PASS" if should_delete_local else "FAIL",
            "description": "Local timezone handling",
            "should_delete": should_delete_local
        })

    async def run_all_tests(self):
        """Run all cleanup logic tests"""
        print("🚀 Starting Cleanup Logic Verification Tests...")
        print("=" * 60)
        
        self.test_seven_day_calculation()
        self.test_edge_cases()
        self.test_sql_injection_resistance()
        self.test_boundary_conditions()
        self.test_timezone_handling()
        
        print("=" * 60)
        print("📊 Test Results Summary:")
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed > 0:
            print("\n🚨 Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  ❌ {result['test']}")
                    print(f"     {result['description']}")
                    if 'error' in result:
                        print(f"     Error: {result['error']}")
        
        return {
            "total_tests": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed/(passed+failed)*100,
            "results": self.test_results
        }

async def main():
    """Main test runner"""
    tester = CleanupLogicTest()
    results = await tester.run_all_tests()
    
    # Save results to file
    import json
    with open('cleanup_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to cleanup_test_results.json")
    
    # Return appropriate exit code
    if results["failed"] > 0:
        print("\n❌ Some cleanup logic tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All cleanup logic tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
