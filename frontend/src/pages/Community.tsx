import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getCommunity, joinCommunity } from "../api/communities";
import { createPost, getFeed } from "../api/posts";
import { useAuthStore } from "../store/authStore";
import PostCard from "../components/feed/PostCard";
import ErrorBoundary from "../components/ErrorBoundary";
import type { Community as CommunityType, Post } from "../types";

export default function Community() {
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuthStore();
  const [community, setCommunity] = useState<CommunityType | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [content, setContent] = useState("");
  const [posting, setPosting] = useState(false);
  const [joined, setJoined] = useState(false);
  const [error, setError] = useState("");

  const PAGE_SIZE = 20;

  useEffect(() => {
    if (!slug) return;
    setIsLoading(true);
    setPage(1);
    setCommunity(null);
    setPosts([]);
    Promise.all([getCommunity(slug), getFeed(slug, 1)])
      .then(([comm, feed]) => {
        setCommunity(comm);
        setPosts(feed.posts);
        setTotal(feed.total);
      })
      .catch(() => setError("Failed to load community."))
      .finally(() => setIsLoading(false));
  }, [slug]);

  const loadMore = async () => {
    if (!slug) return;
    setLoadingMore(true);
    const next = page + 1;
    try {
      const feed = await getFeed(slug, next);
      setPosts((prev) => [...prev, ...feed.posts]);
      setPage(next);
    } finally {
      setLoadingMore(false);
    }
  };

  const handleJoin = async () => {
    if (!slug) return;
    try {
      await joinCommunity(slug);
      setJoined(true);
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Could not join community.");
    }
  };

  const handlePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || !community) return;
    setPosting(true);
    setError("");
    try {
      const post = await createPost(community.id, content);
      setPosts((prev) => [post, ...prev]);
      setTotal((t) => t + 1);
      setContent("");
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Failed to post. Please join the community first.");
    } finally {
      setPosting(false);
    }
  };

  const handleVote = (postId: string) => {
    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? { ...p, upvotes: p.upvotes + 1 } : p))
    );
  };

  if (isLoading) return <div className="p-8 text-gray-400 text-center">Loading community...</div>;
  if (!community) return <div className="p-8 text-gray-500 text-center">Community not found.</div>;

  const hasMore = posts.length < total;

  return (
    <ErrorBoundary>
      <div className="max-w-3xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 text-red-700 text-sm rounded-xl px-4 py-3 mb-4 flex justify-between">
            {error}
            <button onClick={() => setError("")} className="font-bold text-red-400">×</button>
          </div>
        )}

        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{community.name}</h1>
            {community.description && <p className="text-sm text-gray-500 mt-1">{community.description}</p>}
            <p className="text-xs text-gray-400 mt-1">{community.member_count} members · {total} posts</p>
          </div>
          {user && !joined && (
            <button onClick={handleJoin}
              className="shrink-0 bg-brand-600 text-white text-sm px-4 py-2 rounded-xl hover:bg-brand-700 transition">
              Join community
            </button>
          )}
        </div>

        {user && (
          <form onSubmit={handlePost} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 mb-6">
            <p className="text-xs text-gray-400 mb-2">
              Posting as <span className="font-semibold text-brand-600">{user.display_name}</span>
              <span className="text-gray-300"> · anonymous to other users</span>
            </p>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share what's on your mind — this is a safe space..."
              rows={3}
              maxLength={5000}
              className="w-full text-sm border border-gray-200 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-300">{content.length}/5000</span>
              <button type="submit" disabled={posting || !content.trim()}
                className="bg-brand-600 text-white text-sm px-4 py-2 rounded-xl hover:bg-brand-700 transition disabled:opacity-50">
                {posting ? "Posting..." : "Post confession"}
              </button>
            </div>
          </form>
        )}

        {posts.length === 0 ? (
          <div className="text-gray-400 text-sm text-center py-16">
            No posts yet. Be the first to share.
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  communityId={community.id}
                  communitySlug={slug!}
                  onVote={handleVote}
                />
              ))}
            </div>

            {hasMore && (
              <div className="text-center mt-6">
                <button onClick={loadMore} disabled={loadingMore}
                  className="border border-gray-300 text-gray-600 text-sm px-6 py-2 rounded-full hover:bg-gray-50 transition disabled:opacity-50">
                  {loadingMore ? "Loading..." : `Load more (${total - posts.length} remaining)`}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </ErrorBoundary>
  );
}
