import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './HomePage';
import ProjectDashboard from './pages/ProjectDashboard';
import WorkspacePage from './pages/WorkspacePage';
import AdminPage from './pages/AdminPage';
import IntroScreen from './components/IntroScreen';
import authService from './services/authService';

function ProtectedRoute({ children }) {
  return authService.isAuthenticated() ? children : <Navigate to="/login" />;
}

function App() {
  const [showIntro, setShowIntro] = useState(() => {
    return sessionStorage.getItem('introSeen') !== 'true';
  });

  // Apply saved theme on app load
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  // Show splash only once per session
  if (showIntro) {
    return (
      <IntroScreen
        onComplete={() => {
          sessionStorage.setItem('introSeen', 'true');
          setShowIntro(false);
        }}
      />
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/home" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <ProjectDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/workspace/:projectId"
          element={
            <ProtectedRoute>
              <WorkspacePage />
            </ProtectedRoute>
          }
        />

        {/* Default route */}
        <Route path="/" element={<Navigate to="/home" />} />
      </Routes>
    </Router>
  );
}

export default App;
