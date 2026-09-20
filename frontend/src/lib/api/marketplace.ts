/**
 * World-Mine Marketplace API Service
 * Production-ready marketplace API integration
 */

import { get, post, put, del, ApiResponse, PaginatedResponse } from '../api-client';
import { MineralListing, Auction, Bid } from '../types';

export class MarketplaceService {
  private static readonly BASE_PATH = '/api/marketplace';

  // Listings
  static async getListings(params?: {
    page?: number;
    page_size?: number;
    mineral_type?: string;
    quality_grade?: string;
    country?: string;
    min_price?: number;
    max_price?: number;
    search?: string;
  }): Promise<PaginatedResponse<MineralListing>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const queryString = queryParams.toString();
    return get<PaginatedResponse<MineralListing>>(
      `${this.BASE_PATH}/listings${queryString ? `?${queryString}` : ''}`
    );
  }

  static async getListing(id: string): Promise<ApiResponse<MineralListing>> {
    return get<ApiResponse<MineralListing>>(`${this.BASE_PATH}/listings/${id}`);
  }

  static async createListing(data: Partial<MineralListing>): Promise<ApiResponse<MineralListing>> {
    return post<ApiResponse<MineralListing>>(`${this.BASE_PATH}/listings`, data);
  }

  static async updateListing(id: string, data: Partial<MineralListing>): Promise<ApiResponse<MineralListing>> {
    return put<ApiResponse<MineralListing>>(`${this.BASE_PATH}/listings/${id}`, data);
  }

  static async deleteListing(id: string): Promise<ApiResponse<void>> {
    return del<ApiResponse<void>>(`${this.BASE_PATH}/listings/${id}`);
  }

  // Auctions
  static async getAuctions(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<PaginatedResponse<Auction>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const queryString = queryParams.toString();
    return get<PaginatedResponse<Auction>>(
      `${this.BASE_PATH}/auctions${queryString ? `?${queryString}` : ''}`
    );
  }

  static async getAuction(id: string): Promise<ApiResponse<Auction>> {
    return get<ApiResponse<Auction>>(`${this.BASE_PATH}/auctions/${id}`);
  }

  static async placeBid(auctionId: string, amount: number): Promise<ApiResponse<Bid>> {
    return post<ApiResponse<Bid>>(`${this.BASE_PATH}/auctions/${auctionId}/bids`, { amount });
  }

  // Buy It Now
  static async buyNow(listingId: string): Promise<ApiResponse<{ transaction_id: string }>> {
    return post<ApiResponse<{ transaction_id: string }>>(
      `${this.BASE_PATH}/listings/${listingId}/buy-now`,
      {}
    );
  }

  // Watchlist
  static async addToWatchlist(listingId: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/watchlist`, { listing_id: listingId });
  }

  static async removeFromWatchlist(listingId: string): Promise<ApiResponse<void>> {
    return del<ApiResponse<void>>(`${this.BASE_PATH}/watchlist/${listingId}`);
  }

  static async getWatchlist(): Promise<PaginatedResponse<MineralListing>> {
    return get<PaginatedResponse<MineralListing>>(`${this.BASE_PATH}/watchlist`);
  }
}
