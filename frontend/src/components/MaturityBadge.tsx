import React from 'react';

type MaturityLabel = "Production-Grade" | "Prototype" | "Hobby";

interface MaturityBadgeProps {
    label: MaturityLabel;
    score: number;
}

const MaturityBadge: React.FC<MaturityBadgeProps> = ({ label, score }) => {
    let colorClass = "bg-gray-100 text-gray-800 border-gray-200"; // Default Hobby
    let icon = "🎨";

    if (label === "Production-Grade") {
        colorClass = "bg-green-100 text-green-800 border-green-200";
        icon = "🏆";
    } else if (label === "Prototype") {
        colorClass = "bg-yellow-100 text-yellow-800 border-yellow-200";
        icon = "🛠️";
    }

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClass}`}>
            <span className="mr-1.5">{icon}</span>
            {label}
            <span className="ml-1.5 pl-1.5 border-l border-current opacity-75">
                {score}/100
            </span>
        </span>
    );
};

export default MaturityBadge;
