/**
 * Register Page
 */

import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Register() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (password !== confirmPassword) {
      setError('Parolele nu se potrivesc');
      return;
    }

    if (password.length < 8) {
      setError('Parola trebuie să aibă minim 8 caractere');
      return;
    }

    if (!/[A-Z]/.test(password)) {
      setError('Parola trebuie să conțină cel puțin o literă mare');
      return;
    }

    if (!/[0-9]/.test(password)) {
      setError('Parola trebuie să conțină cel puțin o cifră');
      return;
    }

    setLoading(true);

    try {
      await register({ email, username, password });
      navigate('/'); // Redirect to home after successful registration
    } catch (err: any) {
      setError(err.message || 'Înregistrarea a eșuat');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold text-center mb-6">Înregistrare</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="exemplu@email.com"
            />
          </div>

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Nume utilizator
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              pattern="^[a-zA-Z0-9_-]{3,30}$"
              title="3-30 caractere: litere, cifre, _ sau -"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="utilizator123"
            />
            <p className="mt-1 text-xs text-gray-500">3-30 caractere: litere, cifre, _ sau -</p>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Parolă
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
            <p className="mt-1 text-xs text-gray-500">
              Minim 8 caractere, cu cel puțin o literă mare și o cifră
            </p>
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
              Confirmă parola
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Se înregistrează...' : 'Înregistrare'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Ai deja cont?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">
            Autentifică-te
          </Link>
        </p>
      </div>
    </div>
  );
}
