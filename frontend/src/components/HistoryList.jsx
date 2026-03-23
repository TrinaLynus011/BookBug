export default function HistoryList({ history }) {
  return (
    <section className="panel history-panel">
      <h2>Recommendation History</h2>
      {history.length === 0 && <p className="empty">No history yet. Reveal a genre to begin.</p>}
      {history.length > 0 && (
        <ul className="history-list">
          {history.map((entry, index) => (
            <li key={`${entry.genre}-${index}`} className="history-item">
              <div>
                <strong>{entry.genre}</strong>
                <span>{entry.books.length} books</span>
              </div>
              <p>{entry.books.map((book) => book.title).join(', ')}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
