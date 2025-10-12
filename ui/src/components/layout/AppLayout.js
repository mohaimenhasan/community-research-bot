import React from 'react';
import BottomNavigation from './BottomNavigation';
import Header from './Header';

const AppLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="content-with-nav">
        <div className="container py-4">
          {children}
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNavigation />
    </div>
  );
};

export default AppLayout;