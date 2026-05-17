import { create } from "zustand";
import type { Post } from "../types";
import { getFeed, votePost as apiVote } from "../api/posts";

interface FeedState {
  posts: Post[];
  total: number;
  page: number;
  isLoading: boolean;
  communitySlug: string | null;
  loadFeed: (slug: string, page?: number) => Promise<void>;
  vote: (postId: string) => Promise<void>;
  prependPost: (post: Post) => void;
}

export const useFeedStore = create<FeedState>((set, get) => ({
  posts: [],
  total: 0,
  page: 1,
  isLoading: false,
  communitySlug: null,
  loadFeed: async (slug, page = 1) => {
    set({ isLoading: true, communitySlug: slug });
    try {
      const data = await getFeed(slug, page);
      set({ posts: data.posts, total: data.total, page: data.page, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },
  vote: async (postId) => {
    await apiVote(postId);
    set((state) => ({
      posts: state.posts.map((p) =>
        p.id === postId ? { ...p, upvotes: p.upvotes + 1 } : p
      ),
    }));
  },
  prependPost: (post) => set((state) => ({ posts: [post, ...state.posts] })),
}));
