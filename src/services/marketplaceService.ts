/**
 * Enterprise Marketplace Service
 * Handles all marketplace operations including listings, auctions, negotiations, and transactions
 */

import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database';

const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

// Types
export interface MineralType {
  id: string;
  name: string;
  code: string;
  category: 'precious_metals' | 'industrial_minerals' | 'rare_earths' | 'gemstones';
  unit: string;
  description: Record<string, string>;
}

export interface QualityAssessment {
  grade: string;
  purity: number;
  specifications: Record<string, any>;
  certification: string[];
  assessmentDate: string;
  assessedBy: string;
}

export interface GeographicLocation {
  country: string;
  region: string;
  coordinates: [number, number];
  timezone: string;
}

export interface Certification {
  id: string;
  type: 'mining_license' | 'environmental' | 'quality' | 'origin' | 'ethical';
  issuer: string;
  issueDate: string;
  expiryDate: string;
  documentUrl: string;
  verified: boolean;
}

export interface MediaFile {
  id: string;
  type: 'image' | 'video' | 'document';
  url: string;
  thumbnail?: string;
  size: number;
  uploadedAt: string;
}

export interface AuctionSettings {
  enabled: boolean;
  startDate: string;
  endDate: string;
  startingBid: number;
  reservePrice: number;
  bidIncrement: number;
  currentBid?: number;
  currentBidder?: string;
  bids: Bid[];
}

export interface Bid {
  id: string;
  bidderId: string;
  amount: number;
  currency: string;
  timestamp: string;
  isAutoBid: boolean;
  maxAutoBid?: number;
}

export interface ShippingOption {
  id: string;
  method: 'standard' | 'express' | 'freight' | 'air' | 'sea';
  cost: number;
  estimatedDays: number;
  trackingRequired: boolean;
  insuranceIncluded: boolean;
  destinations: string[];
}

export interface MineralListing {
  id: string;
  sellerId: string;
  title: Record<string, string>;
  description: Record<string, string>;
  mineralType: MineralType;
  quantity: number;
  unit: string;
  price: number;
  currency: string;
  location: GeographicLocation;
  quality: QualityAssessment;
  certifications: Certification[];
  photos: MediaFile[];
  documents: MediaFile[];
  auctionSettings?: AuctionSettings;
  negotiationEnabled: boolean;
  shippingOptions: ShippingOption[];
  status: 'draft' | 'active' | 'sold' | 'expired' | 'suspended';
  views: number;
  favorites: number;
  createdAt: string;
  updatedAt: string;
}

export interface SellerProfile {
  id: string;
  businessName: string;
  description: Record<string, string>;
  logo?: MediaFile;
  verificationStatus: 'pending' | 'verified' | 'rejected';
  miningLicense: Certification;
  geologicalReports: MediaFile[];
  listings: MineralListing[];
  rating: SellerRating;
  capabilities: SellerCapabilities;
  joinedAt: string;
  lastActive: string;
}

export interface SellerRating {
  overall: number;
  communication: number;
  quality: number;
  shipping: number;
  totalTransactions: number;
  reviews: Review[];
}

export interface SellerCapabilities {
  mineralTypes: MineralType[];
  shippingMethods: string[];
  paymentMethods: string[];
  maxQuantity: number;
  processingTime: number;
}

export interface Review {
  id: string;
  reviewerId: string;
  listingId: string;
  rating: number;
  comment: Record<string, string>;
  verified: boolean;
  createdAt: string;
}

export interface SearchFilters {
  mineralType?: string[];
  priceRange?: {
    min: number;
    max: number;
  };
  location?: GeographicLocation;
  quality?: string[];
  certification?: string[];
  sellerRating?: {
    min: number;
    max: number;
  };
  availability?: 'in_stock' | 'pre_order' | 'made_to_order';
  shippingOptions?: string[];
  keywords?: string;
}

export interface SearchResults {
  listings: MineralListing[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
  filters: SearchFilters;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

// Main Service Class
export class MarketplaceService {
  private static instance: MarketplaceService;

  private constructor() {}

  static getInstance(): MarketplaceService {
    if (!MarketplaceService.instance) {
      MarketplaceService.instance = new MarketplaceService();
    }
    return MarketplaceService.instance;
  }

  // Listing Management
  async createListing(listing: Omit<MineralListing, 'id' | 'createdAt' | 'updatedAt'>): Promise<MineralListing> {
    try {
      const { data, error } = await supabase
        .from('mineral_listings')
        .insert({
          ...listing,
          status: 'draft',
          views: 0,
          favorites: 0,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error creating listing:', error);
      throw error;
    }
  }

  async updateListing(id: string, updates: Partial<MineralListing>): Promise<MineralListing> {
    try {
      const { data, error } = await supabase
        .from('mineral_listings')
        .update({
          ...updates,
          updatedAt: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error updating listing:', error);
      throw error;
    }
  }

  async deleteListing(id: string, sellerId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('mineral_listings')
        .delete()
        .eq('id', id)
        .eq('sellerId', sellerId);

      if (error) throw error;
    } catch (error) {
      console.error('Error deleting listing:', error);
      throw error;
    }
  }

  async getListing(id: string): Promise<MineralListing | null> {
    try {
      const { data, error } = await supabase
        .from('mineral_listings')
        .select(`
          *,
          seller:seller_profiles(*),
          mineral_types(*)
        `)
        .eq('id', id)
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error getting listing:', error);
      throw error;
    }
  }

  // Search and Discovery
  async searchListings(
    filters: SearchFilters,
    page: number = 1,
    limit: number = 20,
    sortBy: string = 'createdAt',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<SearchResults> {
    try {
      let query = supabase
        .from('mineral_listings')
        .select(`
          *,
          seller:seller_profiles(*),
          mineral_types(*)
        `)
        .eq('status', 'active');

      // Apply filters
      if (filters.mineralType && filters.mineralType.length > 0) {
        query = query.in('mineralType', filters.mineralType);
      }

      if (filters.priceRange) {
        query = query
          .gte('price', filters.priceRange.min)
          .lte('price', filters.priceRange.max);
      }

      if (filters.location?.country) {
        query = query.eq('location->country', filters.location.country);
      }

      if (filters.sellerRating) {
        query = query
          .gte('seller->rating->overall', filters.sellerRating.min)
          .lte('seller->rating->overall', filters.sellerRating.max);
      }

      // Apply sorting
      if (sortOrder === 'desc') {
        query = query.order(sortBy, { ascending: false });
      } else {
        query = query.order(sortBy, { ascending: true });
      }

      // Get total count
      const { count } = await query;

      // Apply pagination
      const from = (page - 1) * limit;
      const to = from + limit - 1;

      const { data: listings, error, count } = await query.range(from, to);

      if (error) throw error;

      return {
        listings: listings || [],
        totalCount: count || 0,
        currentPage: page,
        totalPages: Math.ceil((count || 0) / limit),
        filters,
        sortBy,
        sortOrder
      };
    } catch (error) {
      console.error('Error searching listings:', error);
      throw error;
    }
  }

  async getFeaturedListings(limit: number = 10): Promise<MineralListing[]> {
    try {
      const { data, error } = await supabase
        .from('mineral_listings')
        .select(`
          *,
          seller:seller_profiles(*),
          mineral_types(*)
        `)
        .eq('status', 'active')
        .eq('featured', true)
        .order('views', { ascending: false })
        .limit(limit);

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error getting featured listings:', error);
      throw error;
    }
  }

  // Auction Management
  async placeBid(
    listingId: string,
    bidderId: string,
    amount: number,
    isAutoBid: boolean = false,
    maxAutoBid?: number
  ): Promise<Bid> {
    try {
      // Get current listing and highest bid
      const listing = await this.getListing(listingId);
      if (!listing || !listing.auctionSettings) {
        throw new Error('Listing not found or not an auction');
      }

      if (amount <= (listing.auctionSettings.currentBid || listing.auctionSettings.startingBid)) {
        throw new Error('Bid must be higher than current bid');
      }

      const bid: Omit<Bid, 'id' | 'timestamp'> = {
        bidderId,
        amount,
        currency: listing.currency,
        isAutoBid,
        maxAutoBid
      };

      const { data, error } = await supabase
        .from('bids')
        .insert({
          ...bid,
          listingId,
          timestamp: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;

      // Update auction current bid
      await supabase
        .from('mineral_listings')
        .update({
          auctionSettings: {
            ...listing.auctionSettings,
            currentBid: amount,
            currentBidder: bidderId
          }
        })
        .eq('id', listingId);

      return data;
    } catch (error) {
      console.error('Error placing bid:', error);
      throw error;
    }
  }

  async endAuction(listingId: string): Promise<MineralListing> {
    try {
      const listing = await this.getListing(listingId);
      if (!listing || !listing.auctionSettings) {
        throw new Error('Listing not found or not an auction');
      }

      const winner = listing.auctionSettings.currentBidder 
        ? listing.auctionSettings.currentBidder
        : null;

      const finalPrice = listing.auctionSettings.currentBid 
        ? listing.auctionSettings.currentBid
        : listing.auctionSettings.startingBid;

      const { data, error } = await supabase
        .from('mineral_listings')
        .update({
          status: winner ? 'sold' : 'expired',
          auctionSettings: {
            ...listing.auctionSettings,
            endDate: new Date().toISOString()
          }
        })
        .eq('id', listingId)
        .select()
        .single();

      if (error) throw error;

      // Create transaction if there's a winner
      if (winner) {
        await this.createTransaction({
          listingId,
          buyerId: winner,
          sellerId: listing.sellerId,
          amount: finalPrice,
          currency: listing.currency,
          type: 'auction_sale',
          status: 'pending_payment'
        });
      }

      return data;
    } catch (error) {
      console.error('Error ending auction:', error);
      throw error;
    }
  }

  // Transaction Management
  async createTransaction(transaction: Omit<any, 'id' | 'createdAt'>): Promise<any> {
    try {
      const { data, error } = await supabase
        .from('transactions')
        .insert({
          ...transaction,
          createdAt: new Date().toISOString()
        })
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error creating transaction:', error);
      throw error;
    }
  }

  async getTransaction(id: string): Promise<any | null> {
    try {
      const { data, error } = await supabase
        .from('transactions')
        .select(`
          *,
          buyer:buyer_profiles(*),
          seller:seller_profiles(*),
          listing:mineral_listings(*)
        `)
        .eq('id', id)
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error getting transaction:', error);
      throw error;
    }
  }

  async getUserTransactions(
    userId: string,
    type: 'buyer' | 'seller' = 'buyer',
    status?: string,
    page: number = 1,
    limit: number = 20
  ): Promise<{ transactions: any[]; total: number }> {
    try {
      let query = supabase
        .from('transactions')
        .select(`
          *,
          listing:mineral_listings(*),
          ${type === 'buyer' ? 'seller:seller_profiles(*)' : 'buyer:buyer_profiles(*)'}
        `);

      if (type === 'buyer') {
        query = query.eq('buyerId', userId);
      } else {
        query = query.eq('sellerId', userId);
      }

      if (status) {
        query = query.eq('status', status);
      }

      const from = (page - 1) * limit;
      const to = from + limit - 1;

      const { data, error, count } = await query.range(from, to);

      if (error) throw error;

      return {
        transactions: data || [],
        total: count || 0
      };
    } catch (error) {
      console.error('Error getting user transactions:', error);
      throw error;
    }
  }

  // Favorites and Watchlist
  async addToFavorites(listingId: string, userId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('favorites')
        .insert({
          listingId,
          userId,
          createdAt: new Date().toISOString()
        });

      if (error) throw error;

      // Increment favorites count
      await supabase.rpc('increment_favorites_count', { listing_id: listingId });
    } catch (error) {
      console.error('Error adding to favorites:', error);
      throw error;
    }
  }

  async removeFromFavorites(listingId: string, userId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('favorites')
        .delete()
        .eq('listingId', listingId)
        .eq('userId', userId);

      if (error) throw error;

      // Decrement favorites count
      await supabase.rpc('decrement_favorites_count', { listing_id: listingId });
    } catch (error) {
      console.error('Error removing from favorites:', error);
      throw error;
    }
  }

  async getUserFavorites(userId: string): Promise<MineralListing[]> {
    try {
      const { data, error } = await supabase
        .from('favorites')
        .select(`
          listing:mineral_listings(*),
          seller:seller_profiles(*)
        `)
        .eq('userId', userId)
        .order('createdAt', { ascending: false });

      if (error) throw error;
      return data?.map(f => f.listing) || [];
    } catch (error) {
      console.error('Error getting user favorites:', error);
      throw error;
    }
  }

  // Reviews and Ratings
  async createReview(
    review: Omit<Review, 'id' | 'createdAt' | 'verified'>
  ): Promise<Review> {
    try {
      const { data, error } = await supabase
        .from('reviews')
        .insert({
          ...review,
          createdAt: new Date().toISOString(),
          verified: false
        })
        .select()
        .single();

      if (error) throw error;

      // Update seller rating
      await this.updateSellerRating(review.listingId);

      return data;
    } catch (error) {
      console.error('Error creating review:', error);
      throw error;
    }
  }

  async updateSellerRating(listingId: string): Promise<void> {
    try {
      // Get all reviews for this seller's listings
      const { data: listing } = await supabase
        .from('mineral_listings')
        .select('sellerId')
        .eq('id', listingId)
        .single();

      if (!listing) return;

      const { data: allReviews } = await supabase
        .from('reviews')
        .select('rating')
        .eq('listingId', listingId);

      // Calculate new average
      const averageRating = allReviews?.length 
        ? allReviews.reduce((sum: number, review: any) => sum + review.rating, 0) / allReviews.length
        : 0;

      // Update seller rating
      await supabase
        .from('seller_profiles')
        .update({
          rating: {
            overall: averageRating,
            communication: averageRating,
            quality: averageRating,
            shipping: averageRating,
            totalTransactions: allReviews?.length || 0
          }
        })
        .eq('id', listing.sellerId);
    } catch (error) {
      console.error('Error updating seller rating:', error);
    }
  }

  // Analytics and Insights
  async getMarketplaceStats(): Promise<{
    totalListings: number;
    activeListings: number;
    totalUsers: number;
    totalTransactions: number;
    totalVolume: number;
  }> {
    try {
      const [
        { count: totalListings },
        { count: activeListings },
        { count: totalUsers },
        { count: totalTransactions },
        { data: transactions }
      ] = await Promise.all([
        supabase.from('mineral_listings').select('*', { count: 'exact' }),
        supabase.from('mineral_listings').select('*', { count: 'exact' }).eq('status', 'active'),
        supabase.from('profiles').select('*', { count: 'exact' }),
        supabase.from('transactions').select('*', { count: 'exact' }),
        supabase.from('transactions').select('amount, currency')
      ]);

      const totalVolume = transactions?.reduce((sum, tx) => sum + tx.amount, 0) || 0;

      return {
        totalListings: totalListings || 0,
        activeListings: activeListings || 0,
        totalUsers: totalUsers || 0,
        totalTransactions: totalTransactions || 0,
        totalVolume
      };
    } catch (error) {
      console.error('Error getting marketplace stats:', error);
      throw error;
    }
  }

  async getMineralTypes(): Promise<MineralType[]> {
    try {
      const { data, error } = await supabase
        .from('mineral_types')
        .select('*')
        .order('name');

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error getting mineral types:', error);
      throw error;
    }
  }

  async getSellerProfile(sellerId: string): Promise<SellerProfile | null> {
    try {
      const { data, error } = await supabase
        .from('seller_profiles')
        .select(`
          *,
          listings:mineral_listings(count)
        `)
        .eq('id', sellerId)
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error getting seller profile:', error);
      throw error;
    }
  }

  async updateSellerProfile(
    sellerId: string,
    updates: Partial<SellerProfile>
  ): Promise<SellerProfile> {
    try {
      const { data, error } = await supabase
        .from('seller_profiles')
        .update({
          ...updates,
          lastActive: new Date().toISOString()
        })
        .eq('id', sellerId)
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error updating seller profile:', error);
      throw error;
    }
  }
}

export default MarketplaceService;
