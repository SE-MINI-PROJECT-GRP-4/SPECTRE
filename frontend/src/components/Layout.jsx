import { NavLink, Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function Layout() {
  const { user, isAdmin, logout } = useAuth();
  const nav = useNavigate();

  return (
    <>
      <header className="topbar">
        <div className="inner">
          <Link to="/" className="brand">⚖️ SPECTRE</Link>
          <nav className="nav" aria-label="Main">
            <NavLink to="/" end>Home</NavLink>
            <NavLink to="/chat">Ask</NavLink>
            <NavLink to="/templates">Templates</NavLink>
            {user && <NavLink to="/history">History</NavLink>}
            {isAdmin && <NavLink to="/admin">Admin</NavLink>}
            {user ? (
              <button onClick={async () => { await logout(); nav('/'); }}>Log out ({user.name.split(' ')[0]})</button>
            ) : (
              <>
                <NavLink to="/login">Log in</NavLink>
                <NavLink to="/register">Register</NavLink>
              </>
            )}
          </nav>
        </div>
      </header>
      <Outlet />
      <footer className="footer">
        SPECTRE provides general legal information for India. It is not a substitute for a qualified lawyer and does not guarantee any legal outcome.
      </footer>
    </>
  );
}
