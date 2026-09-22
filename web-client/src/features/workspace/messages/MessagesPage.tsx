/**
 * World Mine — Messages (/messages, Phase 8).
 *
 * `GET /api/notifications/notifications` REQUIRES a `user_id` query parameter
 * server-side (verified), so the inbox is keyed to the authenticated session
 * identity. Without a session the module says so plainly instead of querying
 * blind. "Mark all read" is a real PUT — mutations are never auto-retried (§63)
 * and the outcome is reported back to the user either way.
 */
import { useState } from 'react';
import { useQueryClient } from 'react-query';
import { ModuleFrame } from '../ModuleFrame';
import { DataPanel } from '../DataPanel';
import type { Column } from '../DataPanel';
import { useSession } from '../../../app/providers/SessionContext';
import { api } from '../../../shared/api/client';
import { errorDetail, useResourceList } from '../useResource';
import type { NotificationItem } from '../../../shared/types/domain';
import { dateTime, label, text } from '../../../shared/utils/format';
import { WorldBadge, WorldButton, WorldEmptyState } from '../../../design-system';

type BadgeTone = 'neutral' | 'verified' | 'pending' | 'error' | 'gold';

const TYPE_TONE: Record<string, BadgeTone> = {
  info: 'neutral', success: 'verified', warning: 'pending', error: 'error', alert: 'gold',
};

const PRIORITY_TONE: Record<string, BadgeTone> = {
  low: 'neutral', medium: 'neutral', high: 'pending', urgent: 'error',
};

const COLUMNS: Column<NotificationItem>[] = [
  {
    key: 'message',
    header: 'Notification',
    render: (n) => (
      <div style={{ display: 'grid', gap: 4, maxWidth: '58ch' }}>
        <strong style={{ color: n.read ? 'var(--wm-fog)' : 'var(--wm-porcelain)' }}>{text(n.title)}</strong>
        <span className="wm-hint">{text(n.message)}</span>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Type',
    render: (n) => <WorldBadge tone={TYPE_TONE[n.type] ?? 'neutral'}>{label(n.type)}</WorldBadge>,
  },
  {
    key: 'priority',
    header: 'Priority',
    render: (n) => <WorldBadge tone={PRIORITY_TONE[n.priority] ?? 'neutral'}>{label(n.priority)}</WorldBadge>,
  },
  { key: 'channel', header: 'Channel', render: (n) => label(n.channel) },
  {
    key: 'read',
    header: 'State',
    render: (n) => (
      <WorldBadge tone={n.read ? 'neutral' : 'gold'}>{n.read ? 'read' : 'unread'}</WorldBadge>
    ),
  },
  { key: 'created', header: 'Received', nowrap: true, render: (n) => dateTime(n.created_at) },
];

export function MessagesPage() {
  const { user } = useSession();
  const queryClient = useQueryClient();
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<{ ok: boolean; message: string } | null>(null);

  const userId = user?.id ?? null;
  const path = userId
    ? `/api/notifications/notifications?user_id=${encodeURIComponent(userId)}&limit=50`
    : '';
  const inbox = useResourceList<NotificationItem>(path, { enabled: !!userId });

  const unread = inbox.rows?.filter((n) => !n.read).length ?? 0;

  const markAllRead = async () => {
    if (!userId) return;
    setBusy(true);
    setFeedback(null);
    try {
      const result = await api.put<{ message?: string }>(
        `/api/notifications/mark-all-read?user_id=${encodeURIComponent(userId)}`,
      );
      setFeedback({ ok: true, message: result?.message ?? 'All notifications marked as read.' });
      await queryClient.invalidateQueries(path);
    } catch (err) {
      setFeedback({
        ok: false,
        message: `Could not mark notifications as read (${err instanceof Error ? err.message : 'unknown error'}).`,
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <ModuleFrame
      title="Messages"
      blurb="Your notification inbox — deal updates, verification results, funding and shipment events, with full read state. Counterparty chat arrives with the Deal Rooms phase."
      sources={['GET /api/notifications/notifications?user_id=', 'PUT /api/notifications/mark-all-read']}
      actions={<WorldButton to="/deals" variant="ghost">Deal Rooms</WorldButton>}
    >
      <section
        className="wm-surface"
        style={{ padding: 'var(--space-4) var(--space-5)', display: 'flex', gap: 'var(--space-4)', alignItems: 'center', flexWrap: 'wrap' }}
      >
        <span className="wm-kicker" style={{ margin: 0 }}>Inbox</span>
        <span className="wm-hint">
          {user
            ? `${unread} unread of ${inbox.rows?.length ?? 0} loaded`
            : 'No session — sign in to load your inbox.'}
        </span>
        <span style={{ flex: 1 }} />
        <button
          type="button"
          className="wm-btn wm-btn-secondary wm-btn-sm"
          onClick={markAllRead}
          disabled={!userId || busy || unread === 0}
        >
          {busy ? 'Marking…' : 'Mark all read'}
        </button>
      </section>

      {feedback && (
        <p
          role="status"
          className="wm-hint"
          style={{ margin: 0, color: feedback.ok ? 'var(--wm-verified)' : '#E88B84' }}
        >
          {feedback.message}
        </p>
      )}

      {user ? (
        <DataPanel
          title="Notifications"
          description="Newest first. The backend keeps notifications in memory today, so history resets when the service restarts."
          rows={inbox.rows}
          columns={COLUMNS}
          rowKey={(n) => n.id}
          isLoading={inbox.isLoading}
          isError={inbox.isError}
          errorDetail={errorDetail(inbox.error)}
          onRetry={inbox.refetch}
          emptyTitle="Your inbox is empty"
          emptyHint="Deal, verification and shipment events are delivered here as they occur."
          limitedTo={30}
        />
      ) : (
        <div className="wm-surface" style={{ padding: 'var(--space-6)' }}>
          <WorldEmptyState
            title="Sign in to view your messages"
            hint="The notifications endpoint is scoped to a user id, so an inbox cannot be shown without an authenticated session."
            action={<WorldButton to="/login" variant="primary" size="sm">Sign in</WorldButton>}
          />
        </div>
      )}
    </ModuleFrame>
  );
}
