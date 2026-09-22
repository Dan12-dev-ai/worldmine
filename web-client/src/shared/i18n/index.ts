/**
 * World Mine — i18n (Phase 1). Preserves the existing translation asset and
 * extends it with the new institutional domain vocabulary.
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const en = {
  nav: {
    marketplace: 'Marketplace',
    dashboard: 'Dashboard',
    howItWorks: 'How It Works',
    intelligence: 'Intelligence',
    traceability: 'Traceability',
    login: 'Sign In',
    register: 'Create Account',
    logout: 'Sign Out',
  },
  hero: {
    title: 'Global Mineral Commerce, Connected.',
    subtitle: 'Verified mineral trading with direct buyer-seller interaction — from discovery to traceable delivery.',
    ctaPrimary: 'Explore Minerals',
    ctaSecondary: 'List a Mineral',
  },
  lifecycle: {
    DISCOVER: 'Discover', VERIFY: 'Verify', CONNECT: 'Connect', NEGOTIATE: 'Negotiate',
    CONTRACT: 'Contract', ESCROW: 'Escrow', PAY: 'Pay', SHIP: 'Ship',
    COMPLY: 'Comply', TRACE: 'Trace', COMPLETE: 'Complete',
  },
  listing: {
    view: 'View Mineral', quote: 'Request Quote', origin: 'Origin', grade: 'Grade',
    quantity: 'Quantity', available: 'Available', verification: 'Verification',
    empty: 'No minerals match your filters yet.', emptyHint: 'Adjust filters or clear your search.',
  },
  auth: {
    emailLabel: 'Email address',
    emailPlaceholder: 'name@company.com',
    registerCta: 'Create account',
    checkEmail: 'Check your email',
    checkEmailBody: 'We sent a secure sign-in link. It expires shortly — no password needed.',
    accountType: 'Account type',
    buyer: 'Buyer', seller: 'Seller (Miner)', broker: 'Broker / Representative', inspector: 'Inspector / Partner',
    step: 'Step {{current}} of {{total}}',
  },
  common: { loading: 'Loading…', retry: 'Retry', cancel: 'Cancel', back: 'Back', next: 'Continue' },
  ai: { suggestion: 'AI suggestion', system: 'System' },
};

// Extend (not replace) the legacy translations asset when present.
import { translations as legacyTranslations } from '../../locales/translations';

const legacy: Record<string, unknown> =
  (legacyTranslations as Record<string, Record<string, unknown>> | undefined)?.en ?? {};

const am: Record<string, never> = {}; // legacy am/es dictionaries remain loadable for Phase 4 parity

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: { ...legacy, ...en } },
    am: { translation: am as never },
  },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false }, // React already escapes (XSS-safe, §37)
  returnObjects: true,
});

export default i18n;
