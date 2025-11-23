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

  const stroke = 2.5; // Thinner stroke

  const normalizedRadius = radius - stroke * 2;

  const circumference = normalizedRadius * 2 * Math.PI;

  const strokeDashoffset = circumference - (score.score / 100) * circumference;



  return (

    <>

        <div

            onClick={() => setIsOpen(true)}

            className="group flex flex-col items-center p-6 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors cursor-pointer relative"

        >

            <div className="absolute top-3 right-3 text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity">

                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">

                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />

                </svg>

            </div>



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

            <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-md p-4" onClick={() => setIsOpen(false)}>

                <div className="bg-white rounded-3xl max-w-sm w-full p-8 shadow-2xl ring-1 ring-gray-100 animate-scale-in" onClick={(e) => e.stopPropagation()}>

                    <div className="flex justify-between items-start mb-8">

                        <div>

                            <h3 className="text-2xl font-bold text-gray-900">{label}</h3>

                            <div className={`text-sm font-medium mt-1 ${getColor(score.score).split(' ')[0]}`}>

                                {score.score} / 100 • {score.level}

                            </div>

                        </div>

                        <button onClick={() => setIsOpen(false)} className="p-1 rounded-full hover:bg-gray-100 transition-colors">

                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-gray-500">

                                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />

                            </svg>

                        </button>

                    </div>



                    <div className="space-y-6">

                        {score.positives && score.positives.length > 0 && (

                            <div>

                                <h4 className="text-xs font-bold text-emerald-600 uppercase tracking-widest mb-3">Strengths</h4>

                                <ul className="space-y-3">

                                    {score.positives.map((item, idx) => (

                                        <li key={idx} className="flex items-start gap-3 text-sm text-gray-600 leading-relaxed">

                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />

                                            {item}

                                        </li>

                                    ))}

                                </ul>

                            </div>

                        )}



                        {score.negatives && score.negatives.length > 0 && (

                            <div>

                                <h4 className="text-xs font-bold text-rose-500 uppercase tracking-widest mb-3">Improvements</h4>

                                <ul className="space-y-3">

                                    {score.negatives.map((item, idx) => (

                                        <li key={idx} className="flex items-start gap-3 text-sm text-gray-600 leading-relaxed">

                                            <div className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 shrink-0" />

                                            {item}

                                        </li>

                                    ))}

                                </ul>

                            </div>

                        )}



                        {(!score.positives?.length && !score.negatives?.length) && (

                            <p className="text-sm text-gray-400 text-center py-4">No detailed breakdown available.</p>

                        )}

                    </div>

                </div>

            </div>

        )}

    </>

  );

};

export default ScoreCard;
