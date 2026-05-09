export interface Book {
  id: string;
  isbn: string;
  title: string;
  author: string;
  publisher: string;
  year: number;
  coverUrl?: string;
  bayesianScore: number;
  confidence: number;
  reviewCount: number;
  themes: string[];
}

export type ReviewStatus = 'pending' | 'approved' | 'rejected';

export interface Review {
  id: string;
  bookId: string;
  userId: string;
  userName: string;
  rating: number; // 1 to 5
  text: string;
  status: ReviewStatus;
  createdAt: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  likes?: number;
}

export interface ScoreEvent {
  id: string;
  bookId: string;
  eventType: 'review_added' | 'review_rejected' | 'recalculation';
  previousScore: number;
  newScore: number;
  timestamp: string;
  details: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  bio?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
