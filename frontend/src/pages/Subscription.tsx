import { useEffect, useState } from "react";
import { getTiers, createCheckout } from "../api/subscriptions";
import TierCard from "../components/subscription/TierCard";
import type { TierInfo } from "../types";

export default function Subscription() {
  const [tiers, setTiers] = useState<TierInfo[]>([]);
  const [loadingTier, setLoadingTier] = useState<string | null>(null);

  useEffect(() => {
    getTiers().then(setTiers);
  }, []);

  const handleSelect = async (tier: string) => {
    setLoadingTier(tier);
    try {
      const { checkout_url } = await createCheckout(tier);
      window.location.href = checkout_url;
    } catch {
      setLoadingTier(null);
      alert("Unable to start checkout. Please try again.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-2">
          Professional Support Plans
        </h1>
        <p className="text-gray-500 max-w-xl mx-auto text-sm leading-relaxed">
          Your subscription pools with others to collectively fund vetted professionals.
          Everyone pays the same flat rate — no hidden fees, no per-session billing.
        </p>
      </div>

      <div className="grid sm:grid-cols-3 gap-6">
        {tiers.map((tier) => (
          <TierCard
            key={tier.tier}
            tier={tier}
            onSelect={handleSelect}
            loading={loadingTier === tier.tier}
          />
        ))}
      </div>

      <p className="text-center text-xs text-gray-400 mt-8">
        Payments are securely processed by Stripe. Cancel anytime.
      </p>
    </div>
  );
}
