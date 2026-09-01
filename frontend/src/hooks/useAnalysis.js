import { useState, useCallback } from 'react';

export function useAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const triggerAnalysis = useCallback(async (ticker, riskProfile = 'MODERATE') => {
    if (!ticker || !ticker.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker: ticker.trim().toUpperCase(),
          user_profile: riskProfile,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned status ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      console.error('Analysis API Error:', err);
      setError(err.message || 'Failed to analyze ticker. Please ensure backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    data,
    isDegraded: data ? Boolean(data.is_degraded) : false,
    triggerAnalysis,
  };
}
