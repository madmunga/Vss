import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="bg-brand-900 text-white px-6 py-3 flex items-center justify-between shadow-lg">
      <Link to="/" className="text-xl font-bold tracking-tight">
        VSS<span className="text-brand-500 ml-1 text-sm font-normal">Veil Support</span>
      </Link>

      <div className="flex items-center gap-4 text-sm">
        {user ? (
          <>
            <Link to="/dashboard" className="hover:text-brand-100 transition">Feed</Link>
            <Link to="/professionals" className="hover:text-brand-100 transition">Professionals</Link>
            <Link to="/subscribe" className="hover:text-brand-100 transition">Subscribe</Link>
            {user.role === "PROFESSIONAL" && (
              <Link to="/portal" className="hover:text-brand-100 transition">My Portal</Link>
            )}
            <Link to="/profile" className="hover:text-brand-100 transition">
              <span className="bg-brand-700 rounded-full px-3 py-1">{user.display_name}</span>
            </Link>
            <button onClick={handleLogout} className="text-brand-300 hover:text-white transition">
              Sign out
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="hover:text-brand-100 transition">Sign in</Link>
            <Link
              to="/register"
              className="bg-brand-500 hover:bg-brand-600 px-4 py-1.5 rounded-full font-medium transition"
            >
              Join free
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
