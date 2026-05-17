import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getCommunity, joinCommunity } from "../api/communities";
import { createPost } from "../api/posts";
import { useFeedStore } from "../store/feedStore";
import { useAuthStore } from "../store/authStore";
import PostCard from "../components/feed/PostCard";
import type { Community as CommunityType } from "../types";

export default function Community() {
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuthStore();
  const { posts, isLoading, loadFeed, vote, prependPost } = useFeedStore();
  const [community, setCommunity] = useState<CommunityType | null>(null);
  const [content, setContent] = useState("");
  const [posting, setPosting] = useState(false);
  const [joined, setJoined] = useState(false);

  useEffect(() => {
    if (!slug) return;
    getCommunity(slug).then(setCommunity);
    loadFeed(slug);
  }, [slug]);

  const handleJoin = async () => {
    if (!slug) return;
    await joinCommunity(slug);
    setJoined(true);
  };

  const handlePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || !community) return;
    setPosting(true);
    try {
      const post = await createPost(community.id, content);
      prependPost(post);
      setContent("");
    } finally {
      setPosting(false);
    }
  };

  if (!community) return <div className="p-8 text-gray-400">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{community.name}</h1>
          {community.description && (
            <p className="text-sm text-gray-500 mt-1">{community.description}</p>
          )}
          <p className="text-xs text-gray-400 mt-1">{community.member_count} members</p>
        </div>
        {user && !joined && (
          <button
            onClick={handleJoin}
            className="bg-brand-600 text-white text-sm px-4 py-2 rounded-xl hover:bg-brand-700 transition"
          >
            Join community
          </button>
        )}
      </div>

      {user && (
        <form onSubmit={handlePost} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 mb-6">
          <p className="text-xs text-gray-400 mb-2">
            Posting as <span className="font-semibold text-brand-600">{user.display_name}</span> (anonymous to others)
          </p>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Share what's on your mind — this is a safe space..."
            rows={3}
            className="w-full text-sm border border-gray-200 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
          <div className="flex justify-end mt-2">
            <button
              type="submit"
              disabled={posting || !content.trim()}
              className="bg-brand-600 text-white text-sm px-4 py-2 rounded-xl hover:bg-brand-700 transition disabled:opacity-50"
            >
              {posting ? "Posting..." : "Post confession"}
            </button>
          </div>
        </form>
      )}

      {isLoading ? (
        <div className="text-gray-400 text-sm">Loading posts...</div>
      ) : posts.length === 0 ? (
        <div className="text-gray-400 text-sm text-center py-12">
          No posts yet. Be the first to share.
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              communityId={community.id}
              communitySlug={slug!}
              onVote={vote}
            />
          ))}
        </div>
      )}
    </div>
  );
}
