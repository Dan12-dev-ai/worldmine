import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { translationService, TranslationRequest } from '../services/translationService';
import { contractSecurity, ContractData, ContractHash } from '../services/contractSecurity';

interface DualLanguageContractProps {
  contract: ContractData;
  onContractUpdate?: (updatedContract: ContractData) => void;
}

export const DualLanguageContract: React.FC<DualLanguageContractProps> = ({
  contract,
  onContractUpdate
}) => {
  const { t, i18n } = useTranslation();
  const [showDualView, setShowDualView] = useState(false);
  const [translatedContent, setTranslatedContent] = useState<string>('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationError, setTranslationError] = useState<string>('');
  const [contractHash, setContractHash] = useState<ContractHash | null>(null);
  const [integrityCheck, setIntegrityCheck] = useState<{ isValid: boolean; tamperAlert?: string }>({ isValid: true });

  const targetLanguage = i18n.language === 'en' ? 'es' : i18n.language === 'es' ? 'am' : 'en';

  useEffect(() => {
    loadContractHash();
  }, [contract.id]);

  useEffect(() => {
    if (contractHash) {
      const verification = contractSecurity.verifyContractIntegrity(contract, contractHash);
      setIntegrityCheck(verification);
    }
  }, [contract, contractHash]);

  const loadContractHash = async () => {
    try {
      const hash = await contractSecurity.retrieveContractHash(contract.id);
      setContractHash(hash);
    } catch (error) {
      console.error('Failed to load contract hash:', error);
    }
  };

  const handleTranslate = async () => {
    if (isTranslating) return;

    setIsTranslating(true);
    setTranslationError('');

    try {
      const request: TranslationRequest = {
        text: contract.content,
        from: contract.originalLanguage,
        to: targetLanguage,
        context: 'legal'
      };

      const response = await translationService.translateLegalText(request);
      setTranslatedContent(response.translatedText);

      if (onContractUpdate) {
        const updatedContract = {
          ...contract,
          translatedContent: response.translatedText
        };
        onContractUpdate(updatedContract);

        const newHash = contractSecurity.createContractHashRecord(updatedContract);
        await contractSecurity.storeContractHash(newHash);
        setContractHash(newHash);
      }
    } catch (error) {
      setTranslationError(t('contracts.translationError') || 'Translation failed');
      console.error('Translation error:', error);
    } finally {
      setIsTranslating(false);
    }
  };

  const handleToggleDualView = () => {
    if (!showDualView && !translatedContent) {
      handleTranslate();
    }
    setShowDualView(!showDualView);
  };

  if (!integrityCheck.isValid) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 text-red-800">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span className="font-semibold">{t('contracts.tamperAlert')}</span>
        </div>
        <p className="mt-2 text-red-700">{integrityCheck.tamperAlert}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">{contract.title}</h3>
          <button
            onClick={handleToggleDualView}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
            </svg>
            <span>{t(showDualView ? 'contracts.singleView' : 'contracts.dualLanguage')}</span>
          </button>
        </div>
      </div>

      <div className="p-6">
        {translationError && (
          <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">{translationError}</p>
          </div>
        )}

        {showDualView ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-sm font-medium text-blue-600">{t('contracts.original')}</span>
                <span className="text-xs text-gray-500">({contract.originalLanguage.toUpperCase()})</span>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                  {contract.content}
                </pre>
              </div>
            </div>

            <div>
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-sm font-medium text-green-600">{t('contracts.translated')}</span>
                <span className="text-xs text-gray-500">({targetLanguage.toUpperCase()})</span>
                {isTranslating && (
                  <span className="text-xs text-blue-600 animate-pulse">{t('common.loading')}</span>
                )}
              </div>
              <div className="bg-green-50 rounded-lg p-4 h-96 overflow-y-auto">
                {isTranslating ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : translatedContent ? (
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                    {translatedContent}
                  </pre>
                ) : (
                  <div className="text-gray-500 text-center h-full flex items-center justify-center">
                    {t('contracts.translationPending')}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
              {contract.content}
            </pre>
          </div>
        )}

        {contractHash && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Hash: {contractHash.contentHash.substring(0, 12)}...</span>
              <span>Version: {contractHash.version}</span>
              <span>{new Date(contractHash.timestamp).toLocaleDateString()}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
