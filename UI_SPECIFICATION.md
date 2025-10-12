# Community Hub - Mobile-First UI Implementation Specification

## 🎯 **Project Overview**

Building a complete mobile-first web application for Community Hub using Azure Static Web Apps, React, and full Azure integration with system assigned identities only.

## 🏗️ **Azure Architecture Design**

### **Core Azure Services**
```
┌─────────────────────────────────────────────────────────────────────┐
│                        COMMUNITY HUB ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────┤
│ Frontend: Azure Static Web Apps (React PWA)                          │
│ ├─ Authentication: Azure AD B2C + Social Providers                   │
│ ├─ CDN: Azure CDN for global content delivery                        │
│ └─ Custom Domain: communityhub.ai (configured in Static Web Apps)    │
├─────────────────────────────────────────────────────────────────────┤
│ Backend: Azure Functions (existing - commhub-func)                   │
│ ├─ research_agent: Event discovery with personalization              │
│ ├─ crawl_content: Adaptive web crawling system                       │
│ ├─ user_profile: User management and preferences                     │
│ └─ editorial_queue: Content publishing workflow                      │
├─────────────────────────────────────────────────────────────────────┤
│ Data Layer: Azure Cosmos DB + Azure Storage + Azure AI Search        │
│ ├─ Cosmos DB: User profiles, content, crawl schedules                │
│ ├─ Storage Account: Media files, crawl cache, user-generated content │
│ └─ AI Search: Vector search for content discovery and personalization│
├─────────────────────────────────────────────────────────────────────┤
│ Background Services: Azure Container Apps                            │
│ ├─ Adaptive Crawler: Scheduled content crawling (n, m, hourly)       │
│ ├─ Content Processor: LLM integration for content generation         │
│ └─ Notification Service: Editor alerts and user notifications        │
├─────────────────────────────────────────────────────────────────────┤
│ Authentication & Security                                             │
│ ├─ Azure AD B2C: User authentication (email, Microsoft, Google)      │
│ ├─ System Assigned Identities: All Azure service authentication      │
│ └─ Azure Key Vault: Secrets management (B2C configs only)            │
└─────────────────────────────────────────────────────────────────────┘
```

## 📱 **Mobile-First Application Features**

### **Core User Journey**
1. **Sign Up/Login**: Email, Microsoft, Google authentication
2. **Location Setup**: Primary location + additional locations
3. **Interest Selection**: Topics and content preferences
4. **Content Discovery**: Personalized community feed
5. **Engagement**: Save, share, tip submission, feedback
6. **Profile Management**: Settings, preferences, notifications

### **Application Screens**

#### **1. Authentication Flow**
- **Landing Page**: Hero section with sign-up CTA
- **Sign Up**: Three-step process (credentials, payment, location)
- **Login**: Social + email authentication
- **Profile Setup**: Location selection and interest profiling

#### **2. Main Application (Bottom Navigation)**
- **🏠 Home**: Personalized community news feed
- **💾 Saved**: Bookmarked articles and events
- **📝 Submit**: News tip submission with location
- **🔍 Search**: Content search across locations
- **⚙️ Settings**: Profile, preferences, notifications

#### **3. Content Interaction**
- **Article View**: Full content with save/share/feedback options
- **News Tip Submission**: Location-based content submission
- **Feedback System**: Rate content and provide tips
- **Geographic Feed**: Hot content spreading algorithm

## 🔧 **Technical Implementation Plan**

### **Phase 1: Azure Infrastructure Setup**

#### **1.1 Azure Static Web Apps**
```bash
# Create Static Web Apps with GitHub integration
az staticwebapp create \
  --name "communityhub-app" \
  --resource-group "community-research" \
  --source "https://github.com/mohaimenhasan/community-research-bot" \
  --location "West US 2" \
  --branch "main" \
  --app-location "/ui" \
  --api-location "/function_app" \
  --sku "Standard"

# Enable system assigned identity
az staticwebapp identity assign \
  --name "communityhub-app" \
  --resource-group "community-research"
```

#### **1.2 Azure AD B2C Tenant**
```bash
# Create B2C tenant (manual - Azure Portal required)
# Domain: communityhub.onmicrosoft.com
# Configure social identity providers (Google, Microsoft)
# Set up user flows for sign-up/sign-in
```

#### **1.3 Azure Cosmos DB**
```bash
# Create Cosmos DB for user data and content
az cosmosdb create \
  --name "communityhub-cosmos" \
  --resource-group "community-research" \
  --kind "GlobalDocumentDB" \
  --locations regionName="West US 2" failoverPriority=0 \
  --enable-automatic-failover true \
  --default-consistency-level "Session"

# Create databases and containers
az cosmosdb sql database create \
  --account-name "communityhub-cosmos" \
  --resource-group "community-research" \
  --name "CommunityHub"

# Users container
az cosmosdb sql container create \
  --account-name "communityhub-cosmos" \
  --resource-group "community-research" \
  --database-name "CommunityHub" \
  --name "Users" \
  --partition-key-path "/userId" \
  --throughput 400

# Content container
az cosmosdb sql container create \
  --account-name "communityhub-cosmos" \
  --resource-group "community-research" \
  --database-name "CommunityHub" \
  --name "Content" \
  --partition-key-path "/location" \
  --throughput 400

# Crawl schedules container
az cosmosdb sql container create \
  --account-name "communityhub-cosmos" \
  --resource-group "community-research" \
  --database-name "CommunityHub" \
  --name "CrawlSchedules" \
  --partition-key-path "/domain" \
  --throughput 400
```

#### **1.4 Azure Storage Account for Media**
```bash
# Create storage account for user content and media
az storage account create \
  --name "communityhubstorage" \
  --resource-group "community-research" \
  --location "West US 2" \
  --sku "Standard_LRS" \
  --kind "StorageV2" \
  --enable-hierarchical-namespace false

# Enable system assigned identity
az storage account update \
  --name "communityhubstorage" \
  --resource-group "community-research" \
  --assign-identity
```

#### **1.5 Azure Container Apps for Background Services**
```bash
# Create Container Apps environment
az containerapp env create \
  --name "communityhub-env" \
  --resource-group "community-research" \
  --location "West US 2"

# Deploy adaptive crawler (will create later)
# Deploy content processor
# Deploy notification service
```

### **Phase 2: Frontend Development**

#### **2.1 React PWA Structure**
```
ui/
├── public/
│   ├── manifest.json          # PWA configuration
│   ├── sw.js                  # Service worker for offline support
│   └── icons/                 # App icons for different platforms
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── SignUpWizard.jsx
│   │   │   └── SocialAuth.jsx
│   │   ├── layout/
│   │   │   ├── AppLayout.jsx
│   │   │   ├── BottomNavigation.jsx
│   │   │   └── Header.jsx
│   │   ├── content/
│   │   │   ├── ContentFeed.jsx
│   │   │   ├── ArticleCard.jsx
│   │   │   ├── ArticleView.jsx
│   │   │   └── SearchResults.jsx
│   │   ├── profile/
│   │   │   ├── LocationSelector.jsx
│   │   │   ├── InterestSelector.jsx
│   │   │   └── UserSettings.jsx
│   │   └── forms/
│   │       ├── NewsTipForm.jsx
│   │       └── FeedbackForm.jsx
│   ├── pages/
│   │   ├── Home.jsx            # Main feed
│   │   ├── Saved.jsx           # Bookmarked content
│   │   ├── Submit.jsx          # News tip submission
│   │   ├── Search.jsx          # Content search
│   │   └── Settings.jsx        # User preferences
│   ├── services/
│   │   ├── authService.js      # B2C authentication
│   │   ├── apiService.js       # Backend API calls
│   │   ├── locationService.js  # Location management
│   │   └── cacheService.js     # Offline support
│   ├── hooks/
│   │   ├── useAuth.js          # Authentication state
│   │   ├── useLocation.js      # Location management
│   │   └── useContent.js       # Content fetching
│   ├── context/
│   │   ├── AuthContext.js      # Global auth state
│   │   └── UserContext.js      # User preferences
│   └── utils/
│       ├── constants.js        # App configuration
│       └── helpers.js          # Utility functions
├── package.json
├── .env.example                # Environment variables template
└── staticwebapp.config.json    # Azure SWA configuration
```

#### **2.2 Key Technologies**
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS for mobile-first responsive design
- **State Management**: React Context + Custom Hooks
- **Authentication**: Azure AD B2C React SDK
- **PWA**: Service Workers for offline functionality
- **Icons**: Lucide React for consistent iconography
- **Maps**: Azure Maps for location selection

### **Phase 3: Backend Enhancement**

#### **3.1 New Azure Functions**
```python
# user_profile/__init__.py - User management
# editorial_queue/__init__.py - Content publishing workflow
# content_distribution/__init__.py - Geographic content spreading
# notification_service/__init__.py - Real-time notifications
# crawl_scheduler/__init__.py - Adaptive crawling management
```

#### **3.2 Database Schema (Cosmos DB)**
```json
// Users Collection
{
  "id": "user_12345",
  "userId": "user_12345",
  "email": "user@example.com",
  "primaryLocation": {
    "city": "Vancouver",
    "province": "BC",
    "country": "Canada",
    "coordinates": [49.2827, -123.1207]
  },
  "additionalLocations": [],
  "interests": ["local government", "sports", "culture"],
  "preferences": {
    "notificationSettings": {},
    "contentFilters": {}
  },
  "subscription": {
    "status": "active",
    "tier": "premium"
  },
  "createdAt": "2025-10-12T..."
}

// Content Collection
{
  "id": "content_12345",
  "location": "vancouver_bc",
  "title": "City Council Meeting Minutes",
  "content": "...",
  "source": "vancouver.ca",
  "category": "government",
  "publishedAt": "2025-10-12T...",
  "engagement": {
    "views": 150,
    "saves": 25,
    "shares": 10
  },
  "status": "published",
  "editorId": "editor_123"
}

// CrawlSchedules Collection
{
  "id": "schedule_123",
  "domain": "vancouver.ca",
  "url": "https://vancouver.ca/news",
  "crawlFrequency": "weekly", // weekly, daily, hourly
  "lastCrawl": "2025-10-12T...",
  "lastChange": "2025-10-10T...",
  "changeDetected": false,
  "rules": {
    "minTextLength": 50,
    "requireImageText": true
  }
}
```

## 🚀 **Implementation Roadmap**

### **Week 1: Infrastructure Setup**
- [ ] Create Azure Static Web Apps
- [ ] Set up Azure AD B2C tenant with social providers
- [ ] Configure Cosmos DB with containers
- [ ] Set up Azure Storage for media files
- [ ] Configure system assigned identities

### **Week 2: Authentication & User Management**
- [ ] Implement B2C authentication flow
- [ ] Build user registration wizard (credentials, payment, location)
- [ ] Create user profile management system
- [ ] Implement location selection with Azure Maps

### **Week 3: Core UI Development**
- [ ] Build responsive mobile-first layout
- [ ] Implement bottom navigation
- [ ] Create content feed with infinite scroll
- [ ] Build article view with interaction options

### **Week 4: Content Integration**
- [ ] Connect frontend to existing backend functions
- [ ] Implement personalized content discovery
- [ ] Build search functionality
- [ ] Create news tip submission form

### **Week 5: Advanced Features**
- [ ] Implement adaptive crawling system
- [ ] Build editorial queue for human oversight
- [ ] Create content spreading algorithm (Local → Regional → Federal)
- [ ] Add offline PWA capabilities

### **Week 6: Testing & Deployment**
- [ ] End-to-end testing across devices
- [ ] Performance optimization
- [ ] Security review
- [ ] Production deployment

## 🔐 **Security & Authentication**

### **Azure AD B2C Configuration**
```json
{
  "clientId": "{B2C_CLIENT_ID}",
  "authority": "https://communityhub.b2clogin.com/communityhub.onmicrosoft.com/B2C_1_signupsignin",
  "knownAuthorities": ["communityhub.b2clogin.com"],
  "redirectUri": "https://communityhub.ai/auth/callback",
  "scopes": ["openid", "profile", "email"],
  "socialProviders": ["google", "microsoft"]
}
```

### **System Assigned Identity Architecture**
- Static Web Apps ← Identity → Function Apps
- Function Apps ← Identity → Cosmos DB
- Function Apps ← Identity → Storage Account
- Function Apps ← Identity → Azure AI Services
- Container Apps ← Identity → All Azure Services

## 📊 **Success Metrics**

### **Technical KPIs**
- Page load time < 2 seconds
- Offline functionality for 24 hours
- 99.9% uptime
- Cross-browser compatibility

### **User Experience KPIs**
- User registration completion rate > 80%
- Daily active users per community
- Content engagement (save/share) rates
- Editor productivity improvements

## 💡 **Next Steps**

Ready to start implementation? I'll begin with:

1. **Azure infrastructure setup** using az CLI
2. **React PWA foundation** with authentication
3. **Integration with existing backend functions**
4. **Step-by-step implementation** with regular testing

Would you like me to proceed with Phase 1 (Infrastructure Setup)?