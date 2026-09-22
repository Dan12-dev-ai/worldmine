/**
 * World Mine — VerificationBadge (§19).
 * Verification must never be communicated by color alone: every badge carries
 * text + icon shape. Details surface who/when/what on the detail page.
 */

import type { VerificationState } from '../../shared/types/domain';

const TONE: Record<VerificationState, string> = {
  'VERIFIED': 'wm-badge--verified',
  'PARTIALLY VERIFIED': 'wm-badge--gold',
  'PENDING': 'wm-badge--pending',
  'REQUIRES REVIEW': 'wm-badge--pending',
  'UNVERIFIED': 'wm-badge--neutral',
  'EXPIRED': 'wm-badge--error',
};

const GLYPH: Record<VerificationState, string> = {
  'VERIFIED': '✓',           // check — verified
  'PARTIALLY VERIFIED': '◑', // half — partial
  'PENDING': '◔',            // partial clock — in progress
  'REQUIRES REVIEW': '!',    // attention
  'UNVERIFIED': '○',         // empty — no claim
  'EXPIRED': '×',            // crossed — lapsed
};

export function VerificationBadge({
  state, detail,
}: { state: VerificationState | string; detail?: string }) {
  const key = (state as VerificationState) in TONE ? (state as VerificationState) : 'UNVERIFIED';
  return (
    <span
      className={`wm-badge ${TONE[key]}`}
      data-tip={detail}
      aria-label={`Verification state: ${key}${detail ? ` — ${detail}` : ''}`}
    >
      <span aria-hidden="true" style={{ fontWeight: 700 }}>{GLYPH[key]}</span>
      {key}
    </span>
  );
}
