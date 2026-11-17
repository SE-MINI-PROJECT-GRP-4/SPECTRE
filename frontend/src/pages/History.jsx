import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/index.js';

export default function History() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState('');

  const load = () => api.listConversations().then(setItems).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  async function remove(id) {
    if (!window.confirm('Delete this conversation? This cannot be undone.')) return;
    try { await api.deleteConversation(id); await load(); } catch (e) { setError(e.message); }
  }

  return (
    <main className="container">
      <div className="row spread">
        <h1 style={{ fontSize: '1.4rem' }}>Conversation history</h1>
        <Link className="btn primary sm" to="/chat">New conversation</Link>
      </div>
      {error && <div className="alert error" role="alert">{error}</div>}
      {items === null && !error && <p className="muted">Loading…</p>}
      {items?.length === 0 && <div className="card muted">You have no saved conversations yet. <Link to="/chat">Ask your first question</Link>.</div>}
      <div className="grid">
        {items?.map((c) => (
          <div key={c.id} className="card row spread">
            <div>
              <Link to={`/chat/${c.id}`}><strong>{c.title}</strong></Link>
              <div className="muted" style={{ fontSize: '.85rem' }}>
                {c.domain || 'General'} · {c.messageCount} messages · {new Date(c.createdAt).toLocaleString()} {/* REQ-HIST-03 */}
              </div>
            </div>
            <button className="btn danger sm" onClick={() => remove(c.id)}>Delete</button>
          </div>
        ))}
      </div>
    </main>
  );
}
