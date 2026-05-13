/**
 * My Gift Books — Shows books unlocked by having the most-liked review.
 * Requires login. Links to the full PDF download for each unlocked book.
 */

import { useState, useEffect } from 'react';
import { Gift, BookOpen, Lock, Download } from 'lucide-react';
import { motion } from 'motion/react';
import { useAuth } from '../contexts/AuthContext';
import { getUnlockedBooks, getPreviewBookCoverUrl, getFullBookPdfUrl, listPreviewBooks } from '../lib/api';
import type { UnlockedBook, PreviewBook } from '../types';
import { Link } from 'react-router-dom';

export default function MyGiftBooks() {
  const { user } = useAuth();
  const [unlocked, setUnlocked] = useState<UnlockedBook[]>([]);
  const [previewBooks, setPreviewBooks] = useState<PreviewBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const [unlockedData, previewData] = await Promise.all([
          getUnlockedBooks(),
          listPreviewBooks(),
        ]);
        setUnlocked(unlockedData);
        setPreviewBooks(previewData);
      } catch (err: any) {
        setError(err.message || 'Failed to load gift books');
      } finally {
        setLoading(false);
      }
    })();
  }, [user]);

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
        <Lock className="w-16 h-16 mx-auto mb-6 opacity-20" />
        <h1 className="font-serif text-3xl mb-4">My Gift Books</h1>
        <p className="text-sm opacity-60 mb-8 max-w-md mx-auto">
          Trebuie să fii autentificat pentru a vedea cărțile deblocate. Scrie cea mai apreciată
          recenzie pentru a câștiga o carte!
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            to="/login"
            className="px-6 py-3 bg-[#1a1a1a] text-white rounded-full text-xs uppercase tracking-widest font-bold hover:scale-105 transition-transform"
          >
            Autentificare
          </Link>
          <Link
            to="/register"
            className="px-6 py-3 border border-[#1a1a1a] rounded-full text-xs uppercase tracking-widest font-bold hover:bg-[#1a1a1a] hover:text-white transition-all"
          >
            Înregistrare
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-12">
        <div className="flex items-center gap-3 mb-3">
          <Gift className="w-8 h-8 text-amber-600" />
          <h1 className="font-serif text-4xl md:text-5xl font-light">My Gift Books</h1>
        </div>
        <p className="text-sm opacity-60 max-w-2xl">
          Cărțile pe care le-ai deblocat prin recenziile tale apreciate. Poți descărca versiunea
          completă a fiecărei cărți.
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
          <p className="mt-4 text-sm opacity-50">Se încarcă...</p>
        </div>
      )}

      {!loading && unlocked.length === 0 && !error && (
        <div className="text-center py-16 border border-dashed border-[#1a1a1a]/20 rounded-2xl">
          <Gift className="w-16 h-16 mx-auto mb-6 opacity-15" />
          <p className="font-serif text-2xl italic opacity-50 mb-4">Nicio carte deblocată încă</p>
          <p className="text-sm opacity-40 max-w-md mx-auto mb-8">
            Scrie recenzii pe paginile edițiilor din catalog. Dacă recenzia ta primește cele mai
            multe like-uri, deblochezi cartea completă!
          </p>
          <Link
            to="/book-previews"
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#1a1a1a] text-white rounded-full text-xs uppercase tracking-widest font-bold hover:scale-105 transition-transform"
          >
            <BookOpen className="w-4 h-4" /> Vezi Previzualizări
          </Link>
        </div>
      )}

      {/* Unlocked Books Grid */}
      {!loading && unlocked.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {unlocked.map((book, i) => {
            // Try to match with a preview book for cover
            const matchedPreview = previewBooks.find(
              (pb) => book.book_title.toLowerCase().includes(pb.title.toLowerCase().split(' ')[0])
            );

            return (
              <motion.div
                key={book.edition_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="bg-white rounded-2xl border border-[#1a1a1a]/10 overflow-hidden shadow-sm hover:shadow-lg transition-shadow"
              >
                {/* Cover */}
                <div className="aspect-[3/4] bg-[#e8e4dc] relative overflow-hidden">
                  {matchedPreview ? (
                    <img
                      src={getPreviewBookCoverUrl(matchedPreview.slug)}
                      alt={book.book_title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <BookOpen className="w-16 h-16 opacity-20" />
                    </div>
                  )}
                  {/* Unlocked badge */}
                  <div className="absolute top-3 right-3 px-3 py-1.5 bg-amber-500 text-white rounded-full text-[10px] uppercase tracking-widest font-bold flex items-center gap-1.5">
                    <Gift className="w-3 h-3" /> Unlocked
                  </div>
                </div>

                {/* Info */}
                <div className="p-5">
                  <h3 className="font-serif text-lg font-medium mb-1">{book.book_title}</h3>
                  {book.publisher && (
                    <p className="text-xs opacity-50 mb-1">{book.publisher}</p>
                  )}
                  {book.year && (
                    <p className="text-xs opacity-40 mb-3">{book.year}</p>
                  )}
                  <p className="text-[10px] uppercase tracking-widest opacity-40 mb-4">
                    Deblocat: {new Date(book.unlocked_at).toLocaleDateString('ro-RO')}
                  </p>

                  {matchedPreview && (
                    <a
                      href={getFullBookPdfUrl(matchedPreview.slug)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#1a1a1a] text-white rounded-full text-xs uppercase tracking-widest font-bold hover:bg-[#1a1a1a]/90 transition-colors"
                    >
                      <Download className="w-4 h-4" /> Descarcă PDF
                    </a>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Preview Books Section — show available previews too */}
      {!loading && previewBooks.length > 0 && (
        <div className="mt-16">
          <h2 className="font-serif text-2xl mb-6 flex items-center gap-3">
            <BookOpen className="w-5 h-5 opacity-40" />
            Cărți disponibile pentru previzualizare
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {previewBooks.map((pb) => {
              const isUnlocked = unlocked.some(
                (u) => u.book_title.toLowerCase().includes(pb.title.toLowerCase().split(' ')[0])
              );
              return (
                <Link
                  key={pb.slug}
                  to="/book-previews"
                  className="group flex flex-col items-center text-center"
                >
                  <div className="w-full aspect-[3/4] bg-[#e8e4dc] rounded-xl overflow-hidden border border-[#1a1a1a]/10 mb-2 relative">
                    <img
                      src={getPreviewBookCoverUrl(pb.slug)}
                      alt={pb.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    />
                    {isUnlocked && (
                      <div className="absolute top-2 right-2 w-6 h-6 bg-amber-500 text-white rounded-full flex items-center justify-center">
                        <Gift className="w-3 h-3" />
                      </div>
                    )}
                  </div>
                  <p className="text-xs font-medium opacity-70 line-clamp-2">{pb.title}</p>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
