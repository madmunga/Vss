import { useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post("/auth/forgot-password", { email });
    } catch {
      // Intentionally ignore errors — always show success to avoid email enumeration
    } finally {
      setSubmitted(true);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Reset your password</h1>
        <p className="text-sm text-gray-500 mb-6">
          Enter your email and we'll send a reset link if an account exists.
        </p>

        {submitted ? (
          <div className="bg-green-50 text-green-700 rounded-xl p-4 text-sm text-center">
            If an account with that email exists, a reset link has been sent.
            <br />
            <Link to="/login" className="font-semibold underline mt-2 inline-block">Back to sign in</Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-600 text-white font-semibold py-2.5 rounded-xl hover:bg-brand-700 transition disabled:opacity-50"
            >
              {loading ? "Sending..." : "Send reset link"}
            </button>
            <p className="text-center text-sm text-gray-400">
              <Link to="/login" className="hover:text-brand-600">Back to sign in</Link>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
