import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ContractData } from '../services/contractSecurity';

interface SignatureData {
  party: 'buyer' | 'seller';
  signature: string;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  language: string;
}

interface BilingualContractSigningProps {
  contract: ContractData;
  currentUserRole: 'buyer' | 'seller';
  onSign: (signatureData: SignatureData[]) => void;
}

export const BilingualContractSigning: React.FC<BilingualContractSigningProps> = ({
  contract,
  currentUserRole,
  onSign
}) => {
  const { t, i18n } = useTranslation();
  const [signatures, setSignatures] = useState<SignatureData[]>([]);
  const [isSigning, setIsSigning] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [signatureText, setSignatureText] = useState('');

  useEffect(() => {
    const existingSignatures = localStorage.getItem(`signatures_${contract.id}`);
    if (existingSignatures) {
      setSignatures(JSON.parse(existingSignatures));
    }
  }, [contract.id]);

  const handleSign = async () => {
    if (!agreedToTerms || !signatureText.trim()) {
      return;
    }

    setIsSigning(true);

    try {
      const newSignature: SignatureData = {
        party: currentUserRole,
        signature: signatureText,
        timestamp: new Date().toISOString(),
        ipAddress: await getClientIP(),
        userAgent: navigator.userAgent,
        language: i18n.language
      };

      const updatedSignatures = signatures.filter(s => s.party !== currentUserRole);
      updatedSignatures.push(newSignature);

      setSignatures(updatedSignatures);
      localStorage.setItem(`signatures_${contract.id}`, JSON.stringify(updatedSignatures));

      onSign(updatedSignatures);
    } catch (error) {
      console.error('Signing error:', error);
    } finally {
      setIsSigning(false);
    }
  };

  const getClientIP = async (): Promise<string> => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return 'unknown';
    }
  };

  const hasUserSigned = signatures.some(s => s.party === currentUserRole);
  const isFullySigned = signatures.length === 2;

  return (
    <div className="bg-white rounded-lg shadow-lg">
      <div className="border-b border-gray-200 px-6 py-4">
        <h3 className="text-lg font-semibold text-gray-900">{t('contracts.sign')}</h3>
        <p className="text-sm text-gray-600 mt-1">
          {t('contracts.signInstructions')}
        </p>
      </div>

      <div className="p-6">
        {isFullySigned ? (
          <div className="text-center py-8">
            <svg className="w-16 h-16 text-green-500 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <h4 className="text-lg font-semibold text-green-800">{t('contracts.fullySigned')}</h4>
            <p className="text-gray-600 mt-2">{t('contracts.contractActive')}</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-3">{t('contracts.original')}</h4>
                <div className="bg-white rounded p-3 h-48 overflow-y-auto text-sm">
                  <pre className="whitespace-pre-wrap">{contract.content}</pre>
                </div>
              </div>

              {contract.translatedContent && (
                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="font-medium text-green-900 mb-3">{t('contracts.translated')}</h4>
                  <div className="bg-white rounded p-3 h-48 overflow-y-auto text-sm">
                    <pre className="whitespace-pre-wrap">{contract.translatedContent}</pre>
                  </div>
                </div>
              )}
            </div>

            <div className="border-t pt-6">
              <div className="mb-4">
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={agreedToTerms}
                    onChange={(e) => setAgreedToTerms(e.target.checked)}
                    className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    {t('contracts.agreementText')}
                  </span>
                </label>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('contracts.digitalSignature')}
                </label>
                <input
                  type="text"
                  value={signatureText}
                  onChange={(e) => setSignatureText(e.target.value)}
                  placeholder={t('contracts.signaturePlaceholder')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={hasUserSigned}
                />
              </div>

              <button
                onClick={handleSign}
                disabled={!agreedToTerms || !signatureText.trim() || hasUserSigned || isSigning}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isSigning ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {t('contracts.signing')}
                  </span>
                ) : hasUserSigned ? (
                  t('contracts.alreadySigned')
                ) : (
                  t('contracts.signContract')
                )}
              </button>
            </div>

            {signatures.length > 0 && (
              <div className="mt-6 pt-6 border-t">
                <h4 className="font-medium text-gray-900 mb-3">{t('contracts.signatures')}</h4>
                <div className="space-y-2">
                  {signatures.map((signature, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <span className="font-medium capitalize">{signature.party}</span>
                        <span className="text-sm text-gray-500">
                          {new Date(signature.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700 mt-1">{signature.signature}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {t('contracts.signedIn')} {signature.language}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
