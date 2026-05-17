import client from "./client";
import type { TokenResponse, UserMe } from "../types";

export const register = (data: {
  email: string;
  password: string;
  real_name?: string;
  addiction_types: string[];
}) => client.post<TokenResponse>("/auth/register", data).then((r) => r.data);

export const login = (email: string, password: string) =>
  client.post<TokenResponse>("/auth/login", { email, password }).then((r) => r.data);

export const getMe = () => client.get<UserMe>("/users/me").then((r) => r.data);
