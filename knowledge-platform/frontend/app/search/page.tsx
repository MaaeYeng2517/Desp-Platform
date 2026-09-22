'use client';

import { useState } from 'react';

export default function SearchStudio() {
  const [query, setQuery] = useState('');
  const [metadataFilters, setMetadataFilters] = useState({
    subject: '',
    language: '',
    status: 'published'
  });
  const [results, setResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setSearching(true);
    
    // Mock search results
    setTimeout(() => {
      setResults([
        {
          id: '1',
          title: 'database-basic.pdf',
          content: 'A database is a structured set of data held in a computer...',
          score: 0.94,
          metadata: { subject: 'database', language: 'en', status: 'published' }
        },
        {
          id: '2',
          title: 'sql-fundamentals.pdf',
          content: 'SQL (Structured Query Language) is used for managing databases...',
          score: 0.89,
          metadata: { subject: 'database', language: 'en', status: 'published' }
        }
      ]);
      setSearching(false);
    }, 500);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Search Studio</h1>
      
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Query
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Describe what you're looking for..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject
            </label>
            <input
              type="text"
              value={metadataFilters.subject}
              onChange={(e) => setMetadataFilters({ ...metadataFilters, subject: e.target.value })}
              placeholder="e.g., database"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Language
            </label>
            <input
              type="text"
              value={metadataFilters.language}
              onChange={(e) => setMetadataFilters({ ...metadataFilters, language: e.target.value })}
              placeholder="e.g., en"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={metadataFilters.status}
              onChange={(e) => setMetadataFilters({ ...metadataFilters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Any</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={searching}
          className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Results ({results.length})</h2>
          {results.map((result) => (
            <div key={result.id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-semibold">{result.title}</h3>
                <span className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium">
                  Score: {result.score}
                </span>
              </div>
              <p className="text-gray-600 mt-2">{result.content}</p>
              <div className="mt-3 flex gap-2">
                {Object.entries(result.metadata).map(([key, value]) => (
                  <span key={key} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    {key}: {value as string}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}