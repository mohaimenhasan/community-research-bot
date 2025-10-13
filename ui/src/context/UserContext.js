import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { apiService } from '../services/apiService';

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [userProfile, setUserProfile] = useState(null);
  const [userPreferences, setUserPreferences] = useState({
    primaryLocation: null,
    additionalLocations: [],
    interests: [],
    notificationSettings: {
      email: true,
      push: true,
      inApp: true
    }
  });
  const [loading, setLoading] = useState(false);

  // Load user profile when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      loadUserProfile();
    }
  }, [isAuthenticated, user]);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      const profile = await apiService.getUserProfile(user.localAccountId);

      if (profile) {
        setUserProfile(profile);
        setUserPreferences({
          ...userPreferences,
          ...profile.preferences
        });
      } else {
        // Create new user profile
        await createUserProfile();
      }
    } catch (error) {
      console.error('Failed to load user profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const createUserProfile = async () => {
    try {
      const newProfile = {
        user_id: user.localAccountId,
        primary_location: userPreferences.primaryLocation || {
          city: 'Unknown',
          state: '',
          country: 'USA'
        },
        additional_locations: [],
        interests: [],
        categories: ['news', 'events', 'community'],
        notification_preferences: {
          email: true,
          push: true,
          frequency: 'daily'
        }
      };

      const createdProfile = await apiService.createUserProfile(newProfile);
      setUserProfile(createdProfile);
    } catch (error) {
      console.error('Failed to create user profile:', error);
    }
  };

  const updateUserProfile = async (updates) => {
    try {
      const updatedProfile = await apiService.updateUserProfile(
        user.localAccountId,
        updates
      );
      setUserProfile(updatedProfile);
      return updatedProfile;
    } catch (error) {
      console.error('Failed to update user profile:', error);
      throw error;
    }
  };

  const updatePreferences = async (newPreferences) => {
    try {
      const updatedPreferences = { ...userPreferences, ...newPreferences };
      setUserPreferences(updatedPreferences);

      await updateUserProfile({ preferences: updatedPreferences });
    } catch (error) {
      console.error('Failed to update preferences:', error);
      throw error;
    }
  };

  const updateLocation = async (location, isPrimary = true) => {
    try {
      const updates = isPrimary
        ? { primaryLocation: location }
        : {
            additionalLocations: [
              ...userPreferences.additionalLocations,
              location
            ]
          };

      await updatePreferences(updates);
    } catch (error) {
      console.error('Failed to update location:', error);
      throw error;
    }
  };

  const updateInterests = async (interests) => {
    try {
      await updatePreferences({ interests });
    } catch (error) {
      console.error('Failed to update interests:', error);
      throw error;
    }
  };

  const value = {
    userProfile,
    userPreferences,
    loading,
    updateUserProfile,
    updatePreferences,
    updateLocation,
    updateInterests,
    refreshProfile: loadUserProfile
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};