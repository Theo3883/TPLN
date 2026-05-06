import { Link } from 'react-router-dom';
import { ArrowRight, BookMarked, Search, Trophy, Settings } from 'lucide-react';
import { motion } from 'motion/react';

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center min-h-[60vh]"
      >
        <div className="flex flex-col gap-8 relative z-10">
          <div className="inline-flex items-center gap-3 text-[10px] uppercase tracking-[0.2em] font-medium opacity-70">
            <span className="w-8 h-[1px] bg-[#1a1a1a]"></span>
            Continuous Evaluation
          </div>
          
          <h1 className="font-serif text-5xl md:text-7xl leading-[1.1] font-light">
            Preserving <br />
            <span className="italic">Romanian Literature</span>
          </h1>
          
          <p className="text-lg opacity-70 max-w-md font-serif leading-relaxed">
            A comprehensive web platform for data ingestion, user reviews, and transparent ranking of Romanian literature editions.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 mt-4">
            <Link 
              to="/catalog" 
              className="px-8 py-4 bg-[#1a1a1a] text-[#f5f2ed] border border-[#1a1a1a] rounded-full text-[11px] uppercase tracking-[0.1em] font-medium hover:bg-transparent hover:text-[#1a1a1a] transition-all flex items-center justify-center gap-2 group"
            >
              Browse Catalog
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link 
              to="/search" 
              className="px-8 py-4 bg-transparent text-[#1a1a1a] border border-[#1a1a1a]/20 rounded-full text-[11px] uppercase tracking-[0.1em] font-medium hover:border-[#1a1a1a] transition-all flex items-center justify-center"
            >
              Search Database
            </Link>
          </div>
        </div>
        
        <div className="relative">
          <div className="aspect-[3/4] rounded-t-full bg-[#e8e4dc] overflow-hidden border border-[#1a1a1a]/10 relative">
            <img 
              src="https://images.unsplash.com/photo-1463320726281-696a485928c7?q=80&w=1200&auto=format&fit=crop" 
              alt="Classic books" 
              className="w-full h-full object-cover mix-blend-multiply opacity-80"
            />
            {/* Overlay gradient for atmospheric feel */}
            <div className="absolute inset-0 bg-gradient-to-t from-[#f5f2ed] via-transparent to-transparent opacity-60"></div>
          </div>
          
          {/* Floating badge */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="absolute bottom-12 -left-12 bg-[#1a1a1a] text-white p-6 rounded-full border border-white/20 shadow-2xl flex flex-col items-center justify-center w-32 h-32"
          >
            <span className="font-serif text-3xl italic">140+</span>
            <span className="text-[9px] uppercase tracking-widest mt-1">Editions</span>
          </motion.div>
        </div>
      </motion.div>

      {/* Features Grid */}
      <motion.div 
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="mt-32 pt-24 border-t border-[#1a1a1a]/10"
      >
        <div className="text-center mb-16 relative">
          <h2 className="font-serif text-3xl font-light">Platform Architecture</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-12">
          {[
            { icon: BookMarked, title: 'Data Ingestion', desc: 'Automated collection of metadata using Scrapy crawlers.' },
            { icon: Search, title: 'Meilisearch', desc: 'Blazing-fast full-text lookup with typo tolerance.' },
            { icon: Trophy, title: 'Bayesian Ranking', desc: 'Fair scoring model utilizing Bayesian shrinkage.' },
            { icon: Settings, title: 'Governance', desc: 'Audit trails, moderation endpoints, and review NLP.' },
          ].map((feature, i) => (
             <div key={i} className="flex flex-col group px-6 py-8 border border-[#1a1a1a]/10 hover:bg-white rounded-2xl transition-colors">
              <div className="w-12 h-12 rounded-full bg-[#1a1a1a]/5 flex items-center justify-center mb-6 group-hover:bg-[#1a1a1a] group-hover:text-white transition-colors">
                <feature.icon className="w-5 h-5" />
              </div>
              <h3 className="font-serif text-xl mb-3">{feature.title}</h3>
              <p className="text-sm opacity-60 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
