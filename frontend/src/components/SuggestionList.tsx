import React from 'react';
import { Suggestion } from '../types';
import ReactMarkdown from 'react-markdown';

interface SuggestionListProps {
    suggestions: Suggestion[];
}

const SuggestionList: React.FC<SuggestionListProps> = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) return null;

  const getSeverityColor = (severity: string): string => {
    switch(severity) {
      case 'high': return 'border-l-4 border-red-500 bg-red-50';
      case 'medium': return 'border-l-4 border-yellow-500 bg-yellow-50';
      default: return 'border-l-4 border-blue-500 bg-blue-50';
    }
  };

  return (
    <div className="mb-12">
      <h3 className="text-2xl font-light mb-6 text-gray-900">Actionable Suggestions</h3>
      <div className="grid gap-4">
        {suggestions.map((suggestion, index) => (
          <div key={index} className={`p-4 rounded-r-md ${getSeverityColor(suggestion.severity)}`}>
             <div className="flex justify-between items-start">
                <div>
                    <span className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-1 block">
                        {suggestion.category}
                    </span>
                    <div className="prose prose-sm text-gray-800 font-light max-w-none">
                        <ReactMarkdown>{suggestion.message}</ReactMarkdown>
                    </div>
                </div>
                <span className="text-xs font-medium px-2 py-1 bg-white rounded-full border border-gray-200 text-gray-500 capitalize">
                    {suggestion.severity} Priority
                </span>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuggestionList;
