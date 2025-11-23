import React from 'react';
import { Repository } from '../types';
import MaturityBadge from './MaturityBadge';

interface RepositoryListProps {
    repositories: Repository[];
}

const RepositoryList: React.FC<RepositoryListProps> = ({ repositories }) => {
    if (!repositories || repositories.length === 0) return null;

    // Sort by maturity score desc (accessing score)
    const sortedRepos = [...repositories].sort((a, b) => b.maturity_score.score - a.maturity_score.score);

    const isGhostProject = (repo: Repository) => {
        const lastUpdate = new Date(repo.updated_at);
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        return lastUpdate < oneYearAgo;
    };

    return (
        <div className="mb-12">
            <h3 className="text-xl font-light mb-6 text-gray-900 tracking-tight">Top Repositories</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sortedRepos.slice(0, 6).map((repo) => (
                    <div key={repo.name} className="p-4 bg-white rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col h-full">
                        <div className="flex justify-between items-start mb-2">
                            <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 font-medium hover:underline truncate pr-2">
                                {repo.name}
                            </a>
                            <div className="flex items-center gap-2 flex-shrink-0">
                                {repo.maturity_score.score > 80 && (
                                    <span className="text-xs font-semibold bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Top Quality</span>
                                )}
                                {isGhostProject(repo) && (
                                    <span className="text-xs font-semibold bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">Ghost Project</span>
                                )}
                                <MaturityBadge label={repo.maturity_label} score={repo.maturity_score.score} />
                            </div>
                        </div>
                        
                        <p className="text-gray-500 text-sm mb-3 line-clamp-2 h-10">
                            {repo.description || "No description provided."}
                        </p>
                        
                        {/* Recommendations Section */}
                        {repo.recommendations && repo.recommendations.length > 0 && (
                             <div className="mb-4 p-3 bg-amber-50 rounded-md border border-amber-100">
                                <h4 className="text-xs font-bold text-amber-800 mb-1 uppercase tracking-wide">Fixes Needed:</h4>
                                <ul className="list-none space-y-1">
                                    {repo.recommendations.slice(0, 3).map((rec, i) => (
                                        <li key={i} className="text-xs text-amber-900 flex items-start gap-1.5">
                                             <span className="text-amber-500 mt-0.5">•</span>
                                             {rec}
                                        </li>
                                    ))}
                                </ul>
                             </div>
                        )}
                        
                        <div className="mt-auto flex items-center gap-4 text-xs text-gray-400">
                            {repo.language && (
                                <span className="flex items-center gap-1">
                                    <span className="w-2 h-2 rounded-full bg-gray-300"></span>
                                    {repo.language}
                                </span>
                            )}
                            <span>★ {repo.stargazers_count}</span>
                            <span>🍴 {repo.forks_count}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RepositoryList;
