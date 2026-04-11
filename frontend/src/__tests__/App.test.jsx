import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from '../App';

// Mock every export that App.jsx (and its children) import from api/client
vi.mock('../api/client', () => ({
  // Auth helpers
  getStoredToken:    vi.fn().mockReturnValue(null),
  getStoredUsername: vi.fn().mockReturnValue(null),
  storeAuth:         vi.fn(),
  clearAuth:         vi.fn(),

  // API calls
  getGenre: vi.fn().mockResolvedValue({ genre: 'fantasy' }),
  getRecommendations: vi.fn().mockResolvedValue({
    genre: 'fantasy',
    books: [
      { title: 'Arcane Horizon',    author: 'Lina Porter', genre: 'fantasy', rating: 4.5 },
      { title: 'Moonforge',         author: 'Eric Tole',   genre: 'fantasy', rating: 4.2 },
      { title: 'The Ember Archive', author: 'Mina Faye',   genre: 'fantasy', rating: 4.7 },
    ],
  }),
  getHistory:    vi.fn().mockResolvedValue({ history: [] }),
  getDashboard:  vi.fn().mockResolvedValue({ stats: { total_recommendations: 0, books_explored: 0, books_liked: 0, favorite_genres: [] } }),
  getLikedBooks: vi.fn().mockResolvedValue({ books: [] }),
  getCart:       vi.fn().mockResolvedValue({ books: [] }),
  addToCart:     vi.fn().mockResolvedValue({ message: 'Book added to cart' }),
  toggleLike:    vi.fn().mockResolvedValue({ liked: true, title: 'Arcane Horizon' }),

  // Auth flow
  login:  vi.fn().mockResolvedValue({ access_token: 'test-token' }),
  signup: vi.fn().mockResolvedValue({ message: 'User created successfully' }),
}));
test('shows auth screen when not logged in', () => {
  render(<App />);
  // App shows the Auth component when no token is stored
  expect(screen.getByText(/BookBug/i)).toBeInTheDocument();
});

test('reveals genre and recommended books after login', async () => {
  const { getStoredToken, getStoredUsername } = await import('../api/client');
  getStoredToken.mockReturnValue('test-token');
  getStoredUsername.mockReturnValue('testuser');

  render(<App />);

  const revealBtn = await screen.findByRole('button', { name: /reveal a genre/i });
  fireEvent.click(revealBtn);

  await waitFor(() => {
    expect(screen.getByText(/fantasy/i)).toBeInTheDocument();
    expect(screen.getByText('Arcane Horizon')).toBeInTheDocument();
  });
});
