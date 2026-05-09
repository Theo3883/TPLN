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
  // Source tracking for crawler vs manual
  source?: 'manual' | 'crawler';
  crawler_name?: 'bookzone' | 'carturesti' | 'libris';
  imported_at?: string;
}

export type EditionSource = 'manual' | 'crawler';
export type CrawlerName = 'bookzone' | 'carturesti' | 'libris';

export interface Edition {
  id: number;
  book_id: number;
  isbn?: string;
  publisher?: string;
  year?: number;
  score?: number;
  confidence?: number;
  review_count: number;
  source: EditionSource;
  crawler_name?: CrawlerName;
  imported_at?: string;
  book?: {
    id: number;
    title: string;
  };
  authors?: Array<{
    id: number;
    name: string;
  }>;
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
