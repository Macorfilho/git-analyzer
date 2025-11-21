import React from 'react';
import { Repository } from '../types';
import MaturityBadge from './MaturityBadge';

interface RepositoryListProps {
    repositories: Repository[];
}

const RepositoryList: React.FC<RepositoryListProps> = ({ repositories }) => {
    if (!repositories || repositories.length === 0) return null;

    // Sort by maturity score desc
    const sortedRepos = [...repositories].sort((a, b) => b.maturity_score - a.maturity_score);

    return (
        <div className="mb-12">
            <h3 className="text-xl font-light mb-6 text-gray-900 tracking-tight">Top Repositories</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sortedRepos.slice(0, 6).map((repo) => (
                    <div key={repo.name} className="p-4 bg-white rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-2">
                            <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 font-medium hover:underline truncate pr-2">
                                {repo.name}
                            </a>
                            <MaturityBadge label={repo.maturity_label} score={repo.maturity_score} />
                        </div>
                        <p className="text-gray-500 text-sm mb-3 line-clamp-2 h-10">
                            {repo.description || "No description provided."}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-400">
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
