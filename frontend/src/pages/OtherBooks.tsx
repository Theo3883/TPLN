/**
 * Other Books Page - Displays books imported from crawlers
 * Features filtering by crawler source (Bookzone, Cărturești, Libris)
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listEditionsFiltered } from '../lib/api';
import { Edition, CrawlerName } from '../types';

type FilterType = 'all' | CrawlerName;

export default function OtherBooks() {
  const [editions, setEditions] = useState<Edition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [filter, setFilter] = useState<FilterType>('all');

  useEffect(() => {
    loadEditions();
  }, [filter]);

  const loadEditions = async () => {
    setLoading(true);
    setError('');
    try {
      const filters: any = { source: 'crawler' as const, limit: 100 };
      if (filter !== 'all') {
        filters.crawler_name = filter;
      }
      const data = await listEditionsFiltered(filters);
      setEditions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load editions');
    } finally {
      setLoading(false);
    }
  };

  const getFilterStats = () => {
    if (filter === 'all') return editions.length;
    return editions.filter((e) => e.crawler_name === filter).length;
  };

  const getCrawlerBadgeColor = (crawler?: CrawlerName) => {
    switch (crawler) {
      case 'bookzone':
        return 'bg-blue-100 text-blue-800';
      case 'carturesti':
        return 'bg-green-100 text-green-800';
      case 'libris':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('ro-RO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">Other Books</h1>
      <p className="text-gray-600 mb-6">
        Cărți importate automat din magazine online românești
      </p>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Toate
        </button>
        <button
          onClick={() => setFilter('bookzone')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            filter === 'bookzone'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Bookzone
        </button>
        <button
          onClick={() => setFilter('carturesti')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            filter === 'carturesti'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Cărturești
        </button>
        <button
          onClick={() => setFilter('libris')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            filter === 'libris'
              ? 'bg-orange-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Libris
        </button>
      </div>

      {/* Stats */}
      <div className="mb-6 text-sm text-gray-600">
        {loading ? (
          <span>Se încarcă...</span>
        ) : (
          <span>
            {editions.length} {editions.length === 1 ? 'carte' : 'cărți'} găsite
          </span>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Se încarcă cărțile...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && editions.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">
            Nu au fost găsite cărți{' '}
            {filter !== 'all' && `din ${filter}`}.
          </p>
        </div>
      )}

      {/* Books Grid */}
      {!loading && editions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {editions.map((edition) => (
            <div
              key={edition.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-4 border border-gray-200"
            >
              {/* Crawler Badge */}
              <div className="mb-2">
                <span
                  className={`inline-block px-2 py-1 text-xs font-semibold rounded ${getCrawlerBadgeColor(
                    edition.crawler_name
                  )}`}
                >
                  {edition.crawler_name || 'unknown'}
                </span>
              </div>

              {/* Book Title */}
              <h3 className="font-bold text-lg mb-2 line-clamp-2">
                {edition.book?.title || 'Untitled'}
              </h3>

              {/* Authors */}
              {edition.authors && edition.authors.length > 0 && (
                <p className="text-sm text-gray-600 mb-2 line-clamp-1">
                  {edition.authors.map((a) => a.name).join(', ')}
                </p>
              )}

              {/* Publisher & Year */}
              <div className="text-sm text-gray-500 mb-3">
                {edition.publisher && <span>{edition.publisher}</span>}
                {edition.year && (
                  <span className="ml-2">({edition.year})</span>
                )}
              </div>

              {/* ISBN */}
              {edition.isbn && (
                <p className="text-xs text-gray-400 mb-2">ISBN: {edition.isbn}</p>
              )}

              {/* Score */}
              {edition.score !== undefined && edition.score !== null && (
                <div className="mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-yellow-500">★</span>
                    <span className="font-semibold">{edition.score.toFixed(2)}</span>
                    <span className="text-xs text-gray-500">
                      ({edition.review_count}{' '}
                      {edition.review_count === 1 ? 'recenzie' : 'recenzii'})
                    </span>
                  </div>
                </div>
              )}

              {/* Import Date */}
              {edition.imported_at && (
                <p className="text-xs text-gray-400 mb-3">
                  Importat: {formatDate(edition.imported_at)}
                </p>
              )}

              {/* View Details Link */}
              <Link
                to={`/edition/${edition.id}`}
                className="inline-block w-full text-center bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
              >
                Vezi Detalii
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
