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
export type SentimentLabel = 'pozitiv' | 'negativ' | 'neutru';

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
  preview_text?: string; // For review eligibility
  cover_url?: string;
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
  id: number;
  edition_id: number;
  content: string;
  rating?: number; // 1 to 5
  status: ReviewStatus;
  created_at: string;
  // Sentiment analysis fields
  sentiment_label?: SentimentLabel;
  sentiment_score?: number; // -1 to 1
  sentiment_confidence?: number; // 0 to 1
  // Gamification fields
  like_count: number;
  liked_by_user: boolean;
}

export interface ReviewCreate {
  edition_id: number;
  content: string;
  rating?: number;
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

export interface UnlockedBook {
  edition_id: number;
  book_title: string;
  publisher?: string;
  year?: number;
  unlocked_at: string;
  review_id: number;
}

export interface TopReview extends Review {
  reviewer_name: string;
}

export interface UnlockStatus {
  edition_id: number;
  is_unlocked: boolean;
}

export interface LikeResponse {
  message: string;
  like_count: number;
  unlocked_user_id?: number;
  locked_user_ids?: number[];
}

export interface PreviewBook {
  slug: string;
  title: string;
  author: string;
  pages: number;
  cover_url: string;
}

export interface PreviewBookReview {
  id: number;
  slug: string;
  user_id: number;
  username: string;
  content: string;
  rating?: number;
  status: string;
  created_at: string;
  sentiment_label?: SentimentLabel;
  sentiment_score?: number;
  sentiment_confidence?: number;
  like_count: number;
  liked_by_user: boolean;
}
