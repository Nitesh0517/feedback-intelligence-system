import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Overview } from './pages/Overview';
import { FeedbackList } from './pages/FeedbackList';
import { FeedbackDetail } from './pages/FeedbackDetail';
import { FeedbackForm } from './pages/FeedbackForm';
import { Analytics } from './pages/Analytics';
import { Users } from './pages/Users';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Unauthorized } from './pages/Unauthorized';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* Authenticated Application Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<Overview />} />
              <Route path="feedback" element={<FeedbackList />} />
              <Route path="feedback/:id" element={<FeedbackDetail />} />
              <Route path="analytics" element={<Analytics />} />

              {/* Ingestion restricted to Analyst and Admin */}
              <Route element={<ProtectedRoute allowedRoles={['admin', 'analyst']} />}>
                <Route path="submit" element={<FeedbackForm />} />
              </Route>

              {/* User Directory strictly restricted to Admin */}
              <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
                <Route path="users" element={<Users />} />
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
