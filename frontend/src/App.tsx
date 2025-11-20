import React from 'react';
import SearchBar from './components/SearchBar';
import ScoreCard from './components/ScoreCard';
import SuggestionList from './components/SuggestionList';
import { useGithubAnalysis } from './hooks/useGithubAnalysis';
import ReactMarkdown from 'react-markdown';

const App: React.FC = () => {
  const { data, loading, error, analyzeProfile } = useGithubAnalysis();

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

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded relative mb-8 text-center" role="alert">
            <span className="block sm:inline font-medium">{error}</span>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="animate-fade-in-up">
            
            {/* Summary Section */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 mb-12">
               <div className="flex flex-col md:flex-row items-center justify-between mb-8">
                  <div>
                      <h2 className="text-3xl font-light mb-1">Results for <span className="font-semibold">{data.username}</span></h2>
                      <div className="prose prose-sm text-gray-400 max-w-none">
                        <ReactMarkdown>{data.summary}</ReactMarkdown>
                      </div>
                  </div>
                  <div className="mt-4 md:mt-0">
                      <span className="inline-block px-4 py-1 bg-gray-100 text-gray-600 rounded-full text-sm font-medium">
                          {data.details?.repo_count ?? 0} Repositories Scanned
                      </span>
                  </div>
               </div>

               <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <ScoreCard score={data.overall_score} label="Overall Score" />
                  <ScoreCard score={data.profile_score} label="Profile Health" />
                  <ScoreCard score={data.readme_score} label="README Quality" />
                  <ScoreCard score={data.repo_quality_score} label="Repo Standards" />
               </div>
            </div>

            {/* Suggestions Section */}
            <SuggestionList suggestions={data.suggestions} />

          </div>
        )}
      </main>
    </div>
  );
}

export default App;
