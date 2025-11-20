export interface Suggestion {
    category: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
}

export interface AnalysisDetails {
    profile_details?: {
        readme_length?: number;
        [key: string]: unknown;
    };
    repo_count?: number;
    [key: string]: unknown;
}

export interface AnalysisReport {
    username: string;
    profile_score: number;
    readme_score: number;
    repo_quality_score: number;
    overall_score: number;
    summary: string;
    suggestions: Suggestion[];
    details: AnalysisDetails;
}

export interface ApiError {
    error: string;
    details?: string;
}
