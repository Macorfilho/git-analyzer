import React from 'react';
import SearchBar from './components/SearchBar';
import SuggestionList from './components/SuggestionList';
import RepositoryList from './components/RepositoryList';
import ScoreDisplay from './components/ScoreDisplay';
import { useGithubAnalysis } from './hooks/useGithubAnalysis';
import ReactMarkdown from 'react-markdown';

const App: React.FC = () => {
  const { data, loading, error, status, analyzeProfile } = useGithubAnalysis();

  const getStatusMessage = () => {
      switch(status) {
          case 'queued': return 'Analysis queued...';
          case 'started': return 'Analyzing profile (this may take a minute)...';
          case 'finished': return 'Analysis complete!';
          case 'failed': return 'Analysis failed.';
          default: return 'Loading...';
      }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900 font-sans selection:bg-black selection:text-white">
      <main className="container mx-auto px-4 py-24 max-w-4xl">
        
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-thin tracking-tight mb-4">
            GitHub Profile <span className="font-normal">Analyzer</span>
          </h1>
          <p className="text-lg text-gray-500 font-light max-w-xl mx-auto">
            Receive a professional assessment of your GitHub presence and actionable steps to improve your visibility.
          </p>
        </header>

        {/* Search */}
        <SearchBar onSearch={analyzeProfile} loading={loading} />
        
        {/* Loading Status Indicator */}
        {loading && (
            <div className="mt-8 text-center">
                <div className="inline-block animate-pulse text-sm font-medium text-gray-400 uppercase tracking-widest">
                    {getStatusMessage()}
                </div>
            </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 text-red-600 px-6 py-4 rounded-xl border border-red-100 text-center mt-8 max-w-lg mx-auto" role="alert">
            <span className="block font-medium">{error}</span>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="animate-fade-in-up mt-16 space-y-16">
            
            {/* Summary Section */}
            <div>
               <div className="flex flex-col md:flex-row md:items-baseline md:justify-between mb-8">
                  <h2 className="text-3xl font-bold tracking-tight text-gray-900">Analysis Results</h2>
                  <span className="text-sm font-medium text-gray-500">
                      Analysis Report: {data.username} • {data.details?.repo_count ?? 0} Repositories
                  </span>
               </div>
               
               {/* Score Display Component */}
               <div className="flex flex-col-reverse lg:flex-row gap-16 mb-24 items-stretch">
                   <div className="flex-1 flex flex-col justify-center">
                       <h3 className="text-sm font-bold uppercase tracking-widest text-gray-400 mb-6">Executive Summary</h3>
                       <div className="prose prose-lg text-gray-600 max-w-none leading-relaxed">
                          <ReactMarkdown>{data.summary}</ReactMarkdown>
                       </div>
                   </div>
                   
                   <div className="hidden lg:block w-px bg-gray-100 mx-4"></div>

                   <div className="shrink-0 lg:w-72 flex flex-col items-center justify-center">
                       <span className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-4">Overall Score</span>
                       <div className="text-9xl font-thin tracking-tighter text-gray-900 mb-6 leading-none">
                           {data.overall_score.score}
                       </div>
                       
                       <div className={`px-5 py-2 rounded-full text-sm font-medium mb-10 ${
                            data.overall_score.score >= 80 ? 'bg-emerald-50 text-emerald-700' :
                            data.overall_score.score >= 50 ? 'bg-amber-50 text-amber-700' :
                            'bg-rose-50 text-rose-700'
                       }`}>
                           {data.overall_score.level}
                       </div>
                       
                       <div className="w-full flex justify-between gap-8 px-4">
                           <div className="flex flex-col items-center">
                               <span className="text-xs text-gray-400 uppercase tracking-wide mb-1">Potential</span>
                               <span className="font-medium text-gray-900">High</span>
                           </div>
                           <div className="flex flex-col items-center">
                               <span className="text-xs text-gray-400 uppercase tracking-wide mb-1">Market Ready</span>
                               <span className="font-medium text-gray-900">{data.overall_score.score > 70 ? 'Yes' : 'No'}</span>
                           </div>
                       </div>
                   </div>
               </div>

               <div className="mb-12">
                    <h3 className="text-2xl font-bold mb-8 text-gray-900 tracking-tight">Detailed Metrics</h3>
                    <ScoreDisplay report={data} />
               </div>
            </div>
            
            {/* Repositories Section */}
            {data.details?.repositories && (
                <RepositoryList repositories={data.details.repositories} />
            )}

            {/* Suggestions & Roadmap Section */}
            <SuggestionList 
                suggestions={data.suggestions} 
                roadmap={data.details?.career_roadmap}
            />

          </div>
        )}
      </main>
    </div>
  );
}

export default App;