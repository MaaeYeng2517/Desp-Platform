'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Field, inputClassName } from '@/components/ui/FormField';
import { PageHeader } from '@/components/ui/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States';
import { api, getErrorMessage } from '@/lib/api/client';
import type { KnowledgeBase, SearchResponse, SearchResult } from '@/lib/types';

interface SearchFilters {
  subject: string;
  language: string;
  status: string;
}

export function SearchContent() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKnowledgeBases, setSelectedKnowledgeBases] = useState<string[]>([]);
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({ subject: '', language: '', status: 'published' });
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string>();

  const loadKnowledgeBases = async () => {
    try {
      const response = await api.get<KnowledgeBase[]>('/api/v1/knowledge-bases/');
      setKnowledgeBases(response.data);
      setSelectedKnowledgeBases(response.data.map((item) => item.id));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadKnowledgeBases();
  }, []);

  const toggleKnowledgeBase = (id: string) => {
    setSelectedKnowledgeBases((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  };

  const search = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim() || selectedKnowledgeBases.length === 0) return;
    setSearching(true);
    setError(undefined);
    setResults([]);
    try {
      const metadataFilters: Record<string, string> = {};
      if (filters.subject) metadataFilters.subject = filters.subject;
      if (filters.language) metadataFilters.language = filters.language;
      if (filters.status) metadataFilters.status = filters.status;
      const response = await api.post<SearchResponse>('/api/v1/search/', {
        query: query.trim(),
        kb_ids: selectedKnowledgeBases,
        metadata_filters: Object.keys(metadataFilters).length ? metadataFilters : undefined,
        limit: 20,
        search_type: 'hybrid',
      });
      setResults(response.data.results);
      setTotal(response.data.total);
      setLatency(response.data.latency_ms);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setSearching(false);
    }
  };

  if (loading) return <LoadingState label="กำลังโหลดแหล่งความรู้" />;
  if (error && knowledgeBases.length === 0) return <ErrorState message={error} onRetry={loadKnowledgeBases} />;

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader eyebrow="Search Studio" title="ค้นหาข้อมูลจากแหล่งความรู้" description="สืบค้นแบบไฮบริดจาก knowledge bases ที่เชื่อมต่อกับ backend พร้อมตัวกรองเมตาดาทา" />
        <div className="mt-10 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <section className="rounded-2xl bg-white p-6 shadow-sm sm:p-7">
            <h2 className="text-xl font-bold text-gray-900">ตัวเลือกการค้นหา</h2>
            <form onSubmit={search} className="mt-6 space-y-5">
              {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{error}</div>}
              <Field label="คำค้นหา">
                <textarea required rows={4} value={query} onChange={(event) => setQuery(event.target.value)} className={`${inputClassName()} resize-y`} placeholder="คุณต้องการหาข้อมูลอะไร" />
              </Field>
              <Field label="แหล่งความรู้" hint={`${selectedKnowledgeBases.length} แหล่งที่เลือก`}>
                <div className="grid gap-2 rounded-xl border border-gray-200 p-3">
                  {knowledgeBases.length === 0 ? <p className="text-sm text-gray-500">ยังไม่มี knowledge base</p> : knowledgeBases.map((item) => (
                    <label key={item.id} className="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      <input type="checkbox" checked={selectedKnowledgeBases.includes(item.id)} onChange={() => toggleKnowledgeBase(item.id)} className="h-4 w-4 rounded border-gray-300 text-primary-700 focus:ring-primary-500" />
                      <span className="min-w-0 truncate">{item.name}</span>
                    </label>
                  ))}
                </div>
              </Field>
              <div className="grid gap-4 sm:grid-cols-3">
                <Field label="หัวข้อ">
                  <input value={filters.subject} onChange={(event) => setFilters((current) => ({ ...current, subject: event.target.value }))} className={inputClassName()} placeholder="ตัวกรอง" />
                </Field>
                <Field label="ภาษา">
                  <input value={filters.language} onChange={(event) => setFilters((current) => ({ ...current, language: event.target.value }))} className={inputClassName()} placeholder="th, en" />
                </Field>
                <Field label="สถานะ">
                  <select value={filters.status} onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))} className={inputClassName()}>
                    <option value="published">Published</option>
                    <option value="draft">Draft</option>
                    <option value="">ทั้งหมด</option>
                  </select>
                </Field>
              </div>
              <button type="submit" disabled={searching || selectedKnowledgeBases.length === 0} className="w-full rounded-lg bg-primary-700 px-5 py-3 text-sm font-bold text-white hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:cursor-wait disabled:opacity-60">
                {searching ? 'กำลังค้นหา' : 'ค้นหา'}
              </button>
            </form>
          </section>

          <section className="rounded-2xl bg-white p-6 shadow-sm sm:p-7">
            <div className="flex items-end justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">ผลการค้นหา</h2>
                <p className="mt-1 text-sm text-gray-600">{searching ? 'กำลังค้นหาข้อมูล' : total ? `พบ ${total} ผลลัพธ์` : 'ยังไม่มีผลการค้นหา'}</p>
              </div>
              {latency !== null && <p className="text-xs text-gray-500">{latency.toFixed(1)} ms</p>}
            </div>
            {results.length === 0 ? (
              <div className="mt-8"><EmptyState title="เริ่มต้นด้วยคำค้นหา" message="เลือกแหล่งความรู้และป้อนคำค้นหาเพื่อดูผลลัพธ์จาก API" /></div>
            ) : (
              <ol className="mt-6 space-y-4">
                {results.map((result) => (
                  <li key={result.chunk_id} className="rounded-xl border border-gray-200 p-5">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <h3 className="font-bold text-gray-900">{result.title}</h3>
                        <p className="mt-2 text-sm leading-6 text-gray-600">{result.content}</p>
                      </div>
                      <span className="shrink-0 rounded-full bg-primary-50 px-3 py-1 text-xs font-bold text-primary-800">{Math.round(result.score * 100)}%</span>
                    </div>
                    {result.sources.length > 0 && <p className="mt-3 text-xs text-gray-500">ที่มา: {result.sources.join(', ')}</p>}
                  </li>
                ))}
              </ol>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return <ProtectedRoute><SearchContent /></ProtectedRoute>;
}
