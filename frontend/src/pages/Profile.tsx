import { useEffect, useState } from "react";
import { useAuthStore } from "../store/authStore";
import { getMySubscription } from "../api/subscriptions";
import type { Subscription } from "../types";
import { Link } from "react-router-dom";

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: "bg-green-100 text-green-700",
  CANCELLED: "bg-gray-100 text-gray-500",
  PAST_DUE: "bg-red-100 text-red-600",
  TRIALING: "bg-blue-100 text-blue-600",
};

export default function Profile() {
  const { user } = useAuthStore();
  const [subscription, setSubscription] = useState<Subscription | null>(null);

  useEffect(() => {
    getMySubscription().then(setSubscription).catch(() => {});
  }, []);

  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6 space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-xl">
            {user.display_name.charAt(0)}
          </div>
          <div>
            <p className="font-bold text-gray-900">{user.display_name}</p>
            <p className="text-xs text-gray-400">Your public pseudonym — shown to others</p>
          </div>
        </div>

        <div className="border-t pt-4 space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Email</span>
            <span className="text-gray-900">{user.email}</span>
          </div>
          {user.real_name && (
            <div className="flex justify-between">
              <span className="text-gray-500">Name</span>
              <span className="text-gray-900">{user.real_name}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-gray-500">Support areas</span>
            <div className="flex flex-wrap gap-1 justify-end">
              {user.addiction_types.map((t) => (
                <span key={t} className="bg-brand-50 text-brand-700 px-2 py-0.5 rounded-full text-xs">
                  {t.charAt(0) + t.slice(1).toLowerCase()}
                </span>
              ))}
            </div>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Role</span>
            <span className="text-gray-900 capitalize">{user.role.toLowerCase()}</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <h2 className="font-bold text-gray-900 mb-4">Subscription</h2>
        {subscription ? (
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-gray-500">Tier</span>
              <span className="font-bold text-gray-900">{subscription.tier} Tier</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-500">Status</span>
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${STATUS_COLORS[subscription.status] ?? ""}`}>
                {subscription.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Price</span>
              <span className="text-gray-900">${subscription.price_usd}/month</span>
            </div>
          </div>
        ) : (
          <div className="text-center py-6">
            <p className="text-gray-500 text-sm mb-4">You don't have an active subscription.</p>
            <Link
              to="/subscribe"
              className="bg-brand-600 text-white px-5 py-2 rounded-xl text-sm font-semibold hover:bg-brand-700 transition"
            >
              View plans
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
