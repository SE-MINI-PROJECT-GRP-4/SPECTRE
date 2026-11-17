import { mockApi } from './mockApi.js';
import { httpApi } from './httpApi.js';

// Mock backend is on unless VITE_USE_MOCK=false
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
export const api = USE_MOCK ? mockApi : httpApi;
