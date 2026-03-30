import { createHash } from 'crypto';

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
  generateContractHash(contractData: Omit<ContractData, 'id' | 'createdAt'>): string {
    const hashData = {
      title: contractData.title,
      content: contractData.content,
      parties: contractData.parties,
      version: contractData.version,
      originalLanguage: contractData.originalLanguage
    };

    const dataString = JSON.stringify(hashData, Object.keys(hashData).sort());
    return createHash('sha256').update(dataString).digest('hex');
  }

  verifyContractIntegrity(
    contractData: ContractData, 
    storedHash: ContractHash
  ): { isValid: boolean; tamperAlert?: string } {
    const currentHash = this.generateContractHash(contractData);
    
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
      const currentTranslatedHash = this.generateContractHash(translatedData);
      
      if (currentTranslatedHash !== storedHash.translatedHash) {
        return {
          isValid: false,
          tamperAlert: 'Translated content has been modified'
        };
      }
    }

    return { isValid: true };
  }

  createContractHashRecord(contractData: ContractData): ContractHash {
    const contentHash = this.generateContractHash(contractData);
    let translatedHash: string | undefined;

    if (contractData.translatedContent) {
      const translatedData = {
        ...contractData,
        content: contractData.translatedContent
      };
      translatedHash = this.generateContractHash(translatedData);
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
