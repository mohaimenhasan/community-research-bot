import React, { useState } from 'react';
import { MapPin, Search, X, Navigation } from 'lucide-react';

const LocationSelector = ({ onLocationSelect, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);

  // Popular locations for quick selection
  const popularLocations = [
    {
      city: 'Vancouver',
      province: 'BC',
      country: 'Canada',
      coordinates: [49.2827, -123.1207]
    },
    {
      city: 'Toronto',
      province: 'ON',
      country: 'Canada',
      coordinates: [43.6532, -79.3832]
    },
    {
      city: 'Calgary',
      province: 'AB',
      country: 'Canada',
      coordinates: [51.0447, -114.0719]
    },
    {
      city: 'Montreal',
      province: 'QC',
      country: 'Canada',
      coordinates: [45.5017, -73.5673]
    },
    {
      city: 'Ottawa',
      province: 'ON',
      country: 'Canada',
      coordinates: [45.4215, -75.6972]
    },
    {
      city: 'Langley',
      province: 'BC',
      country: 'Canada',
      coordinates: [49.1042, -122.6604]
    }
  ];

  const handleSearch = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      // Simple search through popular locations for demo
      const results = popularLocations.filter(location =>
        location.city.toLowerCase().includes(query.toLowerCase()) ||
        location.province.toLowerCase().includes(query.toLowerCase())
      );

      setSearchResults(results);
    } catch (error) {
      console.error('Location search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = async () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by this browser.');
      return;
    }

    setLoading(true);
    try {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          // For demo, we'll use Vancouver as current location
          // In production, this would reverse geocode the coordinates
          const detectedLocation = {
            city: 'Vancouver',
            province: 'BC',
            country: 'Canada',
            coordinates: [position.coords.latitude, position.coords.longitude]
          };

          setCurrentLocation(detectedLocation);
          setLoading(false);
        },
        (error) => {
          console.error('Geolocation error:', error);
          setLoading(false);
          alert('Unable to detect your location. Please search manually.');
        }
      );
    } catch (error) {
      console.error('Location detection failed:', error);
      setLoading(false);
    }
  };

  const handleLocationSelect = (location) => {
    onLocationSelect(location);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end sm:items-center justify-center z-50">
      <div className="bg-white w-full sm:max-w-md sm:rounded-lg shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Select Location</h3>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search for a city..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                handleSearch(e.target.value);
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Current Location */}
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={getCurrentLocation}
            disabled={loading}
            className="flex items-center space-x-3 w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <Navigation className="w-5 h-5 text-blue-600" />
            <div>
              <p className="font-medium text-gray-900">Use Current Location</p>
              <p className="text-sm text-gray-500">Detect your location automatically</p>
            </div>
          </button>

          {currentLocation && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-green-800">
                    {currentLocation.city}, {currentLocation.province}
                  </span>
                </div>
                <button
                  onClick={() => handleLocationSelect(currentLocation)}
                  className="text-sm text-green-700 font-medium hover:text-green-800"
                >
                  Use This
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Search Results */}
        <div className="max-h-64 overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="spinner"></div>
            </div>
          )}

          {!loading && searchQuery && searchResults.length > 0 && (
            <div className="p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Search Results</h4>
              <div className="space-y-2">
                {searchResults.map((location, index) => (
                  <button
                    key={index}
                    onClick={() => handleLocationSelect(location)}
                    className="flex items-center space-x-3 w-full p-3 text-left rounded-lg hover:bg-gray-50"
                  >
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">
                        {location.city}, {location.province}
                      </p>
                      <p className="text-sm text-gray-500">{location.country}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {!loading && !searchQuery && (
            <div className="p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Popular Locations</h4>
              <div className="space-y-2">
                {popularLocations.map((location, index) => (
                  <button
                    key={index}
                    onClick={() => handleLocationSelect(location)}
                    className="flex items-center space-x-3 w-full p-3 text-left rounded-lg hover:bg-gray-50"
                  >
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">
                        {location.city}, {location.province}
                      </p>
                      <p className="text-sm text-gray-500">{location.country}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {!loading && searchQuery && searchResults.length === 0 && (
            <div className="p-4 text-center">
              <p className="text-gray-500">No locations found for "{searchQuery}"</p>
              <p className="text-sm text-gray-400 mt-1">
                Try searching for a different city or province
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LocationSelector;