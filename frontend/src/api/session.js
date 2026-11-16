// Token handling. sessionStorage keeps the token out of long-lived storage (NFR-SEC-12).
const KEY = 'spectre.token';
export const session = {
  get: () => sessionStorage.getItem(KEY),
  set: (t) => sessionStorage.setItem(KEY, t),
  clear: () => sessionStorage.removeItem(KEY),
};
