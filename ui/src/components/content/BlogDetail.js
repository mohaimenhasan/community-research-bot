import React from 'react';
import { ArrowLeft, MapPin, Clock, Share2, Heart, MessageCircle, ExternalLink } from 'lucide-react';

const BlogDetail = ({ post, onBack, location }) => {
  if (!post) return null;

  // Parse the post content to extract sections
  const parseContent = (content) => {
    const sections = content.split('**').filter(section => section.trim());
    const parsedSections = [];

    for (let i = 0; i < sections.length; i += 2) {
      if (sections[i + 1]) {
        const title = sections[i].trim();
        const body = sections[i + 1].trim();
        parsedSections.push({ title, body });
      }
    }

    return parsedSections;
  };

  const sections = parseContent(post.content);
  const categoryIcons = {
    'GOVERNMENT & MUNICIPAL': '🏛️',
    'COMMUNITY EVENTS': '🎪',
    'LOCAL NEWS': '📰',
    'PUBLIC SERVICES': '🏢'
  };

  const getCategoryIcon = (title) => {
    for (const [category, icon] of Object.entries(categoryIcons)) {
      if (title.includes(category)) return icon;
    }
    return '📍';
  };

  const getCategoryColor = (title) => {
    if (title.includes('GOVERNMENT')) return 'bg-blue-600';
    if (title.includes('EVENTS')) return 'bg-purple-600';
    if (title.includes('NEWS')) return 'bg-red-600';
    if (title.includes('SERVICES')) return 'bg-green-600';
    return 'bg-gray-600';
  };

  const expandContent = (content) => {
    // Add more detailed information for blog view
    const expanded = {
      'PIKE PLACE MARKET FESTIVAL': {
        details: "Join us for the most anticipated food festival of the year! This weekend's Pike Place Market Festival brings together Seattle's finest artisans, local food vendors, and musicians for an unforgettable experience.",
        schedule: "Saturday 10:00 AM - 6:00 PM",
        location: "Pike Place Market, 85 Pike St, Seattle, WA 98101",
        highlights: [
          "30+ local food vendors featuring Pacific Northwest cuisine",
          "Live acoustic performances throughout the day",
          "Artisan coffee tastings from Seattle's top roasters",
          "Local craft vendors and artist booths",
          "Family-friendly activities and entertainment"
        ],
        tickets: "Free admission - just show up!",
        parking: "Limited street parking available. We recommend public transit or rideshare."
      },
      'SEATTLE CITY COUNCIL': {
        details: "Tonight's city council meeting features crucial votes that will shape Seattle's housing future. The proposed affordable housing initiative could approve thousands of new units across the city.",
        schedule: "Tonight at 6:00 PM",
        location: "Seattle City Hall, 600 4th Ave, Seattle, WA 98104",
        agenda: [
          "Public comment period (6:00-6:30 PM)",
          "Affordable housing proposal vote",
          "Transportation infrastructure updates",
          "Community development funding allocation",
          "Q&A with council members"
        ],
        participate: "Public comments welcome - arrive early for speaking slots",
        streaming: "Live stream available on Seattle Channel"
      },
      'LIGHT RAIL EXPANSION': {
        details: "Major breakthrough for Seattle transit! The long-awaited Capitol Hill to West Seattle light rail extension has received full funding approval and construction timeline.",
        timeline: "Construction begins next month, completion expected 2027",
        route: "Capitol Hill → SoDo → Georgetown → West Seattle",
        impact: [
          "Reduces commute time by 35-45 minutes",
          "Serves 15,000+ daily riders at full capacity",
          "Connects previously underserved neighborhoods",
          "Reduces downtown traffic congestion",
          "Creates 2,000+ construction jobs"
        ],
        funding: "$3.2 billion federal and local funding package",
        updates: "Regular construction updates at soundtransit.org"
      },
      'SEATTLE PUBLIC LIBRARY': {
        details: "Your Seattle Public Library just got a major upgrade! New 24/7 study spaces, gaming setups, and tech lending programs are now available to all cardholders.",
        newFeatures: [
          "24/7 study pods with individual climate control",
          "Gaming stations with PS5, Xbox, and VR setups",
          "WiFi hotspot lending program (7-day checkout)",
          "Laptop and tablet rental service",
          "Maker spaces with 3D printers and laser cutters",
          "Recording studios for podcasts and music"
        ],
        access: "All services free with Seattle library card",
        locations: "Available at Central Library and select branches",
        booking: "Reserve spaces online at spl.org"
      }
    };

    // Find matching expanded content
    for (const [key, expandedInfo] of Object.entries(expanded)) {
      if (content.includes(key)) {
        return expandedInfo;
      }
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={onBack}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Feed</span>
            </button>

            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <MapPin className="w-4 h-4" />
              <span>{location}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Blog Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {sections.map((section, index) => {
          const expandedInfo = expandContent(section.body);
          const icon = getCategoryIcon(section.title);
          const colorClass = getCategoryColor(section.title);

          return (
            <article key={index} className="bg-white rounded-xl shadow-lg mb-8 overflow-hidden">
              {/* Article Header */}
              <div className={`${colorClass} text-white p-6`}>
                <div className="flex items-center space-x-3 mb-4">
                  <span className="text-2xl">{icon}</span>
                  <h1 className="text-2xl font-bold">{section.title}</h1>
                </div>

                {/* Engagement Stats */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-6 text-white/90">
                    <div className="flex items-center space-x-2">
                      <Heart className="w-5 h-5" />
                      <span>{Math.floor(Math.random() * 100) + 50}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <MessageCircle className="w-5 h-5" />
                      <span>{Math.floor(Math.random() * 30) + 10}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Share2 className="w-5 h-5" />
                      <span>Share</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 text-white/80 text-sm">
                    <Clock className="w-4 h-4" />
                    <span>{Math.floor(Math.random() * 60) + 10}m ago</span>
                  </div>
                </div>
              </div>

              {/* Article Body */}
              <div className="p-6">
                {/* Main Content */}
                <div className="prose prose-lg max-w-none mb-8">
                  <p className="text-gray-700 leading-relaxed text-lg">
                    {section.body.split('\\n')[0]}
                  </p>
                </div>

                {/* Expanded Information */}
                {expandedInfo && (
                  <div className="space-y-6">
                    {expandedInfo.details && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-blue-900 mb-2">Details</h3>
                        <p className="text-blue-800">{expandedInfo.details}</p>
                      </div>
                    )}

                    {expandedInfo.schedule && (
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-green-900 mb-2">When</h3>
                        <p className="text-green-800">{expandedInfo.schedule}</p>
                      </div>
                    )}

                    {expandedInfo.location && (
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-purple-900 mb-2">Where</h3>
                        <p className="text-purple-800">{expandedInfo.location}</p>
                      </div>
                    )}

                    {expandedInfo.highlights && (
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-yellow-900 mb-3">Highlights</h3>
                        <ul className="space-y-2">
                          {expandedInfo.highlights.map((highlight, idx) => (
                            <li key={idx} className="flex items-start space-x-2 text-yellow-800">
                              <span className="text-yellow-600 mt-1">•</span>
                              <span>{highlight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {expandedInfo.agenda && (
                      <div className="bg-indigo-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-indigo-900 mb-3">Agenda</h3>
                        <ul className="space-y-2">
                          {expandedInfo.agenda.map((item, idx) => (
                            <li key={idx} className="flex items-start space-x-2 text-indigo-800">
                              <span className="text-indigo-600 mt-1">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {expandedInfo.newFeatures && (
                      <div className="bg-emerald-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-emerald-900 mb-3">New Features</h3>
                        <ul className="space-y-2">
                          {expandedInfo.newFeatures.map((feature, idx) => (
                            <li key={idx} className="flex items-start space-x-2 text-emerald-800">
                              <span className="text-emerald-600 mt-1">•</span>
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {expandedInfo.impact && (
                      <div className="bg-orange-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-orange-900 mb-3">Community Impact</h3>
                        <ul className="space-y-2">
                          {expandedInfo.impact.map((impact, idx) => (
                            <li key={idx} className="flex items-start space-x-2 text-orange-800">
                              <span className="text-orange-600 mt-1">•</span>
                              <span>{impact}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Call to Action */}
                    <div className="bg-gray-100 p-4 rounded-lg">
                      <h3 className="font-semibold text-gray-900 mb-2">Get Involved</h3>
                      <div className="flex items-center space-x-4">
                        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
                          <ExternalLink className="w-4 h-4" />
                          <span>Learn More</span>
                        </button>
                        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                          Share with Friends
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
};

export default BlogDetail;