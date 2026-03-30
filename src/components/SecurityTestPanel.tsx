import React, { useState } from 'react';
import { validateInput, validateFileSize, generateEdgeCaseTests } from '../utils/inputValidation';
import { Button } from './ui/button';
import { Shield, AlertTriangle, CheckCircle, X } from 'lucide-react';

interface TestResult {
  testName: string;
  input: string;
  expected: 'pass' | 'fail';
  actual: 'pass' | 'fail';
  message: string;
}

const SecurityTestPanel: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const runSecurityTests = async () => {
    setIsRunning(true);
    const results: TestResult[] = [];
    const edgeCases = generateEdgeCaseTests();

    // Test SQL Injection attempts
    for (const sqlAttempt of edgeCases.sqlInjection) {
      const result = validateInput(sqlAttempt, 'text');
      results.push({
        testName: 'SQL Injection',
        input: sqlAttempt.substring(0, 50) + '...',
        expected: 'fail',
        actual: result.isValid ? 'pass' : 'fail',
        message: result.error || 'Valid input detected'
      });
    }

    // Test XSS attempts
    for (const xssAttempt of edgeCases.xssAttacks) {
      const result = validateInput(xssAttempt, 'text');
      results.push({
        testName: 'XSS Attack',
        input: xssAttempt.substring(0, 50) + '...',
        expected: 'fail',
        actual: result.isValid ? 'pass' : 'fail',
        message: result.error || 'Valid input detected'
      });
    }

    // Test large inputs
    for (const largeInput of edgeCases.largeInputs) {
      const result = validateInput(largeInput, 'text');
      results.push({
        testName: 'Large Input',
        input: `${largeInput.length} characters`,
        expected: 'fail',
        actual: result.isValid ? 'pass' : 'fail',
        message: result.error || 'Valid input detected'
      });
    }

    // Test empty inputs
    for (const emptyInput of edgeCases.emptyInputs) {
      const result = validateInput(emptyInput, 'text');
      results.push({
        testName: 'Empty Input',
        input: JSON.stringify(emptyInput),
        expected: 'fail',
        actual: result.isValid ? 'pass' : 'fail',
        message: result.error || 'Valid input detected'
      });
    }

    // Test email validation
    const emailTests = [
      { email: 'test@example.com', expected: 'pass' },
      { email: 'invalid-email', expected: 'fail' },
      { email: 'test@.com', expected: 'fail' },
      { email: '<script>alert("xss")>@example.com', expected: 'fail' }
    ];

    for (const emailTest of emailTests) {
      const result = validateInput(emailTest.email, 'email');
      results.push({
        testName: 'Email Validation',
        input: emailTest.email,
        expected: emailTest.expected,
        actual: result.isValid ? 'pass' : 'fail',
        message: result.error || 'Valid email detected'
      });
    }

    setTestResults(results);
    setIsRunning(false);
  };

  const clearResults = () => {
    setTestResults([]);
  };

  const getTestStatusColor = (expected: string, actual: string) => {
    return expected === actual ? 'text-green-600' : 'text-red-600';
  };

  const getTestIcon = (expected: string, actual: string) => {
    return expected === actual ? 
      <CheckCircle className="w-4 h-4" /> : 
      <X className="w-4 h-4" />;
  };

  const failedTests = testResults.filter(r => r.expected !== r.actual).length;
  const totalTests = testResults.length;
  const passRate = totalTests > 0 ? ((totalTests - failedTests) / totalTests * 100).toFixed(1) : '0';

  return (
    <div className="glass-morphism rounded-2xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="w-6 h-6 text-neon-cyan" />
          <h3 className="text-xl font-bold text-white">Security Test Panel</h3>
        </div>
        <div className="flex items-center space-x-3">
          <Button 
            onClick={runSecurityTests} 
            disabled={isRunning}
            className="bg-neon-cyan hover:bg-neon-cyan/80"
          >
            {isRunning ? 'Running Tests...' : 'Run Security Tests'}
          </Button>
          <Button 
            onClick={clearResults} 
            variant="ghost"
            disabled={testResults.length === 0}
          >
            Clear Results
          </Button>
        </div>
      </div>

      {testResults.length > 0 && (
        <div className="bg-black/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <span className="text-gray-400">Tests Run:</span>
                <span className="text-white font-bold ml-2">{totalTests}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-400">Failed:</span>
                <span className={`font-bold ml-2 ${failedTests > 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {failedTests}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-gray-400">Pass Rate:</span>
                <span className={`font-bold ml-2 ${failedTests === 0 ? 'text-green-500' : 'text-yellow-500'}`}>
                  {passRate}%
                </span>
              </div>
            </div>
            {failedTests > 0 && (
              <div className="flex items-center space-x-2 text-red-500">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-medium">Security vulnerabilities detected!</span>
              </div>
            )}
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {testResults.map((result, index) => (
              <div 
                key={index} 
                className="flex items-start justify-between p-3 rounded-lg border border-white/10 hover:border-neon-cyan/30 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-medium text-gray-400 min-w-24">
                      {result.testName}
                    </span>
                    <div className={`flex items-center space-x-1 ${getTestStatusColor(result.expected, result.actual)}`}>
                      {getTestIcon(result.expected, result.actual)}
                      <span className="text-xs font-medium uppercase">
                        {result.actual}
                      </span>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 break-all">
                    Input: {result.input}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {result.message}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {testResults.length === 0 && (
        <div className="text-center py-12">
          <Shield className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">
            Click "Run Security Tests" to validate input sanitization and security measures
          </p>
        </div>
      )}
    </div>
  );
};

export default SecurityTestPanel;
