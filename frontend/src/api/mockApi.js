// In-browser mock backend. Mirrors the contract in httpApi.js so the UI can be built
// and demoed before the real backend exists. NOT secure – never use for real data.
import { seedReferences, seedKnowledge, seedTemplates, seedUsers } from './seed.js';
import { session } from './session.js';
import { DISCLAIMER_TEXT } from '../components/Disclaimer.jsx';

const DB_KEY = 'spectre.mockdb.v1';
const wait = (ms = 450) => new Promise((r) => setTimeout(r, ms));
const uid = (p) => `${p}-${Math.random().toString(36).slice(2, 9)}`;
const fail = (message, status = 400) => Object.assign(new Error(message), { status });

function load() {
  try {
    const raw = localStorage.getItem(DB_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* fall through to seed */ }
  const db = { users: seedUsers, references: seedReferences, knowledge: seedKnowledge, templates: seedTemplates, conversations: [], audit: [] };
  save(db);
  return db;
}
const save = (db) => localStorage.setItem(DB_KEY, JSON.stringify(db));
const publicUser = ({ password, ...u }) => u;

function currentUser(db, required = true) {
  const id = session.get();
  const u = db.users.find((x) => x.id === id && x.active);
  if (!u && required) throw fail('Please log in to continue.', 401);
  return u || null;
}
function requireAdmin(db) {
  const u = currentUser(db);
  if (u.role !== 'admin') throw fail('You are not authorized to perform this action.', 403); // REQ-AUTH-06
  return u;
}
function audit(db, actor, action, target) {
  db.audit.unshift({ id: uid('log'), at: new Date().toISOString(), actor: actor.email, action, target }); // REQ-ADMIN-06
}

// --- lightweight domain classifier + retrieval (REQ-QUERY-03/04) -----------------
function classify(db, text, prevDomain) {
  const t = text.toLowerCase();
  let best = null;
  for (const k of db.knowledge) {
    const score = k.keywords.filter((w) => t.includes(w)).length;
    if (score > 0 && (!best || score > best.score)) best = { k, score };
  }
  if (best) return best.k;
  return prevDomain ? db.knowledge.find((k) => k.domain === prevDomain) || null : null;
}

function buildAnswer(db, text, prevDomain) {
  const kb = classify(db, text, prevDomain);
  const base = { id: uid('m'), role: 'assistant', createdAt: new Date().toISOString(), disclaimer: DISCLAIMER_TEXT };
  if (!kb) {
    return { ...base, confidence: 'insufficient', domain: null, text: "I don't have enough reliable information to answer that confidently. Could you add details such as what happened, when, and where? For case-specific advice, please consult a qualified lawyer.", sources: [], procedure: null, notes: [], template: null };
  }
  const refs = kb.refIds.map((id) => db.references.find((r) => r.id === id)).filter((r) => r && r.status !== 'inactive'); // REQ-REF-09 / BR-04
  const notes = ['Procedures can vary by state, facts and current law (REQ-PROC-04).'];
  refs.filter((r) => r.status === 'outdated').forEach((r) => notes.push(`"${r.title}" is marked as possibly outdated – verify its current status.`));
  const tpl = kb.templateHint ? db.templates.find((t) => t.name === kb.templateHint && t.status === 'active') : null;
  return { ...base, confidence: refs.length ? 'medium' : 'low', domain: kb.domain, text: kb.explanation, procedure: { prerequisites: kb.prerequisites, steps: kb.steps }, sources: refs, notes, template: tpl ? { id: tpl.id, name: tpl.name } : null };
}

export const mockApi = {
  async register({ name, email, password }) {
    await wait();
    const db = load();
    if (db.users.some((u) => u.email.toLowerCase() === email.toLowerCase())) throw fail('An account with this email already exists.', 409); // REQ-AUTH-03
    const user = { id: uid('u'), name, email, password, role: 'user', createdAt: new Date().toISOString(), active: true };
    db.users.push(user); save(db);
    session.set(user.id);
    return { user: publicUser(user) };
  },
  async login({ email, password }) {
    await wait();
    const db = load();
    const u = db.users.find((x) => x.email.toLowerCase() === email.toLowerCase());
    if (!u || u.password !== password || !u.active) throw fail('Invalid email or password.', 401); // REQ-AUTH-05
    session.set(u.id);
    return { user: publicUser(u) };
  },
  async logout() { session.clear(); },
  async me() {
    const db = load();
    const u = currentUser(db, false);
    return u ? { user: publicUser(u) } : { user: null };
  },

  async sendQuery({ text, conversationId }) {
    await wait(900);
    const db = load();
    const user = currentUser(db, false);
    let convo = conversationId && db.conversations.find((c) => c.id === conversationId && c.userId === user?.id);
    const userMsg = { id: uid('m'), role: 'user', text, createdAt: new Date().toISOString() };
    const prevDomain = convo ? [...convo.messages].reverse().find((m) => m.domain)?.domain : null; // REQ-QUERY-12
    const answer = buildAnswer(db, text, prevDomain);
    if (user) {
      if (!convo) {
        convo = { id: uid('c'), userId: user.id, title: text.slice(0, 60), domain: answer.domain, createdAt: new Date().toISOString(), messages: [] };
        db.conversations.unshift(convo);
      }
      convo.messages.push(userMsg, answer);
      if (answer.domain) convo.domain = answer.domain;
      save(db);
    }
    return { conversationId: convo?.id || null, userMessage: userMsg, answer };
  },
  async listConversations() {
    await wait(250);
    const db = load(); const u = currentUser(db);
    return db.conversations.filter((c) => c.userId === u.id).map(({ messages, ...c }) => ({ ...c, messageCount: messages.length })); // REQ-HIST-04
  },
  async getConversation(id) {
    await wait(250);
    const db = load(); const u = currentUser(db);
    const c = db.conversations.find((x) => x.id === id && x.userId === u.id);
    if (!c) throw fail('This conversation is no longer available.', 404); // REQ-HIST-05
    return c;
  },
  async deleteConversation(id) {
    const db = load(); const u = currentUser(db);
    db.conversations = db.conversations.filter((c) => !(c.id === id && c.userId === u.id)); save(db);
  },

  async listReferences() { await wait(200); return load().references; },
  async listTemplates() { await wait(200); return load().templates.filter((t) => t.status === 'active'); },

  admin: {
    async list(resource) {
      await wait(200);
      const db = load(); requireAdmin(db);
      return resource === 'users' ? db.users.map(publicUser) : db[resource];
    },
    async save(resource, item) {
      await wait(250);
      const db = load(); const actor = requireAdmin(db);
      const list = db[resource];
      const i = item.id ? list.findIndex((x) => x.id === item.id) : -1;
      if (i >= 0) { list[i] = { ...list[i], ...item }; audit(db, actor, 'update', `${resource}/${item.id}`); }
      else { const created = { ...item, id: uid(resource.slice(0, 3)) }; list.push(created); audit(db, actor, 'create', `${resource}/${created.id}`); }
      save(db);
    },
    async remove(resource, id) {
      await wait(250);
      const db = load(); const actor = requireAdmin(db);
      db[resource] = db[resource].filter((x) => x.id !== id);
      audit(db, actor, 'delete', `${resource}/${id}`); save(db);
    },
    async audit() { await wait(200); const db = load(); requireAdmin(db); return db.audit; },
    async stats() {
      await wait(200);
      const db = load(); requireAdmin(db);
      return {
        users: db.users.length,
        conversations: db.conversations.length,
        references: db.references.length,
        outdatedReferences: db.references.filter((r) => r.status !== 'active').length,
        templates: db.templates.length,
        knowledgeEntries: db.knowledge.length,
      };
    },
  },
};
