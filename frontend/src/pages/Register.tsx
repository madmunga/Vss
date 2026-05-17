import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register, getMe } from "../api/auth";
import { useAuthStore } from "../store/authStore";

const ADDICTION_OPTIONS = [
  "ALCOHOL", "DRUGS", "GAMBLING", "GAMING", "SEX", "FOOD", "SMOKING", "OTHER",
];

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [realName, setRealName] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useAuthStore();

  const toggleAddiction = (type: string) => {
    setSelected((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selected.length === 0) {
      setError("Please select at least one area you need support with.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const tokens = await register({
        email,
        password,
        real_name: realName || undefined,
        addiction_types: selected,
      });
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      const user = await getMe();
      setUser(user);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Join VSS</h1>
        <p className="text-sm text-gray-500 mb-6">
          Your real name is never shared with other users. You'll appear only by a private pseudonym.
        </p>

        {error && (
          <div className="bg-red-50 text-red-700 text-sm rounded-lg p-3 mb-4">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1">
              Email <span className="text-gray-400 font-normal">(kept private)</span>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1">
              Name <span className="text-gray-400 font-normal">(optional, kept private)</span>
            </label>
            <input
              type="text"
              value={realName}
              onChange={(e) => setRealName(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-2">
              I'm seeking support for <span className="text-red-400">*</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {ADDICTION_OPTIONS.map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => toggleAddiction(type)}
                  className={`px-3 py-1 rounded-full text-xs font-medium border transition ${
                    selected.includes(type)
                      ? "bg-brand-600 text-white border-brand-600"
                      : "border-gray-300 text-gray-600 hover:border-brand-400"
                  }`}
                >
                  {type.charAt(0) + type.slice(1).toLowerCase()}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 text-white font-semibold py-2.5 rounded-xl hover:bg-brand-700 transition disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create anonymous account"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-brand-600 font-semibold hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
