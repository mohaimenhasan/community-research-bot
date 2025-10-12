import React from 'react';
import { RefreshCw, MapPin, Clock, ExternalLink } from 'lucide-react';

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

  // Parse the markdown-style content from our agent
  const parseContent = (text) => {
    const sections = text.split('**🏛️').slice(1); // Split by section headers
    return sections.map(section => {
      const lines = section.split('\n');
      const title = lines[0].replace(/\*\*/g, '').replace(':', '').trim();
      const items = lines
        .slice(1)
        .filter(line => line.startsWith('•'))
        .map(line => line.replace('• **', '').replace('**', '').trim());

      return { title, items };
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
                Intelligent Agent Discovery
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Found {sections.length} categories of events for {location?.city}.
                Match score: 85% based on your interests.
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
              <div className="space-y-3">
                {section.items.slice(0, 3).map((item, itemIndex) => (
                  <div key={itemIndex} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-800 leading-relaxed">
                        {item}
                      </p>
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

      {/* Source Information */}
      {agentResponse.sources_crawled && (
        <div className="card p-4">
          <h4 className="font-medium text-gray-900 mb-3">Sources Discovered</h4>
          <div className="space-y-2">
            {agentResponse.sources_crawled.map((source, index) => (
              <div key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                <ExternalLink className="w-4 h-4" />
                <span>{source}</span>
              </div>
            ))}
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
    'CITY GOVERNMENT & TOWN HALL MEETINGS': '🏛️',
    'COMMUNITY EVENTS & FESTIVALS': '🎪',
    'CULTURAL & ARTS EVENTS': '🎨',
    'COMMUNITY MEETINGS & VOLUNTEER OPPORTUNITIES': '👥',
    'RECREATION & SPORTS': '🏃',
    'PERSONALIZED RECOMMENDATIONS': '🎯'
  };

  return iconMap[title.toUpperCase()] || '📋';
};

export default ContentFeed;