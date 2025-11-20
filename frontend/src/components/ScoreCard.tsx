import React from 'react';

interface ScoreCardProps {
    score: number;
    label: string;
}

const ScoreCard: React.FC<ScoreCardProps> = ({ score, label }) => {
  const getColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="text-center p-6 border border-gray-100 rounded-lg shadow-sm bg-white">
      <div className={`text-5xl font-thin mb-2 ${getColor(score)}`}>
        {score}
      </div>
      <div className="text-gray-500 text-sm uppercase tracking-wider font-medium">
        {label}
      </div>
    </div>
  );
};

export default ScoreCard;
