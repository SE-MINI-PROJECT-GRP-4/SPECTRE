import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/index.js';
import { useAuth } from '../context/AuthContext.jsx';
import Disclaimer from '../components/Disclaimer.jsx';

const TOPICS = [
  ['Consumer refund', 'My online order arrived defective and the seller refuses a refund. What can I do?'],
  ['Landlord deposit', 'My landlord is not returning my security deposit after I vacated.'],
  ['Unpaid salary', 'My employer has not paid my salary for two months.'],
  ['Online fraud', 'I lost money to a UPI scam. How do I report it?'],
  ['File an FIR', 'How do I file an FIR for a theft?'],
  ['RTI application', 'How do I file an RTI application?'],
];

export default function Dashboard() {
  const { user } = useAuth();
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    if (user) api.listConversations().then((c) => setRecent(c.slice(0, 3))).catch(() => setRecent([]));
  }, [user]);

  return (
    <main className="container">
      <section className="hero">
        <h1>{user ? `Hello, ${user.name.split(' ')[0]}` : 'Understand your legal options'}</h1>
        <p>Ask a legal question in plain language and get a step-by-step explanation, relevant references and document templates – for common issues in India.</p>
        <Link to="/chat" className="btn" style={{ background: '#fff', color: '#1e2a52' }}>Ask a legal question</Link>
      </section>

      <h2 style={{ marginTop: '1.5rem' }}>Try a common question</h2>
      <div className="row">
        {TOPICS.map(([label, q]) => (
          <Link key={label} className="chip" to={`/chat?q=${encodeURIComponent(q)}`}>{label}</Link>
        ))}
      </div>

      <div className="grid cols-3" style={{ marginTop: '1.5rem' }}>
        <div className="card"><h3>💬 Guided answers</h3><p className="muted">Plain-language explanations with prerequisites and next steps.</p></div>
        <div className="card"><h3>📚 Verified references</h3><p className="muted">Sources come from stored references – never invented citations.</p></div>
        <div className="card"><h3>📄 Templates</h3><p className="muted">Starter documents like legal notices, RTI and rent agreements.</p><Link to="/templates">Browse templates →</Link></div>
      </div>

      {user && (
        <section style={{ marginTop: '1.5rem' }}>
          <div className="row spread"><h2>Recent conversations</h2><Link to="/history">View all</Link></div>
          {recent.length === 0 ? <p className="muted">No conversations yet.</p> : (
            <div className="grid">
              {recent.map((c) => (
                <Link key={c.id} to={`/chat/${c.id}`} className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <strong>{c.title}</strong>
                  <div className="muted" style={{ fontSize: '.85rem' }}>{c.domain || 'General'} · {new Date(c.createdAt).toLocaleString()}</div>
                </Link>
              ))}
            </div>
          )}
        </section>
      )}

      <div style={{ marginTop: '1.5rem' }}><Disclaimer /></div>
    </main>
  );
}
