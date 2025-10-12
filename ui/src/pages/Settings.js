import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useUser } from '../context/UserContext';
import {
  User,
  MapPin,
  Bell,
  Shield,
  LogOut,
  ChevronRight,
  Mail,
  Smartphone
} from 'lucide-react';

const Settings = () => {
  const { user, logout } = useAuth();
  const { userProfile, userPreferences } = useUser();

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to sign out?')) {
      await logout();
    }
  };

  const settingsGroups = [
    {
      title: 'Account',
      items: [
        {
          icon: User,
          label: 'Profile',
          description: 'Manage your personal information',
          action: () => console.log('Profile clicked')
        },
        {
          icon: MapPin,
          label: 'Locations',
          description: `Primary: ${userPreferences?.primaryLocation?.city || 'Not set'}`,
          action: () => console.log('Locations clicked')
        }
      ]
    },
    {
      title: 'Notifications',
      items: [
        {
          icon: Bell,
          label: 'Push Notifications',
          description: 'Get alerts for breaking news and events',
          action: () => console.log('Push notifications clicked')
        },
        {
          icon: Mail,
          label: 'Email Notifications',
          description: 'Weekly digest and important updates',
          action: () => console.log('Email notifications clicked')
        }
      ]
    },
    {
      title: 'Privacy & Security',
      items: [
        {
          icon: Shield,
          label: 'Privacy Settings',
          description: 'Control your data and visibility',
          action: () => console.log('Privacy clicked')
        },
        {
          icon: Smartphone,
          label: 'Connected Accounts',
          description: 'Manage linked social accounts',
          action: () => console.log('Connected accounts clicked')
        }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      {/* User Info Card */}
      <div className="card p-6">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-blue-600 font-semibold text-xl">
              {user?.name ? user.name[0].toUpperCase() : 'U'}
            </span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {user?.name || 'User'}
            </h3>
            <p className="text-gray-600">{user?.username || user?.email}</p>
            <p className="text-sm text-gray-500">
              Member since {userProfile?.createdAt ?
                new Date(userProfile.createdAt).toLocaleDateString() :
                'Recently'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Settings Groups */}
      {settingsGroups.map((group, groupIndex) => (
        <div key={groupIndex} className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">{group.title}</h2>
          <div className="card">
            {group.items.map((item, itemIndex) => {
              const Icon = item.icon;
              return (
                <button
                  key={itemIndex}
                  onClick={item.action}
                  className={`w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors ${
                    itemIndex !== group.items.length - 1 ? 'border-b border-gray-100' : ''
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                      <Icon className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{item.label}</p>
                      <p className="text-sm text-gray-500">{item.description}</p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </button>
              );
            })}
          </div>
        </div>
      ))}

      {/* App Information */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">About</h2>
        <div className="card p-4">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Version</span>
              <span className="font-medium">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last Updated</span>
              <span className="font-medium">October 2025</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Platform</span>
              <span className="font-medium">Azure Static Web Apps</span>
            </div>
          </div>
        </div>
      </div>

      {/* Logout */}
      <div className="card">
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-red-50 transition-colors text-red-600"
        >
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <LogOut className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="font-medium">Sign Out</p>
              <p className="text-sm text-red-500">Sign out of your account</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Footer */}
      <div className="text-center pt-8 pb-8">
        <p className="text-sm text-gray-500">
          Made with ❤️ for communities everywhere
        </p>
      </div>
    </div>
  );
};

export default Settings;