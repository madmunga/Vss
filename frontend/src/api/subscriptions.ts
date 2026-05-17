import client from "./client";
import type { Subscription, TierInfo } from "../types";

export const getTiers = () =>
  client.get<TierInfo[]>("/subscriptions/tiers").then((r) => r.data);

export const getMySubscription = () =>
  client.get<Subscription | null>("/users/me/subscription").then((r) => r.data);

export const createCheckout = (tier: string) =>
  client.post<{ checkout_url: string }>("/subscriptions/checkout", { tier }).then((r) => r.data);

export const cancelSubscription = () => client.delete("/subscriptions");
