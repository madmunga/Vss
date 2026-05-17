import { useState } from "react";
import type { Post } from "../../types";
import VoteButton from "./VoteButton";
import { createPost } from "../../api/posts";
import { useFeedStore } from "../../store/feedStore";

interface Props {
  post: Post;
  communityId: string;
  communitySlug: string;
  onVote: (postId: string) => void;
}

export default function PostCard({ post, communityId, communitySlug, onVote }: Props) {
  const [showReply, setShowReply] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { prependPost } = useFeedStore();

  const handleReply = async () => {
    if (!replyText.trim()) return;
    setSubmitting(true);
    try {
      await createPost(communityId, replyText, post.id);
      setReplyText("");
      setShowReply(false);
    } finally {
      setSubmitting(false);
    }
  };

  const timeAgo = (iso: string) => {
    const diff = Date.now() - new Date(iso).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-xs">
          {post.display_name.charAt(0)}
        </div>
        <div>
          <span className="text-sm font-semibold text-brand-700">{post.display_name}</span>
          <span className="text-xs text-gray-400 ml-2">{timeAgo(post.created_at)}</span>
        </div>
      </div>

      <p className="text-gray-800 leading-relaxed whitespace-pre-wrap text-sm">
        {post.is_deleted ? <span className="italic text-gray-400">[deleted]</span> : post.content}
      </p>

      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-gray-50">
        <VoteButton count={post.upvotes} onVote={() => onVote(post.id)} />
        <button
          onClick={() => setShowReply(!showReply)}
          className="text-xs text-gray-500 hover:text-brand-600 transition flex items-center gap-1"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          {post.reply_count} {post.reply_count === 1 ? "reply" : "replies"}
        </button>
      </div>

      {showReply && (
        <div className="mt-3 flex gap-2">
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="Write a supportive reply..."
            rows={2}
            className="flex-1 text-sm border border-gray-200 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
          <button
            onClick={handleReply}
            disabled={submitting || !replyText.trim()}
            className="self-end bg-brand-600 text-white text-xs px-3 py-2 rounded-lg hover:bg-brand-700 transition disabled:opacity-50"
          >
            {submitting ? "..." : "Reply"}
          </button>
        </div>
      )}
    </div>
  );
}
