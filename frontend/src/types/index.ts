export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserMe {
  id: string;
  email: string;
  real_name: string | null;
  phone: string | null;
  display_name: string;
  addiction_types: string[];
  role: "USER" | "PROFESSIONAL" | "ADMIN";
  is_verified: boolean;
  created_at: string;
}

export interface Community {
  id: string;
  name: string;
  slug: string;
  addiction_type: string;
  description: string | null;
  required_tier: string | null;
  member_count: number;
  created_at: string;
}

export interface Post {
  id: string;
  community_id: string;
  display_name: string;
  content: string;
  parent_id: string | null;
  upvotes: number;
  is_deleted: boolean;
  created_at: string;
  reply_count: number;
}

export interface PostFeed {
  posts: Post[];
  total: number;
  page: number;
  page_size: number;
}

export interface Professional {
  id: string;
  display_name: string;
  specialty: string;
  tier: string;
  vetting_status: string;
  bio: string | null;
  years_experience: number | null;
  languages: string[];
  created_at: string;
}

export interface Subscription {
  id: string;
  tier: string;
  status: string;
  price_usd: number;
  current_period_start: string | null;
  current_period_end: string | null;
  created_at: string;
}

export interface TierInfo {
  tier: string;
  price_usd: number;
  description: string;
  features: string[];
}
