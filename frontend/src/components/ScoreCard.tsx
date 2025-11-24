import React, { useState } from 'react';
import { ScoreDetail } from '../types';

interface ScoreCardProps {
    score: ScoreDetail;
    label: string;
}

const ScoreCard: React.FC<ScoreCardProps> = ({ score, label }) => {
  const [isOpen, setIsOpen] = useState(false);

  const getColor = (val: number): string => {
    if (val >= 80) return 'text-emerald-600 stroke-emerald-600';
    if (val >= 50) return 'text-amber-500 stroke-amber-500';
    return 'text-rose-500 stroke-rose-500';
  };

  const radius = 28;
  const stroke = 2.5;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score.score / 100) * circumference;

  // Determine if clickable
  const hasDetails = (score.positives && score.positives.length > 0) || (score.negatives && score.negatives.length > 0);

  return (
    <>
        <div
            onClick={() => hasDetails && setIsOpen(true)}
            className={`group flex flex-col items-center p-6 bg-gray-50 rounded-2xl transition-all relative ${hasDetails ? 'hover:bg-gray-100 cursor-pointer hover:shadow-md' : 'cursor-default'}`}
        >
            {hasDetails && (
                <div className="absolute top-3 right-3 text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>
                </div>
            )}

            <div className="relative flex items-center justify-center mb-4">
                <svg
                    height={radius * 2}
                    width={radius * 2}
                    className="transform -rotate-90"
                >
                    <circle
                        stroke="currentColor"
                        className="text-gray-200"
                        strokeWidth={stroke}
                        fill="transparent"
                        r={normalizedRadius}
                        cx={radius}
                        cy={radius}
                    />
                    <circle
                        stroke="currentColor"
                        className={`${getColor(score.score)} transition-all duration-1000 ease-out`}
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
                <div className={`absolute text-lg font-medium ${getColor(score.score).split(' ')[0]}`}>
                    {score.score}
                </div>
            </div>
            <div className="text-gray-900 text-sm font-medium text-center mb-1">
                {label}
            </div>
            <div className="text-xs text-gray-500 font-medium px-2 py-0.5 rounded-full">
                {score.level}
            </div>
        </div>

        {/* Minimal Modal */}
        {isOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm p-4" onClick={() => setIsOpen(false)}>
                <div className="bg-white rounded-3xl max-w-md w-full p-8 shadow-2xl ring-1 ring-gray-100 animate-scale-in relative" onClick={(e) => e.stopPropagation()}>
                    <button onClick={() => setIsOpen(false)} className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-gray-400">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>

                    <div className="mb-6">
                        <h3 className="text-xl font-bold text-gray-900">{label}</h3>
                        <div className={`text-sm font-medium mt-1 ${getColor(score.score).split(' ')[0]}`}>
                            Score: {score.score}/100 • {score.level}
                        </div>
                    </div>

                    <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
                        {score.positives && score.positives.length > 0 && (
                            <div>
                                <h4 className="text-xs font-bold text-emerald-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                                    Strengths
                                </h4>
                                <ul className="space-y-3 pl-1">
                                    {score.positives.map((item, idx) => (
                                        <li key={idx} className="flex items-start gap-3 text-sm text-gray-600 leading-relaxed">
                                            <svg className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {score.negatives && score.negatives.length > 0 && (
                            <div>
                                <h4 className="text-xs font-bold text-rose-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                                    Areas for Improvement
                                </h4>
                                <ul className="space-y-3 pl-1">
                                    {score.negatives.map((item, idx) => (
                                        <li key={idx} className="flex items-start gap-3 text-sm text-gray-600 leading-relaxed">
                                            <svg className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        )}
    </>
  );
};

export default ScoreCard;