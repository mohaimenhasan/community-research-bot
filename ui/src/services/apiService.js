// API Service for Community Hub
// Connects to Azure Functions backend

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://commhub-func-cnbkczf6a4ctdhcz.westus2-01.azurewebsites.net/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    // Disable demo mode - use real Azure Functions backend
    this.isDemoMode = false;
    console.log(`API Service initialized with baseURL: ${this.baseURL}`);
  }

  async makeRequest(endpoint, options = {}) {
    // Always use real API calls - demo mode disabled
    console.log(`Making API request to: ${this.baseURL}${endpoint}`);

    // Remove demo mode check - always make real requests

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

      // Handle user profile 404s gracefully - these are expected when profile doesn't exist
      if (response.status === 404 && endpoint.includes('/user_profile/')) {
        return null; // Return null for non-existent user profiles
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      // Don't fallback to mock - throw the real error so we can see what's wrong
      throw error;
    }
  }

  getMockResponse(endpoint, options) {
    console.log(`Demo mode: Mocking response for ${endpoint}`);

    // Return appropriate mock responses based on endpoint
    if (endpoint.includes('/user_profile') && options.method === 'GET') {
      return null; // Simulate no existing profile
    }

    if (endpoint.includes('/user_profile') && (options.method === 'POST' || options.method === 'PUT')) {
      const body = options.body ? JSON.parse(options.body) : {};
      return {
        id: 'demo-user-123',
        ...body,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
    }

    if (endpoint.includes('/research_agent')) {
      return {
        agent_response: {
          choices: [{
            message: {
              content: `**🏛️ CITY GOVERNMENT & TOWN HALL MEETINGS:**
• **Town Hall Meeting - Community Budget Review** - Monday 7:00 PM at City Hall, discussing next year's community development budget and infrastructure projects.
• **Parks & Recreation Advisory Committee** - Wednesday 6:30 PM, reviewing proposed park improvements and summer programming.
• **Planning Commission Public Hearing** - Thursday 7:00 PM, discussing new housing development proposals and zoning updates.

**🎪 COMMUNITY EVENTS & FESTIVALS:**
• **Neighborhood Block Party** - Saturday 2:00-8:00 PM on Main Street, featuring local vendors, live music, and family activities.
• **Farmers Market Grand Opening** - Sunday 9:00 AM-2:00 PM, celebrating the new location with special vendors and cooking demonstrations.
• **Community Clean-Up Day** - Saturday 10:00 AM, volunteers needed for neighborhood beautification project with BBQ lunch provided.

**🎨 CULTURAL & ARTS EVENTS:**
• **Local Artist Gallery Walk** - Friday 6:00-9:00 PM, showcasing work from 12 neighborhood artists at various downtown venues.
• **Community Theater Auditions** - Tuesday & Wednesday 7:00 PM, seeking actors for upcoming production of "Our Town".
• **Poetry Reading Night** - Thursday 7:30 PM at the library, featuring local poets and open mic opportunities.`
            }
          }],
          location_specific: true,
          sources_crawled: [
            'City Website',
            'Local Community Center',
            'Parks Department',
            'Local News',
            'Event Calendars'
          ]
        },
        metadata: {
          timestamp: new Date().toISOString(),
          location: 'Demo Location'
        }
      };
    }

    // Default mock response
    return { success: true, message: 'Demo mode response' };
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