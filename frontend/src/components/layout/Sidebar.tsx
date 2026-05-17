import { Link } from "react-router-dom";
import type { Community } from "../../types";

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

interface Props {
  communities: Community[];
}

export default function Sidebar({ communities }: Props) {
  return (
    <aside className="w-60 shrink-0 hidden md:block">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Communities</h2>
        <ul className="space-y-1">
          {communities.map((c) => (
            <li key={c.id}>
              <Link
                to={`/c/${c.slug}`}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm text-gray-700 hover:bg-brand-50 hover:text-brand-700 transition"
              >
                <span>{ADDICTION_ICONS[c.addiction_type] ?? "💬"}</span>
                <span className="truncate">{c.name}</span>
                {c.required_tier && (
                  <span className="ml-auto text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded">
                    {c.required_tier}
                  </span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
