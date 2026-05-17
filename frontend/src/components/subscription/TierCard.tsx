import type { TierInfo } from "../../types";

const TIER_COLORS: Record<string, string> = {
  S: "border-purple-400 bg-purple-50",
  A: "border-blue-400 bg-blue-50",
  B: "border-green-400 bg-green-50",
};

const TIER_BADGE: Record<string, string> = {
  S: "bg-purple-600 text-white",
  A: "bg-blue-600 text-white",
  B: "bg-green-600 text-white",
};

interface Props {
  tier: TierInfo;
  onSelect: (tier: string) => void;
  loading: boolean;
}

export default function TierCard({ tier, onSelect, loading }: Props) {
  return (
    <div className={`rounded-2xl border-2 p-6 flex flex-col gap-4 ${TIER_COLORS[tier.tier] ?? "border-gray-200"}`}>
      <div className="flex items-center justify-between">
        <span className={`text-sm font-bold px-3 py-1 rounded-full ${TIER_BADGE[tier.tier]}`}>
          {tier.tier} Tier
        </span>
        <span className="text-2xl font-extrabold text-gray-900">
          ${tier.price_usd}<span className="text-sm font-normal text-gray-500">/mo</span>
        </span>
      </div>

      <p className="text-sm text-gray-600">{tier.description}</p>

      <ul className="space-y-1">
        {tier.features.map((f) => (
          <li key={f} className="flex items-center gap-2 text-sm text-gray-700">
            <svg className="w-4 h-4 text-green-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            {f}
          </li>
        ))}
      </ul>

      <button
        onClick={() => onSelect(tier.tier)}
        disabled={loading}
        className="mt-auto w-full py-2 rounded-xl font-semibold text-sm bg-gray-900 text-white hover:bg-gray-700 transition disabled:opacity-50"
      >
        {loading ? "Redirecting..." : `Choose ${tier.tier} Tier`}
      </button>
    </div>
  );
}
