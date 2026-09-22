/**
 * World Mine — marketplace domain queries (Phase 5).
 * Contract: GET /api/marketplace/listings (shape locked in migration map).
 */
import { useMutation, useQuery } from 'react-query';
import { api } from '../../shared/api/client';
import type { Listing } from '../../shared/types/domain';

export interface MarketplaceFilters {
  q: string;
  mineral: string;
  country: string;
  grade: string;
  status: string;
  sort: string;
}

export const DEFAULT_FILTERS: MarketplaceFilters = {
  q: '', mineral: '', country: '', grade: '', status: 'active', sort: 'newest',
};

/** Client-side filter/sort until server-side params are honored (drift flag #1). */
function applyClientFilters(listings: Listing[], f: MarketplaceFilters): Listing[] {
  const q = f.q.trim().toLowerCase();
  let out = listings.filter((l) => {
    if (f.status && l.status !== f.status) return false;
    if (f.mineral && (l.mineral_type ?? '').toLowerCase() !== f.mineral.toLowerCase()) return false;
    if (f.country && (l.country ?? '').toLowerCase() !== f.country.toLowerCase()) return false;
    if (f.grade && (l.quality_grade ?? '').toLowerCase() !== f.grade.toLowerCase()) return false;
    if (q) {
      const hay = [l.title, l.mineral_type, l.origin, l.country, l.city, l.id]
        .filter(Boolean).join(' ').toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  const byPrice = (l: Listing) => l.unit_price ?? l.total_price ?? Number.POSITIVE_INFINITY;
  switch (f.sort) {
    case 'price-asc': out = [...out].sort((a, b) => byPrice(a) - byPrice(b)); break;
    case 'price-desc': out = [...out].sort((a, b) => byPrice(b) - byPrice(a)); break;
    case 'quantity-desc': out = [...out].sort((a, b) => (b.quantity ?? 0) - (a.quantity ?? 0)); break;
    case 'newest':
    default:
      out = [...out].sort(
        (a, b) => new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime(),
      );
  }
  return out;
}

export function useListings(filters: MarketplaceFilters = DEFAULT_FILTERS) {
  return useQuery<Listing[], Error>(
    ['listings', filters],
    async ({ signal }) => {
      const raw = await api.get<Listing[]>('/api/marketplace/listings', { signal });
      return applyClientFilters(Array.isArray(raw) ? raw : [], filters);
    },
    {
      staleTime: 60_000,
      keepPreviousData: true,
      refetchOnWindowFocus: false,
    },
  );
}

export function useListing(id: string) {
  return useQuery<Listing, Error>(
    ['listing', id],
    async ({ signal }) => {
      const raw = await api.get<Listing | { listing: Listing }>(`/api/marketplace/listings/${id}`, { signal });
      // Some versions wrap the payload; unwrap defensively without faking data.
      if (raw && typeof raw === 'object' && 'listing' in raw) return (raw as { listing: Listing }).listing;
      return raw as Listing;
    },
    { enabled: Boolean(id), staleTime: 60_000, retry: false },
  );
}

export interface ListingCreatePayload {
  title: string;
  description?: string;
  mineral_type?: string;
  quantity?: number;
  unit_price?: number;
  quality_grade?: string;
  origin?: string;
  country?: string;
  city?: string;
}

export function useCreateListing() {
  return useMutation<Listing, Error, ListingCreatePayload>(
    (payload) => api.post('/api/marketplace/listings', payload),
  );
}
