// =====================================================
// src/App.jsx — Main App + Routes
// =====================================================

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Sidebar from "./components/Sidebar";

// Pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminDashboard from "./pages/admin/Dashboard";
import Documents from "./pages/admin/Documents";
import UploadDocuments from "./pages/admin/UploadDocuments";
import AdminUsers from "./pages/admin/Users";
import UserDashboard from "./pages/user/Dashboard";
import Chatbot from "./pages/user/Chatbot";

// =====================================================
// Layout with Sidebar (logged in pages)
// =====================================================
function AppLayout({ children }) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 min-h-screen">
        {children}
      </main>
    </div>
  );
}

// =====================================================
// Protected Routes — login check karo
// =====================================================
function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" />;
  if (role && user.role !== role) return <Navigate to={user.role === "admin" ? "/admin" : "/user"} />;

  return children;
}

// =====================================================
// All Routes
// =====================================================
function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={user ? <Navigate to={user.role === "admin" ? "/admin" : "/user"} /> : <Login />} />
      <Route path="/register" element={<Register />} />

      {/* Admin Routes */}
      <Route path="/admin" element={
        <ProtectedRoute role="admin">
          <AppLayout><AdminDashboard /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/admin/documents" element={
        <ProtectedRoute role="admin">
          <AppLayout><Documents /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/admin/upload" element={
        <ProtectedRoute role="admin">
          <AppLayout><UploadDocuments /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/admin/users" element={
        <ProtectedRoute role="admin">
          <AppLayout><AdminUsers /></AppLayout>
        </ProtectedRoute>
      } />

      {/* User Routes */}
      <Route path="/user" element={
        <ProtectedRoute>
          <AppLayout><UserDashboard /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/user/chat" element={
        <ProtectedRoute>
          <Chatbot /> {/* Chatbot apna layout khud manage karta hai */}
        </ProtectedRoute>
      } />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
