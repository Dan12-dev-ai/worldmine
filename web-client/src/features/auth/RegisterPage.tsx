/**
 * World Mine — Registration (Phase 4, §15).
 * Progressive: account type → identity → verification → done.
 * Contract-faithful: POST /api/auth/register is magic-link based — the final
 * step tells the user to check their email. No password field is invented
 * against the backend contract (drift flag #2).
 */
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from 'react-query';
import { api } from '../../shared/api/client';
import { WorldButton } from '../../design-system';
import { AuthSplitLayout } from './AuthSplitLayout';

const ACCOUNT_TYPES = [
  { key: 'buyer', label: 'Buyer', desc: 'Source verified minerals with evidence.' },
  { key: 'miner', label: 'Seller (Miner)', desc: 'List minerals with verified origin.' },
  { key: 'institutional', label: 'Broker / Representative', desc: 'Trade on behalf of an institution.' },
  { key: 'verifier', label: 'Inspector / Partner', desc: 'Provide inspection and verification services.' },
] as const;

const STEPS = ['Account type', 'Identity', 'Verify email', 'Done'] as const;

interface RegisterResponse { message?: string; email_sent?: boolean; user_id?: string | null }

export function RegisterPage() {
  const [step, setStep] = useState(0);
  const [accountType, setAccountType] = useState<string>('buyer');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);

  const register = useMutation<RegisterResponse, Error, { email: string; username?: string; user_type?: string }>(
    (payload) => api.post('/api/auth/register', payload),
  );

  const canContinue = useMemo(() => {
    if (step === 1) return /\S+@\S+\.\S+/.test(email) && username.trim().length >= 3;
    return true;
  }, [step, email, username]);

  async function submit() {
    setEmailError(null);
    setServerError(null);
    try {
      await register.mutateAsync({ email, username, user_type: accountType });
      setStep(2);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Registration failed';
      if (/exists/i.test(msg)) setEmailError('An account with this email already exists. Try signing in instead.');
      else setServerError(msg);
    }
  }

  return (
    <AuthSplitLayout
      brandTitle="Join the verified mineral marketplace"
      brandBody="One account for discovery, negotiation, contracts, escrow and traceable delivery."
    >
      <div className="wm-auth__card">
        {/* progress */}
        <ol style={{ listStyle: 'none', display: 'flex', gap: 8, margin: 0, padding: 0 }} aria-label="Registration progress">
          {STEPS.map((s, i) => (
            <li key={s} style={{ flex: 1 }}>
              <div aria-hidden="true" style={{
                height: 3, borderRadius: 2,
                background: i <= step ? 'var(--wm-gold)' : 'var(--wm-slate)',
              }} />
              <span style={{ fontSize: 'var(--text-caption)', color: i <= step ? 'var(--wm-fog)' : 'var(--wm-ash)' }}>
                {s}
              </span>
            </li>
          ))}
        </ol>

        {step === 0 && (
          <>
            <h1 style={{ fontSize: 'var(--text-h2)' }}>Choose your account type</h1>
            <div role="radiogroup" aria-label="Account type" style={{ display: 'grid', gap: 10 }}>
              {ACCOUNT_TYPES.map((t) => (
                <button
                  key={t.key}
                  type="button"
                  role="radio"
                  aria-checked={accountType === t.key}
                  onClick={() => setAccountType(t.key)}
                  className="wm-card wm-card--interactive"
                  style={{
                    padding: 14, textAlign: 'left', font: 'inherit', color: 'inherit',
                    borderColor: accountType === t.key ? 'rgba(201,162,39,0.6)' : undefined,
                    background: accountType === t.key ? 'rgba(201,162,39,0.06)' : undefined,
                  }}
                >
                  <strong>{t.label}</strong>
                  <div style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-ash)' }}>{t.desc}</div>
                </button>
              ))}
            </div>
            <WorldButton block disabled={!canContinue} onClick={() => setStep(1)}>Continue</WorldButton>
          </>
        )}

        {step === 1 && (
          <>
            <h1 style={{ fontSize: 'var(--text-h2)' }}>Your identity</h1>
            <div className="wm-field">
              <label className="wm-label" htmlFor="reg-email">Email address</label>
              <input id="reg-email" className="wm-input" type="email" autoComplete="email"
                value={email} onChange={(e) => setEmail(e.target.value)}
                aria-invalid={Boolean(emailError)} aria-describedby={emailError ? 'reg-email-err' : undefined} />
              {emailError && <span id="reg-email-err" className="wm-error-text" role="alert">{emailError}</span>}
            </div>
            <div className="wm-field">
              <label className="wm-label" htmlFor="reg-username">Username</label>
              <input id="reg-username" className="wm-input" autoComplete="username"
                value={username} onChange={(e) => setUsername(e.target.value)} minLength={3} />
              <span className="wm-hint">Shown to counterparties in negotiations. 3+ characters.</span>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <WorldButton variant="secondary" onClick={() => setStep(0)}>Back</WorldButton>
              <WorldButton block disabled={!canContinue} onClick={submit} aria-busy={register.isLoading}>
                {register.isLoading ? 'Creating…' : 'Create account'}
              </WorldButton>
            </div>
            {serverError && <p className="wm-error-text" role="alert" style={{ margin: 0 }}>{serverError}</p>}
          </>
        )}

        {step === 2 && (
          <div style={{ textAlign: 'center', display: 'grid', gap: 12 }}>
            <span className="wm-badge wm-badge--verified" style={{ alignSelf: 'center' }}>
              <span className="wm-badge__dot" />Check your email
            </span>
            <h1 style={{ fontSize: 'var(--text-h2)' }}>One more step</h1>
            <p style={{ color: 'var(--wm-fog)', margin: 0 }}>
              We sent a secure sign-in link to <strong style={{ color: 'var(--wm-porcelain)' }}>{email}</strong>.
              It expires shortly — no password needed.
            </p>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-ash)', margin: 0 }}>
              Didn't receive it? Check spam, or{' '}
              <button type="button" className="wm-btn wm-btn-ghost wm-btn-sm" onClick={submit}>resend</button>
            </p>
            <WorldButton to="/login" variant="secondary" block>Back to sign in</WorldButton>
          </div>
        )}

        <p style={{ margin: 0, fontSize: 'var(--text-caption)', color: 'var(--wm-ash)', textAlign: 'center' }}>
          Already registered? <Link to="/login" style={{ color: 'var(--wm-gold-soft)' }}>Sign in</Link>
        </p>
      </div>
    </AuthSplitLayout>
  );
}
