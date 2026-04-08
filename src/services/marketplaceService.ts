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
  listing_id: string;
  bidder_id: string;
  amount: number;
  currency: string;
  timestamp: string;
  is_auto_bid: boolean;
  max_auto_bid?: number;
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
  seller_id: string;
  title: Record<string, string>;
  description: Record<string, string>;
  mineral_type_id: string;
  quantity: number;
  unit: string;
  price: number;
  currency: string;
  location: GeographicLocation;
  quality_assessment?: QualityAssessment;
  certifications?: Certification[];
  photos?: MediaFile[];
  documents?: MediaFile[];
  auction_settings?: AuctionSettings;
  negotiation_enabled: boolean;
  shipping_options?: ShippingOption[];
  status: 'draft' | 'active' | 'sold' | 'expired' | 'suspended';
  views: number;
  favorites: number;
  featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface SellerProfile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  phone?: string;
  avatar_url?: string;
  business_name?: string;
  business_description?: Record<string, string>;
  verification_status: 'pending' | 'verified' | 'rejected';
  created_at: string;
  updated_at: string;
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
  reviewer_id: string;
  listing_id: string;
  rating: number;
  comment: Record<string, string>;
  verified: boolean;
  created_at: string;
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
  async createListing(listing: Omit<MineralListing, 'id' | 'created_at' | 'updated_at'>): Promise<MineralListing> {
    try {
      const { data, error } = await supabase
        .from('listings')
        .insert({
          ...listing,
          status: 'draft',
          views: 0,
          favorites: 0,
          featured: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
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
        .from('listings')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
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

  async deleteListing(id: string, seller_id: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('listings')
        .delete()
        .eq('id', id)
        .eq('seller_id', seller_id);

      if (error) throw error;
    } catch (error) {
      console.error('Error deleting listing:', error);
      throw error;
    }
  }

  async getListing(id: string): Promise<MineralListing | null> {
    try {
      const { data, error } = await supabase
        .from('listings')
        .select(`
          *,
          seller:user_profiles(*),
          minerals(*)
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
    sortBy: string = 'created_at',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<SearchResults> {
    try {
      let query = supabase
        .from('listings')
        .select(`
          *,
          seller:user_profiles(*),
          minerals(*)
        `)
        .eq('status', 'active');

      // Apply filters
      if (filters.mineralType && filters.mineralType.length > 0) {
        query = query.in('mineral_type_id', filters.mineralType);
      }

      if (filters.priceRange) {
        query = query
          .gte('price', filters.priceRange.min)
          .lte('price', filters.priceRange.max);
      }

      if (filters.location?.country) {
        query = query.eq('location->country', filters.location.country);
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
        .from('listings')
        .select(`
          *,
          seller:user_profiles(*),
          minerals(*)
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
    listing_id: string,
    bidder_id: string,
    amount: number,
    is_auto_bid: boolean = false,
    max_auto_bid?: number
  ): Promise<Bid> {
    try {
      // Get current listing and highest bid
      const listing = await this.getListing(listing_id);
      if (!listing || !listing.auction_settings) {
        throw new Error('Listing not found or not an auction');
      }

      if (amount <= (listing.auction_settings.currentBid || listing.auction_settings.startingBid)) {
        throw new Error('Bid must be higher than current bid');
      }

      const bid: Omit<Bid, 'id' | 'timestamp'> = {
        listing_id,
        bidder_id,
        amount,
        currency: listing.currency,
        is_auto_bid,
        max_auto_bid
      };

      // Note: bids table doesn't exist in current schema, this would need to be created
      // For now, we'll update the listing directly
      await supabase
        .from('listings')
        .update({
          auction_settings: {
            ...listing.auction_settings,
            currentBid: amount,
            currentBidder: bidder_id
          },
          updated_at: new Date().toISOString()
        })
        .eq('id', listing_id);

      return {
        id: `bid_${Date.now()}`,
        ...bid,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error placing bid:', error);
      throw error;
    }
  }

  async endAuction(listing_id: string): Promise<MineralListing> {
    try {
      const listing = await this.getListing(listing_id);
      if (!listing || !listing.auction_settings) {
        throw new Error('Listing not found or not an auction');
      }

      const winner = listing.auction_settings.currentBidder 
        ? listing.auction_settings.currentBidder
        : null;

      const finalPrice = listing.auction_settings.currentBid 
        ? listing.auction_settings.currentBid
        : listing.auction_settings.startingBid;

      const { data, error } = await supabase
        .from('listings')
        .update({
          status: winner ? 'sold' : 'expired',
          auction_settings: {
            ...listing.auction_settings,
            endDate: new Date().toISOString()
          },
          updated_at: new Date().toISOString()
        })
        .eq('id', listing_id)
        .select()
        .single();

      if (error) throw error;

      // Create transaction if there's a winner
      if (winner) {
        await this.createTransaction({
          listing_id,
          buyer_id: winner,
          seller_id: listing.seller_id,
          amount: finalPrice,
          currency: listing.currency,
          transaction_type: 'auction_sale',
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
  async createTransaction(transaction: Omit<any, 'id' | 'created_at'>): Promise<any> {
    try {
      const { data, error } = await supabase
        .from('transactions')
        .insert({
          ...transaction,
          created_at: new Date().toISOString()
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
          buyer:user_profiles(*),
          seller:user_profiles(*),
          listing:listings(*)
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
          listing:listings(*),
          ${type === 'buyer' ? 'seller:user_profiles(*)' : 'buyer:user_profiles(*)'}
        `);

      if (type === 'buyer') {
        query = query.eq('buyer_id', userId);
      } else {
        query = query.eq('seller_id', userId);
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
  async addToFavorites(listing_id: string, user_id: string): Promise<void> {
    try {
      // Note: favorites table doesn't exist in current schema
      // For now, we'll just increment the favorites count on the listing
      const { error } = await supabase
        .from('listings')
        .update({ 
          favorites: supabase.raw('favorites + 1'),
          updated_at: new Date().toISOString()
        })
        .eq('id', listing_id);

      if (error) throw error;
    } catch (error) {
      console.error('Error adding to favorites:', error);
      throw error;
    }
  }

  async removeFromFavorites(listing_id: string, user_id: string): Promise<void> {
    try {
      // Note: favorites table doesn't exist in current schema
      // For now, we'll just decrement the favorites count on the listing
      const { error } = await supabase
        .from('listings')
        .update({ 
          favorites: supabase.raw('GREATEST(favorites - 1, 0)'),
          updated_at: new Date().toISOString()
        })
        .eq('id', listing_id);

      if (error) throw error;
    } catch (error) {
      console.error('Error removing from favorites:', error);
      throw error;
    }
  }

  async getUserFavorites(user_id: string): Promise<MineralListing[]> {
    try {
      // Note: favorites table doesn't exist in current schema
      // For now, return empty array - this would need a favorites table to work properly
      return [];
    } catch (error) {
      console.error('Error getting user favorites:', error);
      throw error;
    }
  }

  // Reviews and Ratings
  async createReview(
    review: Omit<Review, 'id' | 'created_at' | 'verified'>
  ): Promise<Review> {
    try {
      // Note: reviews table doesn't exist in current schema
      // This would need to be created for full functionality
      const newReview: Review = {
        id: `review_${Date.now()}`,
        ...review,
        created_at: new Date().toISOString(),
        verified: false
      };

      // Update seller rating would need reviews table
      console.log('Review created (reviews table not implemented):', newReview);

      return newReview;
    } catch (error) {
      console.error('Error creating review:', error);
      throw error;
    }
  }

  async updateSellerRating(listing_id: string): Promise<void> {
    try {
      // Note: reviews table doesn't exist in current schema
      // This functionality would need reviews table to work properly
      console.log('Update seller rating called (reviews table not implemented)');
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
        supabase.from('listings').select('*', { count: 'exact' }),
        supabase.from('listings').select('*', { count: 'exact' }).eq('status', 'active'),
        supabase.from('users').select('*', { count: 'exact' }),
        supabase.from('transactions').select('*', { count: 'exact' }),
        supabase.from('transactions').select('amount')
      ]);

      const totalVolume = transactions?.reduce((sum: number, tx: any) => sum + (tx.amount || 0), 0) || 0;

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
        .from('minerals')
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
        .from('user_profiles')
        .select(`
          *,
          listings:listings(count)
        `)
        .eq('user_id', sellerId)
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
        .from('user_profiles')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', sellerId)
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
