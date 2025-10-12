import React from 'react';
import { Bookmark, Calendar, MapPin } from 'lucide-react';

const Saved = () => {
  // This would fetch saved content from API in production
  const savedItems = [];

  if (savedItems.length === 0) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center space-y-4 max-w-sm mx-auto">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
            <Bookmark className="w-8 h-8 text-gray-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">No saved items yet</h3>
            <p className="text-gray-600">
              When you save events and articles, they'll appear here for easy access.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Saved Items</h1>
        <p className="text-gray-600">Your bookmarked events and articles</p>
      </div>

      <div className="space-y-4">
        {savedItems.map((item, index) => (
          <div key={index} className="card p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                <p className="text-sm text-gray-600 mb-2">{item.summary}</p>
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{item.date}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MapPin className="w-3 h-3" />
                    <span>{item.location}</span>
                  </div>
                </div>
              </div>
              <button className="p-2 text-blue-600 hover:text-blue-700">
                <Bookmark className="w-4 h-4 fill-current" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Saved;