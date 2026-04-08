// MongoDB initialisation script
// Runs once when the container is first created via docker-compose

db = db.getSiblingDB('bookbug');

// Unique index on username – prevents duplicate accounts at the DB level
db.users.createIndex({ username: 1 }, { unique: true });

// Index history and carts by username for fast per-user lookups
db.history.createIndex({ username: 1 }, { unique: true });
db.carts.createIndex({ username: 1 }, { unique: true });
db.read_books.createIndex({ username: 1 }, { unique: true });

print('BookBug indexes created successfully');
