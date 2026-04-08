export default function GenreCard({ genre, books, onReveal, loading, onAddToCart, onToggleLike, cartTitles, likedTitles }) {
  return (
    <section className="hero-section">
      <p className="hero-eyebrow">Book Discovery</p>
      <h2 className="hero-title">
        Find your next<br /><em>great read</em>
      </h2>
      <p className="hero-tagline">
        Every click reveals a new world. Where will today take you?
      </p>

      <button className="reveal-btn" onClick={onReveal} disabled={loading}>
        {loading ? '✦ Discovering…' : '✦ Reveal a Genre'}
      </button>

      {genre && (
        <div className="genre-reveal">
          <p className="genre-reveal-label">Today's Genre</p>
          <span className="genre-reveal-name">{genre}</span>
        </div>
      )}

      {books.length > 0 && (
        <div className="shelf-section">
          <p className="shelf-title">Recommended for you</p>
          <div className="book-shelf" aria-label="recommended books">
            {books.map((book) => {
              const inCart = cartTitles?.has(book.title);
              const liked  = likedTitles?.has(book.title);
              return (
                <article key={book.title} className="book-card">
                  <div className="book-card-header">
                    <h3 className="book-card-title">{book.title}</h3>
                    <button
                      className={`btn-heart${liked ? ' liked' : ''}`}
                      onClick={() => onToggleLike && onToggleLike(book)}
                      aria-label={liked ? 'Unlike book' : 'Like book'}
                    >
                      {liked ? '♥' : '♡'}
                    </button>
                  </div>
                  <p className="book-card-author">{book.author}</p>
                  <p className="book-card-rating">★ {book.rating.toFixed(1)}</p>
                  {onAddToCart && (
                    <button
                      className={`btn-add-cart${inCart ? ' in-cart' : ''}`}
                      onClick={() => !inCart && onAddToCart(book)}
                      disabled={inCart}
                    >
                      {inCart ? '✓ In Reading List' : '+ Add to List'}
                    </button>
                  )}
                </article>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}
