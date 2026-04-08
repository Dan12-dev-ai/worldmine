/**
 * Database Type Definitions for DEDAN Mine
 * Generated from Neon.tech PostgreSQL schema - Production Ready
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          username: string
          email: string
          password_hash: string
          first_name: string
          last_name: string
          phone: string
          country: string
          is_active: boolean
          is_verified: boolean
          created_at: string
          updated_at: string
          last_login: string
        }
        Insert: {
          id?: string
          username: string
          email: string
          password_hash: string
          first_name?: string
          last_name?: string
          phone?: string
          country?: string
          is_active?: boolean
          is_verified?: boolean
          created_at?: string
          updated_at?: string
          last_login?: string
        }
        Update: {
          id?: string
          username?: string
          email?: string
          password_hash?: string
          first_name?: string
          last_name?: string
          phone?: string
          country?: string
          is_active?: boolean
          is_verified?: boolean
          created_at?: string
          updated_at?: string
          last_login?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_profiles_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "user_profiles"
            referencedColumns: ["user_id"]
          }
        ]
      }
      user_profiles: {
        Row: {
          id: string
          user_id: string
          bio: string
          avatar_url: string
          company: string
          position: string
          website: string
          linkedin: string
          preferences: Json
          security_settings: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          bio?: string
          avatar_url?: string
          company?: string
          position?: string
          website?: string
          linkedin?: string
          preferences?: Json
          security_settings?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          bio?: string
          avatar_url?: string
          company?: string
          position?: string
          website?: string
          linkedin?: string
          preferences?: Json
          security_settings?: Json
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_profiles_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      wallets: {
        Row: {
          id: string
          user_id: string
          wallet_type: string
          currency: string
          balance: number
          frozen_balance: number
          is_active: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          wallet_type: string
          currency: string
          balance?: number
          frozen_balance?: number
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          wallet_type?: string
          currency?: string
          balance?: number
          frozen_balance?: number
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "wallets_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      transactions: {
        Row: {
          id: string
          user_id: string
          transaction_type: string
          currency: string
          amount: number
          fee: number
          from_currency: string
          to_currency: string
          exchange_rate: number
          status: string
          payment_method: string
          payment_details: Json
          metadata: Json
          quantum_signature: string
          created_at: string
          updated_at: string
          completed_at: string
        }
        Insert: {
          id?: string
          user_id: string
          transaction_type: string
          currency: string
          amount: number
          fee?: number
          from_currency?: string
          to_currency?: string
          exchange_rate?: number
          status?: string
          payment_method?: string
          payment_details?: Json
          metadata?: Json
          quantum_signature?: string
          created_at?: string
          updated_at?: string
          completed_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          transaction_type?: string
          currency?: string
          amount?: number
          fee?: number
          from_currency?: string
          to_currency?: string
          exchange_rate?: number
          status?: string
          payment_method?: string
          payment_details?: Json
          metadata?: Json
          quantum_signature?: string
          created_at?: string
          updated_at?: string
          completed_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "transactions_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      minerals: {
        Row: {
          id: string
          name: string
          symbol: string
          description: string
          category: string
          purity: number
          origin: string
          current_price: number
          price_updated_at: string
          is_active: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          symbol: string
          description?: string
          category?: string
          purity?: number
          origin?: string
          current_price?: number
          price_updated_at?: string
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          symbol?: string
          description?: string
          category?: string
          purity?: number
          origin?: string
          current_price?: number
          price_updated_at?: string
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      listings: {
        Row: {
          id: string
          seller_id: string
          title: string
          description: string
          quantity: number
          unit: string
          price_per_unit: number
          total_price: number
          currency: string
          location: string
          certification: Json
          images: Json
          status: string
          views: number
          created_at: string
          updated_at: string
          expires_at: string
        }
        Insert: {
          id?: string
          seller_id: string
          title: string
          description?: string
          quantity: number
          unit: string
          price_per_unit: number
          total_price?: number
          currency: string
          location?: string
          certification?: Json
          images?: Json
          status?: string
          views?: number
          created_at?: string
          updated_at?: string
          expires_at?: string
        }
        Update: {
          id?: string
          seller_id?: string
          title?: string
          description?: string
          quantity?: number
          unit: string
          price_per_unit?: number
          total_price?: number
          currency: string
          location?: string
          certification?: Json
          images?: Json
          status?: string
          views?: number
          created_at?: string
          updated_at?: string
          expires_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "listings_seller_id_fkey"
            columns: ["seller_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      orders: {
        Row: {
          id: string
          buyer_id: string
          seller_id: string
          listing_id: string
          quantity: number
          price_per_unit: number
          total_price: number
          currency: string
          status: string
          payment_status: string
          shipping_address: Json
          tracking_number: string
          notes: string
          created_at: string
          updated_at: string
          confirmed_at: string
          shipped_at: string
          delivered_at: string
        }
        Insert: {
          id?: string
          buyer_id: string
          seller_id: string
          listing_id: string
          quantity: number
          price_per_unit: number
          total_price?: number
          currency: string
          status?: string
          payment_status?: string
          shipping_address?: Json
          tracking_number?: string
          notes?: string
          created_at?: string
          updated_at?: string
          confirmed_at?: string
          shipped_at?: string
          delivered_at?: string
        }
        Update: {
          id?: string
          buyer_id?: string
          seller_id?: string
          listing_id?: string
          quantity: number
          price_per_unit: number
          total_price?: number
          currency: string
          status?: string
          payment_status?: string
          shipping_address?: Json
          tracking_number?: string
          notes?: string
          created_at?: string
          updated_at?: string
          confirmed_at?: string
          shipped_at?: string
          delivered_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "orders_buyer_id_fkey"
            columns: ["buyer_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "orders_seller_id_fkey"
            columns: ["seller_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      payment_methods: {
        Row: {
          id: string
          user_id: string
          method_type: string
          provider: string
          method_identifier: string
          display_name: string
          is_default: boolean
          is_active: boolean
          metadata: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          method_type: string
          provider: string
          method_identifier: string
          display_name?: string
          is_default?: boolean
          is_active?: boolean
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          method_type?: string
          provider?: string
          method_identifier?: string
          display_name?: string
          is_default?: boolean
          is_active?: boolean
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "payment_methods_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      user_sessions: {
        Row: {
          id: string
          user_id: string
          session_token: string
          device_info: Json
          ip_address: string
          user_agent: string
          is_active: boolean
          expires_at: string
          created_at: string
          last_accessed: string
        }
        Insert: {
          id?: string
          user_id: string
          session_token: string
          device_info?: Json
          ip_address?: string
          user_agent?: string
          is_active?: boolean
          expires_at: string
          created_at?: string
          last_accessed?: string
        }
        Update: {
          id?: string
          user_id?: string
          session_token?: string
          device_info?: Json
          ip_address?: string
          user_agent?: string
          is_active?: boolean
          expires_at?: string
          created_at?: string
          last_accessed?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_sessions_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      audit_logs: {
        Row: {
          id: string
          user_id: string
          action: string
          resource_type: string
          resource_id: string
          old_values: Json
          new_values: Json
          ip_address: string
          user_agent: string
          created_at: string
        }
        Insert: {
          id?: string
          user_id?: string
          action: string
          resource_type?: string
          resource_id?: string
          old_values?: Json
          new_values?: Json
          ip_address?: string
          user_agent?: string
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          action?: string
          resource_type?: string
          resource_id?: string
          old_values?: Json
          new_values?: Json
          ip_address?: string
          user_agent?: string
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "audit_logs_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      system_settings: {
        Row: {
          key: string
          value: Json
          description: string
          is_public: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          key?: string
          value: Json
          description?: string
          is_public?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          key?: string
          value: Json
          description?: string
          is_public?: boolean
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      locations: never
    }
  }
}
