import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import Navbar from "./components/layout/Navbar";
import { useAuthStore } from "./store/authStore";
import Admin from "./pages/Admin";
import Community from "./pages/Community";
import Dashboard from "./pages/Dashboard";
import ForgotPassword from "./pages/ForgotPassword";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import ProfessionalPortal from "./pages/ProfessionalPortal";
import Professionals from "./pages/Professionals";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import Subscription from "./pages/Subscription";
import VerifyEmail from "./pages/VerifyEmail";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuthStore();
  if (isLoading) return (
    <div className="flex items-center justify-center h-screen text-gray-400 text-sm">Loading...</div>
  );
  return user ? <>{children}</> : <Navigate to="/login" replace />;
}

function ProfessionalRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuthStore();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!["PROFESSIONAL", "ADMIN"].includes(user.role)) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuthStore();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "ADMIN") return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

export default function App() {
  const { bootstrap } = useAuthStore();

  useEffect(() => {
    bootstrap();
  }, []);

  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Navbar />
        <Routes>
          {/* Public */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/professionals" element={<Professionals />} />
          <Route path="/subscribe" element={<Subscription />} />

          {/* Authenticated */}
          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/c/:slug" element={<PrivateRoute><Community /></PrivateRoute>} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="/subscribe/success" element={
            <PrivateRoute>
              <div className="max-w-xl mx-auto px-4 py-20 text-center">
                <div className="text-5xl mb-4">🎉</div>
                <h1 className="text-2xl font-bold text-green-700 mb-2">Subscription activated!</h1>
                <p className="text-gray-500 text-sm">
                  You'll be assigned a professional shortly. Check your profile for status.
                </p>
              </div>
            </PrivateRoute>
          } />

          {/* Professional portal */}
          <Route path="/portal" element={<ProfessionalRoute><ProfessionalPortal /></ProfessionalRoute>} />

          {/* Admin */}
          <Route path="/admin" element={<AdminRoute><Admin /></AdminRoute>} />

          {/* Catch-all */}
          <Route path="*" element={
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
              <h1 className="text-4xl font-bold text-gray-300 mb-2">404</h1>
              <p className="text-gray-500">Page not found.</p>
            </div>
          } />
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
