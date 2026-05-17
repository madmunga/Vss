import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import client from "../api/client";

export default function VerifyEmail() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) { setStatus("error"); setMessage("No verification token provided."); return; }
    client.post("/auth/verify-email", { token })
      .then(() => setStatus("success"))
      .catch((err) => { setStatus("error"); setMessage(err.response?.data?.detail ?? "Verification failed."); });
  }, [token]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
        {status === "loading" && <p className="text-gray-500">Verifying your email...</p>}
        {status === "success" && (
          <>
            <div className="text-5xl mb-4">✅</div>
            <h1 className="text-xl font-bold text-gray-900 mb-2">Email verified!</h1>
            <p className="text-gray-500 text-sm mb-4">Your account is now verified.</p>
            <Link to="/dashboard" className="bg-brand-600 text-white px-5 py-2 rounded-xl text-sm font-semibold hover:bg-brand-700 transition">
              Go to dashboard
            </Link>
          </>
        )}
        {status === "error" && (
          <>
            <div className="text-5xl mb-4">❌</div>
            <h1 className="text-xl font-bold text-gray-900 mb-2">Verification failed</h1>
            <p className="text-gray-500 text-sm mb-4">{message}</p>
            <Link to="/login" className="text-brand-600 font-semibold hover:underline text-sm">Back to sign in</Link>
          </>
        )}
      </div>
    </div>
  );
}
