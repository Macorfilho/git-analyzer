import React from 'react';

interface ScoreCardProps {
    score: number;
    label: string;
}

const ScoreCard: React.FC<ScoreCardProps> = ({ score, label }) => {
  const getColor = (score: number): string => {
    if (score >= 80) return 'text-green-600 stroke-green-600';
    if (score >= 50) return 'text-yellow-600 stroke-yellow-600';
    return 'text-red-600 stroke-red-600';
  };

  const radius = 30;
  const stroke = 4;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
        <div className="relative flex items-center justify-center mb-3">
            <svg
                height={radius * 2}
                width={radius * 2}
                className="transform -rotate-90"
            >
                <circle
                    stroke="currentColor"
                    className="text-gray-100"
                    strokeWidth={stroke}
                    fill="transparent"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
                <circle
                    stroke="currentColor"
                    className={`${getColor(score)} transition-all duration-1000 ease-out`}
                    strokeWidth={stroke}
                    strokeDasharray={circumference + ' ' + circumference}
                    style={{ strokeDashoffset }}
                    strokeLinecap="round"
                    fill="transparent"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
            </svg>
            <div className={`absolute text-xl font-light ${getColor(score).split(' ')[0]}`}>
                {score}
            </div>
        </div>
      <div className="text-gray-400 text-xs uppercase tracking-widest font-medium">
        {label}
      </div>
    </div>
  );
};

export default ScoreCard;
