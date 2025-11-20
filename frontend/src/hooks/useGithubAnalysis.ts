import { useState } from 'react';
import { AnalysisReport, ApiError } from '../types';

interface UseGithubAnalysisResult {
    data: AnalysisReport | null;
    loading: boolean;
    error: string | null;
    analyzeProfile: (username: string) => Promise<void>;
}

export const useGithubAnalysis = (): UseGithubAnalysisResult => {
  const [data, setData] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeProfile = async (username: string) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await fetch(`http://localhost:5001/api/analyze/${username}`);
      
      if (!response.ok) {
        const errData = (await response.json()) as ApiError;
        throw new Error(errData.error || 'Failed to analyze profile');
      }

      const result = (await response.json()) as AnalysisReport;
      setData(result);
    } catch (err) {
        if (err instanceof Error) {
            setError(err.message);
        } else {
            setError('An unexpected error occurred.');
        }
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, analyzeProfile };
};
