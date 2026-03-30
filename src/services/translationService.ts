export interface TranslationRequest {
  text: string;
  from: string;
  to: string;
  context?: 'legal' | 'general' | 'marketplace';
}

export interface TranslationResponse {
  translatedText: string;
  confidence: number;
  semanticMapping?: Record<string, string>;
}

export class TranslationService {
  private apiKey: string;
  private baseUrl: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_OPENAI_API_KEY || '';
    this.baseUrl = 'https://api.openai.com/v1/chat/completions';
  }

  async translateLegalText(request: TranslationRequest): Promise<TranslationResponse> {
    if (!this.apiKey) {
      throw new Error('OpenAI API key not configured');
    }

    const systemPrompt = this.getLegalTranslationPrompt(request.from, request.to);
    
    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-4',
          messages: [
            {
              role: 'system',
              content: systemPrompt
            },
            {
              role: 'user',
              content: `Translate the following legal/contract text while preserving exact legal meaning:\n\n${request.text}`
            }
          ],
          temperature: 0.1,
          max_tokens: 2000
        })
      });

      if (!response.ok) {
        throw new Error(`Translation API error: ${response.statusText}`);
      }

      const data = await response.json();
      const translatedText = data.choices[0]?.message?.content || '';

      return {
        translatedText: translatedText.trim(),
        confidence: 0.95,
        semanticMapping: this.extractSemanticMapping(request.text)
      };
    } catch (error) {
      console.error('Translation error:', error);
      throw new Error('Failed to translate text');
    }
  }

  private getLegalTranslationPrompt(from: string, to: string): string {
    const languageNames = {
      'en': 'English',
      'es': 'Spanish',
      'am': 'Amharic'
    };

    return `You are a legal translation expert specializing in international contract law. 

Translate legal documents from ${languageNames[from as keyof typeof languageNames]} to ${languageNames[to as keyof typeof languageNames]}.

CRITICAL REQUIREMENTS:
1. Maintain EXACT legal meaning and semantic equivalence
2. Preserve legal terminology accuracy
3. Ensure contractual obligations remain identical
4. Keep the same level of formality and legal precision
5. Do not add, remove, or modify legal concepts
6. Maintain the same structure and formatting where possible

Return ONLY the translated text without any explanations or additional commentary.`;
  }

  private extractSemanticMapping(original: string): Record<string, string> {
    const mapping: Record<string, string> = {};
    
    const legalTerms = [
      'contract', 'agreement', 'party', 'obligation', 'liability',
      'warranty', 'indemnify', 'breach', 'termination', 'jurisdiction'
    ];

    legalTerms.forEach(term => {
      const regex = new RegExp(`\\b${term}\\b`, 'gi');
      if (regex.test(original)) {
        mapping[term] = term;
      }
    });

    return mapping;
  }

  async detectLanguage(text: string): Promise<string> {
    const samples = {
      'en': /\b(the|and|or|but|in|on|at|to|for|of|with|by)\b/i,
      'es': /\b(el|la|y|o|pero|en|de|a|para|con|por)\b/i,
      'am': /\b(እና|ወይም|ግን|በ|ለ|ከ|የ|እንደ|ጋር|በኩል)\b/i
    };

    for (const [lang, pattern] of Object.entries(samples)) {
      if (pattern.test(text)) {
        return lang;
      }
    }

    return 'en';
  }
}

export const translationService = new TranslationService();
