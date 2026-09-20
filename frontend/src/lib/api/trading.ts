/**
 * World-Mine Trading API Service
 * Production-ready trading API integration
 */

import { get, post, ApiResponse } from '../api-client';
import { Order, Trade, OrderBookEntry } from '../types';

export class TradingService {
  private static readonly BASE_PATH = '/api/trading';

  // Orders
  static async placeOrder(data: {
    mineral_id: string;
    side: 'buy' | 'sell';
    order_type: 'market' | 'limit' | 'stop_loss' | 'stop_limit' | 'iceberg';
    amount: number;
    price?: number;
    stop_price?: number;
    leverage?: number;
  }): Promise<ApiResponse<Order>> {
    return post<ApiResponse<Order>>(`${this.BASE_PATH}/orders`, data);
  }

  static async getOrders(params?: {
    status?: string;
    mineral_id?: string;
    limit?: number;
  }): Promise<ApiResponse<Order[]>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const queryString = queryParams.toString();
    return get<ApiResponse<Order[]>>(
      `${this.BASE_PATH}/orders${queryString ? `?${queryString}` : ''}`
    );
  }

  static async getOrder(orderId: string): Promise<ApiResponse<Order>> {
    return get<ApiResponse<Order>>(`${this.BASE_PATH}/orders/${orderId}`);
  }

  static async cancelOrder(orderId: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/orders/${orderId}/cancel`, {});
  }

  // Market Data
  static async getOrderBook(mineralId: string): Promise<ApiResponse<{
    bids: OrderBookEntry[];
    asks: OrderBookEntry[];
  }>> {
    return get<ApiResponse<{ bids: OrderBookEntry[]; asks: OrderBookEntry[] }>>(
      `${this.BASE_PATH}/orderbook/${mineralId}`
    );
  }

  static async getRecentTrades(mineralId: string, limit: number = 20): Promise<ApiResponse<Trade[]>> {
    return get<ApiResponse<Trade[]>>(
      `${this.BASE_PATH}/trades/${mineralId}?limit=${limit}`
    );
  }

  static async getPriceHistory(mineralId: string, timeframe: string = '1H'): Promise<ApiResponse<{
    timestamp: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[]>> {
    return get<ApiResponse<{ timestamp: number; open: number; high: number; low: number; close: number; volume: number }[]>>(
      `${this.BASE_PATH}/price-history/${mineralId}?timeframe=${timeframe}`
    );
  }

  static async getCurrentPrice(mineralId: string): Promise<ApiResponse<{
    price: number;
    change: number;
    change_percent: number;
    volume: number;
  }>> {
    return get<ApiResponse<{ price: number; change: number; change_percent: number; volume: number }>>(
      `${this.BASE_PATH}/price/${mineralId}`
    );
  }

  // Position
  static async getPosition(mineralId: string): Promise<ApiResponse<{
    size: number;
    pnl: number;
    unrealized_pnl: number;
    avg_entry_price: number;
  }>> {
    return get<ApiResponse<{ size: number; pnl: number; unrealized_pnl: number; avg_entry_price: number }>>(
      `${this.BASE_PATH}/position/${mineralId}`
    );
  }
}
