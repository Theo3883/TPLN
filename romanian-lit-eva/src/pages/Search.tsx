import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Search as SearchIcon, ArrowRight, Zap } from 'lucide-react';
import { mockBooks } from '../data/mock';

import StarRating from '../components/ui/StarRating';

export default function Search() {
  const [query, setQuery] = useState('');

  // Simulating Meilisearch typo-tolerance and instant search
  const results = useMemo(() => {
    if (!query.trim()) return [];
    
    const lowerQuery = query.toLowerCase();
    
    return mockBooks.filter(book => {
      // Basic simulation of full-text match
      const searchableText = `${book.title} ${book.author} ${book.publisher} ${book.isbn} ${book.themes.join(' ')}`.toLowerCase();
      
      // Simple exact match or subset match
      if (searchableText.includes(lowerQuery)) return true;
      
      // Basic typo tolerance simulation (if query is > 3 chars, allow slight mismatch - just a naive implementation for the frontend mockup)
      if (lowerQuery.length > 3) {
        let matchCount = 0;
        const queryWords = lowerQuery.split(' ');
        const textWords = searchableText.split(' ');
        
        for (const qWord of queryWords) {
          if (textWords.some(tWord => tWord.includes(qWord) || qWord.includes(tWord))) {
            matchCount++;
          }
        }
        return matchCount > 0 && matchCount >= queryWords.length - 1;
      }
      return false;
    });
  }, [query]);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="font-serif text-4xl mb-4 font-light">Full-Text Lookup</h1>
        <p className="text-sm opacity-60 max-w-lg mx-auto">Fast, typo-tolerant search powered by Meilisearch indexing schema.</p>
      </div>

      <div className="relative mb-12">
        <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none">
          <SearchIcon className="h-5 w-5 opacity-40" />
        </div>
        <input
          type="text"
          className="block w-full pl-16 pr-6 py-6 bg-white border border-[#1a1a1a]/10 rounded-full text-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#1a1a1a]/20 focus:border-[#1a1a1a]/50 transition-all font-serif placeholder:font-sans placeholder:text-base placeholder:opacity-50"
          placeholder="Search by title, author, isbn or themes..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
        />
        <div className="absolute inset-y-0 right-6 flex items-center pointer-events-none">
           <Zap className="w-4 h-4 text-amber-500 opacity-80" />
           <span className="text-[9px] uppercase tracking-wider ml-1 opacity-50 font-medium">Instant</span>
        </div>
      </div>

      <div>
        {query.trim() !== '' && (
          <div className="mb-6 flex justify-between items-center text-[11px] uppercase tracking-widest opacity-50">
            <span>{results.length} Results Found</span>
          </div>
        )}

        <div className="flex flex-col gap-4">
          {query.trim() === '' ? (
            <div className="text-center py-24 opacity-30">
              <SearchIcon className="w-12 h-12 mx-auto mb-4" />
              <p className="font-serif text-xl italic">Ready to search...</p>
            </div>
          ) : results.length > 0 ? (
            results.map((book) => (
              <Link 
                key={book.id} 
                to={`/edition/${book.id}`}
                className="group bg-white p-6 rounded-2xl border border-[#1a1a1a]/10 hover:border-[#1a1a1a]/40 transition-colors flex items-center gap-6"
              >
                <div className="w-16 h-24 bg-[#e8e4dc] rounded-md overflow-hidden shrink-0">
                  {book.coverUrl && <img src={book.coverUrl} className="w-full h-full object-cover mix-blend-multiply" alt=""/>}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-serif text-xl font-medium">{book.title}</h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 bg-[#1a1a1a]/5 rounded-sm">{book.year}</span>
                  </div>
                  <p className="text-sm opacity-70 mb-3">{book.author} — {book.publisher}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {book.themes.map(theme => (
                      <span key={theme} className="text-[9px] uppercase tracking-wider px-2 py-1 bg-[#1a1a1a]/5 text-[#1a1a1a]/70 rounded-full border border-[#1a1a1a]/10">
                        {theme}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="hidden sm:flex flex-col items-center justify-center shrink-0 w-24 h-24 border border-dashed border-[#1a1a1a]/20 rounded-full group-hover:bg-[#1a1a1a] group-hover:text-white transition-colors duration-300">
                  <StarRating rating={book.bayesianScore} size="sm" className="flex-col gap-0 text-current" />
                  <span className="text-[8px] uppercase tracking-widest mt-1 opacity-50 group-hover:opacity-80">Bayesian</span>
                </div>
              </Link>
            ))
          ) : (
            <div className="text-center py-24">
              <p className="font-serif text-xl italic opacity-50 mb-2">No editions found</p>
              <p className="text-sm opacity-40">Try adjusting your search terms or checking for typos.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
