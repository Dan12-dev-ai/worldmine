/**
 * World-Mine Escrow API Service
 * Production-ready escrow API integration
 */

import { get, post, ApiResponse } from '../api-client';
import { Escrow } from '../types';

export class EscrowService {
  private static readonly BASE_PATH = '/api/escrow';

  // Escrow Management
  static async createEscrow(data: {
    transaction_id: string;
    amount: number;
    currency: string;
    buyer_id: string;
    seller_id: string;
    release_conditions: Record<string, unknown>;
  }): Promise<ApiResponse<Escrow>> {
    return post<ApiResponse<Escrow>>(`${this.BASE_PATH}/escrow`, data);
  }

  static async getEscrow(escrowId: string): Promise<ApiResponse<Escrow>> {
    return get<ApiResponse<Escrow>>(`${this.BASE_PATH}/escrow/${escrowId}`);
  }

  static async getEscrows(params?: {
    status?: string;
    user_id?: string;
    limit?: number;
  }): Promise<ApiResponse<Escrow[]>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const queryString = queryParams.toString();
    return get<ApiResponse<Escrow[]>>(
      `${this.BASE_PATH}/escrow${queryString ? `?${queryString}` : ''}`
    );
  }

  // Escrow Actions
  static async fundEscrow(escrowId: string, payment_method: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/escrow/${escrowId}/fund`, { payment_method });
  }

  static async releaseEscrow(escrowId: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/escrow/${escrowId}/release`, {});
  }

  static async disputeEscrow(escrowId: string, reason: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/escrow/${escrowId}/dispute`, { reason });
  }

  static async resolveDispute(escrowId: string, resolution: string, release_to: 'buyer' | 'seller'): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/escrow/${escrowId}/resolve`, {
      resolution,
      release_to
    });
  }

  static async cancelEscrow(escrowId: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/escrow/${escrowId}/cancel`, {});
  }
}
