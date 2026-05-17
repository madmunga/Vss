import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import { useAuthStore } from "./store/authStore";
import Community from "./pages/Community";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import ProfessionalPortal from "./pages/ProfessionalPortal";
import Professionals from "./pages/Professionals";
import Register from "./pages/Register";
import Subscription from "./pages/Subscription";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuthStore();
  if (isLoading) return <div className="flex items-center justify-center h-screen text-gray-400">Loading...</div>;
  return user ? <>{children}</> : <Navigate to="/login" replace />;
}

function ProfessionalRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuthStore();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!["PROFESSIONAL", "ADMIN"].includes(user.role)) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

export default function App() {
  const { bootstrap } = useAuthStore();

  useEffect(() => {
    bootstrap();
  }, []);

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/professionals" element={<Professionals />} />
        <Route path="/subscribe" element={<Subscription />} />

        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/c/:slug"
          element={
            <PrivateRoute>
              <Community />
            </PrivateRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <PrivateRoute>
              <Profile />
            </PrivateRoute>
          }
        />
        <Route
          path="/subscribe/success"
          element={
            <PrivateRoute>
              <div className="max-w-xl mx-auto px-4 py-20 text-center">
                <h1 className="text-2xl font-bold text-green-700 mb-2">Subscription activated!</h1>
                <p className="text-gray-500">You'll be assigned a professional shortly. Check your profile for status.</p>
              </div>
            </PrivateRoute>
          }
        />
        <Route
          path="/portal"
          element={
            <ProfessionalRoute>
              <ProfessionalPortal />
            </ProfessionalRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
