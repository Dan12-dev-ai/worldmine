/**
 * World-Mine Authentication API Service
 * Production-ready authentication API integration
 */

import { post, get, setAuthToken, clearAuthToken, ApiResponse } from '../api-client';
import { User, UserProfile } from '../types';

export class AuthService {
  private static readonly BASE_PATH = '/api/auth';

  // Registration
  static async register(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await post<ApiResponse<{ user: User; token: string }>>(
      `${this.BASE_PATH}/register`,
      data
    );
    if (response.data.token) {
      setAuthToken(response.data.token);
    }
    return response;
  }

  // Login
  static async login(data: {
    email: string;
    password: string;
  }): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await post<ApiResponse<{ user: User; token: string }>>(
      `${this.BASE_PATH}/login`,
      data
    );
    if (response.data.token) {
      setAuthToken(response.data.token);
    }
    return response;
  }

  // Logout
  static async logout(): Promise<ApiResponse<void>> {
    const response = await post<ApiResponse<void>>(`${this.BASE_PATH}/logout`, {});
    clearAuthToken();
    return response;
  }

  // Magic Link
  static async sendMagicLink(email: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/magic-link`, { email });
  }

  static async verifyMagicLink(token: string): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await post<ApiResponse<{ user: User; token: string }>>(
      `${this.BASE_PATH}/magic-link/verify`,
      { token }
    );
    if (response.data.token) {
      setAuthToken(response.data.token);
    }
    return response;
  }

  // Password Reset
  static async requestPasswordReset(email: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/password-reset`, { email });
  }

  static async resetPassword(data: {
    token: string;
    new_password: string;
  }): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/password-reset/confirm`, data);
  }

  // MFA
  static async enableMFA(): Promise<ApiResponse<{ qr_code: string; backup_codes: string[] }>> {
    return post<ApiResponse<{ qr_code: string; backup_codes: string[] }>>(
      `${this.BASE_PATH}/mfa/enable`,
      {}
    );
  }

  static async verifyMFA(code: string): Promise<ApiResponse<{ verified: boolean }>> {
    return post<ApiResponse<{ verified: boolean }>>(`${this.BASE_PATH}/mfa/verify`, { code });
  }

  static async disableMFA(password: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/mfa/disable`, { password });
  }

  // User Profile
  static async getCurrentUser(): Promise<ApiResponse<User>> {
    return get<ApiResponse<User>>(`${this.BASE_PATH}/me`);
  }

  static async updateProfile(data: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    return post<ApiResponse<UserProfile>>(`${this.BASE_PATH}/profile`, data);
  }

  static async changePassword(data: {
    current_password: string;
    new_password: string;
  }): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/password/change`, data);
  }

  // Session Management
  static async getSessions(): Promise<ApiResponse<Array<{
    id: string;
    device: string;
    location: string;
    ip_address: string;
    last_active: string;
    is_current: boolean;
  }>>> {
    return get<ApiResponse<Array<{ id: string; device: string; location: string; ip_address: string; last_active: string; is_current: boolean }>>>(
      `${this.BASE_PATH}/sessions`
    );
  }

  static async revokeSession(sessionId: string): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/sessions/${sessionId}/revoke`, {});
  }

  static async revokeAllSessions(): Promise<ApiResponse<void>> {
    return post<ApiResponse<void>>(`${this.BASE_PATH}/sessions/revoke-all`, {});
  }
}
