/**
 * BookPreviewDetail — Individual page for a preview book.
 * Shows cover, info, embedded 10-page PDF preview, and how to unlock the full book.
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, BookOpen, Eye, Gift, Lock, Send, Star, ShieldAlert, BadgeCheck } from 'lucide-react';
import { motion } from 'motion/react';
import {
  listPreviewBooks,
  getPreviewBookCoverUrl,
  getPreviewBookPdfUrl,
  getPreviewBookReviews,
  createPreviewBookReview,
} from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import StarRating from '../components/ui/StarRating';
import { SentimentBadge } from '../components/ui/SentimentBadge';
import type { PreviewBook, PreviewBookReview } from '../types';

export default function BookPreviewDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuth();
  const [book, setBook] = useState<PreviewBook | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPdf, setShowPdf] = useState(false);
  const [reviews, setReviews] = useState<PreviewBookReview[]>([]);
  const [reviewText, setReviewText] = useState('');
  const [rating, setRating] = useState(5);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const books = await listPreviewBooks();
        const found = books.find((b) => b.slug === slug);
        setBook(found || null);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    })();
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    (async () => {
      try {
        const data = await getPreviewBookReviews(slug);
        setReviews(data);
      } catch (err) {
        console.error(err);
      }
    })();
  }, [slug]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!slug) return;
    setSubmitError('');
    try {
      const newReview = await createPreviewBookReview(slug, {
        content: reviewText,
        rating,
      });
      setReviews((prev) => [newReview, ...prev]);
      setSubmitted(true);
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to submit review');
    }
  };

  if (loading) {
    return (
      <div className="text-center py-24">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#1a1a1a]"></div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center">
        <BookOpen className="w-16 h-16 mx-auto mb-6 opacity-20" />
        <p className="font-serif text-2xl italic opacity-50">Cartea nu a fost găsită.</p>
        <Link to="/book-previews" className="mt-6 inline-block text-sm underline opacity-60 hover:opacity-100">
          Înapoi la previzualizări
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link
        to="/book-previews"
        className="inline-flex items-center gap-2 text-[10px] uppercase tracking-widest opacity-60 hover:opacity-100 transition-opacity mb-12"
      >
        <ArrowLeft className="w-3 h-3" /> Înapoi la Previzualizări
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
        {/* Left — Cover */}
        <div className="lg:col-span-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="aspect-[3/4] bg-[#e8e4dc] rounded-2xl overflow-hidden shadow-xl border border-[#1a1a1a]/10 sticky top-28"
          >
            <img
              src={getPreviewBookCoverUrl(book.slug)}
              alt={book.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </motion.div>
        </div>

        {/* Right — Info & Actions */}
        <div className="lg:col-span-8 flex flex-col pt-4">
          <div className="mb-8">
            <h1 className="font-serif text-4xl md:text-5xl font-light leading-tight mb-3">
              {book.title}
            </h1>
            <p className="text-2xl font-serif italic opacity-70 mb-8">{book.author}</p>

            <div className="grid grid-cols-2 gap-8 py-6 border-y border-[#1a1a1a]/10">
              <div>
                <div className="text-[9px] uppercase tracking-widest opacity-50 mb-1">Previzualizare</div>
                <div className="font-medium text-sm">{book.pages} pagini</div>
              </div>
              <div>
                <div className="text-[9px] uppercase tracking-widest opacity-50 mb-1">Format</div>
                <div className="font-medium text-sm">PDF</div>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap gap-4 mb-12">
            <button
              onClick={() => setShowPdf(!showPdf)}
              className="flex items-center gap-2 px-6 py-3 bg-[#1a1a1a] text-white rounded-full text-xs uppercase tracking-widest font-bold hover:bg-[#1a1a1a]/90 transition-colors"
            >
              <Eye className="w-4 h-4" />
              {showPdf ? 'Ascunde Previzualizarea' : 'Citește Previzualizarea (10 pagini)'}
            </button>
          </div>

          {/* Embedded PDF Preview */}
          {showPdf && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mb-12 rounded-2xl overflow-hidden border border-[#1a1a1a]/10 shadow-lg"
            >
              <div className="bg-[#f5f2ed] px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BookOpen className="w-4 h-4 opacity-50" />
                  <span className="text-[10px] uppercase tracking-widest font-bold opacity-60">
                    Previzualizare — Primele {book.pages} pagini
                  </span>
                </div>
                <span className="text-[10px] uppercase tracking-widest opacity-40">
                  Doar pentru citire
                </span>
              </div>
              <div className="bg-[#525659]" style={{ height: '80vh' }}>
                <iframe
                  src={getPreviewBookPdfUrl(book.slug)}
                  className="w-full h-full border-0"
                  title={`Preview of ${book.title}`}
                />
              </div>
            </motion.div>
          )}

          {/* How to unlock */}
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200/50 rounded-2xl p-8 mb-12">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-amber-500 text-white rounded-full flex items-center justify-center shrink-0">
                <Gift className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-serif text-xl mb-2">Cum deblochezi cartea completă?</h3>
                <ol className="list-decimal list-inside space-y-2 text-sm opacity-70">
                  <li>Citește previzualizarea de mai sus (10 pagini)</li>
                  <li>Scrie o recenzie detaliată mai jos</li>
                  <li>
                    Dacă recenzia ta primește <strong>cele mai multe like-uri</strong>, deblochezi
                    cartea completă!
                  </li>
                  <li>
                    Cartea apare în{' '}
                    <Link to="/my-gift-books" className="underline font-medium">
                      My Gift Books
                    </Link>
                  </li>
                </ol>
              </div>
            </div>
          </div>

          {/* Submit Review */}
          {user ? (
            <div className="mb-16 bg-white p-8 rounded-[2rem] border border-[#1a1a1a]/10 shadow-sm relative overflow-hidden">
              <h3 className="font-serif text-2xl mb-6">Scrie o Recenzie</h3>

              {submitted ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <div className="w-16 h-16 bg-green-50 rounded-full border border-green-200 flex items-center justify-center mb-4 text-green-600">
                    <BadgeCheck className="w-8 h-8" />
                  </div>
                  <p className="font-serif text-xl mb-2">Recenzie Trimisă</p>
                  <p className="text-sm opacity-60 max-w-md">
                    Recenzia ta a fost publicată. Strânge like-uri pentru a debloca cartea completă!
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="flex flex-col gap-6 relative z-10">
                  <div className="flex flex-col gap-2">
                    <label className="text-[10px] uppercase tracking-widest font-medium opacity-70">
                      Evaluare
                    </label>
                    <StarRating rating={rating} interactive size="lg" onChange={setRating} className="mb-2" />
                    <div className="flex justify-between text-xs font-mono opacity-50">
                      <span>Slab</span>
                      <span className="text-[#1a1a1a] font-bold text-sm tracking-widest">{rating} Stele</span>
                      <span>Excelent</span>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <label className="text-[10px] uppercase tracking-widest font-medium opacity-70">
                      Recenzie
                    </label>
                    <textarea
                      rows={4}
                      required
                      minLength={20}
                      value={reviewText}
                      onChange={(e) => setReviewText(e.target.value)}
                      className="w-full p-4 bg-[#f5f2ed]/50 border border-[#1a1a1a]/10 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#1a1a1a] resize-none text-sm font-serif"
                      placeholder="Scrie o recenzie detaliată după ce ai citit previzualizarea (minim 20 caractere)..."
                    ></textarea>
                  </div>

                  {submitError && (
                    <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                      {submitError}
                    </div>
                  )}

                  <div className="flex justify-between items-center mt-2">
                    <div className="flex items-center gap-2 text-[10px] opacity-60">
                      <ShieldAlert className="w-3 h-3" />
                      Câștigă cartea pentru cea mai bună recenzie!
                    </div>
                    <button
                      type="submit"
                      className="px-6 py-3 bg-[#1a1a1a] text-white rounded-full text-[11px] uppercase tracking-widest flex items-center gap-2 hover:bg-[#1a1a1a]/90 transition-colors"
                    >
                      Trimite <Send className="w-3 h-3" />
                    </button>
                  </div>
                </form>
              )}

              <div className="absolute -right-12 -top-12 opacity-[0.03] pointer-events-none">
                <ShieldAlert className="w-64 h-64" />
              </div>
            </div>
          ) : (
            <div className="bg-[#1a1a1a]/5 border border-[#1a1a1a]/10 rounded-2xl p-8 text-center mb-12">
              <Lock className="w-10 h-10 mx-auto mb-4 opacity-20" />
              <p className="font-serif text-lg mb-4">Autentifică-te pentru a scrie o recenzie</p>
              <p className="text-sm opacity-50 mb-6">
                Trebuie să fii logat pentru a scrie recenzii și a debloca cărți.
              </p>
              <div className="flex gap-4 justify-center">
                <Link
                  to="/login"
                  className="px-6 py-3 bg-[#1a1a1a] text-white rounded-full text-xs uppercase tracking-widest font-bold"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-6 py-3 border border-[#1a1a1a] rounded-full text-xs uppercase tracking-widest font-bold"
                >
                  Register
                </Link>
              </div>
            </div>
          )}

          {/* Reviews List */}
          <div>
            <h3 className="font-serif text-2xl mb-8 flex items-center justify-between">
              Recenzii
              <span className="text-[10px] font-sans uppercase tracking-widest opacity-50 bg-[#1a1a1a]/5 px-3 py-1 rounded-full text-[#1a1a1a]">
                NLP Analyzed
              </span>
            </h3>

            <div className="flex flex-col gap-6">
              {reviews.length > 0 ? (
                reviews.map((review) => (
                  <div
                    key={review.id}
                    className="p-6 border border-[#1a1a1a]/10 rounded-2xl bg-white/50 relative overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-[#1a1a1a]/10 flex items-center justify-center font-serif italic text-xs">
                          {review.username[0]?.toUpperCase() || 'U'}
                        </div>
                        <div className="flex flex-col">
                          <span className="text-sm font-medium">{review.username}</span>
                          <span className="text-[10px] opacity-50 font-mono">
                            {new Date(review.created_at).toLocaleDateString('ro-RO')}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {review.rating && <StarRating rating={review.rating} size="sm" />}
                        {review.sentiment_label && (
                          <SentimentBadge
                            label={review.sentiment_label}
                            score={review.sentiment_score}
                            confidence={review.sentiment_confidence}
                            showDetails={true}
                          />
                        )}
                      </div>
                    </div>
                    <p className="font-serif text-sm leading-relaxed opacity-80">{review.content}</p>
                    <div className="mt-3 flex items-center gap-2 text-xs opacity-50">
                      <Star className="w-3 h-3" />
                      {review.like_count} {review.like_count === 1 ? 'like' : 'likes'}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12 border border-dashed border-[#1a1a1a]/20 rounded-2xl">
                  <p className="font-serif italic opacity-50">Nicio recenzie încă. Fii primul!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
