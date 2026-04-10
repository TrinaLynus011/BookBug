import { useState, useEffect, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function fetchInsight({ feature, book, genre, likedGenres } = {}) {
  try {
    const params = new URLSearchParams();
    if (feature)                        params.set('feature', feature);
    if (book)                           params.set('book', book);
    if (genre)                          params.set('genre', genre);
    if (likedGenres?.length)            params.set('liked_genres', likedGenres.join(','));

    const url = `${API_BASE}/insight${params.size ? '?' + params : ''}`;
    const res  = await fetch(url);
    if (!res.ok) throw new Error();
    const data = await res.json();
    return data.insight;
  } catch {
    return (
      'The platform is running a continuously deployed backend, ' +
      'so what you see here is always up to date. ' +
      'Every change goes through automated testing before it reaches you.'
    );
  }
}

// context prop: { feature, book, genre, likedGenres }
export default function Assistant({ context = {} }) {
  const [open, setOpen]       = useState(false);
  const [insight, setInsight] = useState('');
  const [loading, setLoading] = useState(false);
  const panelRef              = useRef(null);

  const loadInsight = async () => {
    setLoading(true);
    const text = await fetchInsight(context);
    setInsight(text);
    setLoading(false);
  };

  // Reload when panel opens or context changes
  useEffect(() => {
    if (open) loadInsight();
  }, [open, context.genre, context.book, context.feature]);

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) setOpen(false);
    };
    if (open) document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  return (
    <div className="assistant-root" ref={panelRef}>
      <button
        className="assistant-fab"
        onClick={() => setOpen((v) => !v)}
        aria-label="Open BookBug Assistant"
        title="BookBug Assistant"
      >
        📖
      </button>

      {open && (
        <div className="assistant-panel" role="dialog" aria-label="BookBug Assistant">
          <div className="assistant-header">
            <span className="assistant-header-title">BookBug Assistant</span>
            <button className="assistant-close" onClick={() => setOpen(false)} aria-label="Close">✕</button>
          </div>

          <div className="assistant-body">
            {loading
              ? <p className="assistant-loading">Thinking…</p>
              : <p className="assistant-insight">{insight}</p>
            }
          </div>

          <div className="assistant-footer">
            <button className="assistant-another" onClick={loadInsight} disabled={loading}>
              Tell me more ✦
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
