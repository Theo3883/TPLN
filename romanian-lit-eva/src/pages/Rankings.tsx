import { useState } from 'react';
import { Link } from 'react-router-dom';
import { mockBooks, mockAuditEvents } from '../data/mock';
import { Trophy, TrendingUp, Info, FileStack, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

import StarRating from '../components/ui/StarRating';

export default function Rankings() {
  const [showAudit, setShowAudit] = useState(false);
  const sortedBooks = [...mockBooks].sort((a, b) => b.bayesianScore - a.bayesianScore);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="max-w-3xl mx-auto text-center mb-16">
        <h1 className="font-serif text-5xl mb-6 font-light">Global Rankings</h1>
        <p className="text-sm opacity-70 leading-relaxed font-serif">
          Scores are calculated using a Bayesian shrinkage model. This prevents editions with a small volume of extreme reviews from dominating the top positions, ensuring a transparent and stable evaluation.
        </p>
        <button 
          onClick={() => setShowAudit(!showAudit)}
          className="mt-6 px-4 py-2 border border-[#1a1a1a]/20 rounded-full text-[10px] uppercase tracking-widest font-medium hover:bg-[#1a1a1a]/5 transition-colors inline-flex items-center gap-2"
        >
          <FileStack className="w-3 h-3" />
          {showAudit ? 'Hide Audit Trail' : 'View Audit Trail'}
        </button>
      </div>

      <AnimatePresence mode="wait">
        {showAudit ? (
          <motion.div 
            key="audit"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mb-16 bg-white p-8 rounded-2xl border border-[#1a1a1a]/10 max-w-4xl mx-auto"
          >
            <div className="flex items-center gap-3 mb-8 border-b border-[#1a1a1a]/10 pb-4">
              <FileStack className="w-5 h-5 opacity-60" />
              <h2 className="font-serif text-2xl">Score Audit Trail</h2>
            </div>
            
            <div className="space-y-6">
              {mockAuditEvents.map((event) => {
                const book = mockBooks.find(b => b.id === event.bookId);
                return (
                  <div key={event.id} className="flex gap-6 pb-6 border-b border-[#1a1a1a]/5 last:border-0 last:pb-0">
                    <div className="w-12 text-[10px] uppercase tracking-widest opacity-50 pt-1">
                      {new Date(event.timestamp).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">{book?.title}</span>
                        <span className="text-[10px] px-2 py-0.5 bg-[#1a1a1a]/5 rounded-sm font-mono">{event.eventType}</span>
                      </div>
                      <p className="text-xs opacity-60 font-serif leading-relaxed mb-3">{event.details}</p>
                      <div className="flex items-center gap-4 text-xs font-mono">
                        <span className="opacity-50 line-through">{event.previousScore.toFixed(2)}</span>
                        <ArrowRight className="w-3 h-3 opacity-30" />
                        <span className="font-bold">{event.newScore.toFixed(2)}</span>
                        <span className="text-[9px] uppercase tracking-widest bg-green-50 text-green-700 px-2 py-0.5 rounded-full ml-2">Updated</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        ) : (
          <motion.div key="rankings" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            {/* Table */}
            <div className="bg-white border border-[#1a1a1a]/10 rounded-2xl shadow-sm overflow-hidden">
              <div className="grid grid-cols-12 gap-4 border-b border-[#1a1a1a]/10 bg-[#1a1a1a]/5 p-4 text-[10px] uppercase tracking-widest font-medium opacity-60">
                <div className="col-span-1 text-center">Rank</div>
                <div className="col-span-5">Edition</div>
                <div className="col-span-2 text-center">Reviews</div>
                <div className="col-span-2 text-center flex items-center justify-center gap-1">Confidence <Info className="w-3 h-3"/></div>
                <div className="col-span-2 text-right pr-4">Bayesian Score</div>
              </div>

              {sortedBooks.map((book, index) => (
                <Link 
                  to={`/edition/${book.id}`} 
                  key={book.id}
                  className="grid grid-cols-12 gap-4 p-4 border-b border-[#1a1a1a]/5 last:border-0 items-center hover:bg-[#1a1a1a]/[0.02] transition-colors"
                >
                  <div className="col-span-1 text-center flex justify-center">
                    {index < 3 ? (
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-sm
                        ${index === 0 ? 'bg-amber-100 text-amber-700 border border-amber-200' : 
                          index === 1 ? 'bg-slate-100 text-slate-700 border border-slate-200' : 
                          'bg-orange-50 text-orange-800 border border-orange-200'}`}
                      >
                        {index + 1}
                      </div>
                    ) : (
                      <div className="w-8 h-8 flex items-center justify-center font-mono text-sm opacity-40">
                        {index + 1}
                      </div>
                    )}
                  </div>
                  
                  <div className="col-span-5 flex items-center gap-4">
                    <div className="w-10 h-14 bg-[#e8e4dc] rounded shadow-sm overflow-hidden hidden sm:block">
                      {book.coverUrl && <img src={book.coverUrl} className="w-full h-full object-cover mix-blend-multiply" alt=""/>}
                    </div>
                    <div>
                      <h3 className="font-serif text-lg font-medium tracking-tight mb-0.5">{book.title}</h3>
                      <p className="text-xs opacity-60">{book.author}</p>
                    </div>
                  </div>
                  
                  <div className="col-span-2 text-center font-serif italic text-sm">
                    {book.reviewCount}
                  </div>
                  
                  <div className="col-span-2 text-center flex justify-center">
                    <div className="flex flex-col items-center">
                      <div className="w-16 h-1.5 bg-[#1a1a1a]/10 rounded-full overflow-hidden mb-1">
                        <div 
                          className="h-full bg-[#1a1a1a]" 
                          style={{ width: `${book.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-[9px] font-mono opacity-60">{book.confidence.toFixed(2)}</span>
                    </div>
                  </div>
                  
                  <div className="col-span-2 text-right pr-4">
                    <StarRating rating={book.bayesianScore} size="sm" className="justify-end" />
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
