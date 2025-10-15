import React from 'react';
import { RefreshCw, MapPin, Clock } from 'lucide-react';

const ContentFeed = ({ content, onRefresh, location }) => {
  if (!content) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No content available</p>
      </div>
    );
  }

  const agentResponse = content.agent_response;
  const contentText = agentResponse?.choices?.[0]?.message?.content;

  if (!contentText) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Unable to load content</p>
        <button onClick={onRefresh} className="btn-secondary mt-4">
          Try Again
        </button>
      </div>
    );
  }

  // Parse the Instagram-style content from our Research Agent
  const parseContent = (text) => {
    // Handle Research Agent discovery status
    if (text.includes('🔍 **Research Agent Discovery Status**')) {
      return [{
        title: 'Research Agent - Source Discovery',
        items: [
          'Identifying local information sources',
          'Cataloging government and municipal websites',
          'Mapping community event platforms',
          'Building content categorization pipeline',
          'Phase 1: Discovery and Classification Active'
        ]
      }];
    }

    // Split by section headers: **🏛️ GOVERNMENT & MUNICIPAL:** etc.
    const sectionPattern = /\*\*([🏛️🎪📰🏢].*?):\*\*/g;
    const sections = [];
    let lastIndex = 0;
    let match;

    while ((match = sectionPattern.exec(text)) !== null) {
      if (sections.length > 0) {
        // Add content from previous section
        const prevContent = text.substring(lastIndex, match.index).trim();
        if (prevContent) {
          sections[sections.length - 1].content = prevContent;
        }
      }

      sections.push({
        title: match[1].trim(),
        content: ''
      });
      lastIndex = sectionPattern.lastIndex;
    }

    // Add content for the last section
    if (sections.length > 0) {
      const lastContent = text.substring(lastIndex).trim();
      if (lastContent) {
        sections[sections.length - 1].content = lastContent;
      }
    }

    // Convert content to items for display
    return sections.map(section => {
      // Split content into paragraphs/posts
      const posts = section.content
        .split(/\n\s*\n/) // Split by double newlines
        .filter(post => post.trim().length > 0)
        .map(post => post.trim());

      return {
        title: section.title,
        items: posts.length > 0 ? posts : ['No content available for this section']
      };
    });
  };

  const sections = parseContent(contentText);

  return (
    <div className="space-y-6">
      {/* Header with refresh */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">
          Your Community Feed
        </h2>
        <button
          onClick={onRefresh}
          className="p-2 text-gray-400 hover:text-gray-600"
          aria-label="Refresh content"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Agent Summary */}
      {agentResponse.location_specific && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-bold">AI</span>
            </div>
            <div>
              <p className="text-sm text-blue-800 font-medium">
                Research Agent - Phase 1
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Discovered {sections.length} content categories for {location?.city}.
                Source discovery and classification in progress.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Content Sections */}
      <div className="space-y-4">
        {sections.map((section, index) => (
          <div key={index} className="card">
            <div className="p-4 border-b border-gray-100">
              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                <span>{getCategoryIcon(section.title)}</span>
                <span>{section.title}</span>
              </h3>
            </div>
            <div className="p-4">
              <div className="space-y-4">
                {section.items.slice(0, 3).map((item, itemIndex) => (
                  <div key={itemIndex} className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border-l-4 border-blue-500">
                    <div className="flex-1">
                      <p className="text-sm text-gray-800 leading-relaxed font-medium">
                        {item}
                      </p>
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-100">
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <button className="flex items-center space-x-1 hover:text-red-500">
                            <span>❤️</span>
                            <span>{Math.floor(Math.random() * 50) + 10}</span>
                          </button>
                          <button className="flex items-center space-x-1 hover:text-blue-500">
                            <span>💬</span>
                            <span>{Math.floor(Math.random() * 15) + 2}</span>
                          </button>
                          <button className="flex items-center space-x-1 hover:text-green-500">
                            <span>📤</span>
                            <span>Share</span>
                          </button>
                        </div>
                        <span className="text-xs text-gray-400">
                          {Math.floor(Math.random() * 60) + 5}m ago
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {section.items.length > 3 && (
                <button className="text-blue-600 text-sm font-medium mt-3 hover:text-blue-700">
                  View all {section.items.length} items
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Research Agent Status */}
      {agentResponse.research_agent_active && (
        <div className="card p-4">
          <h4 className="font-medium text-gray-900 mb-3">Research Agent Status</h4>
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-gray-700">Source Discovery: {agentResponse.discovery_status || 'Active'}</span>
            </div>
            {agentResponse.content_categories && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Content Categories:</p>
                <div className="flex flex-wrap gap-2">
                  {agentResponse.content_categories.map((category, index) => (
                    <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                      {category}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>Last updated: {new Date(content.metadata?.timestamp).toLocaleTimeString()}</span>
          </div>
          <div className="flex items-center space-x-1">
            <MapPin className="w-3 h-3" />
            <span>{location?.city}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to get category icons
const getCategoryIcon = (title) => {
  const iconMap = {
    '🏛️ GOVERNMENT & MUNICIPAL': '🏛️',
    '🎪 COMMUNITY EVENTS': '🎪',
    '📰 LOCAL NEWS': '📰',
    '🏢 PUBLIC SERVICES': '🏢',
    'CITY GOVERNMENT & TOWN HALL MEETINGS': '🏛️',
    'COMMUNITY EVENTS & FESTIVALS': '🎪',
    'CULTURAL & ARTS EVENTS': '🎨',
    'COMMUNITY MEETINGS & VOLUNTEER OPPORTUNITIES': '👥',
    'RECREATION & SPORTS': '🏃',
    'PERSONALIZED RECOMMENDATIONS': '🎯'
  };

  // Extract emoji from title if present
  const emojiMatch = title.match(/^([🏛️🎪📰🏢🎨👥🏃🎯])/);
  if (emojiMatch) {
    return emojiMatch[1];
  }

  return iconMap[title.toUpperCase()] || '📋';
};

export default ContentFeed;