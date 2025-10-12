import React, { useState } from 'react';
import { useUser } from '../context/UserContext';
import { apiService } from '../services/apiService';
import { PlusSquare, MapPin, Calendar, Camera, Send } from 'lucide-react';

const Submit = () => {
  const { userPreferences } = useUser();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    location: userPreferences?.primaryLocation || null,
    eventDate: '',
    source: '',
    contactInfo: '',
    images: []
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const categories = [
    'Government Meeting',
    'Community Event',
    'Local News',
    'Business News',
    'Sports',
    'Arts & Culture',
    'Education',
    'Health & Safety',
    'Environment',
    'Other'
  ];

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const tip = {
        ...formData,
        location: formData.location?.city || 'Unknown',
        submittedBy: 'user', // In production, this would be the actual user ID
        priority: 'normal',
        status: 'pending'
      };

      await apiService.submitNewsTip(tip);
      setSubmitted(true);
    } catch (error) {
      console.error('Failed to submit news tip:', error);
      alert('Failed to submit your tip. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md mx-auto">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <Send className="w-8 h-8 text-green-600" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Thank You!</h3>
            <p className="text-gray-600">
              Your news tip has been submitted successfully. Our editorial team will review it and may reach out if more information is needed.
            </p>
          </div>
          <button
            onClick={() => {
              setSubmitted(false);
              setFormData({
                title: '',
                description: '',
                category: '',
                location: userPreferences?.primaryLocation || null,
                eventDate: '',
                source: '',
                contactInfo: '',
                images: []
              });
            }}
            className="btn-primary"
          >
            Submit Another Tip
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Submit News Tip</h1>
        <p className="text-gray-600">
          Help your community stay informed by sharing local news and events
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div className="space-y-2">
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="What's happening in your community?"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* Category */}
        <div className="space-y-2">
          <label htmlFor="category" className="block text-sm font-medium text-gray-700">
            Category *
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleInputChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description *
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Provide details about this news or event. Include who, what, when, where, and why."
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* Location */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Location
          </label>
          <div className="flex items-center space-x-2 p-3 border border-gray-300 rounded-lg bg-gray-50">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="text-gray-700">
              {formData.location
                ? `${formData.location.city}, ${formData.location.province}`
                : 'No location set'
              }
            </span>
          </div>
        </div>

        {/* Event Date (Optional) */}
        <div className="space-y-2">
          <label htmlFor="eventDate" className="block text-sm font-medium text-gray-700">
            Event Date (if applicable)
          </label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="datetime-local"
              id="eventDate"
              name="eventDate"
              value={formData.eventDate}
              onChange={handleInputChange}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Source */}
        <div className="space-y-2">
          <label htmlFor="source" className="block text-sm font-medium text-gray-700">
            Source (Optional)
          </label>
          <input
            type="text"
            id="source"
            name="source"
            value={formData.source}
            onChange={handleInputChange}
            placeholder="Website, document, or person who provided this information"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Contact Info */}
        <div className="space-y-2">
          <label htmlFor="contactInfo" className="block text-sm font-medium text-gray-700">
            Your Contact Information (Optional)
          </label>
          <input
            type="text"
            id="contactInfo"
            name="contactInfo"
            value={formData.contactInfo}
            onChange={handleInputChange}
            placeholder="Email or phone number (in case we need more details)"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="text-xs text-gray-500">
            This will only be used by our editorial team and will not be published
          </p>
        </div>

        {/* Image Upload Placeholder */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Images (Coming Soon)
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50">
            <Camera className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500 text-sm">
              Image upload feature will be available soon
            </p>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                <span>Submitting...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Submit News Tip</span>
              </>
            )}
          </button>
        </div>

        {/* Guidelines */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">Submission Guidelines</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Ensure information is accurate and factual</li>
            <li>• Include as much detail as possible</li>
            <li>• Respect privacy and avoid personal information</li>
            <li>• Tips are reviewed by our editorial team before publishing</li>
          </ul>
        </div>
      </form>
    </div>
  );
};

export default Submit;