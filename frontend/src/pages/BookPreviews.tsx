/**
 * Book Previews Page — Grid of available book previews.
 * Each card links to its own detail page with the 10-page PDF.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Eye } from 'lucide-react';
import { motion } from 'motion/react';
import { listPreviewBooks, getPreviewBookCoverUrl } from '../lib/api';
import type { PreviewBook } from '../types';

export default function BookPreviews() {
  const [books, setBooks] = useState<PreviewBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const data = await listPreviewBooks();
        setBooks(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load books');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-12">
        <h1 className="font-serif text-4xl md:text-5xl font-light mb-3">Available Previews</h1>
        <p className="text-sm opacity-60 max-w-2xl">
          Explorează primele 10 pagini din fiecare carte. Scrie cea mai apreciată recenzie pe platforma
          noastră și deblochează cartea completă în secțiunea <strong>My Gift Books</strong>!
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-24">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#1a1a1a]"></div>
          <p className="mt-4 text-sm opacity-50">Se încarcă cărțile...</p>
        </div>
      )}

      {!loading && books.length === 0 && !error && (
        <div className="text-center py-24 border border-dashed border-[#1a1a1a]/20 rounded-2xl">
          <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-20" />
          <p className="font-serif italic opacity-50">Nu sunt cărți disponibile momentan.</p>
        </div>
      )}

      {/* Books Grid */}
      {!loading && books.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {books.map((book) => (
            <Link key={book.slug} to={`/book-previews/${book.slug}`}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="group cursor-pointer"
              >
                {/* Cover */}
                <div className="aspect-[3/4] bg-[#e8e4dc] rounded-2xl overflow-hidden shadow-lg border border-[#1a1a1a]/10 mb-4 relative">
                  <img
                    src={getPreviewBookCoverUrl(book.slug)}
                    alt={book.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                  {/* Hover overlay */}
                  <div className="absolute inset-0 bg-[#1a1a1a]/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <div className="px-5 py-2.5 bg-white text-[#1a1a1a] rounded-full text-xs uppercase tracking-widest font-bold flex items-center gap-2">
                      <Eye className="w-4 h-4" /> Deschide
                    </div>
                  </div>
                  {/* Badge */}
                  <div className="absolute top-3 right-3 px-2.5 py-1 bg-white/90 backdrop-blur-sm rounded-full text-[10px] uppercase tracking-widest font-bold">
                    {book.pages} pagini
                  </div>
                </div>

                {/* Info */}
                <h3 className="font-serif text-lg font-medium leading-tight mb-1 group-hover:opacity-70 transition-opacity">
                  {book.title}
                </h3>
                <p className="text-sm opacity-50">{book.author}</p>
              </motion.div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
