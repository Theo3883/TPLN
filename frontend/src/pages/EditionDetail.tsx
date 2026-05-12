import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../lib/api';
import { backendReviewToReview, editionToBook } from '../lib/transformers';
import { ArrowLeft, Star, Send, Fingerprint, ShieldAlert, BadgeCheck, BookOpen, ThumbsUp, X, ChevronLeft, ChevronRight, Gift } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

import StarRating from '../components/ui/StarRating';
import { SentimentBadge } from '../components/ui/SentimentBadge';
import { LikeButton } from '../components/ui/LikeButton';
import type { Edition, Review } from '../types';

export default function EditionDetail() {
  const { id } = useParams<{ id: string }>();
  const [book, setBook] = useState<any | null>(null);
  const [edition, setEdition] = useState<Edition | null>(null);
  const [localReviews, setLocalReviews] = useState<Review[]>([]);

  useEffect(() => {
    let mounted = true;
    if (!id) return;
    (async () => {
      try {
        const ed = await api.getEdition(id);
        if (!mounted) return;
        const editionData = Array.isArray(ed) ? ed[0] : ed;
        setEdition(editionData);
        setBook(editionToBook(editionData));
      } catch (err) {
        console.error(err);
      }

      try {
        const reviews = await api.getEditionReviews(id);
        if (!mounted) return;
        const list = Array.isArray(reviews) ? reviews : reviews.items ?? [];
        const approved = list.filter((r: any) => (r.status ?? 'pending') === 'approved');
        setLocalReviews(approved);
      } catch (err) {
        console.error(err);
      }
    })();
    return () => { mounted = false; };
  }, [id]);

  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  if (!book) {
    return <div className="text-center py-24 font-serif text-2xl italic">Edition not found.</div>;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    (async () => {
      try {
        const newReview = await api.createReview({ 
          edition_id: Number(id), 
          content: reviewText, 
          rating 
        });
        // Add new review to the list
        setLocalReviews(prev => [newReview, ...prev]);
      } catch (err: any) {
        console.error(err);
        alert(err.message || 'Failed to submit review');
        setSubmitted(false);
      }
    })();
  };

  const handleLike = (reviewId: string) => {
    setLocalReviews(prev => prev.map(r => r.id === reviewId ? { ...r, likes: (r.likes || 0) + 1 } : r));
  };

  // Mock content for the first 10 pages
  const mockPages = Array.from({ length: 10 }, (_, i) => ({
    number: i + 1,
    content: `Aceasta este pagina ${i + 1} de text din ediția "${book.title}". În această secțiune, autorul explorează teme complexe legate de ${book.themes.join(', ')}. Textul curge cu o eleganță deosebită, invitând cititorul să se piardă în universul creat de ${book.author}. Proza este densă, plină de subînțelesuri și metafore care îmbogățesc experiența lecturii.`
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link to="/catalog" className="inline-flex items-center gap-2 text-[10px] uppercase tracking-widest opacity-60 hover:opacity-100 transition-opacity mb-12">
        <ArrowLeft className="w-3 h-3" /> Back to Catalog
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
        {/* Left Column: Cover & Stats */}
        <div className="lg:col-span-4 flex flex-col">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="aspect-[3/4] bg-[#e8e4dc] rounded-2xl overflow-hidden shadow-xl border border-[#1a1a1a]/10 mb-8 sticky top-28 group"
          >
            {book.coverUrl && <img src={book.coverUrl} className="w-full h-full object-cover mix-blend-multiply" alt={book.title} onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />}
            <div className="absolute inset-0 bg-[#1a1a1a]/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
               <button 
                onClick={() => setIsPreviewOpen(true)}
                className="px-6 py-3 bg-white text-[#1a1a1a] rounded-full text-xs uppercase tracking-widest font-bold flex items-center gap-2 hover:scale-105 transition-transform"
               >
                 <BookOpen className="w-4 h-4" /> Read Preview
               </button>
            </div>
          </motion.div>

          <div className="bg-[#1a1a1a]/5 p-6 rounded-2xl border border-[#1a1a1a]/10">
            <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold mb-4 flex items-center gap-2">
              <Gift className="w-3.5 h-3.5 text-amber-600" /> Current Contest
            </h4>
            <p className="text-sm font-serif italic mb-4 leading-relaxed">
              "The most appreciated review (most likes) for this edition will receive a physical copy of the book courtesy of our partners."
            </p>
            <div className="flex justify-between items-center text-[10px] uppercase tracking-widest opacity-60">
              <span>Ending in: 12 days</span>
              <span className="font-bold">Active</span>
            </div>
          </div>
        </div>

        {/* Right Column: Details & Reviews */}
        <div className="lg:col-span-8 flex flex-col pt-4">
          <div className="mb-12">
            <div className="flex justify-between items-start mb-4">
              <h1 className="font-serif text-5xl md:text-6xl font-light leading-tight">{book.title}</h1>
              <button 
                onClick={() => setIsPreviewOpen(true)}
                className="hidden md:flex items-center gap-2 px-4 py-2 border border-[#1a1a1a] rounded-full text-[10px] uppercase tracking-widest hover:bg-[#1a1a1a] hover:text-white transition-all"
              >
                <BookOpen className="w-3.5 h-3.5" /> Preview
              </button>
            </div>
            <p className="text-2xl font-serif italic opacity-70 mb-8">{book.author}</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 py-8 border-y border-[#1a1a1a]/10">
               <div>
                  <div className="text-[9px] uppercase tracking-widest opacity-50 mb-1">Publisher</div>
                  <div className="font-medium text-sm">{book.publisher}</div>
               </div>
               <div>
                  <div className="text-[9px] uppercase tracking-widest opacity-50 mb-1">Year</div>
                  <div className="font-mono text-sm">{book.year}</div>
               </div>
               <div>
                  <div className="text-[9px] uppercase tracking-widest opacity-50 mb-1">ISBN</div>
                  <div className="font-mono text-xs mt-0.5">{book.isbn}</div>
               </div>
               <div>
                  <div className="text-[9px] uppercase tracking-widest opacity-50 mb-1">Themes</div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {book.themes.map(t => (
                      <span key={t} className="text-[9px] uppercase tracking-wider px-1.5 py-0.5 bg-[#1a1a1a]/5 rounded-sm">{t}</span>
                    ))}
                  </div>
               </div>
            </div>
            
            <div className="flex items-center gap-6 mt-8 bg-[#1a1a1a] text-white p-6 rounded-2xl">
               <div className="shrink-0">
                  <StarRating rating={book.bayesianScore} size="lg" className="flex-col gap-2 scale-110" />
               </div>
               <div className="flex flex-col">
                 <span className="text-sm font-medium tracking-wide">Bayesian Performance</span>
                 <span className="text-xs opacity-60 mt-1 flex items-center gap-1"><Fingerprint className="w-3 h-3"/> {book.confidence.toFixed(2)} confidence index</span>
                 <span className="text-xs opacity-60 flex items-center gap-1 mt-0.5"><Star className="w-3 h-3"/> Based on {book.reviewCount} total reviews</span>
               </div>
            </div>
          </div>

          {/* Submit Review */}
          <div className="mb-16 bg-white p-8 rounded-[2rem] border border-[#1a1a1a]/10 shadow-sm relative overflow-hidden">
            <h3 className="font-serif text-2xl mb-6">Evaluate Edition</h3>
            
            {submitted ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <div className="w-16 h-16 bg-green-50 rounded-full border border-green-200 flex items-center justify-center mb-4 text-green-600">
                  <BadgeCheck className="w-8 h-8" />
                </div>
                <p className="font-serif text-xl mb-2">Evaluation Submitted</p>
                <p className="text-sm opacity-60 max-w-md">Your review is in the moderation queue. It will update the Bayesian score upon approval.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="flex flex-col gap-6 relative z-10">
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] uppercase tracking-widest font-medium opacity-70">Rate This Edition</label>
                  <StarRating 
                    rating={rating} 
                    interactive 
                    size="lg" 
                    onChange={setRating} 
                    className="mb-2"
                  />
                  <div className="flex justify-between text-xs font-mono opacity-50">
                    <span>Poor</span>
                    <span className="text-[#1a1a1a] font-bold text-sm tracking-widest">{rating} Stars</span>
                    <span>Excellent</span>
                  </div>
                </div>
                
                <div className="flex flex-col gap-2">
                   <label className="text-[10px] uppercase tracking-widest font-medium opacity-70">Review Text</label>
                   <textarea 
                     rows={4}
                     required
                     value={reviewText}
                     onChange={(e) => setReviewText(e.target.value)}
                     className="w-full p-4 bg-[#f5f2ed]/50 border border-[#1a1a1a]/10 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#1a1a1a] resize-none text-sm font-serif"
                     placeholder="Share your detailed analysis after reading the preview..."
                   ></textarea>
                </div>
                
                <div className="flex justify-between items-center mt-2">
                  <div className="flex items-center gap-2 text-[10px] opacity-60">
                    <ShieldAlert className="w-3 h-3" />
                    Win the book for the best review!
                  </div>
                  <button type="submit" className="px-6 py-3 bg-[#1a1a1a] text-white rounded-full text-[11px] uppercase tracking-widest flex items-center gap-2 hover:bg-[#1a1a1a]/90 transition-colors">
                    Submit <Send className="w-3 h-3" />
                  </button>
                </div>
              </form>
            )}
            
            {/* Background pattern */}
            <div className="absolute -right-12 -top-12 opacity-[0.03] pointer-events-none">
              <ShieldAlert className="w-64 h-64" />
            </div>
          </div>

          {/* Approved Reviews */}
          <div>
            <h3 className="font-serif text-2xl mb-8 flex items-center justify-between">
              Public Reviews
              <span className="text-[10px] font-sans uppercase tracking-widest opacity-50 bg-[#1a1a1a]/5 px-3 py-1 rounded-full text-[#1a1a1a]">
                NLP Analyzed
              </span>
            </h3>
            
            <div className="flex flex-col gap-6">
              {localReviews.length > 0 ? localReviews.map(review => (
                <div key={review.id} className="p-6 border border-[#1a1a1a]/10 rounded-2xl bg-white/50 relative overflow-hidden group/card shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-4 relative z-10">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-[#1a1a1a]/10 flex items-center justify-center font-serif italic text-xs">
                        R
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-medium">Reviewer</span>
                        <span className="text-[10px] opacity-50 font-mono">{new Date(review.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
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
                  </div>
                  <p className="font-serif text-sm leading-relaxed opacity-80 relative z-10">{review.content}</p>
                </div>
              )) : (
                <div className="text-center py-12 border border-dashed border-[#1a1a1a]/20 rounded-2xl">
                   <p className="font-serif italic opacity-50">No approved reviews yet.</p>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>

      {/* Preview Modal */}
      <AnimatePresence>
        {isPreviewOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center px-4 sm:px-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsPreviewOpen(false)}
              className="absolute inset-0 bg-[#1a1a1a]/60 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ opacity: 0, y: 100, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 100 }}
              className="relative w-full max-w-4xl bg-white rounded-[2rem] shadow-2xl overflow-hidden flex flex-col h-[85vh]"
            >
              <div className="p-6 border-b border-[#1a1a1a]/10 flex justify-between items-center bg-[#f5f2ed]">
                 <div className="flex items-center gap-4">
                    <div className="w-10 h-14 bg-[#1a1a1a] rounded overflow-hidden">
                       {book.coverUrl && <img src={book.coverUrl} className="w-full h-full object-cover mix-blend-multiply opacity-80" alt=""/>}
                    </div>
                    <div>
                       <h2 className="font-serif text-xl font-medium">{book.title}</h2>
                       <p className="text-[10px] uppercase tracking-widest opacity-50">10 Page Preview • {book.author}</p>
                    </div>
                 </div>
                 <button 
                  onClick={() => setIsPreviewOpen(false)}
                  className="p-2 hover:bg-[#1a1a1a]/5 rounded-full transition-colors"
                 >
                   <X className="w-6 h-6" />
                 </button>
              </div>

              <div className="flex-1 overflow-y-auto p-12 md:px-24 md:py-16 bg-[#fcfbf9]">
                 <div className="max-w-prose mx-auto">
                    <div className="text-[10px] uppercase tracking-[0.3em] font-medium opacity-30 mb-8 border-b border-[#1a1a1a]/10 pb-2">
                       Page {currentPage} of 10
                    </div>
                    <motion.div 
                      key={currentPage}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="font-serif text-xl leading-relaxed text-[#1a1a1a]/80"
                    >
                       <p className="first-letter:text-5xl first-letter:font-serif first-letter:float-left first-letter:mr-3 first-letter:mt-1 first-letter:font-light italic">
                         {mockPages[currentPage - 1].content}
                       </p>
                       <p className="mt-8">
                         Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
                       </p>
                       <p className="mt-6">
                         Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris.
                       </p>
                    </motion.div>
                 </div>
              </div>

              <div className="p-6 border-t border-[#1a1a1a]/10 flex justify-between items-center bg-white">
                 <div className="flex gap-2">
                    <button 
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                      disabled={currentPage === 1}
                      className="p-3 border border-[#1a1a1a]/10 rounded-full hover:bg-[#1a1a1a] hover:text-white disabled:opacity-20 disabled:hover:bg-transparent disabled:hover:text-[#1a1a1a] transition-all"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                    <button 
                      onClick={() => setCurrentPage(prev => Math.min(10, prev + 1))}
                      disabled={currentPage === 10}
                      className="p-3 border border-[#1a1a1a]/10 rounded-full hover:bg-[#1a1a1a] hover:text-white disabled:opacity-20 disabled:hover:bg-transparent disabled:hover:text-[#1a1a1a] transition-all"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                 </div>
                 
                 <div className="flex items-center gap-4">
                    <span className="text-xs font-mono opacity-50">Done reading?</span>
                    <button 
                      onClick={() => {
                        setIsPreviewOpen(false);
                        const reviewSection = document.querySelector('form');
                        reviewSection?.scrollIntoView({ behavior: 'smooth' });
                      }}
                      className="px-6 py-3 bg-[#1a1a1a] text-white rounded-full text-xs uppercase tracking-widest font-bold hover:scale-105 transition-transform"
                    >
                      Write Review
                    </button>
                 </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

const TrophyIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/></svg>
);

