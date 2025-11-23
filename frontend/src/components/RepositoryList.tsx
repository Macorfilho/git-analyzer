import React from 'react';
import { Repository } from '../types';
import MaturityBadge from './MaturityBadge';

interface RepositoryListProps {
    repositories: Repository[];
}

const RepositoryList: React.FC<RepositoryListProps> = ({ repositories }) => {

    if (!repositories || repositories.length === 0) return null;



    // Sort by maturity score desc

    const sortedRepos = [...repositories].sort((a, b) => b.maturity_score.score - a.maturity_score.score);



    const isGhostProject = (repo: Repository) => {

        const lastUpdate = new Date(repo.updated_at);

        const oneYearAgo = new Date();

        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

        return lastUpdate < oneYearAgo;

    };



    return (

        <div className="mb-20">

            <h3 className="text-2xl font-bold mb-8 text-gray-900 tracking-tight">Top Repositories</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {sortedRepos.slice(0, 6).map((repo) => (

                    <div key={repo.name} className="p-6 bg-white rounded-2xl border border-gray-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 flex flex-col h-full group">

                        <div className="flex justify-between items-start mb-4">

                            <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate pr-2">

                                {repo.name}

                            </a>

                            <div className="flex items-center gap-2 flex-shrink-0">

                                {isGhostProject(repo) && (

                                    <span className="w-2 h-2 rounded-full bg-gray-300" title="Ghost Project (Inactive)"></span>

                                )}

                                <MaturityBadge label={repo.maturity_label} score={repo.maturity_score.score} />

                            </div>

                        </div>



                        <p className="text-gray-500 text-sm mb-6 line-clamp-2 h-10 leading-relaxed">

                            {repo.description || "No description provided."}

                        </p>



                                                {/* Recommendations Section */}



                                                {repo.recommendations && repo.recommendations.length > 0 && (



                                                     <div className="mb-6 bg-gray-50 p-4 rounded-xl">



                                                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Suggested Improvements</h4>



                                                        <ul className="space-y-2">



                                                            {repo.recommendations.slice(0, 3).map((rec, i) => (



                                                                <li key={i} className="text-xs text-gray-600 flex items-start gap-2">



                                                                     <span className="text-amber-400 mt-0.5">•</span>



                                                                     {rec}



                                                                </li>



                                                            ))}



                                                        </ul>



                                                     </div>



                                                )}



                        <div className="mt-auto pt-4 border-t border-gray-50 flex items-center gap-6 text-xs text-gray-400 font-medium">

                            {repo.language && (

                                <span className="flex items-center gap-1.5">

                                    <span className="w-2 h-2 rounded-full bg-gray-200"></span>

                                    {repo.language}

                                </span>

                            )}

                            <span className="flex items-center gap-1">

                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>

                                {repo.stargazers_count}

                            </span>

                            <span className="flex items-center gap-1">

                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>

                                {repo.forks_count}

                            </span>

                        </div>

                    </div>

                ))}

            </div>

        </div>

    );

};

export default RepositoryList;
