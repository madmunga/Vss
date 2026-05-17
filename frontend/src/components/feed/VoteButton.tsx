interface Props {
  count: number;
  onVote: () => void;
}

export default function VoteButton({ count, onVote }: Props) {
  return (
    <button
      onClick={onVote}
      className="flex items-center gap-1 text-sm text-gray-500 hover:text-brand-600 transition group"
    >
      <svg
        className="w-4 h-4 group-hover:scale-110 transition"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
      <span>{count}</span>
    </button>
  );
}
