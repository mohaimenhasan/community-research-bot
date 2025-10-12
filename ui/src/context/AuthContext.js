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
      const loginRequest = {
        scopes: ['openid', 'profile', 'email'],
      };

      await instance.loginPopup(loginRequest);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const logout = async () => {
    try {
      const logoutRequest = {
        account: user
      };

      await instance.logoutPopup(logoutRequest);
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const signUp = async () => {
    try {
      const signUpRequest = {
        scopes: ['openid', 'profile', 'email'],
        authority: process.env.REACT_APP_B2C_SIGNUP_AUTHORITY
      };

      await instance.loginPopup(signUpRequest);
    } catch (error) {
      console.error('Sign up failed:', error);
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