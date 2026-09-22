/**
 * World Mine — Market Intelligence (/news).
 *
 * Wired to the real news service: `/api/v2/mineral-news/` plus its `critical`,
 * `high-impact` and `trending` feeds. Response shape is `NewsArticleResponse`
 * (verified from the backend serializer).
 *
 * OPERATIONAL NOTE: the news router was never mounted by `backend/app.py`, so
 * this page explains that plainly until `app.include_router(mineral_news_router)`
 * is present in the API app. Placeholder articles are never substituted (§38).
 */
import { useState } from 'react';
import { ModuleFrame } from '../workspace/ModuleFrame';
import { errorDetail, useResourceList } from '../workspace/useResource';
import type { NewsArticle } from '../../shared/types/domain';
import { dateTime, label, text } from '../../shared/utils/format';
import { WorldBadge, WorldEmptyState, WorldErrorState, WorldSkeleton } from '../../design-system';

type FeedKey = 'latest' | 'critical' | 'high-impact' | 'trending';

const FEEDS: { key: FeedKey; label: string; path: string; blurb: string }[] = [
  { key: 'latest', label: 'Latest', path: '?limit=12', blurb: 'Most recent reporting across every tracked mineral category.' },
  { key: 'critical', label: 'Critical', path: 'critical?limit=12', blurb: 'Items the news service flags as critical for supply or pricing.' },
  { key: 'high-impact', label: 'High impact', path: 'high-impact?limit=12', blurb: 'Stories with a material expected effect on price or availability.' },
  { key: 'trending', label: 'Trending', path: 'trending?limit=12', blurb: 'Fastest-moving coverage right now.' },
];

const IMPACT_TONE: Record<string, 'error' | 'pending' | 'neutral'> = {
  critical: 'error', high: 'pending', medium: 'neutral', low: 'neutral',
};

const SENTIMENT_TONE: Record<string, 'verified' | 'error' | 'neutral'> = {
  positive: 'verified', negative: 'error', neutral: 'neutral',
};

function ArticleCard({ article }: { article: NewsArticle }) {
  return (
    <article className="wm-card" style={{ padding: 'var(--space-5)', display: 'grid', gap: 10 }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        {article.impact_level && (
          <WorldBadge tone={IMPACT_TONE[article.impact_level] ?? 'neutral'}>
            {label(article.impact_level)} impact
          </WorldBadge>
        )}
        {article.sentiment && (
          <WorldBadge tone={SENTIMENT_TONE[article.sentiment] ?? 'neutral'}>{label(article.sentiment)}</WorldBadge>
        )}
        <span className="wm-hint">{label(article.category)}</span>
        <span className="wm-hint">{text(article.source)}</span>
        <span className="wm-hint wm-mono">{dateTime(article.published_at)}</span>
      </div>

      <h3 style={{ margin: 0, fontSize: 'var(--text-h3)' }}>
        {article.url ? (
          <a href={article.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--wm-porcelain)' }}>
            {text(article.title)}
          </a>
        ) : (
          text(article.title)
        )}
      </h3>

      <p style={{ margin: 0, color: 'var(--wm-fog)', maxWidth: '76ch' }}>{text(article.summary)}</p>

      {article.ai_analysis && (
        <p
          className="wm-hint"
          style={{ margin: 0, maxWidth: '76ch', borderLeft: '2px solid var(--wm-gold-line)', paddingLeft: 10 }}
        >
          <strong style={{ color: 'var(--wm-ash)' }}>AI analysis: </strong>
          {article.ai_analysis}
        </p>
      )}

      {(article.mentioned_minerals?.length || article.mentioned_countries?.length) && (
        <p className="wm-hint" style={{ margin: 0 }}>
          {article.mentioned_minerals?.length ? `Minerals: ${article.mentioned_minerals.join(', ')}` : ''}
          {article.mentioned_minerals?.length && article.mentioned_countries?.length ? ' · ' : ''}
          {article.mentioned_countries?.length ? `Countries: ${article.mentioned_countries.join(', ')}` : ''}
        </p>
      )}
    </article>
  );
}

export function NewsPage() {
  const [feed, setFeed] = useState<FeedKey>('latest');
  const active = FEEDS.find((f) => f.key === feed) ?? FEEDS[0];
  const news = useResourceList<NewsArticle>(`/api/v2/mineral-news/${active.path}`);

  return (
    <ModuleFrame
      title="Market intelligence"
      blurb="Mineral market reporting with impact classification, sentiment and mineral/country tagging, served by the platform news service."
      sources={['GET /api/v2/mineral-news/', 'GET /api/v2/mineral-news/critical', 'GET /api/v2/mineral-news/high-impact', 'GET /api/v2/mineral-news/trending']}
    >
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }} role="tablist" aria-label="News feeds">
        {FEEDS.map((f) => (
          <button
            key={f.key}
            type="button"
            role="tab"
            aria-selected={f.key === feed}
            className={`wm-btn wm-btn-sm ${f.key === feed ? 'wm-btn-primary' : 'wm-btn-secondary'}`}
            onClick={() => setFeed(f.key)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <p className="wm-hint" style={{ margin: 0 }}>{active.blurb}</p>

      {news.isLoading && (
        <div style={{ display: 'grid', gap: 'var(--space-4)' }} role="status" aria-live="polite">
          <span className="wm-sr-only">Loading market intelligence</span>
          {[0, 1, 2].map((i) => <WorldSkeleton key={i} h={150} />)}
        </div>
      )}

      {!news.isLoading && news.isError && (
        <WorldErrorState
          title="Market intelligence could not be loaded"
          detail={errorDetail(news.error)}
          onRetry={news.refetch}
          preserveNote="The mineral-news router must be mounted in the API app (app.include_router(mineral_news_router)) for this feed to respond. No articles are fabricated in the meantime."
        />
      )}

      {!news.isLoading && !news.isError && news.rows === null && (
        <WorldErrorState
          title="Unexpected news response"
          detail="The endpoint did not return a JSON array of articles."
          onRetry={news.refetch}
        />
      )}

      {!news.isLoading && !news.isError && news.rows?.length === 0 && (
        <WorldEmptyState
          title="No articles in this feed"
          hint="The news service returned an empty result for this feed. Nothing is substituted in its place."
        />
      )}

      {!news.isLoading && !news.isError && news.rows && news.rows.length > 0 && (
        <div style={{ display: 'grid', gap: 'var(--space-4)' }}>
          {news.rows.map((a) => <ArticleCard key={a.id} article={a} />)}
        </div>
      )}
    </ModuleFrame>
  );
}
