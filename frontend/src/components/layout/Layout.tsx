import { Link, Outlet, useLocation } from 'react-router-dom';
import { BookOpen, Search, Shield, Trophy, Menu, X, User, LogOut, Gift, Eye } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  const navLinks = [
    { name: 'Home', path: '/', icon: BookOpen },
    { name: 'Catalog', path: '/catalog', icon: BookOpen },
    { name: 'Previews', path: '/book-previews', icon: Eye },
    { name: 'Search', path: '/search', icon: Search },
    { name: 'Rankings', path: '/rankings', icon: Trophy },
    ...(user ? [{ name: 'My Gift Books', path: '/my-gift-books', icon: Gift }] : []),
    { name: 'Moderation', path: '/moderation', icon: Shield },
  ];

  return (
    <div className="min-h-screen bg-[#f5f2ed] text-[#1a1a1a] font-sans selection:bg-[#5A5A40] selection:text-white">
      <header className="sticky top-0 z-50 bg-[#f5f2ed]/80 backdrop-blur-md border-b border-[#1a1a1a]/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-full border border-[#1a1a1a] flex items-center justify-center bg-[#1a1a1a] text-white group-hover:scale-105 transition-transform">
                <span className="font-serif italic font-bold">R</span>
              </div>
              <div className="flex flex-col">
                <span className="font-serif text-xl leading-none">Romanian Lit</span>
                <span className="text-[10px] uppercase tracking-[0.2em] opacity-60">Evaluation Platform</span>
              </div>
            </Link>

            <nav className="hidden md:flex gap-8">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`text-[11px] uppercase tracking-[0.1em] font-medium flex items-center gap-2 transition-opacity ${
                    location.pathname === link.path ? 'opacity-100 border-b border-[#1a1a1a] pb-1' : 'opacity-60 hover:opacity-100 pb-1'
                  }`}
                >
                  <link.icon className="w-3.5 h-3.5" />
                  {link.name}
                </Link>
              ))}
            </nav>

            {/* User menu */}
            <div className="hidden md:block relative">
              {user ? (
                <>
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#1a1a1a]/20 hover:bg-[#1a1a1a]/5 transition"
                  >
                    <User className="w-4 h-4" />
                    <span className="text-sm">{user.username}</span>
                  </button>
                  {userMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-[#1a1a1a]/10 py-2">
                      <div className="px-4 py-2 border-b border-[#1a1a1a]/10">
                        <p className="text-sm font-medium">{user.username}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                      <button
                        onClick={async () => {
                          await logout();
                          setUserMenuOpen(false);
                        }}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-[#1a1a1a]/5 flex items-center gap-2 text-red-600"
                      >
                        <LogOut className="w-4 h-4" />
                        Deconectare
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex gap-3">
                  <Link
                    to="/login"
                    className="text-[11px] uppercase tracking-[0.1em] font-medium px-4 py-2 opacity-60 hover:opacity-100 transition"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="text-[11px] uppercase tracking-[0.1em] font-medium px-4 py-2 bg-[#1a1a1a] text-white rounded hover:bg-[#1a1a1a]/90 transition"
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>

            <button 
              className="md:hidden p-2 opacity-60 hover:opacity-100"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden absolute top-20 left-0 w-full bg-[#f5f2ed] border-b border-[#1a1a1a]/10 pb-4">
            <div className="flex flex-col px-4 space-y-4">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMenuOpen(false)}
                  className={`text-xs uppercase tracking-[0.1em] font-medium flex items-center gap-3 p-3 transition-colors ${
                    location.pathname === link.path ? 'bg-[#1a1a1a]/5' : ''
                  }`}
                >
                  <link.icon className="w-4 h-4" />
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="mt-24 border-t border-[#1a1a1a]/10 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex flex-col text-center md:text-left">
            <span className="font-serif italic text-lg">Platforma CRET</span>
            <span className="text-[10px] uppercase tracking-[0.2em] opacity-50 mt-1">Continuous Evaluation of Romanian Editions</span>
          </div>
          <div className="flex gap-6 text-[10px] uppercase tracking-[0.1em] opacity-60">
            <a href="#" className="hover:opacity-100 transition-opacity">Documentation</a>
            <a href="#" className="hover:opacity-100 transition-opacity">API</a>
            <a href="#" className="hover:opacity-100 transition-opacity">Admin</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
