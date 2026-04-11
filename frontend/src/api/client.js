const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const UNAUTHORIZED_EVENT = 'bookbee:unauthorized';

function handleUnauthorized() {
  clearAuth();
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
  }
}

function throwIfUnauthorized(response) {
  if (response.status === 401) {
    handleUnauthorized();
    throw new Error('Session expired. Please sign in again.');
  }
}

export async function getGenre(token = null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await fetch(`${API_BASE_URL}/genre`, { headers });
  if (!response.ok) {
    throw new Error('Failed to fetch genre');
  }
  return response.json();
}

export async function getRecommendations(genre, token = null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await fetch(`${API_BASE_URL}/recommend/${genre}`, { headers });
  if (!response.ok) {
    throw new Error('Failed to fetch recommendations');
  }
  return response.json();
}

export async function getHistory(token = null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await fetch(`${API_BASE_URL}/history`, { headers });
  if (!response.ok) {
    throw new Error('Failed to fetch history');
  }
  return response.json();
}

export async function signup(username, password) {
  const response = await fetch(`${API_BASE_URL}/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Signup failed');
  }
  return data;
}

export async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Login failed');
  }
  return data;
}

export async function getDashboard(username, token) {
  const response = await fetch(`${API_BASE_URL}/dashboard/${username}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  throwIfUnauthorized(response);
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard');
  }
  return response.json();
}

export function getStoredToken() {
  return localStorage.getItem('bookbee_token');
}

export function getStoredUsername() {
  return localStorage.getItem('bookbee_username');
}

export function storeAuth(token, username) {
  localStorage.setItem('bookbee_token', token);
  localStorage.setItem('bookbee_username', username);
}

export function clearAuth() {
  localStorage.removeItem('bookbee_token');
  localStorage.removeItem('bookbee_username');
}

export async function getCart(token) {
  const response = await fetch(`${API_BASE_URL}/cart`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  throwIfUnauthorized(response);
  if (!response.ok) {
    throw new Error('Failed to fetch cart');
  }
  return response.json();
}

export async function addToCart(book, token) {
  const response = await fetch(`${API_BASE_URL}/cart`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(book),
  });
  throwIfUnauthorized(response);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to add to cart');
  }
  return data;
}

export async function removeFromCart(bookTitle, token) {
  const response = await fetch(`${API_BASE_URL}/cart/${encodeURIComponent(bookTitle)}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  throwIfUnauthorized(response);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to remove from cart');
  }
  return data;
}

export async function clearCart(token) {
  const response = await fetch(`${API_BASE_URL}/cart`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  throwIfUnauthorized(response);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to clear cart');
  }
  return data;
}

export async function getReadBooks(token) {
  const response = await fetch(`${API_BASE_URL}/read`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  throwIfUnauthorized(response);
  if (!response.ok) {
    throw new Error('Failed to fetch read books');
  }
  return response.json();
}

export async function markAsRead(book, token) {
  const response = await fetch(`${API_BASE_URL}/read`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(book),
  });
  throwIfUnauthorized(response);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to mark as read');
  }
  return data;
}

export async function toggleLike(book, token) {
  const response = await fetch(`${API_BASE_URL}/like`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(book),
  });
  throwIfUnauthorized(response);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to toggle like');
  }
  return data; // { liked: bool, title: string }
}

export async function getLikedBooks(token) {
  const response = await fetch(`${API_BASE_URL}/likes`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  throwIfUnauthorized(response);
  if (!response.ok) throw new Error('Failed to fetch liked books');
  return response.json();
}