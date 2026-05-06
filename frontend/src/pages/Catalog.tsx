import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { useEditions } from '../lib/useApi';
import { Filter, ChevronDown, Download } from 'lucide-react';

import StarRating from '../components/ui/StarRating';

export default function Catalog() {
  const [filter, setFilter] = useState('all');
  const { data: books, loading } = useEditions(90);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex flex-col md:flex-row justify-between items-end border-b border-[#1a1a1a]/10 pb-8 mb-12">
        <div>
          <h1 className="font-serif text-4xl mb-2 font-light">Literary Catalog</h1>
          <p className="text-sm opacity-60">Browse, review, and evaluate Romanian editions.</p>
        </div>
        
        <div className="flex gap-4 mt-6 md:mt-0">
          <button className="flex items-center gap-2 px-4 py-2 border border-[#1a1a1a]/20 rounded-full text-[10px] uppercase tracking-wider hover:bg-[#1a1a1a]/5 transition-colors">
            <Filter className="w-3 h-3" />
            Filter <ChevronDown className="w-3 h-3" />
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] text-white rounded-full text-[10px] uppercase tracking-wider hover:bg-[#1a1a1a]/90 transition-colors">
            <Download className="w-3 h-3" />
            Export CSV
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {(books || []).map((book, index) => (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            key={book.id}
          >
            <Link to={`/edition/${book.id}`} className="group flex flex-col h-full bg-white p-6 rounded-[2rem] border border-[#1a1a1a]/5 shadow-sm hover:shadow-md transition-shadow">
              <div className="aspect-[3/4] overflow-hidden rounded-2xl mb-6 bg-[#xf5f2ed] border border-[#1a1a1a]/5">
                 {book.coverUrl ? (
                   <img src={book.coverUrl} alt={book.title} className="w-full h-full object-cover mix-blend-multiply group-hover:scale-105 transition-transform duration-700" />
                 ) : (
                   <div className="w-full h-full flex items-center justify-center font-serif text-2xl italic opacity-30 bg-[#eae7e0]">
                     {book.title[0]}
                   </div>
                 )}
              </div>
              
              <div className="flex-1 flex flex-col">
                <div className="flex justify-between items-start mb-2">
                  <h2 className="font-serif text-xl font-medium leading-tight group-hover:underline underline-offset-4 decoration-[#1a1a1a]/30">{book.title}</h2>
                  <div className="px-2 py-1 bg-[#1a1a1a]/5 rounded-sm text-[10px] font-mono whitespace-nowrap ml-4">
                    {book.year}
                  </div>
                </div>
                
                <h3 className="text-sm opacity-60 mb-6">{book.author}</h3>
                
                <div className="mt-auto pt-6 border-t border-[#1a1a1a]/10 flex justify-between items-center">
                  <div className="flex flex-col">
                    <span className="text-[9px] uppercase tracking-widest opacity-50 mb-1">Bayesian Score</span>
                    <StarRating rating={book.bayesianScore} size="sm" />
                  </div>
                  
                  <div className="flex flex-col items-end">
                    <span className="text-[9px] uppercase tracking-widest opacity-50 mb-1">Reviews</span>
                    <span className="font-serif italic">{book.reviewCount}</span>
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
