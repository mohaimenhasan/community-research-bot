import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useIsAuthenticated } from '@azure/msal-react';

// Context providers
import { AuthProvider, useAuth } from './context/AuthContext';
import { UserProvider } from './context/UserContext';

// Layout components
import AppLayout from './components/layout/AppLayout';
import AuthLayout from './components/layout/AuthLayout';

// Page components
import Home from './pages/Home';
import Saved from './pages/Saved';
import Submit from './pages/Submit';
import Search from './pages/Search';
import Settings from './pages/Settings';

// Auth components
import Login from './components/auth/LoginForm';
import SignUp from './components/auth/SignUpWizard';

function AppContent() {
  const msalAuthenticated = useIsAuthenticated();
  const { isAuthenticated } = useAuth();

  // Use either MSAL authentication or our demo authentication
  const userIsAuthenticated = msalAuthenticated || isAuthenticated;

  return (
    <UserProvider>
      <div className="App">
        {userIsAuthenticated ? (
          // Authenticated app
          <AppLayout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/saved" element={<Saved />} />
              <Route path="/submit" element={<Submit />} />
              <Route path="/search" element={<Search />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </AppLayout>
        ) : (
          // Authentication flow
          <AuthLayout>
            <Routes>
              <Route path="/" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/login" element={<Login />} />
            </Routes>
          </AuthLayout>
        )}
      </div>
    </UserProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;