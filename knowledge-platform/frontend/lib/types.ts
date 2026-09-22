export type Role = 'guest' | 'member' | 'admin';

export interface User {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  role: Role;
  created_at: string;
  updated_at: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type?: string;
  csrf_token: string;
  user: User;
}

export interface MembershipPlan {
  id: string;
  tenant_id: string;
  code: string;
  stripe_price_id: string | null;
  stripe_product_id: string | null;
  name: string;
  description: string | null;
  price_cents: number;
  currency: string;
  interval: string;
  api_calls_per_month: number;
  features: string[];
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: string;
  tenant_id: string;
  user_id: string;
  plan_id: string;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  stripe_price_id: string | null;
  status: string;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  canceled_at: string | null;
  trial_start: string | null;
  trial_end: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Entitlement {
  plan: string;
  status: string;
  api_calls_limit: number;
  features: string[];
  current_period_end: string | null;
}

export type ApiKeyScope =
  | 'read'
  | 'write'
  | 'admin'
  | 'search'
  | 'rag'
  | 'documents'
  | 'workflows';

export interface ApiKey {
  id: string;
  user_id: string;
  tenant_id: string;
  name: string;
  key_prefix: string;
  scopes: ApiKeyScope[];
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiKeyCreateResponse {
  api_key: ApiKey;
  plain_key: string;
}

export interface ApiUsageLog {
  id: string;
  api_key_id: string;
  user_id: string;
  tenant_id: string;
  endpoint: string;
  method: string;
  status_code: number | null;
  request_size: number | null;
  response_size: number | null;
  latency_ms: number | null;
  ip_address: string | null;
  user_agent: string | null;
  error_message: string | null;
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_tenants: number;
  total_subscriptions: number;
  active_subscriptions: number;
  total_api_keys: number;
  active_api_keys: number;
  total_api_calls_today: number;
  total_api_calls_month: number;
  revenue_cents: number;
  contact_messages: number;
  pending_contact_messages: number;
}

export interface AdminUserList {
  users: User[];
  total: number;
  page: number;
  page_size: number;
}

export interface ContactMessage {
  id: string;
  user_id: string | null;
  tenant_id: string | null;
  name: string;
  email: string;
  subject: string;
  message: string;
  status: string;
  admin_notes: string | null;
  resolved_at: string | null;
  resolved_by: string | null;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
  updated_at: string;
}
