import { useEffect, useState } from 'react';
import { api } from '../api/index.js';
import { DOMAINS } from '../api/seed.js';
import ResourceManager from '../components/ResourceManager.jsx';

const STATUS = ['active', 'inactive', 'outdated'];

const RESOURCES = {
  knowledge: {
    label: 'Legal knowledge entries',
    columns: [{ key: 'title', label: 'Title' }, { key: 'domain', label: 'Domain' }],
    fields: [
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'domain', label: 'Domain', type: 'select', options: DOMAINS },
      { key: 'explanation', label: 'Explanation', type: 'textarea', required: true },
      { key: 'keywords', label: 'Keywords', type: 'csv' },
      { key: 'prerequisites', label: 'Prerequisites', type: 'list' },
      { key: 'steps', label: 'Procedure steps', type: 'list' },
      { key: 'refIds', label: 'Reference IDs', type: 'csv' },
      { key: 'templateHint', label: 'Linked template name', type: 'text' },
    ],
  },
  references: {
    label: 'Case-law / legal references',
    columns: [{ key: 'title', label: 'Title' }, { key: 'source', label: 'Source' }, { key: 'domain', label: 'Domain' }, { key: 'status', label: 'Status' }],
    fields: [
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'source', label: 'Source', type: 'text', required: true },
      { key: 'domain', label: 'Domain', type: 'select', options: DOMAINS },
      { key: 'date', label: 'Date (YYYY-MM-DD)', type: 'text' },
      { key: 'link', label: 'Link', type: 'text' },
      { key: 'status', label: 'Status', type: 'select', options: STATUS },
    ],
  },
  templates: {
    label: 'Document templates',
    columns: [{ key: 'name', label: 'Name' }, { key: 'category', label: 'Category' }, { key: 'version', label: 'Version' }, { key: 'status', label: 'Status' }],
    fields: [
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'category', label: 'Category', type: 'select', options: DOMAINS },
      { key: 'description', label: 'Description', type: 'textarea', rows: 2, required: true },
      { key: 'version', label: 'Version', type: 'text', required: true },
      { key: 'status', label: 'Status', type: 'select', options: ['active', 'inactive'] },
      { key: 'content', label: 'Template content', type: 'textarea', rows: 10, required: true },
    ],
  },
};

function Overview() {
  const [s, setS] = useState(null);
  const [err, setErr] = useState('');
  useEffect(() => { api.admin.stats().then(setS).catch((e) => setErr(e.message)); }, []);
  if (err) return <div className="alert error">{err}</div>;
  if (!s) return <p className="muted">Loading…</p>;
  const items = [['Users', s.users], ['Conversations', s.conversations], ['Knowledge entries', s.knowledgeEntries], ['References', s.references], ['Outdated / inactive refs', s.outdatedReferences], ['Templates', s.templates]];
  return (
    <div className="grid cols-3">
      {items.map(([k, v]) => <div className="card" key={k}><div className="stat">{v}</div><div className="muted">{k}</div></div>)}
    </div>
  );
}

function Users() {
  const [rows, setRows] = useState(null);
  const [err, setErr] = useState('');
  const load = () => api.admin.list('users').then(setRows).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  const update = async (u, patch) => { try { await api.admin.save('users', { id: u.id, ...patch }); load(); } catch (e) { setErr(e.message); } };
  return (
    <div className="card">
      <h2 style={{ fontSize: '1.15rem' }}>Users</h2>
      {err && <div className="alert error">{err}</div>}
      <div className="table-wrap"><table>
        <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Created</th><th>Status</th></tr></thead>
        <tbody>{rows?.map((u) => (
          <tr key={u.id}>
            <td>{u.name}</td><td>{u.email}</td>
            <td><select value={u.role} onChange={(e) => update(u, { role: e.target.value })} aria-label={`Role for ${u.email}`}><option>user</option><option>admin</option></select></td>
            <td>{new Date(u.createdAt).toLocaleDateString()}</td>
            <td><button className={`btn sm ${u.active ? '' : 'danger'}`} onClick={() => update(u, { active: !u.active })}>{u.active ? 'Active – deactivate' : 'Inactive – activate'}</button></td>
          </tr>
        ))}</tbody>
      </table></div>
    </div>
  );
}

function AuditLog() {
  const [rows, setRows] = useState(null);
  useEffect(() => { api.admin.audit().then(setRows).catch(() => setRows([])); }, []);
  return (
    <div className="card">
      <h2 style={{ fontSize: '1.15rem' }}>Audit log</h2>
      <div className="table-wrap"><table>
        <thead><tr><th>When</th><th>Admin</th><th>Action</th><th>Target</th></tr></thead>
        <tbody>
          {rows?.map((r) => <tr key={r.id}><td>{new Date(r.at).toLocaleString()}</td><td>{r.actor}</td><td>{r.action}</td><td>{r.target}</td></tr>)}
          {rows?.length === 0 && <tr><td colSpan="4" className="muted">No administrative actions recorded yet.</td></tr>}
        </tbody>
      </table></div>
    </div>
  );
}

const TABS = [['overview', 'Overview'], ['knowledge', 'Knowledge'], ['references', 'References'], ['templates', 'Templates'], ['users', 'Users'], ['audit', 'Audit log']];

export default function Admin() {
  const [tab, setTab] = useState('overview');
  return (
    <main className="container">
      <h1 style={{ fontSize: '1.4rem' }}>Administrator dashboard</h1>
      <div className="row" style={{ marginBottom: '1rem' }} role="tablist">
        {TABS.map(([k, l]) => (
          <button key={k} role="tab" aria-selected={tab === k} className="chip" style={tab === k ? { borderColor: 'var(--accent)', fontWeight: 600 } : {}} onClick={() => setTab(k)}>{l}</button>
        ))}
      </div>
      {tab === 'overview' && <Overview />}
      {RESOURCES[tab] && <ResourceManager key={tab} resource={tab} {...RESOURCES[tab]} />}
      {tab === 'users' && <Users />}
      {tab === 'audit' && <AuditLog />}
    </main>
  );
}
