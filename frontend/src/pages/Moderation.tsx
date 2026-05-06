import { useState, useEffect } from 'react';
import { useEditions } from '../lib/useApi';
import api from '../lib/api';
import { Shield, Check, X, Search, Filter } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import StarRating from '../components/ui/StarRating';

export default function Moderation() {
  const { data: books = [] } = useEditions(200);
  const [queue, setQueue] = useState<any[]>([]);

  useEffect(() => {
    let mounted = true;
    api.listPendingReviews()
      .then((res: any) => {
        if (!mounted) return;
        const list = Array.isArray(res) ? res : res.items ?? [];
        setQueue(list);
      })
      .catch(() => {
        setQueue([]);
      });
    return () => { mounted = false; };
  }, []);

  const handleDecision = async (id: string, decision: 'approved' | 'rejected') => {
    try {
      if (decision === 'approved') await api.approveReview(id);
      else await api.rejectReview(id);
      setQueue(prev => prev.filter(r => String(r.id) !== String(id)));
    } catch (err) {
      // ignore for now; UI could show error
      console.error(err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="flex flex-col md:flex-row justify-between items-end mb-12">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#1a1a1a]/5 rounded-full text-[10px] uppercase tracking-widest text-red-600 font-medium mb-4">
            <Shield className="w-3 h-3" /> Admin Area
          </div>
          <h1 className="font-serif text-4xl mb-2 font-light">Moderation Workspace</h1>
          <p className="text-sm opacity-60">Review pending evaluations for platform integrity.</p>
        </div>
        <div className="mt-6 md:mt-0 px-4 py-2 bg-[#1a1a1a] text-white rounded-lg text-sm font-mono flex items-center gap-3">
          Queue Size <span className="px-2 py-0.5 bg-white/20 rounded">{queue.length}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="col-span-1 border-r border-[#1a1a1a]/10 pr-8">
           <h3 className="font-serif text-lg mb-6">Filters</h3>
           <div className="space-y-4 text-sm opacity-70">
             <div className="flex items-center gap-2 cursor-pointer hover:opacity-100 transition-opacity">
               <div className="w-4 h-4 border border-[#1a1a1a]/30 rounded bg-[#1a1a1a] text-white flex items-center justify-center"><Check className="w-3 h-3" /></div>
               Pending
             </div>
             <div className="flex items-center gap-2 cursor-pointer hover:opacity-100 transition-opacity">
               <div className="w-4 h-4 border border-[#1a1a1a]/30 rounded"></div>
               Flagged by NLP
             </div>
             <div className="flex items-center gap-2 cursor-pointer hover:opacity-100 transition-opacity">
               <div className="w-4 h-4 border border-[#1a1a1a]/30 rounded"></div>
               Score Anomaly
             </div>
           </div>
           
           <div className="mt-8 pt-8 border-t border-[#1a1a1a]/10">
             <h3 className="text-[10px] uppercase tracking-widest opacity-50 mb-3 text-red-600">Strict Rules</h3>
             <p className="text-xs opacity-60 leading-relaxed font-serif">
               - Reject abusive language<br/>
               - Reject off-topic content<br/>
               - Verify NLP theme extraction<br/>
               - Approve valid literary critique
             </p>
           </div>
        </div>

        {/* Queue */}
        <div className="col-span-1 md:col-span-3">
           <AnimatePresence>
             {queue.length === 0 ? (
               <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="py-24 text-center border border-dashed border-[#1a1a1a]/20 rounded-2xl">
                 <Shield className="w-12 h-12 mx-auto mb-4 opacity-20" />
                 <p className="font-serif text-xl italic opacity-50">Queue is empty</p>
                 <p className="text-sm opacity-40 mt-2">All pending evaluations have been processed.</p>
               </motion.div>
             ) : (
               queue.map((review) => {
                 const book = books.find((b: any) => String(b.id) === String(review.bookId ?? review.edition_id ?? review.editionId));
                 return (
                   <motion.div 
                     key={review.id}
                     layout
                     initial={{ opacity: 0, y: 10 }}
                     animate={{ opacity: 1, y: 0 }}
                     exit={{ opacity: 0, scale: 0.95 }}
                     className="bg-white border border-[#1a1a1a]/10 mb-6 rounded-2xl overflow-hidden shadow-sm"
                   >
                      <div className="bg-[#1a1a1a]/5 px-6 py-3 border-b border-[#1a1a1a]/10 flex justify-between items-center text-xs">
                        <span className="font-mono opacity-60">ID: {review.id}</span>
                        <span className="opacity-60">{new Date(review.createdAt).toLocaleString()}</span>
                      </div>
                      
                      <div className="p-6">
                        <div className="flex justify-between items-start mb-6">
                           <div>
                             <h4 className="font-medium">{book?.title}</h4>
                             <p className="text-xs opacity-60">{book?.author} • ISBN: {book?.isbn}</p>
                           </div>
                           <div className="flex flex-col items-end">
                             <div className="text-[10px] uppercase tracking-widest opacity-50 mb-1">Proposed Rating</div>
                             <StarRating rating={review.rating} size="sm" />
                           </div>
                        </div>
                        
                        <div className="bg-[#f5f2ed]/50 p-4 rounded-xl border border-[#1a1a1a]/5 mb-6 text-sm font-serif leading-relaxed">
                          "{review.text}"
                        </div>
                        
                        <div className="flex justify-between items-center">
                           <div className="flex items-center gap-2 text-xs">
                             <div className="w-6 h-6 rounded-full bg-[#1a1a1a]/10 flex items-center justify-center font-serif italic">{review.userName[0]}</div>
                             <span className="font-medium">{review.userName}</span>
                             <span className="opacity-50">({review.userId})</span>
                           </div>
                           
                           <div className="flex gap-3">
                             <button 
                               onClick={() => handleDecision(review.id, 'rejected')}
                               className="px-4 py-2 border border-red-200 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg text-xs uppercase tracking-wider font-medium flex items-center gap-2 transition-colors"
                             >
                               <X className="w-3 h-3" /> Reject
                             </button>
                             <button 
                               onClick={() => handleDecision(review.id, 'approved')}
                               className="px-4 py-2 border border-[#1a1a1a] bg-[#1a1a1a] text-white hover:bg-[#1a1a1a]/90 rounded-lg text-xs uppercase tracking-wider font-medium flex items-center gap-2 transition-colors"
                             >
                               <Check className="w-3 h-3" /> Approve
                             </button>
                           </div>
                        </div>
                      </div>
                   </motion.div>
                 );
               })
             )}
           </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
