import { useTranslation } from 'react-i18next';

// Localization overflow detection utilities
export const detectLocalizationIssues = () => {
  const { t, i18n } = useTranslation();
  
  const issues = {
    // Test 1: Check for hardcoded strings
    hardcodedStrings: () => {
      const hardcodedPatterns = [
        /Login|Sign Up|Register|Search|Cart|Profile/i,
        /Price|Quantity|Category|Description/i,
        /Submit|Cancel|Delete|Edit|Save/i,
        /Welcome|Hello|Goodbye|Thank you/i
      ];
      
      const elements = document.querySelectorAll('*');
      const issues: { element: string; text: string; pattern: string }[] = [];
      
      elements.forEach(element => {
        const text = element.textContent || '';
        hardcodedPatterns.forEach(pattern => {
          if (pattern.test(text) && !text.includes('{{') && !text.includes('${')) {
            issues.push({
              element: element.tagName.toLowerCase(),
              text: text.substring(0, 100),
              pattern: pattern.source
            });
          }
        });
      });
      
      return issues;
    },

    // Test 2: Check for text overflow in different languages
    textOverflow: () => {
      const testTexts = {
        en: {
          title: 'Global Mining Marketplace',
          description: 'Trade commodities with secure smart contracts',
          longText: 'This is a very long text that might cause overflow in certain languages especially when translated to Amharic which uses different character widths and spacing patterns'
        },
        es: {
          title: 'Mercado Global de Minería',
          description: 'Comercie materias primas con contratos inteligentes seguros',
          longText: 'Este es un texto muy largo que podría causar desbordamiento en ciertos idiomas, especialmente cuando se traduce al amárico que usa diferentes anchos de carácter y patrones de espaciado'
        },
        am: {
          title: 'ዓለማዊ የማዕድን ገበያ',
          description: 'ንዣንዎታንዎችንዎችንዎችንዎችንዎችንዎችንዎችንዎችንዎችንዎች ከደህናት ጋቢያያያይ ማርተማ',
          longText: 'ይህ በጣም ተረጽፍ የሚለው ከሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው የሚለው'
        }
      };
      
      const overflowIssues: { language: string; element: string; issue: string }[] = [];
      
      Object.entries(testTexts).forEach(([lang, texts]) => {
        // Create test elements
        const testDiv = document.createElement('div');
        testDiv.style.width = '200px';
        testDiv.style.padding = '8px';
        testDiv.style.fontSize = '14px';
        testDiv.style.lineHeight = '1.4';
        testDiv.style.overflow = 'hidden';
        testDiv.style.whiteSpace = 'nowrap';
        testDiv.textContent = texts.longText;
        
        document.body.appendChild(testDiv);
        
        const scrollWidth = testDiv.scrollWidth;
        const clientWidth = testDiv.clientWidth;
        const isOverflowing = scrollWidth > clientWidth;
        
        if (isOverflowing) {
          overflowIssues.push({
            language: lang,
            element: 'test-div',
            issue: `Text overflow detected (${scrollWidth}px vs ${clientWidth}px)`
          });
        }
        
        document.body.removeChild(testDiv);
      });
      
      return overflowIssues;
    },

    // Test 3: Check for missing translations
    missingTranslations: () => {
      const currentLanguage = i18n.language;
      const requiredKeys = [
        'navbar.marketplace',
        'navbar.contracts',
        'navbar.profile',
        'marketplace.search',
        'marketplace.price',
        'contracts.sign',
        'auth.signIn',
        'auth.signUp',
        'common.loading',
        'common.error',
        'common.save'
      ];
      
      const missingKeys: string[] = [];
      
      requiredKeys.forEach(key => {
        try {
          const translation = t(key);
          if (translation === key) { // If translation returns the key itself
            missingKeys.push(key);
          }
        } catch (error) {
          missingKeys.push(key);
        }
      });
      
      return {
        language: currentLanguage,
        missingKeys,
        totalRequired: requiredKeys.length,
        translatedCount: requiredKeys.length - missingKeys.length
      };
    },

    // Test 4: Check for font rendering issues
    fontRendering: () => {
      const testCharacters = {
        amharic: ['ሀ', 'ሁ', 'ሂ', 'ሃ', 'ሄ', 'ህ', 'ሆ', 'ሇ', 'ለ', 'ሉ', 'ሊ', 'ላ', 'ሌ', 'ል', 'ሎ', 'ሏ', 'ሐ', 'ሑ', 'ሒ', 'ሓ', 'ሔ', 'ሕ', 'ሖ', 'ሗ', 'መ', 'ሙ', 'ሚ', 'ማ', 'ሜ', 'ም'],
        spanish: ['ñ', 'á', 'é', 'í', 'ó', 'ú', 'ü', '¿', '¡', 'ß', 'ç', 'ë', 'ï', 'ö'],
        english: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
      };
      
      const fontIssues: { language: string; character: string; rendered: boolean; supported: boolean }[] = [];
      
      Object.entries(testCharacters).forEach(([language, characters]) => {
        characters.forEach(character => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          if (ctx) {
            ctx.font = '14px Arial';
            const metrics = ctx.measureText(character);
            const isRendered = metrics.width > 0;
            const isSupported = !isNaN(metrics.width);
            
            fontIssues.push({
              language,
              character,
              rendered: isRendered,
              supported: isSupported
            });
          }
        });
      });
      
      return fontIssues;
    },

    // Test 5: Check RTL/LTR layout issues
    layoutDirection: () => {
      const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
      const currentLanguage = i18n.language;
      
      const shouldBeRTL = rtlLanguages.includes(currentLanguage);
      const actualDirection = getComputedStyle(document.body).direction;
      
      return {
        language: currentLanguage,
        expectedDirection: shouldBeRTL ? 'rtl' : 'ltr',
        actualDirection,
        isCorrect: (shouldBeRTL && actualDirection === 'rtl') || (!shouldBeRTL && actualDirection === 'ltr')
      };
    }
  };

  return issues;
};

// Localization fix utilities
export const fixLocalizationIssues = () => {
  const issues = detectLocalizationIssues();
  const fixes = [];

  // Fix hardcoded strings
  if (issues.hardcodedStrings().length > 0) {
    fixes.push({
      type: 'hardcoded_strings',
      description: 'Replace hardcoded strings with i18n keys',
      action: 'Use t() function for all user-facing text',
      priority: 'high'
    });
  }

  // Fix text overflow
  if (issues.textOverflow().length > 0) {
    fixes.push({
      type: 'text_overflow',
      description: 'Implement responsive text handling',
      action: 'Add text truncation, responsive fonts, or dynamic sizing',
      priority: 'medium'
    });
  }

  // Fix missing translations
  const missingTrans = issues.missingTranslations();
  if (missingTrans.missingKeys.length > 0) {
    fixes.push({
      type: 'missing_translations',
      description: `${missingTrans.missingKeys.length} missing translations in ${missingTrans.language}`,
      action: 'Add missing keys to language files',
      priority: 'high'
    });
  }

  // Fix font rendering
  if (issues.fontRendering().some(issue => !issue.supported)) {
    fixes.push({
      type: 'font_support',
      description: 'Some characters not rendering properly',
      action: 'Load appropriate fonts (Noto Sans for Amharic, etc.)',
      priority: 'high'
    });
  }

  // Fix layout direction
  const layoutIssue = issues.layoutDirection();
  if (!layoutIssue.isCorrect) {
    fixes.push({
      type: 'layout_direction',
      description: `Incorrect text direction for ${layoutIssue.language}`,
      action: 'Apply proper RTL/LTR styles based on language',
      priority: 'medium'
    });
  }

  return fixes;
};

// CSS generation for language-specific styles
export const generateLanguageCSS = (language: string) => {
  const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
  const isRTL = rtlLanguages.includes(language);
  
  const fontFamilies = {
    am: "'Noto Sans Ethiopic', 'Babel Unicode MS', sans-serif",
    es: "'Roboto', 'Noto Sans', sans-serif",
    en: "'Inter', 'Helvetica Neue', sans-serif",
    ar: "'Noto Sans Arabic', 'Tahoma', sans-serif"
  };

  return `
    html[dir="${isRTL ? 'rtl' : 'ltr'}"] {
      direction: ${isRTL ? 'rtl' : 'ltr'};
      text-align: ${isRTL ? 'right' : 'left'};
    }
    
    body {
      font-family: ${fontFamilies[language as keyof typeof fontFamilies] || fontFamilies.en};
      line-height: 1.6;
    }
    
    .text-truncate {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .text-responsive {
      font-size: clamp(12px, 2vw, 16px);
    }
  `;
};
