import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import AuthShell from '../components/AuthShell.jsx';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// REQ-AUTH-02: validate required registration fields (Appendix B.1)
function validate({ name, email, password, confirm }) {
  const e = {};
  if (!name.trim()) e.name = 'Name is required.';
  if (!EMAIL_RE.test(email)) e.email = 'Enter a valid email address.';
  if (password.length < 8) e.password = 'Use at least 8 characters.';
  if (confirm !== password) e.confirm = 'Passwords do not match.';
  return e;
}

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    const v = validate(form); setErrors(v); setError('');
    if (Object.keys(v).length) return;
    setBusy(true);
    try { await register({ name: form.name.trim(), email: form.email.trim(), password: form.password }); nav('/', { replace: true }); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  const field = (k, label, type = 'text', auto) => (
    <div className="field">
      <label htmlFor={k}>{label}</label>
      <input id={k} type={type} autoComplete={auto} value={form[k]} onChange={set(k)} aria-invalid={!!errors[k]} />
      {errors[k] && <div className="field-error">{errors[k]}</div>}
    </div>
  );

  return (
    <AuthShell title="Create your account" subtitle="Registered users get conversation history.">
      <form onSubmit={submit} noValidate>
        {error && <div className="alert error" role="alert">{error}</div>}
        {field('name', 'Full name', 'text', 'name')}
        {field('email', 'Email', 'email', 'email')}
        {field('password', 'Password', 'password', 'new-password')}
        {field('confirm', 'Confirm password', 'password', 'new-password')}
        <button className="btn primary" style={{ width: '100%' }} disabled={busy}>{busy ? 'Creating…' : 'Register'}</button>
      </form>
      <p className="muted" style={{ marginTop: '1rem' }}>Already registered? <Link to="/login">Log in</Link></p>
    </AuthShell>
  );
}
