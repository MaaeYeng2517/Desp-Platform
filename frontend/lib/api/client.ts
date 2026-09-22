import axios, {
  AxiosError,
  AxiosHeaders,
  InternalAxiosRequestConfig,
} from 'axios';

const API_ROOT = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const CSRF_SESSION_KEY = 'knowledge_platform_csrf_token';
const AUTH_CHANGE_EVENT = 'knowledge-platform-auth-change';
const CSRF_EXEMPT_PATHS = [
  '/api/v1/auth/login',
  '/api/v1/auth/register',
  '/api/v1/auth/logout',
  '/api/v1/auth/refresh',
  '/api/v1/auth/verify-csrf',
];
const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

type RetryableRequest = InternalAxiosRequestConfig & {
  _csrfRetry?: boolean;
  _retry?: boolean;
};

let csrfRequest: Promise<string> | null = null;

function readStoredCsrfToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.sessionStorage.getItem(CSRF_SESSION_KEY);
}

export function setCsrfToken(token: string): void {
  if (typeof window === 'undefined') return;
  window.sessionStorage.setItem(CSRF_SESSION_KEY, token);
}

export function clearAuthClientState(notify = true): void {
  if (typeof window === 'undefined') return;
  window.sessionStorage.removeItem(CSRF_SESSION_KEY);
  if (notify) {
    window.dispatchEvent(new CustomEvent(AUTH_CHANGE_EVENT));
  }
}

function getCsrfToken(): Promise<string> {
  const stored = readStoredCsrfToken();
  if (stored) return Promise.resolve(stored);
  if (!csrfRequest) {
    csrfRequest = api
      .get<{ csrf_token: string }>('/api/v1/auth/csrf-token')
      .then((response) => {
        setCsrfToken(response.data.csrf_token);
        return response.data.csrf_token;
      })
      .finally(() => {
        csrfRequest = null;
      });
  }
  return csrfRequest;
}

export const api = axios.create({
  baseURL: API_ROOT,
  withCredentials: true,
  timeout: 20000,
  headers: {
    Accept: 'application/json',
  },
});

api.interceptors.request.use(async (request: InternalAxiosRequestConfig) => {
  const config = request as RetryableRequest;
  const method = (config.method || 'GET').toUpperCase();
  const path = config.url || '';
  if (UNSAFE_METHODS.has(method) && !CSRF_EXEMPT_PATHS.some((prefix) => path.startsWith(prefix))) {
    const token = await getCsrfToken();
    config.headers = AxiosHeaders.from(config.headers);
    config.headers.set('X-CSRF-Token', token);
  }
  return config;
});

api.interceptors.response.use(
  (response) => {
    if (response.data?.csrf_token) {
      setCsrfToken(response.data.csrf_token);
    }
    return response;
  },
  async (error: AxiosError<unknown>) => {
    if (error.response?.status !== 401) return Promise.reject(error);

    const request = error.config as RetryableRequest | undefined;
    if (
      !request ||
      request._retry ||
      !request.url ||
      request.url.includes('/api/v1/auth/refresh') ||
      request.url.includes('/api/v1/auth/login') ||
      request.url.includes('/api/v1/auth/register') ||
      request.url.includes('/api/v1/auth/logout') ||
      request.url.includes('/api/v1/auth/verify-csrf')
    ) {
      clearAuthClientState(false);
      return Promise.reject(error);
    }

    request._retry = true;
    try {
      const refreshResponse = await api.post('/api/v1/auth/refresh');
      if (refreshResponse.data?.csrf_token) {
        setCsrfToken(refreshResponse.data.csrf_token);
      }
      return api(request);
    } catch (refreshError) {
      clearAuthClientState(false);
      return Promise.reject(refreshError);
    }
  },
);

export function getErrorMessage(error: unknown, fallback = 'เกิดข้อผิดพลาด เชื่อมต่อไม่ได้'): string {
  if (!axios.isAxiosError(error)) return fallback;

  const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (!item || typeof item !== 'object') return '';
        const entry = item as Record<string, unknown>;
        const field = Array.isArray(entry.loc) ? entry.loc.filter(Boolean).join('.') : 'คำขอ';
        const message = typeof entry.msg === 'string' ? entry.msg : 'ข้อมูลไม่ถูกต้อง';
        return `${field}: ${message}`;
      })
      .join('\n');
  }
  if (detail && typeof detail === 'object') {
    return Object.values(detail as Record<string, unknown>)
      .filter((value): value is string => typeof value === 'string')
      .join('\n');
  }
  return fallback;
}

export function onAuthChange(listener: () => void): () => void {
  if (typeof window === 'undefined') return () => undefined;
  window.addEventListener(AUTH_CHANGE_EVENT, listener);
  return () => window.removeEventListener(AUTH_CHANGE_EVENT, listener);
}
