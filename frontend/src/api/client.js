const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function getGenre() {
  const response = await fetch(`${API_BASE_URL}/genre`);
  if (!response.ok) {
    throw new Error('Failed to fetch genre');
  }
  return response.json();
}

export async function getRecommendations(genre) {
  const response = await fetch(`${API_BASE_URL}/recommend/${genre}`);
  if (!response.ok) {
    throw new Error('Failed to fetch recommendations');
  }
  return response.json();
}

export async function getHistory() {
  const response = await fetch(`${API_BASE_URL}/history`);
  if (!response.ok) {
    throw new Error('Failed to fetch history');
  }
  return response.json();
}
