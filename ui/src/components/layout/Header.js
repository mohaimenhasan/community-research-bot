import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useUser } from '../../context/UserContext';
import { Bell, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const { user } = useAuth();
  const { userPreferences } = useUser();
  const navigate = useNavigate();

  const currentLocation = userPreferences?.primaryLocation;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="container">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Location */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CH</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Community Hub</h1>
              {currentLocation && (
                <p className="text-xs text-gray-500">
                  📍 {currentLocation.city}, {currentLocation.province}
                </p>
              )}
            </div>
          </div>

          {/* User Actions */}
          <div className="flex items-center space-x-3">
            {/* Notifications */}
            <button
              className="p-2 text-gray-400 hover:text-gray-600 relative"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
              {/* Notification badge (if there are unread notifications) */}
              {/* <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span> */}
            </button>

            {/* Settings */}
            <button
              onClick={() => navigate('/settings')}
              className="p-2 text-gray-400 hover:text-gray-600"
              aria-label="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>

            {/* User Avatar */}
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-medium text-sm">
                {user?.name ? user.name[0].toUpperCase() : 'U'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;