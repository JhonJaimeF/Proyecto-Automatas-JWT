import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';  // Mantenemos por si quieres auth en otras partes
import App from './App.jsx';
import Login from './pages/Login.jsx';
import User from './pages/User.jsx';
import Admin from './pages/Admin.jsx';
// Imports de tools (mantenemos para Admin)
import Generar from './pages/Generar.jsx';
import Verificar from './pages/Verificar.jsx';
import Decodificar from './pages/Decodificar.jsx';
import AnalisisLexico from './pages/AnalisisLexico.jsx';
import AnalisisSintactico from './pages/AnalisisSintactico.jsx';
import AnalisisSemantico from './pages/AnalisisSemantico.jsx';
// ← Removimos ProtectedRoute temporalmente para simplicidad

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<Navigate to="/login" replace />} />  {/* O cambia a /generar si quieres */}
            <Route path="login" element={<Login />} />
            <Route path="user" element={<User />} />  {/* Sin ProtectedRoute por ahora */}
            <Route path="admin" element={<Admin />}>  {/* Sin ProtectedRoute */}
              <Route path="tools/generar" element={<Generar />} />
              <Route path="tools/verificar" element={<Verificar />} />
              <Route path="tools/decodificar" element={<Decodificar />} />
              <Route path="tools/analisis-lexico" element={<AnalisisLexico />} />
              <Route path="tools/analisis-sintactico" element={<AnalisisSintactico />} />
              <Route path="tools/analisis-semantico" element={<AnalisisSemantico />} />
              <Route index element={<Navigate to="tools/generar" replace />} />
            </Route>
            
            {/* ← NUEVA: Ruta independiente para Generar, sin auth ni Admin */}
            <Route path="generar" element={<Generar />} />
            <Route path="verificar" element={<Verificar />} />
              <Route path="decodificar" element={<Decodificar />} />
              <Route path="analisis-lexico" element={<AnalisisLexico />} />
              <Route path="analisis-sintactico" element={<AnalisisSintactico />} />
              <Route path="analisis-semantico" element={<AnalisisSemantico />} />
            
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
);