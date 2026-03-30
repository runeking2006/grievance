import { apiClient } from "@/api/client";
import type { AuthUser } from "@/store/authStore";

export type RegisterPayload = {
  email: string;
  full_name?: string;
};

export type RegisterResponse = AuthUser & {
  api_key?: string | null;
};

export type TokenPayload = {
  email: string;
  api_key: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  role: string;
};

export async function registerUser(payload: RegisterPayload): Promise<RegisterResponse> {
  const { data } = await apiClient.post<RegisterResponse>("/auth/register", payload);
  return data;
}

export async function createToken(payload: TokenPayload): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/token", payload);
  return data;
}

export async function fetchMe(token?: string): Promise<AuthUser> {
  const { data } = await apiClient.get<AuthUser>("/me", {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  return data;
}
