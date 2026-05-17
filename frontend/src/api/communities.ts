import client from "./client";
import type { Community } from "../types";

export const listCommunities = () =>
  client.get<{ communities: Community[]; total: number }>("/communities").then((r) => r.data);

export const getCommunity = (slug: string) =>
  client.get<Community>(`/communities/${slug}`).then((r) => r.data);

export const joinCommunity = (slug: string) => client.post(`/communities/${slug}/join`);

export const leaveCommunity = (slug: string) => client.delete(`/communities/${slug}/leave`);
