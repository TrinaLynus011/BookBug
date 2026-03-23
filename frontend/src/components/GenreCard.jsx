export default function GenreCard({ genre, books, onReveal, loading }) {
  return (
    <section className="panel hero-panel">
      <h1>BookBee DevOps Platform</h1>
      <p className="subtitle">Scalable recommendation flow simulated fully on local infrastructure.</p>
      <button className="reveal-btn" onClick={onReveal} disabled={loading}>
        {loading ? 'Fetching...' : 'Reveal a Genre'}
      </button>

      {genre && (
        <div className="genre-chip-wrap">
          <span className="chip-label">Current Genre</span>
          <span className="genre-chip">{genre}</span>
        </div>
      )}

      {books.length > 0 && (
        <div className="book-grid" aria-label="recommended books">
          {books.map((book) => (
            <article key={book.title} className="book-card">
              <h3>{book.title}</h3>
              <p>{book.author}</p>
              <div className="rating">Rating: {book.rating.toFixed(1)}</div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
