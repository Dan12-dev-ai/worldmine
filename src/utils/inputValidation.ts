// Input validation and sanitization utilities
export interface ValidationResult {
  isValid: boolean;
  error?: string;
  sanitizedValue?: any;
}

// SQL Injection detection patterns
const sqlInjectionPatterns = [
  /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)/i,
  /(--|;|\/\*|\*\/|@@|@|CHAR|NCHAR|VARCHAR|NVARCHAR|ALTER|BEGIN|CAST|CREATE|CURSOR|DECLARE|DELETE|DENY|DROP|END|EXEC|EXECUTE|FETCH|INSERT|KILL|OPEN|REVOKE|SET|UNION|UPDATE|WHERE|XP_CMD)/i,
  /('|(\\')|;|\\x00|\\n|\\r|\\\\|\\Z)/i
];

// XSS detection patterns
const xssPatterns = [
  /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
  /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
  /javascript:/gi,
  /on\w+\s*=/gi,
  /<img[^>]*src[^>]*javascript:/gi,
  /<\s*script[^>]*>[^<]*<\s*\/\s*script\s*>/gi
];

export const validateInput = (input: string, type: 'text' | 'email' | 'url' | 'number' = 'text'): ValidationResult => {
  if (!input || typeof input !== 'string') {
    return { isValid: false, error: 'Invalid input type' };
  }

  // Check for null/empty submissions
  if (input.trim() === '' || input.toLowerCase() === 'null') {
    return { isValid: false, error: 'Required field cannot be empty' };
  }

  // Check for extremely large inputs (100MB+ check)
  if (input.length > 104857600) { // 100MB in bytes
    return { isValid: false, error: 'Input too large (max 100MB)' };
  }

  // SQL Injection detection
  for (const pattern of sqlInjectionPatterns) {
    if (pattern.test(input)) {
      return { isValid: false, error: 'Invalid characters detected' };
    }
  }

  // XSS detection
  for (const pattern of xssPatterns) {
    if (pattern.test(input)) {
      return { isValid: false, error: 'Invalid content detected' };
    }
  }

  // Type-specific validation
  switch (type) {
    case 'email':
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(input)) {
        return { isValid: false, error: 'Invalid email format' };
      }
      break;

    case 'url':
      try {
        new URL(input);
      } catch {
        return { isValid: false, error: 'Invalid URL format' };
      }
      break;

    case 'number':
      const num = parseFloat(input);
      if (isNaN(num) || !isFinite(num)) {
        return { isValid: false, error: 'Invalid number format' };
      }
      if (num < 0) {
        return { isValid: false, error: 'Number must be positive' };
      }
      return { isValid: true, sanitizedValue: num };
  }

  // Sanitize text input
  const sanitized = input
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/<iframe[^>]*>.*?<\/iframe>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .trim();

  return { isValid: true, sanitizedValue: sanitized };
};

export const validateFileSize = (file: File, maxSize: number = 104857600): ValidationResult => {
  if (file.size > maxSize) {
    return { 
      isValid: false, 
      error: `File too large. Maximum size is ${Math.round(maxSize / 1024 / 1024)}MB` 
    };
  }

  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain'];
  if (!allowedTypes.includes(file.type)) {
    return { 
      isValid: false, 
      error: 'Invalid file type. Only images, PDFs, and text files are allowed' 
    };
  }

  return { isValid: true };
};

export const sanitizeHTML = (html: string): string => {
  const temp = document.createElement('div');
  temp.textContent = html;
  return temp.innerHTML;
};

// Edge case test utilities
export const generateEdgeCaseTests = () => {
  return {
    sqlInjection: [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "1'; DELETE FROM users WHERE '1'='1",
      "admin'--",
      "' UNION SELECT * FROM passwords--"
    ],
    xssAttacks: [
      "<script>alert('XSS')</script>",
      "<img src=x onerror=alert('XSS')>",
      "javascript:alert('XSS')",
      "<svg onload=alert('XSS')>",
      "<iframe src='javascript:alert(\"XSS\")'></iframe>",
      "'; alert('XSS'); var x='"
    ],
    largeInputs: [
      'A'.repeat(104857601), // Just over 100MB
      '0'.repeat(200000000),  // 200MB of zeros
      '\n'.repeat(50000000)   // 50MB of newlines
    ],
    emptyInputs: [
      '',
      '   ',
      'null',
      'NULL',
      'undefined',
      '[]',
      '{}'
    ]
  };
};
