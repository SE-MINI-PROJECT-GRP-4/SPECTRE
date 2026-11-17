import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import AuthShell from '../components/AuthShell.jsx';

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const from = useLocation().state?.from || '/';
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    if (!form.email || !form.password) return setError('Please enter your email and password.');
    setBusy(true); setError('');
    try { await login(form); nav(from, { replace: true }); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Log in to save your conversations and access history.">
      <form onSubmit={submit} noValidate>
        {error && <div className="alert error" role="alert">{error}</div>}
        <div className="field"><label htmlFor="email">Email</label>
          <input id="email" type="email" autoComplete="email" value={form.email} onChange={set('email')} /></div>
        <div className="field"><label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="current-password" value={form.password} onChange={set('password')} /></div>
        <button className="btn primary" style={{ width: '100%' }} disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
      </form>
      <p className="muted" style={{ marginTop: '1rem' }}>New here? <Link to="/register">Create an account</Link></p>
      <p className="muted" style={{ fontSize: '.8rem' }}>Demo (mock mode): demo@spectre.dev / demo1234 · admin@spectre.dev / admin123</p>
    </AuthShell>
  );
}
