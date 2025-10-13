import React, { useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { User, Mail, MapPin, Heart, CreditCard, ArrowRight, ArrowLeft, Check } from 'lucide-react';

const SignUpWizard = ({ onComplete }) => {
  const { instance } = useMsal();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    location: '',
    interests: [],
    paymentInfo: {
      cardNumber: '',
      expiryDate: '',
      cvv: ''
    }
  });

  const steps = [
    { id: 1, title: 'Account', icon: User, description: 'Create your account' },
    { id: 2, title: 'Payment', icon: CreditCard, description: 'Verify payment method' },
    { id: 3, title: 'Location', icon: MapPin, description: 'Set your location' },
    { id: 4, title: 'Interests', icon: Heart, description: 'Choose your interests' }
  ];

  const interests = [
    'Local Government', 'Community Events', 'Sports', 'Arts & Culture',
    'Business', 'Health & Wellness', 'Education', 'Environment',
    'Food & Dining', 'Entertainment', 'Volunteering', 'Transportation'
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleInterestToggle = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // In a real app, this would save user data to the backend
    console.log('Sign up completed:', formData);
    if (onComplete) {
      onComplete(formData);
    }
  };

  const handleSocialSignUp = async (provider) => {
    try {
      const loginRequest = {
        scopes: ['openid', 'profile', 'email'],
        prompt: 'select_account'
      };

      await instance.loginPopup(loginRequest);
      if (onComplete) {
        onComplete({ socialProvider: provider });
      }
    } catch (error) {
      console.error('Social sign up failed:', error);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <div className="flex justify-center space-x-4 mb-6">
                <button
                  onClick={() => handleSocialSignUp('microsoft')}
                  className="flex items-center justify-center w-full py-3 px-4 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#00BCF2" d="M0 0h11v11H0z"/>
                    <path fill="#00BCF2" d="M13 0h11v11H13z"/>
                    <path fill="#00BCF2" d="M0 13h11v11H0z"/>
                    <path fill="#00BCF2" d="M13 13h11v11H13z"/>
                  </svg>
                  Microsoft
                </button>
                <button
                  onClick={() => handleSocialSignUp('google')}
                  className="flex items-center justify-center w-full py-3 px-4 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Google
                </button>
              </div>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or continue with email</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="your@email.com"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Create a secure password"
                  autoComplete="new-password"
                />
              </div>
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                />
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <CreditCard className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Payment Verification</h3>
              <p className="text-sm text-gray-600">We require a valid payment method for verification purposes</p>
            </div>
            <div>
              <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-700 mb-1">
                Card Number
              </label>
              <input
                id="cardNumber"
                type="text"
                value={formData.paymentInfo.cardNumber}
                onChange={(e) => handleInputChange('paymentInfo', {
                  ...formData.paymentInfo,
                  cardNumber: e.target.value
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="1234 5678 9012 3456"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="expiryDate" className="block text-sm font-medium text-gray-700 mb-1">
                  Expiry Date
                </label>
                <input
                  id="expiryDate"
                  type="text"
                  value={formData.paymentInfo.expiryDate}
                  onChange={(e) => handleInputChange('paymentInfo', {
                    ...formData.paymentInfo,
                    expiryDate: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="MM/YY"
                />
              </div>
              <div>
                <label htmlFor="cvv" className="block text-sm font-medium text-gray-700 mb-1">
                  CVV
                </label>
                <input
                  id="cvv"
                  type="text"
                  value={formData.paymentInfo.cvv}
                  onChange={(e) => handleInputChange('paymentInfo', {
                    ...formData.paymentInfo,
                    cvv: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="123"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <MapPin className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Set Your Location</h3>
              <p className="text-sm text-gray-600">Tell us where you're located to get relevant local content</p>
            </div>
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                Primary Location
              </label>
              <input
                id="location"
                type="text"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Vancouver, BC"
              />
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Popular locations:</strong> Vancouver BC, Toronto ON, Montreal QC, Calgary AB, Ottawa ON, Langley BC
              </p>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <Heart className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Choose Your Interests</h3>
              <p className="text-sm text-gray-600">Select topics you're interested in to personalize your feed</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {interests.map((interest) => (
                <button
                  key={interest}
                  onClick={() => handleInterestToggle(interest)}
                  className={`p-3 rounded-lg border text-sm font-medium transition-colors ${
                    formData.interests.includes(interest)
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {interest}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 text-center">
              Selected: {formData.interests.length} interest{formData.interests.length !== 1 ? 's' : ''}
            </p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Join Community Hub
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Discover what's happening in your community
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="flex justify-between items-center mb-8">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`rounded-full p-2 ${
                currentStep >= step.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-300 text-gray-500'
              }`}>
                {currentStep > step.id ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <step.icon className="w-4 h-4" />
                )}
              </div>
              {index < steps.length - 1 && (
                <div className={`h-0.5 w-8 ${
                  currentStep > step.id ? 'bg-blue-500' : 'bg-gray-300'
                }`} />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white py-8 px-6 shadow rounded-lg">
          {renderStep()}

          <div className="flex justify-between mt-8">
            {currentStep > 1 && (
              <button
                onClick={handleBack}
                className="flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </button>
            )}

            <button
              onClick={handleNext}
              className={`flex items-center px-6 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                currentStep === 1 ? 'w-full justify-center' : 'ml-auto'
              }`}
            >
              {currentStep === 4 ? 'Complete' : 'Continue'}
              {currentStep < 4 && <ArrowRight className="w-4 h-4 ml-2" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUpWizard;