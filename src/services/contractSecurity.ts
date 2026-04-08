// Browser-compatible crypto implementation using Web Crypto API
const createHash = (algorithm: string) => {
  const encoder = new TextEncoder();
  
  return {
    update: (data: string) => {
      const encodedData = encoder.encode(data);
      return {
        digest: async () => {
          const buffer = await crypto.subtle.digest(algorithm.toUpperCase(), encodedData);
          const hashArray = Array.from(new Uint8Array(buffer));
          const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
          return hashHex;
        }
      };
    }
  };
};

export interface ContractData {
  id: string;
  title: string;
  content: string;
  originalLanguage: string;
  translatedContent?: string;
  parties: {
    buyer: string;
    seller: string;
  };
  createdAt: string;
  version: number;
}

export interface ContractHash {
  contractId: string;
  contentHash: string;
  translatedHash?: string;
  timestamp: string;
  version: number;
}

export class ContractSecurityService {
  async generateContractHash(contractData: Omit<ContractData, 'id' | 'createdAt'>): Promise<string> {
    const hashData = {
      title: contractData.title,
      content: contractData.content,
      parties: contractData.parties,
      version: contractData.version,
      originalLanguage: contractData.originalLanguage
    };

    const dataString = JSON.stringify(hashData, Object.keys(hashData).sort());
    return await createHash('sha256').update(dataString).digest();
  }

  async verifyContractIntegrity(
    contractData: ContractData, 
    storedHash: ContractHash
  ): Promise<{ isValid: boolean; tamperAlert?: string }> {
    const currentHash = await this.generateContractHash(contractData);
    
    if (currentHash !== storedHash.contentHash) {
      return {
        isValid: false,
        tamperAlert: 'Contract content has been modified since creation'
      };
    }

    if (contractData.translatedContent && storedHash.translatedHash) {
      const translatedData = {
        ...contractData,
        content: contractData.translatedContent
      };
      const currentTranslatedHash = await this.generateContractHash(translatedData);
      
      if (currentTranslatedHash !== storedHash.translatedHash) {
        return {
          isValid: false,
          tamperAlert: 'Translated content has been modified'
        };
      }
    }

    return { isValid: true };
  }

  async createContractHashRecord(contractData: ContractData): Promise<ContractHash> {
    const contentHash = await this.generateContractHash(contractData);
    let translatedHash: string | undefined;

    if (contractData.translatedContent) {
      const translatedData = {
        ...contractData,
        content: contractData.translatedContent
      };
      translatedHash = await this.generateContractHash(translatedData);
    }

    return {
      contractId: contractData.id,
      contentHash,
      translatedHash,
      timestamp: new Date().toISOString(),
      version: contractData.version
    };
  }

  generateTamperEvidence(originalHash: string, currentHash: string): {
    hasBeenModified: boolean;
    modificationTime?: string;
    severity: 'low' | 'medium' | 'high';
  } {
    if (originalHash === currentHash) {
      return { hasBeenModified: false, severity: 'low' };
    }

    return {
      hasBeenModified: true,
      modificationTime: new Date().toISOString(),
      severity: 'high'
    };
  }

  async storeContractHash(contractHash: ContractHash): Promise<void> {
    try {
      const storageKey = `contract_hash_${contractHash.contractId}`;
      localStorage.setItem(storageKey, JSON.stringify(contractHash));
    } catch (error) {
      console.error('Failed to store contract hash:', error);
      throw new Error('Could not secure contract data');
    }
  }

  async retrieveContractHash(contractId: string): Promise<ContractHash | null> {
    try {
      const storageKey = `contract_hash_${contractId}`;
      const stored = localStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Failed to retrieve contract hash:', error);
      return null;
    }
  }

  createSecureContractId(): string {
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substring(2, 15);
    return `contract_${timestamp}_${randomPart}`;
  }
}

export const contractSecurity = new ContractSecurityService();
