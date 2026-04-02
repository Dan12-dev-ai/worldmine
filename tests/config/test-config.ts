/**
 * Comprehensive Testing Strategy Configuration
 * Defines testing frameworks, coverage requirements, and quality standards
 */

export interface TestConfig {
  unit: {
    frameworks: ['jest', 'vitest'];
    coverage: {
      threshold: number;
      excludePatterns: string[];
      includePatterns: string[];
      reporters: string[];
    };
    types: ['unit', 'integration'];
  };
  
  e2e: {
    frameworks: ['playwright', 'cypress'];
    browsers: ['chromium', 'firefox', 'webkit'];
    devices: ['desktop', 'mobile', 'tablet'];
    viewports: {
      desktop: { width: 1920, height: 1080 };
      mobile: { width: 375, height: 667 };
      tablet: { width: 768, height: 1024 };
    };
    timeout: number;
    retries: number;
  };
  
  performance: {
    tools: ['k6', 'artillery'];
    scenarios: ['normal_load', 'peak_load', 'stress_test', 'spike_test'];
    metrics: ['response_time', 'throughput', 'error_rate', 'cpu_usage', 'memory_usage'];
    thresholds: {
      responseTime: { p50: 200, p95: 500, p99: 1000 };
      throughput: { min: 100, target: 500 };
      errorRate: { max: 0.01 }; // 1%
      cpuUsage: { max: 80 }; // 80%
      memoryUsage: { max: 85 }; // 85%
    };
  };
  
  security: {
    tools: ['owasp_zap', 'burp_suite', 'sonarqube'];
    scans: ['sast', 'dast', 'dependency_check', 'container_scan'];
    severity: ['low', 'medium', 'high', 'critical'];
    schedules: ['daily', 'weekly', 'on_commit'];
  };
  
  accessibility: {
    tools: ['axe', 'lighthouse', 'wave'];
    standards: ['wcag_2_2_aa', 'section_508'];
    levels: ['A', 'AA', 'AAA'];
    automated: boolean;
    manual: boolean;
  };
  
  api: {
    tools: ['postman', 'insomnia', 'rest_assured'];
    environments: ['development', 'staging', 'production'];
    authentication: ['jwt', 'oauth', 'api_key'];
    rateLimiting: boolean;
    documentation: boolean;
  };
  
  integration: {
    services: ['supabase', 'stripe', 'openai', 'google_maps'];
    mocks: ['database', 'external_apis', 'payment_gateways'];
    contracts: ['api', 'database', 'messaging'];
  };
}

export const WORLDMINE_TEST_CONFIG: TestConfig = {
  unit: {
    frameworks: ['vitest'],
    coverage: {
      threshold: 80,
      excludePatterns: [
        'node_modules/**',
        'dist/**',
        'tests/**',
        '**/*.d.ts',
        '**/*.config.*',
        'coverage/**'
      ],
      includePatterns: [
        'src/**/*.{ts,tsx}',
        '!src/**/*.stories.*',
        '!src/**/*.test.*',
        '!src/**/*.spec.*'
      ],
      reporters: ['text', 'lcov', 'html', 'json']
    },
    types: ['unit', 'integration']
  },
  
  e2e: {
    frameworks: ['playwright'],
    browsers: ['chromium', 'firefox', 'webkit'],
    devices: ['desktop', 'mobile', 'tablet'],
    viewports: {
      desktop: { width: 1920, height: 1080 },
      mobile: { width: 375, height: 667 },
      tablet: { width: 768, height: 1024 }
    },
    timeout: 30000, // 30 seconds
    retries: 3
  },
  
  performance: {
    tools: ['k6'],
    scenarios: ['normal_load', 'peak_load', 'stress_test'],
    metrics: ['response_time', 'throughput', 'error_rate', 'cpu_usage', 'memory_usage'],
    thresholds: {
      responseTime: { p50: 200, p95: 500, p99: 1000 },
      throughput: { min: 100, target: 500 },
      errorRate: { max: 0.01 },
      cpuUsage: { max: 80 },
      memoryUsage: { max: 85 }
    }
  },
  
  security: {
    tools: ['owasp_zap', 'sonarqube'],
    scans: ['sast', 'dast', 'dependency_check', 'container_scan'],
    severity: ['low', 'medium', 'high', 'critical'],
    schedules: ['daily', 'weekly', 'on_commit']
  },
  
  accessibility: {
    tools: ['axe', 'lighthouse'],
    standards: ['wcag_2_2_aa', 'section_508'],
    levels: ['A', 'AA'],
    automated: true,
    manual: true
  },
  
  api: {
    tools: ['postman'],
    environments: ['development', 'staging', 'production'],
    authentication: ['jwt', 'oauth', 'api_key'],
    rateLimiting: true,
    documentation: true
  },
  
  integration: {
    services: ['supabase', 'stripe', 'openai'],
    mocks: ['database', 'external_apis', 'payment_gateways'],
    contracts: ['api', 'database', 'messaging']
  }
};

export default WORLDMINE_TEST_CONFIG;
