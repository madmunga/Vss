import client from "./client";
import type { Professional } from "../types";

export const listProfessionals = (tier?: string) =>
  client.get<Professional[]>("/professionals", { params: tier ? { tier } : {} }).then((r) => r.data);

export const getMyProfessionalProfile = () =>
  client.get<Professional>("/professionals/me").then((r) => r.data);

export const getMyGroups = () =>
  client.get("/professionals/me/groups").then((r) => r.data);

export const enroll = (data: {
  license_number: string;
  specialty: string;
  tier: string;
  vetting_facility: string;
  bio?: string;
  years_experience?: number;
  languages: string[];
}) => client.post<Professional>("/professionals/enroll", data).then((r) => r.data);
