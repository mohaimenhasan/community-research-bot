import React, { useState, useEffect } from 'react';
import { MapPin, Search, X, Navigation, Clock } from 'lucide-react';
import locationService from '../../services/locationService';

const LocationSelector = ({ onLocationSelect, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [nearbyCities, setNearbyCities] = useState([]);
  const [popularLocations, setPopularLocations] = useState([]);
  const [locationDetected, setLocationDetected] = useState(false);

  // Try to detect user location on component mount
  useEffect(() => {
    detectUserLocation();
  }, []);

  const detectUserLocation = async () => {
    try {
      setLoading(true);
      const location = await locationService.getCurrentLocation();

      setCurrentLocation(location);
      setLocationDetected(true);

      // Get nearby cities within 100 miles
      const nearby = locationService.getCitiesWithinRadius(
        location.coordinates[0],
        location.coordinates[1],
        100
      );
      setNearbyCities(nearby);

      // Get popular locations for this area
      const popular = locationService.getPopularLocationsForArea(
        location.coordinates[0],
        location.coordinates[1]
      );
      setPopularLocations(popular);

    } catch (error) {
      console.error('Location detection failed:', error);
      // Show only major cities when location detection fails
      const majorCities = [
        { city: 'Seattle', state: 'WA', country: 'USA', coordinates: [47.6062, -122.3321] },
        { city: 'Vancouver', province: 'BC', country: 'Canada', coordinates: [49.2827, -123.1207] },
        { city: 'Portland', state: 'OR', country: 'USA', coordinates: [45.5152, -122.6784] },
        { city: 'San Francisco', state: 'CA', country: 'USA', coordinates: [37.7749, -122.4194] },
        { city: 'Los Angeles', state: 'CA', country: 'USA', coordinates: [34.0522, -118.2437] },
        { city: 'Toronto', province: 'ON', country: 'Canada', coordinates: [43.6532, -79.3832] },
        { city: 'New York', state: 'NY', country: 'USA', coordinates: [40.7128, -74.0060] },
        { city: 'Chicago', state: 'IL', country: 'USA', coordinates: [41.8781, -87.6298] }
      ];
      setPopularLocations(majorCities);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      // Search through our comprehensive city database
      const results = locationService.searchCities(query);

      // If user has location, add distance info
      if (currentLocation) {
        results.forEach(city => {
          city.distance = Math.round(locationService.calculateDistance(
            currentLocation.coordinates[0],
            currentLocation.coordinates[1],
            city.coordinates[0],
            city.coordinates[1]
          ));
        });

        // Sort by distance
        results.sort((a, b) => a.distance - b.distance);
      }

      setSearchResults(results);
    } catch (error) {
      console.error('Location search failed:', error);
    }
  };

  const getCurrentLocation = async () => {
    await detectUserLocation();
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
                    {currentLocation.city}, {currentLocation.state || currentLocation.province}
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
                        {location.city}, {location.state || location.province}
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
                        {location.city}, {location.state || location.province}
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