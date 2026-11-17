// Real backend client. Expected REST contract is documented in README.md.
import { session } from './session.js';

const BASE = import.meta.env.VITE_API_BASE || '/api';

async function http(path, { method = 'GET', body } = {}) {
  const token = session.get();
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    // REQ-QUERY-10 / NFR-QUAL-02: never leak internals, fail gracefully on network errors
    throw Object.assign(new Error('Cannot reach the server. Please check your connection and try again.'), { status: 0 });
  }
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) throw Object.assign(new Error(data?.message || 'Something went wrong. Please try again.'), { status: res.status });
  return data;
}

export const httpApi = {
  async register(b) { const d = await http('/auth/register', { method: 'POST', body: b }); session.set(d.token); return d; },
  async login(b) { const d = await http('/auth/login', { method: 'POST', body: b }); session.set(d.token); return d; },
  async logout() { try { await http('/auth/logout', { method: 'POST' }); } finally { session.clear(); } },
  async me() { return session.get() ? http('/auth/me').catch(() => ({ user: null })) : { user: null }; },
  sendQuery: (b) => http('/query', { method: 'POST', body: b }),
  listConversations: () => http('/conversations'),
  getConversation: (id) => http(`/conversations/${id}`),
  deleteConversation: (id) => http(`/conversations/${id}`, { method: 'DELETE' }),
  listReferences: () => http('/references'),
  listTemplates: () => http('/templates'),
  admin: {
    list: (r) => http(`/admin/${r}`),
    save: (r, item) => (item.id ? http(`/admin/${r}/${item.id}`, { method: 'PUT', body: item }) : http(`/admin/${r}`, { method: 'POST', body: item })),
    remove: (r, id) => http(`/admin/${r}/${id}`, { method: 'DELETE' }),
    audit: () => http('/admin/audit'),
    stats: () => http('/admin/stats'),
  },
};
