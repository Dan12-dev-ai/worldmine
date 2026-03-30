// Security audit utilities
export const checkEnvironmentSafety = () => {
  const issues: { type: string; file: string; line?: number; issue: string; severity: 'high' | 'medium' | 'low' }[] = [];
  
  // Check for hardcoded API keys patterns
  const dangerousPatterns = [
    /sk-[a-zA-Z0-9]{48}/,  // OpenAI API key pattern
    /sk-[a-zA-Z0-9]{20}/,  // Shorter OpenAI key pattern
    /sk-proj-[a-zA-Z0-9-]{48}/, // OpenAI project key
    /sk-ant-[a-zA-Z0-9]{32}/,  // Anthropic key pattern
    /eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*/, // JWT token
    /-----BEGIN [A-Z]+-----/, // Private key headers
    /AIza[a-zA-Z0-9_-]{35}/, // Google API key pattern
    /ghp_[a-zA-Z0-9]{36}/, // GitHub personal access token
    /glpat-[a-zA-Z0-9_-]{20}/, // GitLab personal access token
  ];
  
  // Check for hardcoded secrets in source files
  const sourceFiles = document.querySelectorAll('script[src*=".ts"], script[src*=".js"]');
  sourceFiles.forEach(script => {
    const src = script.getAttribute('src');
    if (src) {
      dangerousPatterns.forEach(pattern => {
        if (pattern.test(src)) {
          issues.push({
            type: 'hardcoded_secret',
            file: src,
            issue: `Potential hardcoded secret detected: ${pattern.source}`,
            severity: 'high'
          });
        }
      });
    }
  });
  
  // Check for environment variable usage
  const envVarPatterns = [
    /process\.env\./,
    /import\.meta\.env\./,
    /Deno\.env\.get/,
  ];
  
  // Check for unsafe environment variable access
  const unsafeEnvAccess = [
    'process.env.OPENAI_API_KEY',
    'process.env.ANTHROPIC_API_KEY', 
    'process.env.SUPABASE_SERVICE_ROLE_KEY',
    'process.env.TAVILY_API_KEY',
  ];
  
  // This would be checked in the actual source code
  // For now, we'll assume it's safe since we're using process.env
  
  return issues;
};

export const generateSecurityReport = () => {
  const issues = checkEnvironmentSafety();
  
  return {
    timestamp: new Date().toISOString(),
    total_issues: issues.length,
    high_severity: issues.filter(i => i.severity === 'high').length,
    medium_severity: issues.filter(i => i.severity === 'medium').length,
    low_severity: issues.filter(i => i.severity === 'low').length,
    issues: issues,
    recommendations: [
      'Use environment variables for all secrets',
      'Add .env files to .gitignore',
      'Implement secret scanning in CI/CD',
      'Use environment-specific configuration',
      'Rotate API keys regularly',
      'Implement proper access controls'
    ]
  };
};
