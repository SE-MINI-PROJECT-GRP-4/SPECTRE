import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api/index.js';
import Disclaimer from '../components/Disclaimer.jsx';

function download(t) {
  const blob = new Blob([t.content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement('a'), { href: url, download: `${t.name.replace(/\W+/g, '_')}_v${t.version}.txt` });
  a.click();
  URL.revokeObjectURL(url);
}

export default function Templates() {
  const [params] = useSearchParams();
  const [items, setItems] = useState([]);
  const [category, setCategory] = useState('All');
  const [open, setOpen] = useState(params.get('open'));
  const [state, setState] = useState('loading');

  useEffect(() => {
    api.listTemplates().then((t) => { setItems(t); setState('ready'); }).catch(() => setState('error'));
  }, []);

  const categories = useMemo(() => ['All', ...new Set(items.map((t) => t.category))], [items]); // REQ-DOC-02
  const shown = items.filter((t) => category === 'All' || t.category === category);

  return (
    <main className="container">
      <h1 style={{ fontSize: '1.4rem' }}>Document templates</h1>
      <div className="disclaimer" style={{ marginBottom: '1rem' }}>
        <strong>Note: </strong>Templates are starting points and may need professional review and customization before use.
      </div>

      {state === 'loading' && <p className="muted">Loading templates…</p>}
      {state === 'error' && <div className="alert error">Could not load templates. Please try again later.</div>}

      {state === 'ready' && (
        <>
          <div className="row" style={{ marginBottom: '1rem' }}>
            {categories.map((c) => (
              <button key={c} className={`chip ${c === category ? 'active' : ''}`} style={c === category ? { borderColor: 'var(--accent)', fontWeight: 600 } : {}} onClick={() => setCategory(c)}>{c}</button>
            ))}
          </div>
          {shown.length === 0 && <p className="muted">No templates in this category.</p>}
          <div className="grid cols-2">
            {shown.map((t) => (
              <article key={t.id} className="card">
                <div className="row spread"><h3 style={{ margin: 0 }}>{t.name}</h3><span className="badge">v{t.version}</span></div>
                <span className="badge">{t.category}</span>
                <p className="muted">{t.description}</p>
                <div className="row">
                  <button className="btn sm" onClick={() => setOpen(open === t.id ? null : t.id)}>{open === t.id ? 'Hide preview' : 'Preview'}</button>
                  <button className="btn sm primary" onClick={() => download(t)}>Download</button>
                </div>
                {open === t.id && <pre style={{ whiteSpace: 'pre-wrap', fontSize: '.85rem', background: 'var(--bg)', padding: '.75rem', borderRadius: 8, overflowX: 'auto' }}>{t.content}</pre>}
              </article>
            ))}
          </div>
        </>
      )}
      <div style={{ marginTop: '1.5rem' }}><Disclaimer /></div>
    </main>
  );
}
