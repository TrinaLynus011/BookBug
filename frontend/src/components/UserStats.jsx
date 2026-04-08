export default function UserStats({ stats, recentHistory }) {
  return (
    <>
      {/* Reading Journey card */}
      <div className="sidebar-card fade-up">
        <h3 className="sidebar-card-title">Reading Journey</h3>
        <div className="journey-stats">
          <div className="journey-stat">
            <div className="journey-stat-icon">📚</div>
            <div className="journey-stat-info">
              <span className="journey-stat-value">{stats?.total_recommendations ?? 0}</span>
              <span className="journey-stat-label">Recommendations</span>
            </div>
          </div>
          <div className="journey-stat">
            <div className="journey-stat-icon">🔍</div>
            <div className="journey-stat-info">
              <span className="journey-stat-value">{stats?.books_explored ?? 0}</span>
              <span className="journey-stat-label">Books Explored</span>
            </div>
          </div>
          <div className="journey-stat">
            <div className="journey-stat-icon">♥</div>
            <div className="journey-stat-info">
              <span className="journey-stat-value">{stats?.books_liked ?? 0}</span>
              <span className="journey-stat-label">Books Liked</span>
            </div>
          </div>
        </div>
      </div>

      {/* Favorite Genres card — only shown when there are liked books */}
      {stats?.favorite_genres?.length > 0 && (
        <div className="sidebar-card fade-up">
          <h3 className="sidebar-card-title">Favourite Genres</h3>
          <div className="sidebar-genres">
            {stats.favorite_genres.map((g) => (
              <span key={g} className="genre-pill">{g}</span>
            ))}
          </div>
        </div>
      )}

      {/* Recent activity */}
      {recentHistory?.length > 0 && (
        <div className="sidebar-card fade-up">
          <h3 className="sidebar-card-title">Recent Sessions</h3>
          <div className="sidebar-history">
            {recentHistory.slice(0, 5).map((entry, i) => (
              <div key={i} className="sidebar-history-item">
                <div className="sidebar-history-dot" />
                <span className="sidebar-history-genre">{entry.genre}</span>
                <span className="sidebar-history-count">{entry.books.length} books</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
