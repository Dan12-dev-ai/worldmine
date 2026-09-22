/**
 * World Mine — LifecycleStepper.
 * The product spine (§2): DISCOVER → … → COMPLETE, always visible where relevant.
 * Communicates stage with text + shape + position, never color alone (§19 spirit).
 */
import 'react';
import { LIFECYCLE_STAGES } from '../../shared/types/domain';

export function LifecycleStepper({
  current, className = '',
}: { current?: string | null; className?: string }) {
  const idx = current ? LIFECYCLE_STAGES.indexOf(current.toUpperCase() as never) : -1;

  return (
    <ol className={`wm-lifecycle ${className}`} aria-label="Transaction lifecycle" style={{ listStyle: 'none', margin: 0, padding: 0 }}>
      {LIFECYCLE_STAGES.map((stage, i) => {
        const state = idx === -1 ? 'idle' : i < idx ? 'done' : i === idx ? 'active' : 'idle';
        return (
          <li key={stage} style={{ display: 'inline-flex', alignItems: 'center' }}>
            <span
              className={[
                'wm-lifecycle__stage',
                state === 'active' && 'wm-lifecycle__stage--active',
                state === 'done' && 'wm-lifecycle__stage--done',
              ].filter(Boolean).join(' ')}
              aria-current={state === 'active' ? 'step' : undefined}
            >
              {state === 'done' ? '✓ ' : ''}{stage}
            </span>
            {i < LIFECYCLE_STAGES.length - 1 && (
              <span className="wm-lifecycle__arrow" aria-hidden="true">▸</span>
            )}
          </li>
        );
      })}
    </ol>
  );
}
