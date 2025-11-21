import React from 'react';
import { Suggestion, CareerRoadmapStep } from '../types';
import ReactMarkdown from 'react-markdown';

interface SuggestionListProps {
    suggestions: Suggestion[];
    roadmap?: CareerRoadmapStep[];
}

const SuggestionList: React.FC<SuggestionListProps> = ({ suggestions, roadmap }) => {
  const getSeverityStyles = (severity: string) => {
    switch(severity) {
      case 'high': return 'border-red-500 text-red-600';
      case 'medium': return 'border-yellow-500 text-yellow-600';
      default: return 'border-blue-500 text-blue-600';
    }
  };

  return (
    <div className="mt-12 space-y-12">
        {/* Career Roadmap Section */}
        {roadmap && roadmap.length > 0 && (
            <div>
                 <h3 className="text-xl font-light mb-6 text-gray-900 tracking-tight flex items-center gap-2">
                    <span>🚀</span> Career Roadmap
                 </h3>
                 <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-8 border border-blue-100">
                    <div className="space-y-8">
                        {roadmap.map((step, index) => (
                            <div key={index} className="relative flex gap-6">
                                <div className="flex flex-col items-center">
                                    <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm shrink-0 z-10">
                                        {index + 1}
                                    </div>
                                    {index < roadmap.length - 1 && (
                                        <div className="w-0.5 h-full bg-indigo-200 my-2"></div>
                                    )}
                                </div>
                                <div className="pb-2">
                                    <h4 className="text-lg font-medium text-indigo-900 mb-2">{step.step}</h4>
                                    <p className="text-indigo-700/80 text-sm leading-relaxed">{step.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                 </div>
            </div>
        )}

        {/* Suggestions Section */}
        {suggestions && suggestions.length > 0 && (
            <div>
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
        )}
    </div>
  );
};

export default SuggestionList;