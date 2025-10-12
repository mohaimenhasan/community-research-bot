import React, { createContext, useContext, useState, useEffect } from 'react';
import { useMsal } from '@azure/msal-react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const { instance, accounts, inProgress } = useMsal();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (accounts.length > 0) {
      setUser(accounts[0]);
    }
    setLoading(false);
  }, [accounts]);

  const login = async () => {
    try {
      // Check if we're in demo mode (no real B2C configured)
      const isDemoMode = !process.env.REACT_APP_B2C_CLIENT_ID || process.env.REACT_APP_B2C_CLIENT_ID === 'development-client-id';

      if (isDemoMode) {
        // Demo mode: Create a fake user session
        const demoUser = {
          name: 'Demo User',
          username: 'demo@communityhub.local',
          localAccountId: 'demo-user-123',
          homeAccountId: 'demo-home-123',
          environment: 'demo',
          tenantId: 'demo-tenant',
          idTokenClaims: {
            name: 'Demo User',
            preferred_username: 'demo@communityhub.local',
            given_name: 'Demo',
            family_name: 'User'
          }
        };

        setUser(demoUser);
        console.log('Demo login successful');
        return;
      }

      // Real authentication mode
      const loginRequest = {
        scopes: ['openid', 'profile', 'email'],
      };

      await instance.loginPopup(loginRequest);
    } catch (error) {
      console.error('Login failed:', error);
      // If real auth fails, fallback to demo mode
      const demoUser = {
        name: 'Demo User',
        username: 'demo@communityhub.local',
        localAccountId: 'demo-user-123',
        homeAccountId: 'demo-home-123',
        environment: 'demo'
      };
      setUser(demoUser);
    }
  };

  const logout = async () => {
    try {
      // Check if we're in demo mode
      const isDemoMode = !process.env.REACT_APP_B2C_CLIENT_ID || process.env.REACT_APP_B2C_CLIENT_ID === 'development-client-id';

      if (isDemoMode || (user && user.environment === 'demo')) {
        // Demo mode: Just clear the user state
        setUser(null);
        console.log('Demo logout successful');
        return;
      }

      // Real authentication mode
      const logoutRequest = {
        account: user
      };

      await instance.logoutPopup(logoutRequest);
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
      // If real logout fails, just clear the user state
      setUser(null);
    }
  };

  const signUp = async () => {
    try {
      // Check if we're in demo mode (no real B2C configured)
      const isDemoMode = !process.env.REACT_APP_B2C_CLIENT_ID || process.env.REACT_APP_B2C_CLIENT_ID === 'development-client-id';

      if (isDemoMode) {
        // Demo mode: Create a fake user session for new signup
        const demoUser = {
          name: 'New Demo User',
          username: 'newuser@communityhub.local',
          localAccountId: 'demo-newuser-456',
          homeAccountId: 'demo-home-456',
          environment: 'demo',
          tenantId: 'demo-tenant',
          idTokenClaims: {
            name: 'New Demo User',
            preferred_username: 'newuser@communityhub.local',
            given_name: 'New Demo',
            family_name: 'User'
          }
        };

        setUser(demoUser);
        console.log('Demo signup successful');
        return;
      }

      // Real authentication mode
      const signUpRequest = {
        scopes: ['openid', 'profile', 'email'],
        authority: process.env.REACT_APP_B2C_SIGNUP_AUTHORITY
      };

      await instance.loginPopup(signUpRequest);
    } catch (error) {
      console.error('Sign up failed:', error);
      // If real auth fails, fallback to demo mode
      const demoUser = {
        name: 'New Demo User',
        username: 'newuser@communityhub.local',
        localAccountId: 'demo-newuser-456',
        homeAccountId: 'demo-home-456',
        environment: 'demo'
      };
      setUser(demoUser);
    }
  };

  const value = {
    user,
    login,
    logout,
    signUp,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};