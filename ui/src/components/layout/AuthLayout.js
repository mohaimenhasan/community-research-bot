import React from 'react';

const AuthLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">CH</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Community Hub</h1>
          <p className="text-gray-600 mt-1">Stay connected with your community</p>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-sm text-gray-500">
            Discover local events, news, and stay connected
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;