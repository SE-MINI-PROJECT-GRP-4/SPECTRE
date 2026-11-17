import { useEffect, useState } from 'react';
import { api } from '../api/index.js';

// Generic admin CRUD for knowledge entries, references and templates.
// field.type: text | textarea | select | list (one item per line) | csv
const toForm = (fields, item) => Object.fromEntries(fields.map((f) => {
  const v = item?.[f.key] ?? (f.type === 'list' || f.type === 'csv' ? [] : f.options?.[0] ?? '');
  return [f.key, f.type === 'list' ? v.join('\n') : f.type === 'csv' ? v.join(', ') : v];
}));
const fromForm = (fields, form) => Object.fromEntries(fields.map((f) => [f.key,
  f.type === 'list' ? form[f.key].split('\n').map((s) => s.trim()).filter(Boolean)
  : f.type === 'csv' ? form[f.key].split(',').map((s) => s.trim()).filter(Boolean) : form[f.key]]));

export default function ResourceManager({ resource, label, columns, fields }) {
  const [rows, setRows] = useState(null);
  const [editing, setEditing] = useState(null); // item | {} for new
  const [form, setForm] = useState({});
  const [msg, setMsg] = useState({ type: '', text: '' });

  const load = () => api.admin.list(resource).then(setRows).catch((e) => setMsg({ type: 'error', text: e.message }));
  useEffect(() => { setEditing(null); setRows(null); load(); }, [resource]);

  const start = (item) => { setEditing(item); setForm(toForm(fields, item)); setMsg({ type: '', text: '' }); };

  async function submit(e) {
    e.preventDefault();
    const missing = fields.find((f) => f.required && !String(form[f.key]).trim());
    if (missing) return setMsg({ type: 'error', text: `${missing.label} is required.` });
    try {
      await api.admin.save(resource, { ...(editing?.id ? { id: editing.id } : {}), ...fromForm(fields, form) });
      setEditing(null); setMsg({ type: 'ok', text: 'Saved.' }); load();
    } catch (err) { setMsg({ type: 'error', text: err.message }); }
  }
  async function remove(item) {
    if (!window.confirm('Delete this entry?')) return;
    try { await api.admin.remove(resource, item.id); setMsg({ type: 'ok', text: 'Deleted.' }); load(); }
    catch (err) { setMsg({ type: 'error', text: err.message }); }
  }

  return (
    <div className="card">
      <div className="row spread">
        <h2 style={{ margin: 0, fontSize: '1.15rem' }}>{label}</h2>
        {!editing && <button className="btn primary sm" onClick={() => start({})}>+ Add</button>}
      </div>
      {msg.text && <div className={`alert ${msg.type}`} style={{ marginTop: '.75rem' }} role="status">{msg.text}</div>}

      {editing && (
        <form onSubmit={submit} style={{ margin: '1rem 0' }}>
          {fields.map((f) => (
            <div className="field" key={f.key}>
              <label htmlFor={`f-${f.key}`}>{f.label}{f.required && ' *'}{f.type === 'list' && ' (one per line)'}{f.type === 'csv' && ' (comma separated)'}</label>
              {f.type === 'select' ? (
                <select id={`f-${f.key}`} value={form[f.key]} onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}>{f.options.map((o) => <option key={o}>{o}</option>)}</select>
              ) : f.type === 'text' ? (
                <input id={`f-${f.key}`} value={form[f.key]} onChange={(e) => setForm({ ...form, [f.key]: e.target.value })} />
              ) : (
                <textarea id={`f-${f.key}`} rows={f.rows || 4} value={form[f.key]} onChange={(e) => setForm({ ...form, [f.key]: e.target.value })} />
              )}
            </div>
          ))}
          <div className="row"><button className="btn primary">Save</button><button type="button" className="btn" onClick={() => setEditing(null)}>Cancel</button></div>
        </form>
      )}

      {rows === null ? <p className="muted">Loading…</p> : (
        <div className="table-wrap">
          <table>
            <thead><tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}<th /></tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  {columns.map((c) => <td key={c.key}>{c.key === 'status' ? <span className={`badge ${r.status}`}>{r.status}</span> : String(r[c.key] ?? '')}</td>)}
                  <td style={{ whiteSpace: 'nowrap' }}>
                    <button className="btn sm" onClick={() => start(r)}>Edit</button>{' '}
                    <button className="btn sm danger" onClick={() => remove(r)}>Delete</button>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && <tr><td colSpan={columns.length + 1} className="muted">Nothing here yet.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
