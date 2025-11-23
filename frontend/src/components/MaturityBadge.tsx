import React from 'react';

type MaturityLabel = "Production-Grade" | "Prototype" | "Hobby";

interface MaturityBadgeProps {
    label: MaturityLabel;
    score: number;
}

const MaturityBadge: React.FC<MaturityBadgeProps> = ({ label, score }) => {
    let dotColor = "bg-gray-400"; // Default Hobby
    
    if (label === "Production-Grade") {
        dotColor = "bg-emerald-500";
    } else if (label === "Prototype") {
        dotColor = "bg-amber-400";
    }

    return (
        <span className="inline-flex items-center text-xs font-medium text-gray-600">
            <span className={`w-2 h-2 rounded-full mr-2 ${dotColor}`}></span>
            {label}
            <span className="ml-1.5 pl-1.5 border-l border-gray-300 text-gray-400">
                {score}
            </span>
        </span>
    );
};
export default MaturityBadge;
