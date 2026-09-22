import {
  ComponentDefinition,
  DocumentInput,
  KnowledgeBaseRecord,
  RetrieveResponse,
  RunResponse,
  SearchResponse,
  StatusResponse,
} from './types';

export class ApiError extends Error {
  constructor(message: string, public status?: number, public payload?: unknown) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface KnowledgeBaseInput {
  name: string;
  description?: string;
  metadata?: Record<string, unknown>;
  workflow?: Partial<KnowledgeBaseRecord['workflow']>;
}

const defaultApiBase =
  process.env.EXPO_PUBLIC_API_BASE ||
  (typeof window !== 'undefined' && window.location.hostname
    ? `${window.location.protocol}//${window.location.hostname}:3000/api/knowledge-base`
    : 'http://localhost:3000/api/knowledge-base');

async function request<T>(apiBase: string, path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) {
    headers.set('Content-Type', 'application/json');
  }
  const response = await fetch(`${apiBase}${path}`, { ...options, headers });
  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : null;
  if (!response.ok) {
    const message =
      typeof payload === 'string'
        ? payload
        : typeof payload?.message === 'string'
          ? payload.message
          : `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, payload);
  }
  return payload as T;
}

export const knowledgeBaseApi = {
  catalog: (apiBase: string) => request<ComponentDefinition[]>(apiBase, '/catalog'),
  list: (apiBase: string) => request<KnowledgeBaseRecord[]>(apiBase, ''),
  get: (apiBase: string, id: string) => request<KnowledgeBaseRecord>(apiBase, `/${id}`),
  create: (apiBase: string, input: KnowledgeBaseInput) =>
    request<KnowledgeBaseRecord>(apiBase, '', { method: 'POST', body: JSON.stringify(input) }),
  update: (apiBase: string, id: string, input: Partial<KnowledgeBaseInput>) =>
    request<KnowledgeBaseRecord>(apiBase, `/${id}`, { method: 'PATCH', body: JSON.stringify(input) }),
  validate: (apiBase: string, id: string) =>
    request<{ id: string; validation: KnowledgeBaseRecord['validation']; status: KnowledgeBaseRecord['status'] }>(apiBase, `/${id}/validate`, { method: 'POST' }),
  run: (apiBase: string, id: string, documents: DocumentInput[]) =>
    request<RunResponse>(apiBase, `/${id}/run`, { method: 'POST', body: JSON.stringify({ documents }) }),
  search: (apiBase: string, id: string, query: string, topK = 4) =>
    request<SearchResponse>(apiBase, `/${id}/search`, { method: 'POST', body: JSON.stringify({ query, topK }) }),
  retrieve: (apiBase: string, id: string, query: string, topK = 4) =>
    request<RetrieveResponse>(apiBase, `/${id}/retrieve`, { method: 'POST', body: JSON.stringify({ query, topK }) }),
  status: (apiBase: string, id: string) => request<StatusResponse>(apiBase, `/${id}/status`),
  demo: (apiBase: string) => request<RunResponse>(apiBase, '/demo', { method: 'POST' }),
};

export const normalizeApiBase = (value: string) => value.trim().replace(/\/+$/, '');
export const getFallbackApiBase = () => defaultApiBase;
