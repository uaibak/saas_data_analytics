export type AuthTokenResponse = {
  access_token: string;
  token_type: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  full_name: string;
  email: string;
  password: string;
  organization_name: string;
};

export type User = {
  id: string;
  email: string;
  full_name: string;
  role: "Admin" | "Researcher" | "Viewer";
  organization_id: string;
  organization_name?: string | null;
  is_active: boolean;
  created_at: string;
};
