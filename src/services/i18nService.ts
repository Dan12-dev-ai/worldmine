/**
 * Internationalization Service
 * Handles multi-language support for Worldmine marketplace
 */

import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database';

const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

// Types
export interface Language {
  code: string;
  name: string;
  nativeName: string;
  rtl: boolean;
  flag: string;
  region: string;
  dateFormat: string;
  numberFormat: string;
  currencyFormat: string;
}

export interface Translation {
  key: string;
  value: string;
  context?: string;
  plural?: boolean;
  variables?: Record<string, any>;
}

export interface TranslationNamespace {
  name: string;
  translations: Record<string, Translation>;
  lastUpdated: string;
  version: string;
}

export interface LocalizedContent {
  [key: string]: {
    [language: string]: string;
  };
}

export interface UserLanguagePreference {
  userId: string;
  language: string;
  region: string;
  dateFormat: string;
  timeFormat: string;
  numberFormat: string;
  timezone: string;
  currency: string;
  createdAt: string;
  updatedAt: string;
}

export interface TranslationMemory {
  id: string;
  sourceLanguage: string;
  targetLanguage: string;
  sourceText: string;
  translatedText: string;
  context: string;
  confidence: number; // 0-100
  approved: boolean;
  createdAt: string;
  approvedAt?: string;
}

export interface MachineTranslationResult {
  translatedText: string;
  confidence: number;
  sourceLanguage: string;
  targetLanguage: string;
  alternatives?: string[];
  detectedLanguage?: string;
}

export interface CurrencyLocalization {
  code: string;
  symbol: string;
  position: 'before' | 'after';
  decimalSeparator: string;
  thousandsSeparator: string;
  precision: number;
}

export interface DateLocalization {
  formats: {
    short: string;
    medium: string;
    long: string;
    full: string;
  };
  relativeFormats: {
    seconds: string;
    minutes: string;
    hours: string;
    days: string;
    weeks: string;
    months: string;
    years: string;
  };
}

export interface NumberLocalization {
  decimalSeparator: string;
  thousandsSeparator: string;
  precision: number;
  grouping: boolean;
}

// Supported Languages
export const SUPPORTED_LANGUAGES: Language[] = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    rtl: false,
    flag: '🇺🇸',
    region: 'global',
    dateFormat: 'MM/DD/YYYY',
    numberFormat: '1,234.56',
    currencyFormat: '$1,234.56'
  },
  {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    rtl: false,
    flag: '🇪🇸',
    region: 'global',
    dateFormat: 'DD/MM/YYYY',
    numberFormat: '1.234,56',
    currencyFormat: '1.234,56 €'
  },
  {
    code: 'am',
    name: 'Amharic',
    nativeName: 'አማርኛ',
    rtl: true,
    flag: '🇪🇹',
    region: 'ethiopia',
    dateFormat: 'DD/MM/YYYY',
    numberFormat: '1,234.56',
    currencyFormat: 'ETB 1,234.56'
  },
  {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    rtl: true,
    flag: '🇸🇦',
    region: 'global',
    dateFormat: 'DD/MM/YYYY',
    numberFormat: '1,234.56',
    currencyFormat: '1,234.56 ر.س'
  },
  {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    rtl: false,
    flag: '🇫🇷',
    region: 'global',
    dateFormat: 'DD/MM/YYYY',
    numberFormat: '1 234,56',
    currencyFormat: '1 234,56 €'
  },
  {
    code: 'zh',
    name: 'Chinese',
    nativeName: '中文',
    rtl: false,
    flag: '🇨🇳',
    region: 'global',
    dateFormat: 'YYYY-MM-DD',
    numberFormat: '1,234.56',
    currencyFormat: '¥1,234.56'
  }
];

// Currency Localizations
export const CURRENCY_LOCALIZATIONS: Record<string, CurrencyLocalization> = {
  USD: {
    code: 'USD',
    symbol: '$',
    position: 'before',
    decimalSeparator: '.',
    thousandsSeparator: ',',
    precision: 2
  },
  EUR: {
    code: 'EUR',
    symbol: '€',
    position: 'after',
    decimalSeparator: ',',
    thousandsSeparator: '.',
    precision: 2
  },
  ETB: {
    code: 'ETB',
    symbol: 'ETB',
    position: 'before',
    decimalSeparator: '.',
    thousandsSeparator: ',',
    precision: 2
  },
  CNY: {
    code: 'CNY',
    symbol: '¥',
    position: 'before',
    decimalSeparator: '.',
    thousandsSeparator: ',',
    precision: 2
  }
};

// Main Internationalization Service
export class I18nService {
  private static instance: I18nService;
  private currentLanguage: string = 'en';
  private translations: Map<string, Map<string, string>> = new Map();
  private translationMemory: Map<string, TranslationMemory[]> = new Map();

  private constructor() {
    this.initializeTranslations();
    this.loadUserLanguagePreference();
  }

  static getInstance(): I18nService {
    if (!I18nService.instance) {
      I18nService.instance = new I18nService();
    }
    return I18nService.instance;
  }

  // Language Management
  async setLanguage(language: string, userId?: string): Promise<void> {
    try {
      if (!SUPPORTED_LANGUAGES.find(lang => lang.code === language)) {
        throw new Error(`Unsupported language: ${language}`);
      }

      this.currentLanguage = language;
      
      // Save user preference
      if (userId) {
        await this.saveUserLanguagePreference(userId, language);
      }

      // Load translations for new language
      await this.loadTranslations(language);

      // Update HTML lang attribute
      document.documentElement.lang = language;
      
      // Update RTL direction
      const lang = SUPPORTED_LANGUAGES.find(l => l.code === language);
      if (lang) {
        document.documentElement.dir = lang.rtl ? 'rtl' : 'ltr';
      }

      // Dispatch language change event
      window.dispatchEvent(new CustomEvent('languageChange', {
        detail: { language, direction: lang?.rtl ? 'rtl' : 'ltr' }
      }));
    } catch (error) {
      console.error('Error setting language:', error);
      throw error;
    }
  }

  getCurrentLanguage(): Language {
    return SUPPORTED_LANGUAGES.find(lang => lang.code === this.currentLanguage) || SUPPORTED_LANGUAGES[0];
  }

  getSupportedLanguages(): Language[] {
    return SUPPORTED_LANGUAGES;
  }

  // Translation Management
  async loadTranslations(language: string): Promise<void> {
    try {
      // Load from cache first
      if (this.translations.has(language)) {
        return;
      }

      // Load from database
      const { data, error } = await supabase
        .from('translations')
        .select('*')
        .eq('language', language);

      if (error) throw error;

      const translationMap = new Map();
      for (const translation of data || []) {
        translationMap.set(translation.key, translation.value);
      }

      this.translations.set(language, translationMap);
    } catch (error) {
      console.error('Error loading translations:', error);
      throw error;
    }
  }

  translate(key: string, variables?: Record<string, any>, context?: string): string {
    const languageTranslations = this.translations.get(this.currentLanguage);
    if (!languageTranslations) {
      return key; // Fallback to key
    }

    let translation = languageTranslations.get(key);
    
    // Handle context-specific translations
    if (context && translation) {
      const contextKey = `${key}.${context}`;
      const contextTranslation = languageTranslations.get(contextKey);
      if (contextTranslation) {
        translation = contextTranslation;
      }
    }

    // Handle variable substitution
    if (translation && variables) {
      for (const [variable, value] of Object.entries(variables)) {
        translation = translation.replace(new RegExp(`\\{${variable}\\}`, 'g'), String(value));
      }
    }

    return translation || key; // Fallback to key
  }

  translatePlural(key: string, count: number, variables?: Record<string, any>): string {
    const languageTranslations = this.translations.get(this.currentLanguage);
    if (!languageTranslations) {
      return key;
    }

    // Get plural form based on count
    const pluralKey = this.getPluralKey(key, count);
    let translation = languageTranslations.get(pluralKey) || languageTranslations.get(key) || key;

    // Handle variable substitution
    if (translation && variables) {
      for (const [variable, value] of Object.entries(variables)) {
        translation = translation.replace(new RegExp(`\\{${variable}\\}`, 'g'), String(value));
      }
    }

    return translation;
  }

  // Machine Translation
  async translateText(
    text: string,
    targetLanguage: string,
    sourceLanguage?: string
  ): Promise<MachineTranslationResult> {
    try {
      // Detect source language if not provided
      const detectedLanguage = sourceLanguage || await this.detectLanguage(text);

      // Check translation memory first
      const memoryKey = `${detectedLanguage}-${targetLanguage}-${text.substring(0, 100)}`;
      const memoryTranslations = this.translationMemory.get(memoryKey);
      
      if (memoryTranslations && memoryTranslations.length > 0) {
        const bestMatch = memoryTranslations
          .filter(t => t.approved)
          .sort((a, b) => b.confidence - a.confidence)[0];
        
        if (bestMatch && bestMatch.confidence > 0.8) {
          return {
            translatedText: bestMatch.translatedText,
            confidence: bestMatch.confidence,
            sourceLanguage: detectedLanguage,
            targetLanguage,
            alternatives: memoryTranslations
              .filter(t => t.approved && t !== bestMatch)
              .map(t => t.translatedText)
          };
        }
      }

      // Use machine translation API
      const result = await this.callMachineTranslationAPI(text, detectedLanguage, targetLanguage);
      
      // Store in translation memory
      await this.storeTranslationMemory(
        detectedLanguage,
        targetLanguage,
        text,
        result.translatedText,
        result.confidence
      );

      return {
        ...result,
        detectedLanguage
      };
    } catch (error) {
      console.error('Error translating text:', error);
      throw error;
    }
  }

  // Localization Functions
  formatCurrency(amount: number, currency?: string, language?: string): string {
    const lang = language || this.currentLanguage;
    const currencyCode = currency || this.getCurrencyForLanguage(lang);
    const currencyConfig = CURRENCY_LOCALIZATIONS[currencyCode] || CURRENCY_LOCALIZATIONS.USD;
    
    const formattedAmount = amount.toFixed(currencyConfig.precision);
    const [integerPart, decimalPart] = formattedAmount.split('.');
    
    const formattedInteger = integerPart.replace(
      /\B(?=(\d{3})+(?!\d))/g,
      currencyConfig.thousandsSeparator + '$1'
    );
    
    const finalAmount = decimalPart 
      ? `${formattedInteger}${currencyConfig.decimalSeparator}${decimalPart}`
      : formattedInteger;

    return currencyConfig.position === 'before'
      ? `${currencyConfig.symbol}${finalAmount}`
      : `${finalAmount}${currencyConfig.symbol}`;
  }

  formatDate(date: Date, format?: 'short' | 'medium' | 'long' | 'full', language?: string): string {
    const lang = language || this.currentLanguage;
    const langConfig = SUPPORTED_LANGUAGES.find(l => l.code === lang);
    
    if (!langConfig) {
      return date.toLocaleDateString();
    }

    const formatType = format || 'medium';
    const dateFormats = this.getDateFormats(langConfig.code);
    
    switch (formatType) {
      case 'short':
        return this.formatDateString(date, dateFormats.short);
      case 'medium':
        return this.formatDateString(date, dateFormats.medium);
      case 'long':
        return this.formatDateString(date, dateFormats.long);
      case 'full':
        return this.formatDateString(date, dateFormats.full);
      default:
        return this.formatDateString(date, dateFormats.medium);
    }
  }

  formatNumber(number: number, language?: string): string {
    const lang = language || this.currentLanguage;
    const langConfig = SUPPORTED_LANGUAGES.find(l => l.code === lang);
    
    if (!langConfig) {
      return number.toLocaleString();
    }

    const numberConfig = this.getNumberFormats(langConfig.code);
    const formattedNumber = number.toFixed(numberConfig.precision);
    
    if (numberConfig.grouping) {
      const [integerPart, decimalPart] = formattedNumber.split('.');
      const groupedInteger = integerPart.replace(
        /\B(?=(\d{3})+(?!\d))/g,
        numberConfig.thousandsSeparator + '$1'
      );
      
      return decimalPart 
        ? `${groupedInteger}${numberConfig.decimalSeparator}${decimalPart}`
        : groupedInteger;
    }

    return formattedNumber;
  }

  getRelativeTime(date: Date, language?: string): string {
    const lang = language || this.currentLanguage;
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    const relativeFormats = this.getRelativeFormats(lang);
    
    if (diffInSeconds < 60) {
      return relativeFormats.seconds.replace('{count}', diffInSeconds.toString());
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return relativeFormats.minutes.replace('{count}', minutes.toString());
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return relativeFormats.hours.replace('{count}', hours.toString());
    } else if (diffInSeconds < 2592000) {
      const days = Math.floor(diffInSeconds / 86400);
      return relativeFormats.days.replace('{count}', days.toString());
    } else {
      const months = Math.floor(diffInSeconds / 2592000);
      return relativeFormats.months.replace('{count}', months.toString());
    }
  }

  // Translation Memory Management
  async updateTranslation(
    key: string,
    language: string,
    value: string,
    context?: string
  ): Promise<void> {
    try {
      const { error } = await supabase
        .from('translations')
        .upsert({
          key,
          language,
          value,
          context,
          lastUpdated: new Date().toISOString()
        })
        .eq('key', key)
        .eq('language', language);

      if (error) throw error;

      // Update cache
      const languageTranslations = this.translations.get(language);
      if (languageTranslations) {
        languageTranslations.set(key, value);
      }
    } catch (error) {
      console.error('Error updating translation:', error);
      throw error;
    }
  }

  async approveTranslation(translationId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('translation_memory')
        .update({
          approved: true,
          approvedAt: new Date().toISOString()
        })
        .eq('id', translationId);

      if (error) throw error;
    } catch (error) {
      console.error('Error approving translation:', error);
      throw error;
    }
  }

  // Helper Methods
  private async initializeTranslations(): Promise<void> {
    try {
      // Load all available translations
      const { data, error } = await supabase
        .from('translations')
        .select('*');

      if (error) throw error;

      // Group by language
      const groupedTranslations = new Map<string, Map<string, string>>();
      for (const translation of data || []) {
        if (!groupedTranslations.has(translation.language)) {
          groupedTranslations.set(translation.language, new Map());
        }
        groupedTranslations.get(translation.language)!.set(translation.key, translation.value);
      }

      this.translations = groupedTranslations;
    } catch (error) {
      console.error('Error initializing translations:', error);
    }
  }

  private async loadUserLanguagePreference(): Promise<void> {
    try {
      const { data: user } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('user_language_preferences')
        .select('language')
        .eq('userId', user.id)
        .single();

      if (error || !data) return;

      await this.setLanguage(data.language, user.id);
    } catch (error) {
      console.error('Error loading user language preference:', error);
    }
  }

  private async saveUserLanguagePreference(userId: string, language: string): Promise<void> {
    try {
      await supabase
        .from('user_language_preferences')
        .upsert({
          userId,
          language,
          region: this.getRegionForLanguage(language),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        });
    } catch (error) {
      console.error('Error saving user language preference:', error);
    }
  }

  private getPluralKey(key: string, count: number): string {
    // Simple pluralization logic - can be enhanced for different languages
    if (count === 1) {
      return key;
    }
    return `${key}_plural`;
  }

  private getCurrencyForLanguage(language: string): string {
    const currencyMap: Record<string, string> = {
      'en': 'USD',
      'es': 'EUR',
      'am': 'ETB',
      'ar': 'SAR',
      'fr': 'EUR',
      'zh': 'CNY'
    };
    return currencyMap[language] || 'USD';
  }

  private getDateFormats(language: string): any {
    const formatMap: Record<string, any> = {
      'en': {
        short: 'MM/DD/YY',
        medium: 'MM/DD/YYYY',
        long: 'MMMM DD, YYYY',
        full: 'dddd, MMMM DD, YYYY'
      },
      'es': {
        short: 'DD/MM/YY',
        medium: 'DD/MM/YYYY',
        long: 'DD [de] MMMM [de] YYYY',
        full: 'dddd, DD [de] MMMM [de] YYYY'
      },
      'am': {
        short: 'DD/MM/YY',
        medium: 'DD/MM/YYYY',
        long: 'DD/MM/YYYY',
        full: 'dddd, DD/MM/YYYY'
      },
      'ar': {
        short: 'DD/MM/YY',
        medium: 'DD/MM/YYYY',
        long: 'DD/MM/YYYY',
        full: 'dddd, DD/MM/YYYY'
      },
      'fr': {
        short: 'DD/MM/YY',
        medium: 'DD/MM/YYYY',
        long: 'DD MMMM YYYY',
        full: 'dddd DD MMMM YYYY'
      },
      'zh': {
        short: 'YY/MM/DD',
        medium: 'YYYY/MM/DD',
        long: 'YYYY年MM月DD日',
        full: 'YYYY年MM月DD日 dddd'
      }
    };
    return formatMap[language] || formatMap['en'];
  }

  private getNumberFormats(language: string): NumberLocalization {
    const formatMap: Record<string, NumberLocalization> = {
      'en': {
        decimalSeparator: '.',
        thousandsSeparator: ',',
        precision: 2,
        grouping: true
      },
      'es': {
        decimalSeparator: ',',
        thousandsSeparator: '.',
        precision: 2,
        grouping: true
      },
      'am': {
        decimalSeparator: '.',
        thousandsSeparator: ',',
        precision: 2,
        grouping: true
      },
      'ar': {
        decimalSeparator: '.',
        thousandsSeparator: ',',
        precision: 2,
        grouping: true
      },
      'fr': {
        decimalSeparator: ',',
        thousandsSeparator: ' ',
        precision: 2,
        grouping: true
      },
      'zh': {
        decimalSeparator: '.',
        thousandsSeparator: ',',
        precision: 2,
        grouping: false
      }
    };
    return formatMap[language] || formatMap['en'];
  }

  private getRelativeFormats(language: string): any {
    const formatMap: Record<string, any> = {
      'en': {
        seconds: '{count} seconds ago',
        minutes: '{count} minutes ago',
        hours: '{count} hours ago',
        days: '{count} days ago',
        weeks: '{count} weeks ago',
        months: '{count} months ago',
        years: '{count} years ago'
      },
      'es': {
        seconds: 'hace {count} segundos',
        minutes: 'hace {count} minutos',
        hours: 'hace {count} horas',
        days: 'hace {count} días',
        weeks: 'hace {count} semanas',
        months: 'hace {count} meses',
        years: 'hace {count} años'
      },
      'am': {
        seconds: '{count} ሰነዎት በላድ',
        minutes: '{count} ደቂነት ዠላድ',
        hours: '{count} ሰዓት ዠላድ',
        days: '{count} ቀንስ ዠላድ',
        weeks: '{count} ሳምንት ዠላድ',
        months: '{count} ወር ዠላድ',
        years: '{count} ዓመት ዠላድ'
      },
      'ar': {
        seconds: 'منذ {count} ثانية',
        minutes: 'منذ {count} دقيقة',
        hours: 'منذ {count} ساعة',
        days: 'منذ {count} يوم',
        weeks: 'منذ {count} أسبوع',
        months: 'منذ {count} شهر',
        years: 'منذ {count} سنة'
      },
      'fr': {
        seconds: 'il y a {count} secondes',
        minutes: 'il y a {count} minutes',
        hours: 'il y a {count} heures',
        days: 'il y a {count} jours',
        weeks: 'il y a {count} semaines',
        months: 'il y a {count} mois',
        years: 'il y a {count} ans'
      },
      'zh': {
        seconds: '{count} 秒前',
        minutes: '{count} 分钟前',
        hours: '{count} 小时前',
        days: '{count} 天前',
        weeks: '{count} 周前',
        months: '{count} 个月前',
        years: '{count} 年前'
      }
    };
    return formatMap[language] || formatMap['en'];
  }

  private getRegionForLanguage(language: string): string {
    const regionMap: Record<string, string> = {
      'en': 'global',
      'es': 'global',
      'am': 'ethiopia',
      'ar': 'global',
      'fr': 'global',
      'zh': 'global'
    };
    return regionMap[language] || 'global';
  }

  private formatDateString(date: Date, format: string): string {
    const day = date.getDate();
    const month = date.getMonth() + 1;
    const year = date.getFullYear();
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const seconds = date.getSeconds();
    
    return format
      .replace('DD', day.toString().padStart(2, '0'))
      .replace('MM', month.toString().padStart(2, '0'))
      .replace('YYYY', year.toString())
      .replace('YY', year.toString().slice(-2))
      .replace('HH', hours.toString().padStart(2, '0'))
      .replace('mm', minutes.toString().padStart(2, '0'))
      .replace('ss', seconds.toString().padStart(2, '0'));
  }

  private async detectLanguage(text: string): Promise<string> {
    // Simple language detection - in production, use proper language detection API
    const patterns = {
      'am': /[\u1200-\u137F]/,
      'ar': /[\u0600-\u06FF]/,
      'zh': /[\u4e00-\u9fff]/,
      'es': /[ñáéíóúü]/i,
      'fr': /[àâäçéèêëïîôöù]/i
    };

    for (const [lang, pattern] of Object.entries(patterns)) {
      if (pattern.test(text)) {
        return lang;
      }
    }

    return 'en'; // Default to English
  }

  private async callMachineTranslationAPI(
    text: string,
    sourceLanguage: string,
    targetLanguage: string
  ): Promise<MachineTranslationResult> {
    // This would integrate with actual translation API (Google Translate, DeepL, etc.)
    // For now, return mock result
    return {
      translatedText: `[Translated from ${sourceLanguage} to ${targetLanguage}]: ${text}`,
      confidence: 85,
      sourceLanguage,
      targetLanguage
    };
  }

  private async storeTranslationMemory(
    sourceLanguage: string,
    targetLanguage: string,
    sourceText: string,
    translatedText: string,
    confidence: number
  ): Promise<void> {
    try {
      const memoryKey = `${sourceLanguage}-${targetLanguage}-${sourceText.substring(0, 100)}`;
      
      await supabase
        .from('translation_memory')
        .insert({
          sourceLanguage,
          targetLanguage,
          sourceText,
          translatedText,
          context: 'auto_translation',
          confidence,
          approved: false,
          createdAt: new Date().toISOString()
        });
    } catch (error) {
      console.error('Error storing translation memory:', error);
    }
  }

  // Export/Import Functions
  async exportTranslations(language: string): Promise<TranslationNamespace[]> {
    try {
      const { data, error } = await supabase
        .from('translations')
        .select('*')
        .eq('language', language);

      if (error) throw error;

      // Group by namespace
      const namespaces = new Map<string, Translation[]>();
      for (const translation of data || []) {
        if (!namespaces.has(translation.namespace || 'common')) {
          namespaces.set(translation.namespace || 'common', []);
        }
        namespaces.get(translation.namespace || 'common')!.push(translation);
      }

      return Array.from(namespaces.entries()).map(([name, translations]) => ({
        name,
        translations: translations.reduce((acc, t) => {
          acc[t.key] = t;
          return acc;
        }, {}),
        lastUpdated: new Date().toISOString(),
        version: '1.0.0'
      }));
    } catch (error) {
      console.error('Error exporting translations:', error);
      throw error;
    }
  }

  async importTranslations(
    translations: TranslationNamespace[],
    language: string
  ): Promise<void> {
    try {
      for (const namespace of translations) {
        for (const translation of namespace.translations) {
          await supabase
            .from('translations')
            .upsert({
              key: translation.key,
              language,
              value: translation.value,
              context: namespace.name,
              lastUpdated: new Date().toISOString()
            });
        }
      }
    } catch (error) {
      console.error('Error importing translations:', error);
      throw error;
    }
  }
}

export default I18nService;
