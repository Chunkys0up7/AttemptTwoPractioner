import React, { useEffect, useState } from 'react';

interface Recommendation {
  id: number;
  title: string;
  score: number;
}

const fetchRecommendations = async (): Promise<Recommendation[]> => {
  // TODO: Replace with real API call
  return [
    { id: 1, title: 'Example Recommendation', score: 0.95 },
    { id: 2, title: 'Another Recommendation', score: 0.90 },
  ];
};

export const RecommendationsPanel: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Placeholder for analytics tracking
    // TODO: Track recommendation panel view
    fetchRecommendations()
      .then(setRecommendations)
      .catch((err) => setError(err.message || 'Failed to load recommendations'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading recommendations...</div>;
  if (error) return <div>Error: {error}</div>;
  if (recommendations.length === 0) return <div>No recommendations available.</div>;

  return (
    <div>
      <h3>Recommendations</h3>
      <ul>
        {recommendations.map((rec) => (
          <li key={rec.id}>
            {rec.title} (Score: {rec.score})
          </li>
        ))}
      </ul>
    </div>
  );
}; 