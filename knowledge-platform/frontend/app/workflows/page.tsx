'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Field, inputClassName } from '@/components/ui/FormField';
import { PageHeader } from '@/components/ui/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States';
import { api, getErrorMessage } from '@/lib/api/client';
import { formatDateTime } from '@/lib/format';
import type { KnowledgeBase, Workflow } from '@/lib/types';

interface WorkflowForm {
  name: string;
  description: string;
  kb_id: string;
}

export function WorkflowsContent() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [form, setForm] = useState<WorkflowForm>({ name: '', description: '', kb_id: '' });
  const [submitting, setSubmitting] = useState(false);
  const [executing, setExecuting] = useState<string>();
  const [executionResult, setExecutionResult] = useState<string>();

  const load = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const [kbResponse, workflowResponse] = await Promise.all([
        api.get<KnowledgeBase[]>('/api/v1/knowledge-bases/'),
        api.get<Workflow[]>('/api/v1/workflows/'),
      ]);
      setKnowledgeBases(kbResponse.data);
      setWorkflows(workflowResponse.data);
      if (!form.kb_id && kbResponse.data[0]) {
        setForm((current) => ({ ...current, kb_id: kbResponse.data[0].id }));
      }
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
      const response = await api.post<Workflow>('/api/v1/workflows/', {
        ...form,
        description: form.description || undefined,
        nodes: [],
        edges: [],
      });
      setWorkflows((current) => [response.data, ...current]);
      setForm((current) => ({ ...current, name: '', description: '' }));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  };

  const execute = async (id: string) => {
    setExecuting(id);
    setError(undefined);
    setExecutionResult(undefined);
    try {
      const response = await api.post<{ status: string; workflow_id: string }>(`/api/v1/workflows/${id}/execute`);
      setExecutionResult(`Workflow ${response.data.workflow_id} สิ้นสุดด้วยสถานะ ${response.data.status}`);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setExecuting(undefined);
    }
  };

  if (loading) return <LoadingState label="กำลังโหลด workflows" />;
  if (error && workflows.length === 0 && knowledgeBases.length === 0) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader eyebrow="Automation" title="Workflows" description="สร้างและรัน workflow ผ่าน backend พร้อมเชื่อมกับ knowledge base ที่เลือก" />
        {error && <div role="alert" className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{error}</div>}
        {executionResult && <div role="status" className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-900">{executionResult}</div>}

        <div className="mt-10 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <section className="rounded-2xl bg-white p-6 shadow-sm sm:p-7">
            <h2 className="text-xl font-bold text-gray-900">สร้าง workflow</h2>
            <form onSubmit={create} className="mt-6 space-y-5">
              <Field label="ชื่อ">
                <input required maxLength={255} value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} className={inputClassName()} placeholder="ชื่อ workflow" />
              </Field>
              <Field label="คำอธิบาย" hint="ไม่บังคับ">
                <textarea rows={4} value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} maxLength={2000} className={`${inputClassName()} resize-y`} placeholder="อธิบายลำดับการทำงาน" />
              </Field>
              <Field label="Knowledge base">
                <select required value={form.kb_id} onChange={(event) => setForm((current) => ({ ...current, kb_id: event.target.value }))} className={inputClassName()}>
                  <option value="">เลือกแหล่งความรู้</option>
                  {knowledgeBases.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                </select>
              </Field>
              <button type="submit" disabled={submitting || !form.kb_id} className="w-full rounded-lg bg-primary-700 px-5 py-3 text-sm font-bold text-white hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:cursor-wait disabled:opacity-60">
                {submitting ? 'กำลังสร้าง' : 'สร้าง workflow'}
              </button>
            </form>
          </section>

          <section className="rounded-2xl bg-white p-6 shadow-sm sm:p-7">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Workflow ที่มี</h2>
                <p className="mt-1 text-sm text-gray-600">{workflows.length ? `ทั้งหมด ${workflows.length} รายการ` : 'ยังไม่มี workflow'}</p>
              </div>
              <button type="button" onClick={() => void load()} className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-semibold hover:bg-gray-50">รีเฟรช</button>
            </div>
            {workflows.length === 0 ? (
              <div className="mt-8"><EmptyState title="เริ่มต้นด้วย workflow แรก" message="เลือก knowledge base แล้วสร้าง workflow ใหม่" /></div>
            ) : (
              <ul className="mt-6 space-y-4">
                {workflows.map((workflow) => (
                  <li key={workflow.id} className="rounded-xl border border-gray-200 p-5">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-bold text-gray-900">{workflow.name}</h3>
                          <span className={`rounded-full px-2 py-1 text-[10px] font-bold uppercase ${workflow.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-200 text-gray-600'}`}>{workflow.is_active ? 'active' : 'inactive'}</span>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-gray-600">{workflow.description || 'ไม่มีคำอธิบาย'}</p>
                        <p className="mt-3 text-xs text-gray-500">Knowledge base · {workflow.kb_id}</p>
                      </div>
                      <button type="button" disabled={executing === workflow.id} onClick={() => void execute(workflow.id)} className="shrink-0 rounded-lg bg-gray-950 px-4 py-2.5 text-xs font-bold text-white hover:bg-gray-800 disabled:cursor-wait disabled:opacity-50">
                        {executing === workflow.id ? 'กำลังรัน' : 'รัน workflow'}
                      </button>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 border-t border-gray-100 pt-3 text-xs text-gray-500">
                      <span>Version {workflow.version}</span>
                      <span>Nodes {workflow.nodes.length}</span>
                      <span>Edges {workflow.edges.length}</span>
                      <span>สร้าง {formatDateTime(workflow.created_at)}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default function WorkflowsPage() {
  return <ProtectedRoute><WorkflowsContent /></ProtectedRoute>;
}
