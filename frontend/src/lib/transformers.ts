import type { Book, Review } from '../types';

export function editionToBook(edition: any): Book {
  const book = edition?.book || {};
  const authors = (edition?.authors || []).map((a: any) => a.name).join(', ');

  return {
    id: String(edition.id ?? book.id ?? ''),
    isbn: edition.isbn ?? edition.isbn13 ?? '',
    title: book.title ?? edition.title ?? '',
    author: authors || book.author || 'Unknown',
    publisher: edition.publisher ?? book.publisher ?? '',
    year: edition.year ?? book.year ?? 0,
    coverUrl: edition.cover_url ?? edition.coverUrl ?? book.coverUrl ?? undefined,
    bayesianScore: Number(edition.score ?? edition.bayesian_score ?? 0),
    confidence: Number(edition.confidence ?? 0),
    reviewCount: Number(edition.review_count ?? edition.reviews_count ?? 0),
    themes: edition.themes ?? book.themes ?? [],
  } as Book;
}

export function backendReviewToReview(r: any): Review {
  return {
    id: String(r.id),
    bookId: String(r.edition_id ?? r.book_id ?? r.bookId ?? ''),
    userId: String(r.reviewer_id ?? r.user_id ?? ''),
    userName: r.reviewer_name ?? r.user_name ?? r.userName ?? 'Anonymous',
    rating: Number(r.rating ?? 0),
    text: r.content ?? r.text ?? '',
    status: (r.status ?? 'pending') as Review['status'],
    createdAt: r.created_at ?? r.createdAt ?? new Date().toISOString(),
    sentiment: r.sentiment_label ?? undefined,
    likes: r.likes ?? undefined,
  } as Review;
}

export function editionsToBooks(list: any[]): Book[] {
  return (list || []).map(editionToBook);
}
