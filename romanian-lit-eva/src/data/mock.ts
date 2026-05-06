import { Book, Review, ScoreEvent, User } from '../types';

export const mockBooks: Book[] = [
  {
    id: 'b1',
    isbn: '978-973-50-6844-3',
    title: 'Solenoid',
    author: 'Mircea Cărtărescu',
    publisher: 'Humanitas',
    year: 2015,
    coverUrl: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=600&auto=format&fit=crop',
    bayesianScore: 4.7,
    confidence: 0.95,
    reviewCount: 142,
    themes: ['existentialism', 'bucharest', 'surrealism'],
  },
  {
    id: 'b2',
    isbn: '978-973-46-7788-2',
    title: 'Nostalgia',
    author: 'Mircea Cărtărescu',
    publisher: 'Humanitas',
    year: 1993,
    coverUrl: 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?q=80&w=600&auto=format&fit=crop',
    bayesianScore: 4.5,
    confidence: 0.88,
    reviewCount: 95,
    themes: ['memory', 'dreams', 'childhood'],
  },
  {
    id: 'b3',
    isbn: '978-973-689-980-0',
    title: 'Maitreyi',
    author: 'Mircea Eliade',
    publisher: 'Editura Națională',
    year: 1933,
    coverUrl: 'https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=600&auto=format&fit=crop',
    bayesianScore: 4.3,
    confidence: 0.91,
    reviewCount: 210,
    themes: ['romance', 'india', 'orientalism'],
  },
  {
    id: 'b4',
    isbn: '978-973-46-2415-2',
    title: 'Poezii',
    author: 'Mihai Eminescu',
    publisher: 'Polirom',
    year: 1883,
    coverUrl: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?q=80&w=600&auto=format&fit=crop',
    bayesianScore: 4.9,
    confidence: 0.99,
    reviewCount: 1024,
    themes: ['romanticism', 'nature', 'love', 'philosophy'],
  },
  {
    id: 'b5',
    isbn: '978-973-103-605-7',
    title: 'Amintiri din copilărie',
    author: 'Ion Creangă',
    publisher: 'Arthur',
    year: 1892,
    coverUrl: 'https://images.unsplash.com/photo-1474932430478-367d16b99031?q=80&w=600&auto=format&fit=crop',
    bayesianScore: 4.5,
    confidence: 0.94,
    reviewCount: 540,
    themes: ['childhood', 'village life', 'humor'],
  },
  {
    id: 'b6',
    isbn: '978-973-50-4822-3',
    title: 'De ce iubim femeile',
    author: 'Mircea Cărtărescu',
    publisher: 'Humanitas',
    year: 2004,
    coverUrl: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?q=80&w=600&auto=format&fit=crop',
    bayesianScore: 3.9,
    confidence: 0.82,
    reviewCount: 110,
    themes: ['essays', 'love', 'observations'],
  }
];

export const mockReviews: Review[] = [
  {
    id: 'r1',
    bookId: 'b1',
    userId: 'u1',
    userName: 'Alexandru P.',
    rating: 5,
    text: 'O capodoperă absolută. Stilul lui Cărtărescu este inegalabil.',
    status: 'approved',
    createdAt: '2023-11-12T10:00:00Z',
    sentiment: 'positive',
    likes: 12
  },
  {
    id: 'r2',
    bookId: 'b3',
    userId: 'u2',
    userName: 'Maria V.',
    rating: 4.5,
    text: 'Foarte interesantă perspectiva asupra culturii indiene, dar uneori ritmul este lent.',
    status: 'approved',
    createdAt: '2024-01-05T14:30:00Z',
    sentiment: 'neutral',
    likes: 3
  },
  {
    id: 'r3',
    bookId: 'b5',
    userId: 'u3',
    userName: 'Mihai D.',
    rating: 4.5,
    text: 'O întoarcere nostalgică în copilărie! Umorul este la fel de proaspăt și azi.',
    status: 'pending',
    createdAt: '2024-03-20T09:15:00Z',
  },
  {
    id: 'r4',
    bookId: 'b1',
    userId: 'u4',
    userName: 'Elena C.',
    rating: 1,
    text: 'Prea lung și plictisitor. Nu recomand.',
    status: 'rejected',
    createdAt: '2024-02-14T18:45:00Z',
    sentiment: 'negative'
  }
];

export const mockAuditEvents: ScoreEvent[] = [
  {
    id: 'e1',
    bookId: 'b1',
    eventType: 'review_added',
    previousScore: 4.65,
    newScore: 4.7,
    timestamp: '2023-11-12T10:05:00Z',
    details: 'Score recalculated successfully using Bayesian update.'
  },
  {
    id: 'e2',
    bookId: 'b3',
    eventType: 'review_added',
    previousScore: 4.35,
    newScore: 4.3,
    timestamp: '2024-01-05T14:35:00Z',
    details: 'Review from user u2 added to distribution.'
  }
];
