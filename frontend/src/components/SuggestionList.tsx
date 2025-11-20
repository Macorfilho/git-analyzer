import React from 'react';
import { Suggestion } from '../types';
import ReactMarkdown from 'react-markdown';

interface SuggestionListProps {
    suggestions: Suggestion[];
}

const SuggestionList: React.FC<SuggestionListProps> = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) return null;

  const getSeverityStyles = (severity: string) => {
    switch(severity) {
      case 'high': return 'border-red-500 text-red-600';
      case 'medium': return 'border-yellow-500 text-yellow-600';
      default: return 'border-blue-500 text-blue-600';
    }
  };

  return (
    <div className="mt-12">
      <h3 className="text-xl font-light mb-6 text-gray-900 tracking-tight">Actionable Suggestions</h3>
      <div className="space-y-4">
        {suggestions.map((suggestion, index) => {
            const severityStyle = getSeverityStyles(suggestion.severity);
            return (
                <div key={index} className={`p-5 bg-white border-l-2 shadow-sm rounded-r-lg ${severityStyle.split(' ')[0]}`}>
                    <div className="flex justify-between items-baseline mb-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                            {suggestion.category}
                        </span>
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full border capitalize ${severityStyle.includes('red') ? 'bg-red-50 border-red-100 text-red-600' : severityStyle.includes('yellow') ? 'bg-yellow-50 border-yellow-100 text-yellow-600' : 'bg-blue-50 border-blue-100 text-blue-600'}`}>
                            {suggestion.severity} Priority
                        </span>
                    </div>
                    <div className="prose prose-sm text-gray-600 font-light max-w-none leading-relaxed">
                        <ReactMarkdown>{suggestion.message}</ReactMarkdown>
                    </div>
                </div>
            );
        })}
      </div>
    </div>
  );
};

export default SuggestionList;
