/**
 * World-Mine Wallet API Service
 * Production-ready wallet API integration
 */

import { get, post, ApiResponse } from '../api-client';
import { Wallet, Transaction } from '../types';

export class WalletService {
  private static readonly BASE_PATH = '/api/wallet';

  // Wallets
  static async getWallets(): Promise<ApiResponse<Wallet[]>> {
    return get<ApiResponse<Wallet[]>>(`${this.BASE_PATH}/wallets`);
  }

  static async getWallet(walletId: string): Promise<ApiResponse<Wallet>> {
    return get<ApiResponse<Wallet>>(`${this.BASE_PATH}/wallets/${walletId}`);
  }

  static async createWallet(data: {
    wallet_type: 'sovereign' | 'crypto' | 'bank';
    currency: string;
  }): Promise<ApiResponse<Wallet>> {
    return post<ApiResponse<Wallet>>(`${this.BASE_PATH}/wallets`, data);
  }

  // Transactions
  static async getTransactions(params?: {
    wallet_id?: string;
    type?: string;
    status?: string;
    limit?: number;
  }): Promise<ApiResponse<Transaction[]>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const queryString = queryParams.toString();
    return get<ApiResponse<Transaction[]>>(
      `${this.BASE_PATH}/transactions${queryString ? `?${queryString}` : ''}`
    );
  }

  static async getTransaction(transactionId: string): Promise<ApiResponse<Transaction>> {
    return get<ApiResponse<Transaction>>(`${this.BASE_PATH}/transactions/${transactionId}`);
  }

  // Deposits
  static async createDeposit(data: {
    wallet_id: string;
    amount: number;
    payment_method: string;
  }): Promise<ApiResponse<{ transaction_id: string; payment_url?: string }>> {
    return post<ApiResponse<{ transaction_id: string; payment_url?: string }>>(
      `${this.BASE_PATH}/deposits`,
      data
    );
  }

  // Withdrawals
  static async createWithdrawal(data: {
    wallet_id: string;
    amount: number;
    destination_address: string;
    payment_method: string;
  }): Promise<ApiResponse<{ transaction_id: string }>> {
    return post<ApiResponse<{ transaction_id: string }>>(
      `${this.BASE_PATH}/withdrawals`,
      data
    );
  }

  // Transfers
  static async createTransfer(data: {
    from_wallet_id: string;
    to_wallet_id: string;
    amount: number;
  }): Promise<ApiResponse<{ transaction_id: string }>> {
    return post<ApiResponse<{ transaction_id: string }>>(
      `${this.BASE_PATH}/transfers`,
      data
    );
  }

  // Balance
  static async getBalance(walletId: string): Promise<ApiResponse<{
    available: number;
    frozen: number;
    total: number;
  }>> {
    return get<ApiResponse<{ available: number; frozen: number; total: number }>>(
      `${this.BASE_PATH}/wallets/${walletId}/balance`
    );
  }
}
