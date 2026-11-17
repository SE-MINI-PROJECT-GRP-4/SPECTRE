import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { api } from '../api/index.js';
import { useAuth } from '../context/AuthContext.jsx';
import ResponseView from '../components/ResponseView.jsx';
import Disclaimer from '../components/Disclaimer.jsx';

const MAX_LEN = 1000; // NFR-PERF-03: reasonable limit on query length
const MIN_LEN = 5;

export default function Chat() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const nav = useNavigate();
  const { user } = useAuth();
  const [conversationId, setConversationId] = useState(id || null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState(params.get('q') || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const endRef = useRef(null);

  useEffect(() => {
    if (!id) return;
    setError('');
    api.getConversation(id)
      .then((c) => { setMessages(c.messages); setConversationId(c.id); })
      .catch((e) => setError(e.message));
  }, [id]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, busy]);

  async function send(e) {
    e.preventDefault();
    const text = input.trim();
    if (text.length < MIN_LEN) return setError('Please describe your legal question in a little more detail.'); // REQ-QUERY-02
    setError(''); setBusy(true); setInput('');
    setMessages((m) => [...m, { id: `tmp-${Date.now()}`, role: 'user', text }]);
    try {
      const res = await api.sendQuery({ text, conversationId });
      setMessages((m) => [...m.filter((x) => !String(x.id).startsWith('tmp-')), res.userMessage, res.answer]);
      if (res.conversationId && res.conversationId !== conversationId) {
        setConversationId(res.conversationId);
        nav(`/chat/${res.conversationId}`, { replace: true });
      }
    } catch (err) {
      setMessages((m) => m.filter((x) => !String(x.id).startsWith('tmp-')));
      setInput(text);
      setError(err.status === 0 || !err.status ? err.message : 'The assistant is unavailable right now. Please try again shortly.'); // REQ-QUERY-10
    } finally { setBusy(false); }
  }

  function newChat() { setMessages([]); setConversationId(null); setError(''); nav('/chat'); }

  return (
    <main className="container">
      <div className="row spread">
        <h1 style={{ fontSize: '1.4rem' }}>AI Legal Assistant</h1>
        {messages.length > 0 && <button className="btn sm" onClick={newChat}>New conversation</button>}
      </div>
      {!user && <div className="alert warn"><Link to="/login">Log in</Link> or <Link to="/register">register</Link> to save this conversation to your history.</div>}

      <div className="chat" aria-live="polite">
        {messages.length === 0 && !busy && (
          <div className="card muted">Describe your situation – for example, <em>"My landlord is not returning my deposit."</em> Add key facts such as dates, amounts and what you have already tried.</div>
        )}
        {messages.map((m) => m.role === 'user'
          ? <div key={m.id} className="msg user">{m.text}</div>
          : <div key={m.id} className="msg assistant"><ResponseView message={m} /></div>)}
        {busy && <div className="typing">Researching stored references…</div>}
        <div ref={endRef} />
      </div>

      <form className="composer" onSubmit={send}>
        {error && <div className="alert error" role="alert">{error}</div>}
        <textarea
          aria-label="Your legal question"
          placeholder="Type your legal question…"
          maxLength={MAX_LEN}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) send(e); }}
        />
        <div className="row spread" style={{ marginTop: '.5rem' }}>
          <span className="muted" style={{ fontSize: '.8rem' }}>{input.length}/{MAX_LEN} · Ctrl/⌘+Enter to send</span>
          <button className="btn primary" disabled={busy}>{busy ? 'Thinking…' : 'Send'}</button>
        </div>
        <div style={{ marginTop: '.6rem' }}><Disclaimer /></div>
      </form>
    </main>
  );
}
