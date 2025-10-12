// API Service for Community Hub
// Connects to Azure Functions backend

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://commhub-func-cnbkczf6a4ctdhcz.westus2-01.azurewebsites.net/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // User Profile Management
  async getUserProfile(userId) {
    return this.makeRequest(`/user_profile/${userId}`, {
      method: 'GET'
    });
  }

  async createUserProfile(profile) {
    return this.makeRequest('/user_profile', {
      method: 'POST',
      body: JSON.stringify(profile)
    });
  }

  async updateUserProfile(userId, updates) {
    return this.makeRequest(`/user_profile/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  // Content Discovery
  async getPersonalizedContent(location, preferences = {}) {
    return this.makeRequest('/research_agent', {
      method: 'POST',
      body: JSON.stringify({
        location,
        query: 'community events and local news',
        preferences
      })
    });
  }

  async searchContent(query, location = null, filters = {}) {
    return this.makeRequest('/research_agent', {
      method: 'POST',
      body: JSON.stringify({
        location: location || 'general search',
        query,
        preferences: filters
      })
    });
  }

  async getCrawledContent(location) {
    return this.makeRequest('/crawl_content', {
      method: 'POST',
      body: JSON.stringify({ location })
    });
  }

  // Content Interaction
  async saveContent(userId, contentId) {
    return this.makeRequest(`/user_profile/${userId}/saved`, {
      method: 'POST',
      body: JSON.stringify({ contentId })
    });
  }

  async removeSavedContent(userId, contentId) {
    return this.makeRequest(`/user_profile/${userId}/saved/${contentId}`, {
      method: 'DELETE'
    });
  }

  async getSavedContent(userId) {
    return this.makeRequest(`/user_profile/${userId}/saved`, {
      method: 'GET'
    });
  }

  // News Tip Submission
  async submitNewsTip(tip) {
    return this.makeRequest('/editorial_queue', {
      method: 'POST',
      body: JSON.stringify({
        ...tip,
        type: 'user_submission',
        status: 'pending',
        submittedAt: new Date().toISOString()
      })
    });
  }

  // Content Feedback
  async submitFeedback(contentId, feedback) {
    return this.makeRequest('/content_distribution', {
      method: 'POST',
      body: JSON.stringify({
        contentId,
        action: 'feedback',
        feedback
      })
    });
  }

  // Analytics and Engagement
  async trackContentView(contentId, userId, location) {
    return this.makeRequest('/content_distribution', {
      method: 'POST',
      body: JSON.stringify({
        contentId,
        userId,
        location,
        action: 'view',
        timestamp: new Date().toISOString()
      })
    });
  }

  async trackContentEngagement(contentId, userId, action, location) {
    return this.makeRequest('/content_distribution', {
      method: 'POST',
      body: JSON.stringify({
        contentId,
        userId,
        location,
        action, // 'save', 'share', 'like', etc.
        timestamp: new Date().toISOString()
      })
    });
  }

  // Location Services
  async getLocationSuggestions(query) {
    // In production, this would integrate with Azure Maps
    return this.makeRequest('/research_agent', {
      method: 'POST',
      body: JSON.stringify({
        location: query,
        query: 'location validation',
        preferences: { type: 'location_lookup' }
      })
    });
  }

  // System Health
  async checkSystemHealth() {
    return this.makeRequest('/test_simple', {
      method: 'GET'
    });
  }

  // Editorial Queue (for editors)
  async getEditorialQueue(location, status = 'pending') {
    return this.makeRequest(`/editorial_queue/${location}?status=${status}`, {
      method: 'GET'
    });
  }

  async updateEditorialItem(itemId, updates) {
    return this.makeRequest(`/editorial_queue/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  // Real-time Features (future)
  async getNotifications(userId) {
    return this.makeRequest(`/user_profile/${userId}/notifications`, {
      method: 'GET'
    });
  }

  async markNotificationRead(userId, notificationId) {
    return this.makeRequest(`/user_profile/${userId}/notifications/${notificationId}`, {
      method: 'PUT',
      body: JSON.stringify({ read: true })
    });
  }
}

export const apiService = new ApiService();