import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import Layout from './components/Layout.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Chat from './pages/Chat.jsx';
import Templates from './pages/Templates.jsx';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat/:id" element={<Chat />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
