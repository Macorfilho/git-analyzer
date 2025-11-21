import { useState, useCallback } from 'react';
import { AnalysisReport, ApiError, JobStatus } from '../types';

interface UseGithubAnalysisResult {
    data: AnalysisReport | null;
    loading: boolean;
    error: string | null;
    status: string;
    analyzeProfile: (username: string) => Promise<void>;
}

const API_BASE_URL = 'http://localhost:5001/api';

export const useGithubAnalysis = (): UseGithubAnalysisResult => {
  const [data, setData] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');

  const pollStatus = useCallback(async (jobId: string) => {
    const intervalId = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
            if (!response.ok) {
                 throw new Error('Failed to check status');
            }
            const jobStatus: JobStatus = await response.json();
            setStatus(jobStatus.status);

            if (jobStatus.status === 'finished' && jobStatus.result) {
                clearInterval(intervalId);
                setData(jobStatus.result);
                setLoading(false);
            } else if (jobStatus.status === 'failed') {
                clearInterval(intervalId);
                setError(jobStatus.error || 'Analysis failed');
                setLoading(false);
            }
            // If 'queued' or 'started', continue polling
        } catch (err) {
            clearInterval(intervalId);
            setError(err instanceof Error ? err.message : 'Polling error');
            setLoading(false);
        }
    }, 2000);
  }, []);

  const analyzeProfile = async (username: string) => {
    setLoading(true);
    setError(null);
    setData(null);
    setStatus('starting');

    try {
      const response = await fetch(`${API_BASE_URL}/analyze/${username}`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ model: 'llama3' })
      });
      
      if (!response.ok) {
        const errData = (await response.json()) as ApiError;
        throw new Error(errData.error || 'Failed to start analysis');
      }

      const result = await response.json();
      // result should be { message: "...", job_id: "...", status_url: "..." }
      
      if (result.job_id) {
          pollStatus(result.job_id);
      } else {
          throw new Error('No job ID returned');
      }

    } catch (err) {
        setLoading(false);
        if (err instanceof Error) {
            setError(err.message);
        } else {
            setError('An unexpected error occurred.');
        }
    }
  };

  return { data, loading, error, status, analyzeProfile };
};