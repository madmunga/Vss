import { useEffect, useState } from "react";
import { listProfessionals } from "../api/professionals";
import ProfessionalCard from "../components/professional/ProfessionalCard";
import type { Professional } from "../types";

const TIERS = ["S", "A", "B"] as const;

export default function Professionals() {
  const [professionals, setProfessionals] = useState<Professional[]>([]);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = (tier?: string) => {
    setLoading(true);
    listProfessionals(tier)
      .then(setProfessionals)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleFilter = (tier: string | null) => {
    setActiveFilter(tier);
    load(tier ?? undefined);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Vetted Professionals</h1>
      <p className="text-sm text-gray-500 mb-6">
        All professionals are licensed and vetted by accredited psychological facilities.
      </p>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => handleFilter(null)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
            activeFilter === null
              ? "bg-gray-900 text-white"
              : "border border-gray-300 text-gray-600 hover:border-gray-400"
          }`}
        >
          All
        </button>
        {TIERS.map((t) => (
          <button
            key={t}
            onClick={() => handleFilter(t)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              activeFilter === t
                ? "bg-gray-900 text-white"
                : "border border-gray-300 text-gray-600 hover:border-gray-400"
            }`}
          >
            {t} Tier
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-gray-400 text-sm">Loading professionals...</div>
      ) : professionals.length === 0 ? (
        <div className="text-gray-400 text-sm text-center py-16">
          No approved professionals in this tier yet.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
          {professionals.map((p) => (
            <ProfessionalCard key={p.id} professional={p} />
          ))}
        </div>
      )}
    </div>
  );
}
