import { useEffect, useState } from "react";
import { listCommunities } from "../api/communities";
import Sidebar from "../components/layout/Sidebar";
import type { Community } from "../types";
import { Link } from "react-router-dom";

const ADDICTION_ICONS: Record<string, string> = {
  ALCOHOL: "🍷",
  DRUGS: "💊",
  GAMBLING: "🎲",
  GAMING: "🎮",
  SEX: "🔒",
  FOOD: "🍔",
  SMOKING: "🚬",
  OTHER: "💬",
};

export default function Dashboard() {
  const [communities, setCommunities] = useState<Community[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listCommunities()
      .then((data) => setCommunities(data.communities))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 flex gap-6">
      <Sidebar communities={communities} />

      <main className="flex-1">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Support Communities</h1>

        {loading ? (
          <div className="text-gray-400 text-sm">Loading communities...</div>
        ) : communities.length === 0 ? (
          <div className="text-gray-400 text-sm">No communities yet.</div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-4">
            {communities.map((c) => (
              <Link key={c.id} to={`/c/${c.slug}`}>
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-brand-200 transition">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl">{ADDICTION_ICONS[c.addiction_type] ?? "💬"}</span>
                    <div>
                      <h2 className="font-semibold text-gray-900">{c.name}</h2>
                      <p className="text-xs text-gray-400">{c.member_count} members</p>
                    </div>
                    {c.required_tier && (
                      <span className="ml-auto text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-medium">
                        {c.required_tier} Tier
                      </span>
                    )}
                  </div>
                  {c.description && (
                    <p className="text-sm text-gray-500 line-clamp-2">{c.description}</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
