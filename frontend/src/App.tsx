import React from 'react';
import SearchBar from './components/SearchBar';
import ScoreCard from './components/ScoreCard';
import SuggestionList from './components/SuggestionList';
import RepositoryList from './components/RepositoryList';
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
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-black selection:text-white">
      <main className="container mx-auto px-4 py-16 max-w-4xl">
        
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
            <div className="mt-4 text-center text-gray-500 animate-pulse">
                {getStatusMessage()}
            </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded relative mb-8 text-center mt-8" role="alert">
            <span className="block sm:inline font-medium">{error}</span>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="animate-fade-in-up mt-12">
            
            {/* Summary Section */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 mb-12">
               <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
                  <h2 className="text-3xl font-light">Results for <span className="font-semibold">{data.username}</span></h2>
                  <span className="inline-flex items-center px-3 py-1 text-sm font-medium bg-gray-100 text-gray-600 rounded-full whitespace-nowrap">
                      {data.details?.repo_count ?? 0} Repositories Scanned
                  </span>
               </div>
               
               <div className="prose prose-sm text-gray-500 max-w-none mb-8">
                  <ReactMarkdown>{data.summary}</ReactMarkdown>
               </div>

               <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <ScoreCard score={data.overall_score} label="Overall Score" />
                  <ScoreCard score={data.profile_score} label="Profile Health" />
                  <ScoreCard score={data.readme_score} label="README Quality" />
                  <ScoreCard score={data.repo_quality_score} label="Repo Standards" />
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