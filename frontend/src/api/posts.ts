import client from "./client";
import type { Post, PostFeed } from "../types";

export const getFeed = (communitySlug: string, page = 1) =>
  client
    .get<PostFeed>("/posts", { params: { community: communitySlug, page, page_size: 20 } })
    .then((r) => r.data);

export const createPost = (community_id: string, content: string, parent_id?: string) =>
  client.post<Post>("/posts", { community_id, content, parent_id }).then((r) => r.data);

export const votePost = (postId: string) => client.post(`/posts/${postId}/vote`);

export const deletePost = (postId: string) => client.delete(`/posts/${postId}`);

export const getReplies = (communitySlug: string, parentId: string) =>
  client
    .get<PostFeed>("/posts", { params: { community: communitySlug, parent_id: parentId } })
    .then((r) => r.data);
