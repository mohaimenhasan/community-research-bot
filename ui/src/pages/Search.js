import React, { useState } from 'react';
import { Search as SearchIcon, TrendingUp, Clock, MapPin } from 'lucide-react';

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recentSearches] = useState([
    'community events',
    'town hall meetings',
    'local festivals',
    'sports leagues'
  ]);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      // In production, this would call the API
      // const results = await apiService.searchContent(searchQuery);
      setTimeout(() => {
        setResults([]);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Search failed:', error);
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch(query);
  };

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Search</h1>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="relative">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for events, news, or topics..."
            className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          {query && (
            <button
              type="submit"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 btn-primary px-4 py-1 text-sm"
            >
              Search
            </button>
          )}
        </form>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="spinner mr-3"></div>
          <span className="text-gray-600">Searching...</span>
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Search Results ({results.length})
          </h2>
          {/* Results would be displayed here */}
        </div>
      )}

      {/* No Results */}
      {!loading && query && results.length === 0 && (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <SearchIcon className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search terms or browse popular topics below.
          </p>
        </div>
      )}

      {/* Recent Searches */}
      {!query && recentSearches.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <Clock className="w-5 h-5" />
            <span>Recent Searches</span>
          </h2>
          <div className="space-y-2">
            {recentSearches.map((search, index) => (
              <button
                key={index}
                onClick={() => {
                  setQuery(search);
                  handleSearch(search);
                }}
                className="flex items-center space-x-3 w-full p-3 text-left rounded-lg hover:bg-gray-50"
              >
                <SearchIcon className="w-4 h-4 text-gray-400" />
                <span className="text-gray-700">{search}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Popular Topics */}
      {!query && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Trending Topics</span>
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              'City Council',
              'Local Events',
              'Community News',
              'Sports',
              'Arts & Culture',
              'Business'
            ].map((topic, index) => (
              <button
                key={index}
                onClick={() => {
                  setQuery(topic.toLowerCase());
                  handleSearch(topic.toLowerCase());
                }}
                className="p-3 text-center bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                <span className="font-medium text-gray-700">{topic}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;