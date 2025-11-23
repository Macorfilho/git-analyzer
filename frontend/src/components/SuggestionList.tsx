import React from 'react';
import { Suggestion, CareerRoadmapStep } from '../types';
import ReactMarkdown from 'react-markdown';

interface SuggestionListProps {
    suggestions: Suggestion[];
    roadmap?: CareerRoadmapStep[];
}

const SuggestionList: React.FC<SuggestionListProps> = ({ suggestions, roadmap }) => {

  const getSeverityIcon = (severity: string) => {

    switch(severity) {

      case 'high': return '🔴';

      case 'medium': return '🟡';

      default: return '🔵';

    }

  };



  return (

    <div className="mt-20 space-y-20">

        {/* Career Roadmap Section */}

        {roadmap && roadmap.length > 0 && (

            <div>

                 <h3 className="text-2xl font-bold mb-8 text-gray-900 tracking-tight">Strategic Roadmap</h3>

                 <div className="bg-gray-50 rounded-2xl p-10 relative overflow-hidden">

                    <div className="absolute top-0 right-0 p-32 bg-blue-50 rounded-full blur-3xl opacity-50 pointer-events-none -mr-16 -mt-16"></div>

                    <div className="space-y-12 relative z-10">

                        {roadmap.map((step, index) => (

                            <div key={index} className="flex gap-8 group">

                                <div className="flex flex-col items-center">

                                    <div className="w-10 h-10 rounded-full bg-white border border-gray-200 text-gray-900 shadow-sm flex items-center justify-center font-bold text-sm shrink-0 z-10 group-hover:border-blue-500 group-hover:text-blue-600 transition-colors">

                                        {index + 1}

                                    </div>

                                    {index < roadmap.length - 1 && (

                                        <div className="w-px h-full bg-gray-200 my-2 group-hover:bg-blue-100 transition-colors"></div>

                                    )}

                                </div>

                                <div className="pb-2 pt-1">

                                    <h4 className="text-xl font-semibold text-gray-900 mb-2">{step.step}</h4>

                                    <p className="text-gray-600 text-base leading-relaxed max-w-2xl">{step.description}</p>

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

                <h3 className="text-2xl font-bold mb-8 text-gray-900 tracking-tight">Priority Actions</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {suggestions.map((suggestion, index) => {

                        const icon = getSeverityIcon(suggestion.severity);

                        return (

                            <div key={index} className="p-6 bg-white rounded-2xl border border-gray-100 hover:border-gray-200 shadow-sm hover:shadow-md transition-all">

                                <div className="flex justify-between items-baseline mb-4">

                                    <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">

                                        {suggestion.category}

                                    </span>

                                    <span className="text-xs font-medium px-2 py-1 bg-gray-50 rounded-md text-gray-500">

                                        {suggestion.severity} Priority

                                    </span>

                                </div>

                                <div className="prose prose-sm text-gray-600 font-light leading-relaxed">

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