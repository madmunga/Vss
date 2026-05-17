import type { Professional } from "../../types";

const TIER_COLORS: Record<string, string> = {
  S: "bg-purple-100 text-purple-700",
  A: "bg-blue-100 text-blue-700",
  B: "bg-green-100 text-green-700",
};

interface Props {
  professional: Professional;
}

export default function ProfessionalCard({ professional: p }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold">
            {p.display_name.charAt(0)}
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">{p.display_name}</p>
            <p className="text-xs text-gray-500 capitalize">{p.specialty.toLowerCase()}</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${TIER_COLORS[p.tier]}`}>
          {p.tier} Tier
        </span>
      </div>

      {p.bio && <p className="text-sm text-gray-600 line-clamp-3">{p.bio}</p>}

      <div className="flex items-center gap-3 text-xs text-gray-500">
        {p.years_experience && <span>{p.years_experience} yrs exp</span>}
        <span>{p.languages.join(", ")}</span>
      </div>
    </div>
  );
}
