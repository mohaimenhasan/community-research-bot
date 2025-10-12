import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { PublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';
import './index.css';
import App from './App';

// MSAL configuration
const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_B2C_CLIENT_ID || 'development-client-id',
    authority: process.env.REACT_APP_B2C_AUTHORITY || 'https://communityhub.b2clogin.com/communityhub.onmicrosoft.com/B2C_1_signupsignin',
    knownAuthorities: [process.env.REACT_APP_B2C_DOMAIN || 'communityhub.b2clogin.com'],
    redirectUri: '/',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  }
};

const msalInstance = new PublicClientApplication(msalConfig);

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <MsalProvider instance={msalInstance}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </MsalProvider>
  </React.StrictMode>
);