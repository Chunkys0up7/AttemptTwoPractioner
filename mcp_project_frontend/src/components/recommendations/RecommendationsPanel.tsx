import React, { useEffect, useState } from 'react';

interface Recommendation {
  id: number;
  title: string;
  score: number;
  category?: string;
}

interface RecommendationsPanelProps {
  category?: string;
  topN?: number;
}

export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({ category, topN = 3 }) => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // TODO: Track recommendation panel view (analytics)
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (topN) params.append('top_n', String(topN));
    fetch(`/api/recommendations?${params.toString()}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch recommendations');
        return res.json();
      })
      .then((data) => setRecommendations(Array.isArray(data) ? data : data.recommendations || []))
      .catch((err) => setError(err.message || 'Failed to load recommendations'))
      .finally(() => setLoading(false));
  }, [category, topN]);

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