import { Link } from 'react-router-dom';

export default function AuthShell({ title, subtitle, children }) {
  return (
    <main className="container" style={{ maxWidth: 440, paddingTop: '3rem' }}>
      <Link to="/" style={{ textDecoration: 'none' }}><h2>⚖️ SPECTRE</h2></Link>
      <div className="card">
        <h1 style={{ fontSize: '1.4rem' }}>{title}</h1>
        <p className="muted">{subtitle}</p>
        {children}
      </div>
    </main>
  );
}
