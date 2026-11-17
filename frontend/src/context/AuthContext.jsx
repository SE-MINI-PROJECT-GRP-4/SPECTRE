import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api } from '../api/index.js';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.me().then((d) => setUser(d.user)).catch(() => setUser(null)).finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (creds) => { const d = await api.login(creds); setUser(d.user); return d.user; }, []);
  const register = useCallback(async (data) => { const d = await api.register(data); setUser(d.user); return d.user; }, []);
  const logout = useCallback(async () => { await api.logout(); setUser(null); }, []); // REQ-AUTH-08

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthContext.Provider>
  );
}
