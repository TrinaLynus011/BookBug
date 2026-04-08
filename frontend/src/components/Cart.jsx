import { useEffect, useRef, useState } from 'react';
import { clearCart, getCart, getStoredToken, markAsRead, removeFromCart } from '../api/client';

export default function Cart({ cartBooks, onCartChange, onReadStateChange }) {
  const [cart, setCart] = useState(cartBooks || []);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const panelRef = useRef(null);

  const loadCart = async () => {
    const token = getStoredToken();
    if (!token) return;
    try {
      const data = await getCart(token);
      const books = data.books || [];
      setCart(books);
      if (onCartChange) onCartChange(books);
    } catch (err) {
      console.error('Failed to load cart:', err);
    }
  };

  // Sync when parent pushes an optimistic update
  useEffect(() => {
    if (cartBooks) setCart(cartBooks);
  }, [cartBooks]);

  useEffect(() => { loadCart(); }, []);

  useEffect(() => {
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) setExpanded(false);
    };
    if (expanded) document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [expanded]);

  const handleRemove = async (title) => {
    setLoading(true);
    try {
      await removeFromCart(title, getStoredToken());
      await loadCart();
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleMarkRead = async (book) => {
    setLoading(true);
    try {
      await markAsRead(book, getStoredToken());
      await removeFromCart(book.title, getStoredToken());
      await loadCart();
      if (onReadStateChange) onReadStateChange();
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleClear = async () => {
    setLoading(true);
    try {
      await clearCart(getStoredToken());
      setCart([]);
      if (onCartChange) onCartChange([]);
      setExpanded(false);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  return (
    <div className="cart-container" ref={panelRef}>
      <button className="cart-toggle" onClick={() => setExpanded((v) => !v)} aria-expanded={expanded}>
        <span className="cart-icon">📚</span>
        Reading List
        {cart.length > 0 && <span className="cart-badge">{cart.length}</span>}
      </button>

      {expanded && (
        <div className="cart-panel">
          <div className="cart-panel-header">
            <h3 className="cart-panel-title">My Reading List</h3>
            <button className="cart-close" onClick={() => setExpanded(false)} aria-label="Close">✕</button>
          </div>

          {cart.length === 0 ? (
            <div className="cart-empty">
              <span className="cart-empty-icon">📖</span>
              <p>Your reading list is empty.<br />Add books from your recommendations.</p>
            </div>
          ) : (
            <>
              <ul className="cart-list">
                {cart.map((book, idx) => (
                  <li key={`${book.title}-${idx}`} className="cart-item">
                    <div className="cart-item-body">
                      <div className="cart-item-info">
                        <strong>{book.title}</strong>
                        <span className="cart-item-author">{book.author}</span>
                        <span className="genre-tag-small">{book.genre}</span>
                      </div>
                      <span className="cart-item-rating">★ {Number(book.rating).toFixed(1)}</span>
                    </div>
                    <div className="cart-item-actions">
                      <button className="btn-read" onClick={() => handleMarkRead(book)} disabled={loading}>
                        ✓ Read
                      </button>
                      <button className="btn-remove" onClick={() => handleRemove(book.title)} disabled={loading}>
                        ✕
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
              <button className="btn-clear" onClick={handleClear} disabled={loading}>
                Clear all
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
