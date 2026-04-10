import { useState, useEffect, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function fetchInsight() {
  try {
    const res = await fetch(`${API_BASE}/insight`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    return data.insight;
  } catch {
    return 'Did you know? BookBug automatically verifies every update before it reaches you, keeping the platform reliable and stable.';
  }
}

export default function Assistant() {
  const [open, setOpen]       = useState(false);
  const [insight, setInsight] = useState('');
  const [loading, setLoading] = useState(false);
  const panelRef              = useRef(null);

  const loadInsight = async () => {
    setLoading(true);
    const text = await fetchInsight();
    setInsight(text);
    setLoading(false);
  };

  // Load first insight when panel opens
  useEffect(() => {
    if (open && !insight) loadInsight();
  }, [open]);

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
      {/* Floating trigger button */}
      <button
        className="assistant-fab"
        onClick={() => setOpen((v) => !v)}
        aria-label="Open BookBug Assistant"
        title="BookBug Assistant"
      >
        📖
      </button>

      {/* Chat window */}
      {open && (
        <div className="assistant-panel" role="dialog" aria-label="BookBug Assistant">
          <div className="assistant-header">
            <span className="assistant-header-title">BookBug Assistant</span>
            <button
              className="assistant-close"
              onClick={() => setOpen(false)}
              aria-label="Close assistant"
            >✕</button>
          </div>

          <div className="assistant-body">
            {loading ? (
              <p className="assistant-loading">Finding an insight…</p>
            ) : (
              <p className="assistant-insight">{insight}</p>
            )}
          </div>

          <div className="assistant-footer">
            <button className="assistant-another" onClick={loadInsight} disabled={loading}>
              Another fact ✦
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
