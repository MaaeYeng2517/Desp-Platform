'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Field, inputClassName } from '@/components/ui/FormField';
import { PageHeader } from '@/components/ui/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States';
import { api, getErrorMessage } from '@/lib/api/client';
import { formatDateTime } from '@/lib/format';
import type { KnowledgeBase } from '@/lib/types';

export function KnowledgeBasesContent() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [formOpen, setFormOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [busyId, setBusyId] = useState<string>();

  const load = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const response = await api.get<KnowledgeBase[]>('/api/v1/knowledge-bases/');
      setKnowledgeBases(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(undefined);
    try {
      const response = await api.post<KnowledgeBase>('/api/v1/knowledge-bases/', {
        name,
        description: description || undefined,
        settings: {},
      });
      setKnowledgeBases((current) => [response.data, ...current]);
      setName('');
      setDescription('');
      setFormOpen(false);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  };

  const publish = async (id: string) => {
    setBusyId(id);
    setError(undefined);
    try {
      await api.post(`/api/v1/knowledge-bases/${id}/publish`);
      setKnowledgeBases((current) => current.map((item) => item.id === id ? { ...item, is_published: true, status: 'published' } : item));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusyId(undefined);
    }
  };

  const remove = async (id: string) => {
    if (!window.confirm('ต้องการลบ knowledge base นี้หรือไม่')) return;
    setBusyId(id);
    setError(undefined);
    try {
      await api.delete(`/api/v1/knowledge-bases/${id}`);
      setKnowledgeBases((current) => current.filter((item) => item.id !== id));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusyId(undefined);
    }
  };

  if (loading) return <LoadingState label="กำลังโหลด knowledge bases" />;
  if (error && knowledgeBases.length === 0) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader eyebrow="Knowledge Operations" title="Knowledge Bases" description="จัดการแหล่งความรู้ที่เชื่อมต่อกับระบบจริง พร้อมสถานะ การเผยแพร่ และวงจรชีพ" action={<button type="button" onClick={() => setFormOpen((current) => !current)} className="rounded-lg bg-primary-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800">{formOpen ? 'ปิดแบบฟอร์ม' : 'สร้าง knowledge base'}</button>} />
        {error && <div role="alert" className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{error}</div>}

        {formOpen && (
          <section className="mt-8 rounded-2xl bg-white p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">สร้างแหล่งความรู้ใหม่</h2>
            <form onSubmit={create} className="mt-5 grid gap-5 sm:grid-cols-2">
              <Field label="ชื่อ">
                <input required maxLength={255} value={name} onChange={(event) => setName(event.target.value)} className={inputClassName()} placeholder="ชื่อ knowledge base" />
              </Field>
              <Field label="คำอธิบาย" hint="ไม่บังคับ">
                <input value={description} onChange={(event) => setDescription(event.target.value)} maxLength={1000} className={inputClassName()} placeholder="อธิบายเนื้อหาและผู้ใช้งาน" />
              </Field>
              <div className="sm:col-span-2 flex justify-end gap-3">
                <button type="button" onClick={() => setFormOpen(false)} className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold hover:bg-gray-50">ยกเลิก</button>
                <button type="submit" disabled={submitting} className="rounded-lg bg-primary-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800 disabled:cursor-wait disabled:opacity-60">{submitting ? 'กำลังสร้าง' : 'สร้าง'}</button>
              </div>
            </form>
          </section>
        )}

        {knowledgeBases.length === 0 ? (
          <div className="mt-8"><EmptyState title="ยังไม่มี knowledge base" message="สร้างแหล่งความรู้แรกเพื่อเริ่มเชื่อมต่อเอกสารและเครื่องมือค้นหา" /></div>
        ) : (
          <div className="mt-8 grid gap-5 md:grid-cols-2">
            {knowledgeBases.map((item) => (
              <article key={item.id} className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="truncate text-lg font-bold text-gray-900">{item.name}</h2>
                      <span className={`rounded-full px-2 py-1 text-[10px] font-bold uppercase ${item.is_published ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>{item.status}</span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-gray-600">{item.description || 'ไม่มีคำอธิบาย'}</p>
                    <p className="mt-3 font-mono text-xs text-gray-500">{item.slug}</p>
                  </div>
                  <div className="flex shrink-0 gap-2">
                    {!item.is_published && <button type="button" disabled={busyId === item.id} onClick={() => void publish(item.id)} className="rounded-lg border border-primary-200 px-3 py-2 text-xs font-bold text-primary-700 hover:bg-primary-50 disabled:cursor-wait disabled:opacity-50">{busyId === item.id ? 'กำลังเผยแพร่' : 'เผยแพร่'}</button>}
                    <button type="button" disabled={busyId === item.id} onClick={() => void remove(item.id)} className="rounded-lg border border-red-200 px-3 py-2 text-xs font-bold text-red-700 hover:bg-red-50 disabled:cursor-wait disabled:opacity-50">{busyId === item.id ? 'กำลังลบ' : 'ลบ'}</button>
                  </div>
                </div>
                <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 border-t border-gray-100 pt-4 text-xs text-gray-500">
                  <span>Version {item.version}</span>
                  <span>สร้าง {formatDateTime(item.created_at)}</span>
                  <span>อัปเดต {formatDateTime(item.updated_at)}</span>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function KnowledgeBasesPage() {
  return <ProtectedRoute><KnowledgeBasesContent /></ProtectedRoute>;
}
