import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Home, Bookmark, PlusSquare, Search, Settings } from 'lucide-react';

const BottomNavigation = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    {
      id: 'home',
      label: 'Home',
      icon: Home,
      path: '/',
      badge: null
    },
    {
      id: 'saved',
      label: 'Saved',
      icon: Bookmark,
      path: '/saved',
      badge: null
    },
    {
      id: 'submit',
      label: 'Submit',
      icon: PlusSquare,
      path: '/submit',
      badge: null
    },
    {
      id: 'search',
      label: 'Search',
      icon: Search,
      path: '/search',
      badge: null
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      path: '/settings',
      badge: null
    }
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 bottom-nav-safe">
      <div className="container">
        <div className="flex justify-around items-center h-16">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);

            return (
              <button
                key={item.id}
                onClick={() => handleNavigation(item.path)}
                className={`flex flex-col items-center justify-center space-y-1 min-w-0 flex-1 py-2 px-1 relative ${
                  active
                    ? 'text-blue-600'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
                aria-label={item.label}
              >
                <Icon
                  className={`w-5 h-5 ${active ? 'fill-current' : ''}`}
                  strokeWidth={active ? 2 : 1.5}
                />
                <span className={`text-xs font-medium truncate max-w-full ${
                  active ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {item.label}
                </span>

                {/* Badge for notifications/counts */}
                {item.badge && (
                  <span className="absolute top-1 right-3 w-2 h-2 bg-red-500 rounded-full"></span>
                )}

                {/* Active indicator */}
                {active && (
                  <div className="absolute -top-px left-1/2 transform -translate-x-1/2 w-6 h-0.5 bg-blue-600 rounded-full"></div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default BottomNavigation;