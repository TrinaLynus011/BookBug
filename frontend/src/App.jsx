import { useEffect, useState } from 'react';
import GenreCard from './components/GenreCard';
import HistoryList from './components/HistoryList';
import { getGenre, getHistory, getRecommendations } from './api/client';

export default function App() {
  const [genre, setGenre] = useState('');
  const [books, setBooks] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const refreshHistory = async () => {
    try {
      const data = await getHistory();
      setHistory(data.history || []);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReveal = async () => {
    setLoading(true);
    setError('');
    try {
      const genreData = await getGenre();
      const genreName = genreData.genre;
      setGenre(genreName);
      const recData = await getRecommendations(genreName);
      setBooks(recData.books || []);
      await refreshHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshHistory();
  }, []);

  return (
    <main className="layout">
      <div className="ambient-shape shape-a" aria-hidden="true" />
      <div className="ambient-shape shape-b" aria-hidden="true" />
      <GenreCard genre={genre} books={books} loading={loading} onReveal={handleReveal} />
      <HistoryList history={history} />
      {error && <p className="error-banner">{error}</p>}
    </main>
  );
}
