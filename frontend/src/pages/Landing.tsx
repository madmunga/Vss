import { Link } from "react-router-dom";

const FEATURES = [
  {
    icon: "🛡️",
    title: "Radically Anonymous",
    desc: "Your identity is yours alone. Only your pseudonym is visible to others — always.",
  },
  {
    icon: "💬",
    title: "Community Confessions",
    desc: "Share, listen, and find solidarity in peer groups organized by addiction type.",
  },
  {
    icon: "🩺",
    title: "Vetted Professionals",
    desc: "Licensed psychiatrists and therapists, vetted by accredited psychological facilities.",
  },
  {
    icon: "💸",
    title: "Affordable by Design",
    desc: "Collective subscriptions pool funds so professional help is accessible to everyone.",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-900 to-brand-700 text-white">
      <div className="max-w-5xl mx-auto px-6 pt-24 pb-20 text-center">
        <h1 className="text-5xl md:text-6xl font-extrabold leading-tight mb-6">
          You don't have to face<br />
          <span className="text-brand-300">addiction alone.</span>
        </h1>
        <p className="text-lg text-brand-100 max-w-2xl mx-auto mb-10">
          VSS is a discreet, community-driven support platform connecting people with peer communities and
          vetted professionals — at a price anyone can afford.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/register"
            className="bg-white text-brand-900 font-semibold px-8 py-3 rounded-full hover:bg-brand-50 transition shadow-lg"
          >
            Join anonymously, free
          </Link>
          <Link
            to="/subscribe"
            className="border border-brand-300 text-white font-semibold px-8 py-3 rounded-full hover:bg-brand-800 transition"
          >
            See professional plans
          </Link>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 pb-24 grid sm:grid-cols-2 md:grid-cols-4 gap-6">
        {FEATURES.map((f) => (
          <div key={f.title} className="bg-white/10 backdrop-blur rounded-2xl p-6">
            <div className="text-4xl mb-3">{f.icon}</div>
            <h3 className="font-bold mb-2">{f.title}</h3>
            <p className="text-brand-100 text-sm leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>

      <div className="text-center text-brand-300 text-xs pb-8">
        All data is encrypted. We never sell your information.
      </div>
    </div>
  );
}
