import React, { useState } from 'react';
import { ScoreDetail } from '../types';

interface ScoreCardProps {
    score: ScoreDetail;
    label: string;
}

const ScoreCard: React.FC<ScoreCardProps> = ({ score, label }) => {
  const [isOpen, setIsOpen] = useState(false);

  const getColor = (val: number): string => {
    if (val >= 80) return 'text-green-600 stroke-green-600';
    if (val >= 50) return 'text-yellow-600 stroke-yellow-600';
    return 'text-red-600 stroke-red-600';
  };

  const radius = 30;
  const stroke = 4;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score.score / 100) * circumference;

  return (
    <>
        <div 
            onClick={() => setIsOpen(true)}
            className="flex flex-col items-center p-4 bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md hover:border-gray-200 transition-all cursor-pointer group relative"
        >
            <div className="absolute top-2 right-2 text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                </svg>
            </div>

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
                <div className={`absolute text-xl font-light ${getColor(score.score).split(' ')[0]}`}>
                    {score.score}
                </div>
            </div>
            <div className="text-gray-400 text-xs uppercase tracking-widest font-medium text-center">
                {label}
            </div>
            <div className="mt-1 text-xs text-gray-500 font-medium bg-gray-50 px-2 py-0.5 rounded-full">
                {score.level}
            </div>
        </div>

        {/* Simple Modal for Details */}
        {isOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4" onClick={() => setIsOpen(false)}>
                <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl animate-fade-in-up" onClick={(e) => e.stopPropagation()}>
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h3 className="text-xl font-semibold text-gray-900">{label} Details</h3>
                            <div className={`text-sm font-medium mt-1 ${getColor(score.score).split(' ')[0]}`}>
                                Score: {score.score} - {score.level}
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-gray-600">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <div className="space-y-4">
                        {score.positives && score.positives.length > 0 && (
                            <div>
                                <h4 className="text-xs font-bold text-green-700 uppercase tracking-wider mb-2">Positives</h4>
                                <ul className="space-y-2">
                                    {score.positives.map((item, idx) => (
                                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                                            <svg className="w-5 h-5 text-green-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                            </svg>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {score.negatives && score.negatives.length > 0 && (
                            <div>
                                <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">Improvements Needed</h4>
                                <ul className="space-y-2">
                                    {score.negatives.map((item, idx) => (
                                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                                            <svg className="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                            </svg>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        
                        {(!score.positives?.length && !score.negatives?.length) && (
                            <p className="text-sm text-gray-500 italic">No detailed breakdown available.</p>
                        )}
                    </div>
                </div>
            </div>
        )}
    </>
  );
};

export default ScoreCard;
