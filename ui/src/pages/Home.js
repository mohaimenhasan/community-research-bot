import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { apiService } from '../services/apiService';
import ContentFeed from '../components/content/ContentFeed';
import LocationSelector from '../components/profile/LocationSelector';
import { MapPin, Calendar, Users, TrendingUp } from 'lucide-react';

const Home = () => {
  const { userPreferences, updateLocation } = useUser();
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showLocationSelector, setShowLocationSelector] = useState(false);

  const hasLocation = userPreferences?.primaryLocation;

  useEffect(() => {
    if (hasLocation) {
      loadPersonalizedContent();
    } else {
      setLoading(false);
    }
  }, [hasLocation, userPreferences]);

  const loadPersonalizedContent = async () => {
    try {
      setLoading(true);
      const location = `${userPreferences.primaryLocation.city}, ${userPreferences.primaryLocation.province}`;

      const response = await apiService.getPersonalizedContent(location, {
        interests: userPreferences.interests,
        past_events: [] // TODO: Track user's past events
      });

      setContent(response);
    } catch (error) {
      console.error('Failed to load content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = async (location) => {
    try {
      await updateLocation(location, true);
      setShowLocationSelector(false);
    } catch (error) {
      console.error('Failed to update location:', error);
    }
  };

  // Location setup screen
  if (!hasLocation) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center space-y-6 max-w-md mx-auto px-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
            <MapPin className="w-8 h-8 text-blue-600" />
          </div>

          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Welcome to Community Hub!
            </h2>
            <p className="text-gray-600">
              To get started, let us know where you're located so we can find relevant local events and news for you.
            </p>
          </div>

          <button
            onClick={() => setShowLocationSelector(true)}
            className="btn-primary w-full"
          >
            Set Your Location
          </button>
        </div>

        {/* Location Selector Modal */}
        {showLocationSelector && (
          <LocationSelector
            onLocationSelect={handleLocationSelect}
            onClose={() => setShowLocationSelector(false)}
          />
        )}
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="spinner mx-auto"></div>
          <p className="text-gray-600">Discovering community events...</p>
        </div>
      </div>
    );
  }

  // Main content view
  return (
    <div className="space-y-6">
      {/* Location Header */}
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <MapPin className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">
                {userPreferences.primaryLocation.city}
              </h3>
              <p className="text-sm text-gray-500">
                {userPreferences.primaryLocation.province}, {userPreferences.primaryLocation.country}
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowLocationSelector(true)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Change
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      {content && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {content.agent_response?.sources_crawled?.length || 0}
                </p>
                <p className="text-sm text-gray-500">Local Sources</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {content.agent_response?.location_specific ? '85%' : '60%'}
                </p>
                <p className="text-sm text-gray-500">Match Score</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content Feed */}
      <ContentFeed
        content={content}
        onRefresh={loadPersonalizedContent}
        location={userPreferences.primaryLocation}
      />

      {/* Location Selector Modal */}
      {showLocationSelector && (
        <LocationSelector
          onLocationSelect={handleLocationSelect}
          onClose={() => setShowLocationSelector(false)}
        />
      )}
    </div>
  );
};

export default Home;