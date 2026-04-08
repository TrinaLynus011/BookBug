export default function HistoryList({ history }) {
  return (
    <section className="section-card history-panel">
      <div className="history-panel-header">
        <h2 className="history-panel-title">Reading History</h2>
        {history.length > 0 && (
          <span className="history-count-badge">{history.length} sessions</span>
        )}
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          <span className="empty-state-icon">📜</span>
          <p>No history yet. Reveal a genre to begin your journey.</p>
        </div>
      ) : (
        <ul className="history-list">
          {history.map((entry, index) => (
            <li key={`${entry.genre}-${index}`} className="history-item">
              <div className="history-item-header">
                <span className="history-item-genre">{entry.genre}</span>
                <span className="history-item-count">{entry.books.length} books</span>
              </div>
              <p className="history-item-books">
                {entry.books.map((b) => b.title).join(' · ')}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
