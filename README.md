# Community Hub - AI-Powered Local News & Content Platform

## 🎯 Project Vision

Community Hub is an AI-powered platform that automatically discovers, curates, and delivers hyper-local news and community content to users based on their geographic location and interests. The platform combines intelligent web crawling, Azure AI Foundry Agents, and adaptive content discovery to create personalized community feeds.

## 🏗️ System Architecture

### Core Concept
**Location-Based Content Discovery + AI Curation + Human Editorial Control**

```
[User Location Input]
     ↓
[Research Agent with Vector Search]
  ├─ Adaptive Web Crawling
  ├─ Content Change Detection
  ├─ AI Summarization & Categorization
  └─ Structured Data Storage
     ↓
[Azure AI Search Vector Store]
     ↓
[Personalization Agent]
  ├─ User Interest Modeling
  ├─ Content Relevance Ranking
  └─ Geographic Content Spreading
     ↓
[Human Editorial Queue] → [Community Feeds]
     ↓
[Mobile-First App Experience]
```

## 🤖 Azure AI Foundry Agent System

### Primary Agents

1. **Research Agent** (`asst_Ij5hGoGiriNuG7VGLGIAZ0zi`)
   - Accepts location input (e.g., "Vancouver", "Toronto")
   - Searches internet for local news, events, community updates
   - Uses vector search for contextual awareness
   - Returns structured, categorized content

2. **Summarization Agent**
   - Processes raw crawled content
   - Generates human-readable summaries
   - Applies content quality filters (50+ character minimum)
   - Maintains source attribution and metadata

3. **Sentiment Analysis Agent**
   - Analyzes content tone and sentiment
   - Provides structured sentiment scoring
   - Helps prioritize positive community content

### Future Agents
- **Personalization Agent**: User preference learning and content ranking
- **Classification Agent**: Geographic hierarchy management (Local → Regional → Provincial → Federal)

## 📊 Adaptive Content Discovery

### Intelligent Crawling Frequency
- **Baseline**: Weekly crawling for all sources (n)
- **Change Detection**: Daily crawling when content changes detected (m)
- **Hot Content**: Hourly crawling (7am-12am) for rapidly changing sources
- **Auto-Revert**: Return to previous frequency after 30 days of no changes

### Content Quality Rules
- Minimum 50 characters for text content
- Images must have associated descriptive text
- Source categorization and metadata preservation
- Duplicate content detection and filtering

## 🌍 Geographic Content Distribution

### Community Hierarchy
```
Local → Local+ → Regional → Provincial → Federal
```

### Viral Content Algorithm
Content automatically spreads to neighboring communities based on engagement:
- **Local**: 25% user selection threshold
- **Local+**: 20% threshold
- **Regional**: 15% threshold
- **Provincial**: 10% threshold
- **Federal**: 5% threshold

## 👥 Human-in-the-Loop Editorial System

### Editorial Queue Management
- Geographic-based editor assignment
- Real-time content notifications
- Editorial review and approval workflow
- Scheduling system for steady content flow

### Publishing Controls
- **Publish Now**: Immediate publication
- **Scheduled Post**: Automatic time slot distribution (default)
- Content editing capabilities
- Source verification and fact-checking tools

## 📱 Mobile-First Application

### Core Features
- **Home**: Personalized community feed
- **Saved**: User bookmarked content
- **Submit**: Community news tip submission
- **Search**: Content discovery across locations
- **Settings**: Feed preferences and profile management

### User Onboarding
1. Username/password creation
2. Credit card verification
3. Primary location setting
4. Interest profiling through engagement

## 🛠️ Technical Implementation

### Current Infrastructure
- **Azure Function App**: `commhub-func` (Python 3.12, Flex Consumption)
- **Azure AI Foundry**: Agent orchestration and LLM processing
- **Azure AI Search**: Vector storage and semantic search
- **GitHub Actions**: Continuous deployment pipeline
- **Application Insights**: Monitoring and observability

### Function Endpoints
```
/api/research_agent      - Location-based content discovery
/api/summarize_events    - Content summarization
/api/analyze_sentiment   - Sentiment analysis
/api/fetch_news          - External news integration
/api/get_agent_status    - Health check and configuration
```

### Technology Stack
- **Backend**: Azure Functions (Python)
- **AI/ML**: Azure AI Foundry Agents
- **Search**: Azure AI Search (Vector Store)
- **Database**: Azure Cosmos DB (planned)
- **Frontend**: React Native (mobile-first)
- **Authentication**: Azure AD B2C
- **Monitoring**: Application Insights

## 🚀 Development Phases

### ✅ Phase 1: Foundation (Completed)
- Azure Function App deployment
- Azure AI Foundry Agent integration
- Basic research, summarization, and sentiment analysis functions
- CI/CD pipeline with GitHub Actions

### 🔄 Phase 2: Enhanced Agent Memory (In Progress)
- Vector search integration with Azure AI Search
- Contextual content discovery
- Enhanced research agent with local context awareness
- Adaptive crawling frequency implementation

### 📋 Phase 3: Content Pipeline (Planned)
- Web crawling automation
- Content change detection
- Editorial queue system
- Publishing workflow

### 📱 Phase 4: Mobile Application (Planned)
- React Native app development
- User authentication and profiles
- Personalized feed algorithms
- Community interaction features

### 🌐 Phase 5: Scale & Intelligence (Future)
- Multi-agent orchestration
- Machine learning recommendation engine
- Real-time content processing
- Advanced personalization

## 🎯 Business Model

### Revenue Streams
- Subscription-based access to curated local content
- Premium features for power users
- Partnership with local businesses and organizations
- Community-driven content monetization

### Value Propositions
- **For Users**: Hyper-local, AI-curated content discovery
- **For Communities**: Increased civic engagement and awareness
- **For Local Organizations**: Enhanced visibility and community reach
- **For Editors**: Efficient content curation tools

## 📈 Success Metrics

### Technical KPIs
- Agent response time and accuracy
- Content discovery coverage per location
- User engagement and retention rates
- Editorial efficiency improvements

### Business KPIs
- Monthly active users per community
- Content viral spread effectiveness
- Editor productivity metrics
- Revenue per user growth

## 🔮 Future Vision

Community Hub aims to become the definitive platform for local community engagement, combining the power of AI with human editorial oversight to create authentic, relevant, and timely community content experiences. The platform will evolve into a comprehensive ecosystem supporting local journalism, civic engagement, and community building at scale.

---

## 🚦 Getting Started

### Prerequisites
- Azure subscription with AI Foundry access
- GitHub account for CI/CD
- Python 3.12+ for local development

### Quick Deploy
1. Clone this repository
2. Configure Azure resources (see `CLAUDE.md` for details)
3. Set environment variables in Function App
4. Push to main branch to trigger deployment

### Local Development
```bash
cd function_app
func start
```

For detailed setup instructions, see `CLAUDE.md`.

---

**Built with Azure AI Foundry • Deployed on Azure Functions • Powered by Community**