import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from '../App';

vi.mock('../api/client', () => ({
  getGenre: vi.fn().mockResolvedValue({ genre: 'fantasy' }),
  getRecommendations: vi.fn().mockResolvedValue({
    genre: 'fantasy',
    books: [
      { title: 'Arcane Horizon', author: 'Lina Porter', genre: 'fantasy', rating: 4.5 },
      { title: 'Moonforge', author: 'Eric Tole', genre: 'fantasy', rating: 4.2 },
      { title: 'The Ember Archive', author: 'Mina Faye', genre: 'fantasy', rating: 4.7 }
    ]
  }),
  getHistory: vi.fn().mockResolvedValue({ history: [] })
}));

test('reveals genre and recommended books', async () => {
  render(<App />);

  fireEvent.click(screen.getByRole('button', { name: /reveal a genre/i }));

  await waitFor(() => {
    expect(screen.getByText(/fantasy/i)).toBeInTheDocument();
    expect(screen.getByText('Arcane Horizon')).toBeInTheDocument();
  });
});
