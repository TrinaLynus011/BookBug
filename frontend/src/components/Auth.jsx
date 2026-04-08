import { useState } from 'react';
import { login, signup } from '../api/client';

export default function Auth({ onAuth }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        const data = await login(username, password);
        onAuth(username, data.access_token);
      } else {
        await signup(username, password);
        const data = await login(username, password);
        onAuth(username, data.access_token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-layout">
      <div className="ambient-shape shape-a" aria-hidden="true" />
      <div className="ambient-shape shape-b" aria-hidden="true" />

      <div className="auth-brand">
        <h1 className="auth-brand-title">BookBug</h1>
        <p className="auth-brand-tagline">Discover stories that stay with you.</p>
      </div>

      <section className="auth-panel">
        <h2 className="auth-panel-title">
          {isLogin ? 'Welcome back' : 'Start your journey'}
        </h2>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              placeholder="Your username"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={4}
              placeholder="Your password"
              autoComplete={isLogin ? 'current-password' : 'new-password'}
            />
          </div>

          {error && <p className="error-text" role="alert">{error}</p>}

          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? 'Please wait…' : isLogin ? 'Enter the Library' : 'Create Account'}
          </button>

          <p className="auth-toggle">
            {isLogin ? "New here? " : 'Already a member? '}
            <button type="button" onClick={() => { setIsLogin(!isLogin); setError(''); }} className="toggle-link">
              {isLogin ? 'Create an account' : 'Sign in'}
            </button>
          </p>
        </form>
      </section>

      <p className="auth-footer">Where every reader finds their next story.</p>
    </main>
  );
}
