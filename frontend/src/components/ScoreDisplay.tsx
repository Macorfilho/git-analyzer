import React from 'react';
import ScoreCard from './ScoreCard';
import { AnalysisReport } from '../types';

interface ScoreDisplayProps {
    report: AnalysisReport;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ report }) => {
    const scores = [
        { label: 'Overall', score: report.overall_score },
        { label: 'Profile Health', score: report.personal_readme_score },
        { label: 'Repo Docs', score: report.avg_repo_docs_score },
        { label: 'Repo Standards', score: report.repo_quality_score }, // This combines maturity and other quality aspects
        { label: 'Code Hygiene', score: report.avg_code_hygiene_score },
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {scores.map((s) => (
                <ScoreCard key={s.label} label={s.label} score={s.score} />
            ))}
        </div>
    );
};

export default ScoreDisplay;
