// Bilingual Terminology Dictionary for Worldmine
// Ensures consistent translation of financial and technical terms
// ISO/IEC 25010 - Maintainability & Interoperability Compliance

export interface BilingualTerm {
  english: string;
  spanish: string;
  amharic: string;
  context: 'financial' | 'legal' | 'technical' | 'ui' | 'compliance';
  consistency: 'strict' | 'flexible';
  pronunciation?: {
    spanish?: string;
    amharic?: string;
  };
  notes?: string;
}

export interface BilingualDictionary {
  [key: string]: BilingualTerm;
}

// Comprehensive bilingual dictionary
export const WORLDMIN_DICTIONARY: BilingualDictionary = {
  // Financial Terms
  'escrow': {
    english: 'escrow',
    spanish: 'depósito en garantía',
    amharic: 'ኤስክሮ',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'deh-POH-see-toh en gah-ran-TEE-ah',
      amharic: 'es-KRO'
    },
    notes: 'Financial arrangement where a third party holds funds during transaction'
  },
  
  'commission': {
    english: 'commission',
    spanish: 'comisión',
    amharic: 'ኮሚሽን',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'koh-mee-SEE-ohn',
      amharic: 'kom-SHIN'
    },
    notes: 'Fee charged for services rendered in a transaction'
  },

  'transaction': {
    english: 'transaction',
    spanish: 'transacción',
    amharic: 'ግብይት',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'trahns-ahk-see-ohn',
      amharic: 'gib-YET'
    },
    notes: 'Exchange of goods, services, or funds between parties'
  },

  'payment': {
    english: 'payment',
    spanish: 'pago',
    amharic: 'ክፍያኛ',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'PAH-goh',
      amharic: 'kri-YA'
    },
    notes: 'Transfer of money for goods or services'
  },

  'withdrawal': {
    english: 'withdrawal',
    spanish: 'retiro',
    amharic: 'መውጣት',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'reh-TREE-roh',
      amharic: 'me-WAT'
    },
    notes: 'Taking money out of an account'
  },

  'deposit': {
    english: 'deposit',
    spanish: 'depósito',
    amharic: 'ክምብር',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'deh-POH-see-toh',
      amharic: 'kim-BER'
    },
    notes: 'Putting money into an account'
  },

  'balance': {
    english: 'balance',
    spanish: 'saldo',
    amharic: 'ሚዛን',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'SAHL-doh',
      amharic: 'miz-ZAY'
    },
    notes: 'Amount of money in an account'
  },

  'invoice': {
    english: 'invoice',
    spanish: 'factura',
    amharic: 'ኢንቮይስ',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'fahk-TOO-rah',
      amharic: 'in-VOYS'
    },
    notes: 'Bill for goods or services provided'
  },

  'receipt': {
    english: 'receipt',
    spanish: 'recibo',
    amharic: 'ደቤዛ',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'reh-SEE-boh',
      amharic: 'de-BEZA'
    },
    notes: 'Proof of payment or transaction'
  },

  'profit': {
    english: 'profit',
    spanish: 'ganancia',
    amharic: 'ገቢራ',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'gah-NAHN-see-ah',
      amharic: 'gin-GEE-ra'
    },
    notes: 'Financial gain from investment or business'
  },

  'loss': {
    english: 'loss',
    spanish: 'pérdida',
    amharic: 'ንጣቕ',
    context: 'financial',
    consistency: 'strict',
    pronunciation: {
      spanish: 'PEHR-dee-dah',
      amharic: 'ne-TSAK'
    },
    notes: 'Financial loss or reduction in value'
  },

  // Legal Terms
  'contract': {
    english: 'contract',
    spanish: 'contrato',
    amharic: 'ድርዛኝ',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'kohn-TRAH-toh',
      amharic: 'dir-ZAGN'
    },
    notes: 'Legally binding agreement between parties'
  },

  'agreement': {
    english: 'agreement',
    spanish: 'acuerdo',
    amharic: 'ስምምንታ',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'ahk-WER-doh',
      amharic: 'sim-MINT-a'
    },
    notes: 'Mutual understanding or arrangement'
  },

  'signature': {
    english: 'signature',
    spanish: 'firma',
    amharic: 'ፊርማ',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'FEER-mah',
      amharic: 'fi-RA'
    },
    notes: 'Person\'s name written in distinctive way as proof of identity'
  },

  'terms': {
    english: 'terms',
    spanish: 'términos',
    amharic: 'ውልውጥ',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'TEHR-mee-nohs',
      amharic: 'wol-WET'
    },
    notes: 'Conditions or provisions of an agreement'
  },

  'conditions': {
    english: 'conditions',
    spanish: 'condiciones',
    amharic: 'ሁኔታዎች',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'kohn-dee-see-ohn-ays',
      amharic: 'ho-NE-tawoch'
    },
    notes: 'Circumstances or requirements'
  },

  'liability': {
    english: 'liability',
    spanish: 'responsabilidad',
    amharic: 'ኃላበዛኝ',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'res-pohn-sah-bee-DAHD',
      amharic: 'halab-ZAGN'
    },
    notes: 'Legal responsibility for one\'s actions or omissions'
  },

  'compliance': {
    english: 'compliance',
    spanish: 'cumplimiento',
    amharic: 'አማካኙ',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'koom-plee-ME-ehn-toh',
      amharic: 'ama-KAW'
    },
    notes: 'Adherence to laws, regulations, guidelines'
  },

  'regulation': {
    english: 'regulation',
    spanish: 'regulación',
    amharic: 'ደንቀ',
    context: 'legal',
    consistency: 'strict',
    pronunciation: {
      spanish: 'reh-goo-lah-see-ohn',
      amharic: 'dereg-KE'
    },
    notes: 'Rule or directive made by an authority'
  },

  // Technical Terms
  'authentication': {
    english: 'authentication',
    spanish: 'autenticación',
    amharic: 'ማረጋገጣ',
    context: 'technical',
    consistency: 'strict',
    pronunciation: {
      spanish: 'ow-tehn-tee-kah-see-ohn',
      amharic: 'mareg-GAGTA'
    },
    notes: 'Process of verifying identity'
  },

  'verification': {
    english: 'verification',
    spanish: 'verificación',
    amharic: 'ማረጋገጢ',
    context: 'technical',
    consistency: 'strict',
    pronunciation: {
      spanish: 'beh-ree-fee-kah-see-ohn',
      amharic: 'mareg-GAGI'
    },
    notes: 'Process of confirming accuracy or truth'
  },

  'encryption': {
    english: 'encryption',
    spanish: 'encriptación',
    amharic: 'መሰደዱ',
    context: 'technical',
    consistency: 'strict',
    pronunciation: {
      spanish: 'een-krip-tah-see-ohn',
      amharic: 'maseda-DU'
    },
    notes: 'Process of encoding information'
  },

  'database': {
    english: 'database',
    spanish: 'base de datos',
    amharic: 'ዳታቤዝ',
    context: 'technical',
    consistency: 'strict',
    pronunciation: {
      spanish: 'bah-seh deh DAH-tohs',
      amharic: 'data-BEZ'
    },
    notes: 'Organized collection of structured information'
  },

  'server': {
    english: 'server',
    spanish: 'servidor',
    amharic: 'ሰርቨር',
    context: 'technical',
    consistency: 'strict',
    pronunciation: {
      spanish: 'sehr-bee-DOHR',
      amharic: 'ser-WER'
    },
    notes: 'Computer that provides services to other computers'
  },

  'network': {
    english: 'network',
    spanish: 'red',
    amharic: 'ኔትወርክ',
    context: 'technical',
    consistency: 'strict',
    pronunciation: {
      spanish: 'rehd',
      amharic: 'net-WERK'
    },
    notes: 'System of interconnected computers or devices'
  },

  'interface': {
    english: 'interface',
    spanish: 'interfaz',
    amharic: 'ግንንገልባይ',
    context: 'technical',
    consistency: 'strict',
    pronunciation: {
      spanish: 'een-tehr-FAHS',
      amharic: 'gereg-GEL-bay'
    },
    notes: 'Point where systems interact and communicate'
  },

  // UI Terms
  'dashboard': {
    english: 'dashboard',
    spanish: 'panel de control',
    amharic: 'ዳሽቦርድ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'pah-nehl deh kohn-TROHL',
      amharic: 'dash-BORD'
    },
    notes: 'Control panel displaying key information'
  },

  'profile': {
    english: 'profile',
    spanish: 'perfil',
    amharic: 'መገለጫ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'pehr-FEEL',
      amharic: 'megele-CHA'
    },
    notes: 'User\'s personal information and settings'
  },

  'settings': {
    english: 'settings',
    spanish: 'configuración',
    amharic: 'ቅንጻዎች',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'kohn-fee-goo-rah-see-ohn',
      amharic: 'kum-TAWoch'
    },
    notes: 'Configuration options and preferences'
  },

  'notification': {
    english: 'notification',
    spanish: 'notificación',
    amharic: 'ማስታወቂያ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'noh-tee-fee-kah-see-ohn',
      amharic: 'mastaw-KEYA'
    },
    notes: 'Alert or message to inform user'
  },

  'search': {
    english: 'search',
    spanish: 'búsqueda',
    amharic: 'ላጋ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'boo-KEHS-dah',
      amharic: 'tela-GA'
    },
    notes: 'Function to find specific information'
  },

  'filter': {
    english: 'filter',
    spanish: 'filtro',
    amharic: 'ማጣለጫ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'FEEL-troh',
      amharic: 'mata-LACH'
    },
    notes: 'Function to narrow down results'
  },

  // Marketplace Terms
  'marketplace': {
    english: 'marketplace',
    spanish: 'mercado',
    amharic: 'ገበያ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'mehr-KAH-doh',
      amharic: 'ge-BEYA'
    },
    notes: 'Platform where buyers and sellers interact'
  },

  'listing': {
    english: 'listing',
    spanish: 'listado',
    amharic: 'ርዝ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'lees-TAH-doh',
      amharic: 'tirt-ERZ'
    },
    notes: 'Item or service offered for sale'
  },

  'seller': {
    english: 'seller',
    spanish: 'vendedor',
    amharic: 'ሻክተማ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'vehn-DEH-dor',
      amharic: 'seke-TAMA'
    },
    notes: 'Person who sells goods or services'
  },

  'buyer': {
    english: 'buyer',
    spanish: 'comprador',
    amharic: 'ገዛኛ',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'kohm-prah-DOHR',
      amharic: 'geza-ZE'
    },
    notes: 'Person who purchases goods or services'
  },

  'price': {
    english: 'price',
    spanish: 'precio',
    amharic:ዋግ,
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'PREH-see-oh',
      amharic: 'price'
    },
    notes: 'Amount of money required to purchase something'
  },

  'quantity': {
    english: 'quantity',
    spanish: 'cantidad',
    amharic: 'ብዛን',
    context: 'ui',
    consistency: 'strict',
    pronunciation: {
      spanish: 'kahn-tee-DAHD',
      amharic: 'beza-YEN'
    },
    notes: 'Amount or number of something'
  },

  // Compliance Terms
  'kyc': {
    english: 'KYC (Know Your Customer)',
    spanish: 'KYC (Conoce a tu cliente)',
    amharic: 'ኪይይሲ (ደንቀን)',
    context: 'compliance',
    consistency: 'strict',
    pronunciation: {
      spanish: 'KOH-neh-seh ah too klee-EHN-teh',
      amharic: 'KYC (dereg-EN)'
    },
    notes: 'Process of verifying customer identity'
  },

  'aml': {
    english: 'AML (Anti-Money Laundering)',
    spanish: 'AML (Anti-lavado de dinero)',
    amharic: 'ኤምኤል (ገንበት መከማሪያ)',
    context: 'compliance',
    consistency: 'strict',
    pronunciation: {
      spanish: 'AHN-tee lah-VAH-doh deh dee-NEH-roh',
      amharic: 'AML (gebet mekmariya)'
    },
    notes: 'Prevention of illegal money generation'
  },

  'audit': {
    english: 'audit',
    spanish: 'auditoría',
    amharic: 'ክለምና',
    context: 'compliance',
    consistency: 'strict',
    pronunciation: {
      spanish: 'ow-dee-TOH-ree-ah',
      amharic: 'kelam-NA'
    },
    notes: 'Systematic examination of records'
  },

  'verification': {
    english: 'verification',
    spanish: 'verificación',
    amharic: 'ማረጋገጢ',
    context: 'compliance',
    consistency: 'strict',
    pronunciation: {
      spanish: 'beh-ree-fee-kah-see-ohn',
      amharic: 'mareg-GAGI'
    },
    notes: 'Process of confirming accuracy or truth'
  },

  'sanction': {
    english: 'sanction',
    spanish: 'sanción',
    amharic: 'ብድል',
    context: 'compliance',
    consistency: 'strict',
    pronunciation: {
      spanish: 'sahn-see-ohn',
      amharic: 'hube-DL'
    },
    notes: 'Official permission or approval'
  }
};

// Term categories for easy access
export const TERM_CATEGORIES = {
  FINANCIAL: Object.keys(WORLDMIN_DICTIONARY).filter(key => 
    WORLDMIN_DICTIONARY[key].context === 'financial'
  ),
  LEGAL: Object.keys(WORLDMIN_DICTIONARY).filter(key => 
    WORLDMIN_DICTIONARY[key].context === 'legal'
  ),
  TECHNICAL: Object.keys(WORLDMIN_DICTIONARY).filter(key => 
    WORLDMIN_DICTIONARY[key].context === 'technical'
  ),
  UI: Object.keys(WORLDMIN_DICTIONARY).filter(key => 
    WORLDMIN_DICTIONARY[key].context === 'ui'
  ),
  COMPLIANCE: Object.keys(WORLDMIN_DICTIONARY).filter(key => 
    WORLDMIN_DICTIONARY[key].context === 'compliance'
  )
} as const;

// Translation service for consistent terminology
export class BilingualTranslationService {
  private dictionary: BilingualDictionary;

  constructor(dictionary: BilingualDictionary = WORLDMIN_DICTIONARY) {
    this.dictionary = dictionary;
  }

  // Get term in specific language
  getTerm(term: string, language: 'english' | 'spanish' | 'amharic'): string {
    const termData = this.dictionary[term.toLowerCase()];
    if (!termData) {
      console.warn(`Term '${term}' not found in dictionary`);
      return term; // Return original term if not found
    }
    return termData[language];
  }

  // Get all translations for a term
  getAllTranslations(term: string): BilingualTerm | null {
    return this.dictionary[term.toLowerCase()] || null;
  }

  // Check if term exists
  hasTerm(term: string): boolean {
    return term.toLowerCase() in this.dictionary;
  }

  // Add new term to dictionary
  addTerm(key: string, term: BilingualTerm): void {
    this.dictionary[key.toLowerCase()] = term;
  }

  // Get terms by category
  getTermsByCategory(category: BilingualTerm['context']): BilingualDictionary {
    const filtered: BilingualDictionary = {};
    for (const [key, value] of Object.entries(this.dictionary)) {
      if (value.context === category) {
        filtered[key] = value;
      }
    }
    return filtered;
  }

  // Validate translation consistency
  validateConsistency(term: string, translation: string, language: 'spanish' | 'amharic'): boolean {
    const termData = this.dictionary[term.toLowerCase()];
    if (!termData) return false;
    
    if (termData.consistency === 'strict') {
      return termData[language] === translation;
    }
    
    return true; // Flexible consistency allows variations
  }

  // Get pronunciation guide
  getPronunciation(term: string, language: 'spanish' | 'amharic'): string | null {
    const termData = this.dictionary[term.toLowerCase()];
    if (!termData || !termData.pronunciation) return null;
    return termData.pronunciation[language] || null;
  }

  // Search for terms (fuzzy search)
  searchTerms(query: string, language: 'english' | 'spanish' | 'amharic'): Array<{key: string, term: BilingualTerm}> {
    const results: Array<{key: string, term: BilingualTerm}> = [];
    const lowerQuery = query.toLowerCase();

    for (const [key, term] of Object.entries(this.dictionary)) {
      // Search in English
      if (language === 'english' && key.includes(lowerQuery)) {
        results.push({ key, term });
        continue;
      }

      // Search in target language
      if (term[language].toLowerCase().includes(lowerQuery)) {
        results.push({ key, term });
      }
    }

    return results;
  }

  // Export dictionary for external use
  exportDictionary(): BilingualDictionary {
    return { ...this.dictionary };
  }

  // Import and merge dictionary
  importDictionary(newDictionary: Partial<BilingualDictionary>): void {
    Object.assign(this.dictionary, newDictionary);
  }

  // Get statistics
  getStatistics(): {
    totalTerms: number;
    termsByCategory: Record<string, number>;
    termsByConsistency: Record<string, number>;
  } {
    const stats = {
      totalTerms: Object.keys(this.dictionary).length,
      termsByCategory: {} as Record<string, number>,
      termsByConsistency: {} as Record<string, number>
    };

    for (const term of Object.values(this.dictionary)) {
      stats.termsByCategory[term.context] = (stats.termsByCategory[term.context] || 0) + 1;
      stats.termsByConsistency[term.consistency] = (stats.termsByConsistency[term.consistency] || 0) + 1;
    }

    return stats;
  }
}

// Singleton instance for global use
export const bilingualService = new BilingualTranslationService();

// Helper functions for common operations
export const translateTerm = (term: string, language: 'spanish' | 'amharic'): string => {
  return bilingualService.getTerm(term, language);
};

export const getFinancialTerms = (): string[] => TERM_CATEGORIES.FINANCIAL;
export const getLegalTerms = (): string[] => TERM_CATEGORIES.LEGAL;
export const getTechnicalTerms = (): string[] => TERM_CATEGORIES.TECHNICAL;
export const getUITerms = (): string[] => TERM_CATEGORIES.UI;
export const getComplianceTerms = (): string[] => TERM_CATEGORIES.COMPLIANCE;

// Validation functions
export const validateFinancialTranslation = (term: string, translation: string, language: 'spanish' | 'amharic'): boolean => {
  return bilingualService.validateConsistency(term, translation, language);
};

export const searchFinancialTerms = (query: string, language: 'spanish' | 'amharic'): Array<{key: string, term: BilingualTerm}> => {
  const financialTerms = bilingualService.getTermsByCategory('financial');
  const results: Array<{key: string, term: BilingualTerm}> = [];
  const lowerQuery = query.toLowerCase();

  for (const [key, term] of Object.entries(financialTerms)) {
    if (term[language].toLowerCase().includes(lowerQuery)) {
      results.push({ key, term });
    }
  }

  return results;
};

export default bilingualService;
