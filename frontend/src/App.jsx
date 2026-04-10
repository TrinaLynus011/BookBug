import { useEffect, useState, useCallback } from 'react';
import GenreCard from './components/GenreCard';
import HistoryList from './components/HistoryList';
import UserStats from './components/UserStats';
import Cart from './components/Cart';
import Auth from './components/Auth';
import Assistant from './components/Assistant';
import {
  getGenre, getHistory, getRecommendations,
  getStoredToken, getStoredUsername, storeAuth, clearAuth,
  addToCart, getDashboard, toggleLike, getLikedBooks,
} from './api/client';

export default function App() {
  const [genre, setGenre]       = useState('');
  const [books, setBooks]       = useState([]);
  const [history, setHistory]   = useState([]);
  const [stats, setStats]       = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [user, setUser]         = useState(null);
  const [token, setToken]       = useState(null);
  const [cartTitles, setCartTitles]   = useState(new Set());
  const [likedTitles, setLikedTitles] = useState(new Set());

  const refreshHistory = useCallback(async (tok) => {
    if (!tok) return;
    try {
      const data = await getHistory(tok);
      setHistory(data.history || []);
    } catch (err) { setError(err.message); }
  }, []);

  const refreshStats = useCallback(async (tok, usr) => {
    if (!tok || !usr) return;
    try {
      const data = await getDashboard(usr, tok);
      setStats(data.stats);
    } catch (err) { console.error('Stats fetch failed:', err); }
  }, []);

  const refreshLikes = useCallback(async (tok) => {
    if (!tok) return;
    try {
      const data = await getLikedBooks(tok);
      setLikedTitles(new Set((data.books || []).map((b) => b.title)));
    } catch (err) { console.error('Likes fetch failed:', err); }
  }, []);

  const refreshAll = useCallback(async (tok, usr) => {
    if (!tok || !usr) return;
    await Promise.all([refreshHistory(tok), refreshStats(tok, usr), refreshLikes(tok)]);
  }, [refreshHistory, refreshStats, refreshLikes]);

  const handleReveal = async () => {
    setLoading(true);
    setError('');
    try {
      const genreData = await getGenre(token);
      const genreName = genreData.genre;
      setGenre(genreName);
      const recData = await getRecommendations(genreName, token);
      setBooks(recData.books || []);
      await refreshAll(token, user);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const handleAddToCart = async (book) => {
    if (!token || cartTitles.has(book.title)) return;
    // Optimistic update — badge and button state change instantly
    setCartTitles((prev) => new Set([...prev, book.title]));
    setCartBooks((prev) => [...prev, book]);
    try {
      await addToCart(book, token);
    } catch (err) {
      // Roll back on failure
      setCartTitles((prev) => { const n = new Set(prev); n.delete(book.title); return n; });
      setCartBooks((prev) => prev.filter((b) => b.title !== book.title));
      setError(err.message);
    }
  };

  const handleToggleLike = async (book) => {
    if (!token) return;
    try {
      const result = await toggleLike(book, token);
      setLikedTitles((prev) => {
        const next = new Set(prev);
        result.liked ? next.add(book.title) : next.delete(book.title);
        return next;
      });
      await refreshStats(token, user);
    } catch (err) { setError(err.message); }
  };

  const [cartBooks, setCartBooks] = useState([]);

  const handleCartChange = (books) => {
    setCartBooks(books);
    setCartTitles(new Set(books.map((b) => b.title)));
  };

  const handleAuth = (username, accessToken) => {
    storeAuth(accessToken, username);
    setUser(username);
    setToken(accessToken);
    refreshAll(accessToken, username);
  };

  const handleLogout = () => {
    clearAuth();
    setUser(null); setToken(null);
    setGenre(''); setBooks([]); setHistory([]);
    setStats(null); setCartTitles(new Set()); setLikedTitles(new Set()); setCartBooks([]);
  };

  useEffect(() => {
    const storedToken = getStoredToken();
    const storedUser  = getStoredUsername();
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(storedUser);
      refreshAll(storedToken, storedUser);
    }
  }, []);

  if (!user && !token) return <Auth onAuth={handleAuth} />;

  return (
    <div className="app-shell">
      {/* ── Top navigation bar ── */}
      <header className="topbar">
        <div className="topbar-left">
          <span className="topbar-brand">Book<span>Bug</span></span>
          <span className="topbar-tagline">Where every reader finds their next story.</span>
        </div>
        <div className="topbar-right">
          <span className="topbar-user">Welcome, <strong>{user}</strong></span>
          <Cart
            cartBooks={cartBooks}
            onCartChange={handleCartChange}
            onReadStateChange={() => refreshStats(token, user)}
          />
          <button onClick={handleLogout} className="btn-logout">Sign out</button>
        </div>
      </header>

      {/* ── Page body ── */}
      <div className="page-body">

        {/* Sidebar */}
        <aside className="sidebar">
          <UserStats stats={stats} recentHistory={history} />
        </aside>

        {/* Main content */}
        <main className="main-content">
          {/* Genre discovery hero */}
          <GenreCard
            genre={genre}
            books={books}
            loading={loading}
            onReveal={handleReveal}
            onAddToCart={handleAddToCart}
            onToggleLike={handleToggleLike}
            cartTitles={cartTitles}
            likedTitles={likedTitles}
          />

          {/* Reading history */}
          <HistoryList history={history} />

          {error && <p className="error-banner" role="alert">{error}</p>}
        </main>
      </div>

      <footer className="app-footer">
        <strong>BookBug</strong> — Where every reader finds their next story.
      </footer>

      <Assistant context={{
        genre:       genre || null,
        book:        books[0]?.title || null,
        likedGenres: stats?.favorite_genres || [],
        feature:     null,
      }} />
    </div>
  );
}
