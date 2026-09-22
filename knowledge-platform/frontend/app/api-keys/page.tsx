'use client';

import { useEffect, useRef, useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Field, inputClassName } from '@/components/ui/FormField';
import { PageHeader } from '@/components/ui/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States';
import { api, getErrorMessage } from '@/lib/api/client';
import { formatDateTime } from '@/lib/format';
import type { ApiKey, ApiKeyCreateResponse, ApiKeyScope } from '@/lib/types';

const scopes: ApiKeyScope[] = ['read', 'write', 'search', 'rag', 'documents', 'workflows', 'admin'];

export function ApiKeysContent() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [name, setName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<ApiKeyScope[]>(['read']);
  const [expiresAt, setExpiresAt] = useState('');
  const [creating, setCreating] = useState(false);
  const [revoking, setRevoking] = useState<string>();
  const [created, setCreated] = useState<ApiKeyCreateResponse | null>(null);
  const [actionError, setActionError] = useState<string>();
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  const load = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const response = await api.get<ApiKey[]>('/api/v1/api-keys/');
      setKeys(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    if (created) closeButtonRef.current?.focus();
  }, [created]);

  const toggleScope = (scope: ApiKeyScope) => {
    setSelectedScopes((current) => current.includes(scope) ? current.filter((item) => item !== scope) : [...current, scope]);
  };

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    setCreating(true);
    setActionError(undefined);
    try {
      const response = await api.post<ApiKeyCreateResponse>('/api/v1/api-keys/', {
        name,
        scopes: selectedScopes.length ? selectedScopes : ['read'],
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : undefined,
      });
      setCreated(response.data);
      setName('');
      setExpiresAt('');
      await load();
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setCreating(false);
    }
  };

  const revoke = async (key: ApiKey) => {
    if (!window.confirm(`ต้องการเพิกถอน API Key "${key.name}" หรือไม่`)) return;
    setRevoking(key.id);
    setActionError(undefined);
    try {
      await api.delete(`/api/v1/api-keys/${key.id}`);
      setKeys((current) => current.filter((item) => item.id !== key.id));
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setRevoking(undefined);
    }
  };

  const copyKey = async () => {
    if (!created) return;
    await navigator.clipboard.writeText(created.plain_key);
  };

  if (loading) return <LoadingState label="กำลังโหลด API Keys" />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader eyebrow="Developer Security" title="API Keys" description="สร้างและจัดการสิทธิ์เชิงโปรแกรมสำหรับเชื่อมต่อกับ Knowledge Platform" action={<span className="text-sm text-gray-600">แสดง {keys.length} รายการ</span>} />
        {actionError && <div role="alert" className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{actionError}</div>}

        <div className="mt-10 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <section className="rounded-2xl bg-white p-6 shadow-sm sm:p-7">
            <h2 className="text-xl font-bold text-gray-900">สร้าง API Key ใหม่</h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">คัดลอกคีย์ที่แสดงทันทีหลังสร้าง เพราะระบบจะไม่แสดงค่าเต็มอีกครั้ง</p>
            <form onSubmit={create} className="mt-6 space-y-5">
              <Field label="ชื่อ">
                <input required maxLength={100} value={name} onChange={(event) => setName(event.target.value)} className={inputClassName()} placeholder="เช่น Production Search" />
              </Field>
              <Field label="สิทธิ์" hint="เลือกได้มากกว่า 1 รายการ">
                <div className="grid grid-cols-2 gap-2 rounded-xl border border-gray-200 p-3">
                  {scopes.map((scope) => (
                    <label key={scope} className="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      <input type="checkbox" checked={selectedScopes.includes(scope)} onChange={() => toggleScope(scope)} className="h-4 w-4 rounded border-gray-300 text-primary-700 focus:ring-primary-500" />
                      {scope}
                    </label>
                  ))}
                </div>
              </Field>
              <Field label="วันหมดอายุ" hint="ไม่บังคับ">
                <input type="datetime-local" value={expiresAt} min={new Date().toISOString()} onChange={(event) => setExpiresAt(event.target.value)} className={inputClassName()} />
              </Field>
              <button disabled={creating} className="w-full rounded-lg bg-primary-700 px-5 py-3 text-sm font-bold text-white hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:cursor-wait disabled:opacity-60">
                {creating ? 'กำลังสร้าง' : 'สร้าง API Key'}
              </button>
            </form>
          </section>

          <section className="rounded-2xl bg-white p-6 shadow-sm sm:p-7">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">คีย์ของคุณ</h2>
                <p className="mt-1 text-sm text-gray-600">สิทธิ์และสถานะของ API Key ทุกรายการ</p>
              </div>
              <button type="button" onClick={load} className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-semibold hover:bg-gray-50">รีเฟรช</button>
            </div>
            {keys.length === 0 ? (
              <div className="mt-8"><EmptyState title="ยังไม่มี API Key" message="สร้างคีย์แรกด้านซ้ายเพื่อเริ่มเชื่อมต่อ API" /></div>
            ) : (
              <ul className="mt-6 space-y-3">
                {keys.map((key) => (
                  <li key={key.id} className={`rounded-xl border p-4 ${key.is_active ? 'border-gray-200 bg-white' : 'border-gray-100 bg-gray-50'}`}>
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="truncate font-bold text-gray-900">{key.name}</h3>
                          <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase ${key.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-200 text-gray-600'}`}>{key.is_active ? 'active' : 'revoked'}</span>
                        </div>
                        <p className="mt-2 font-mono text-xs text-gray-500">{key.key_prefix}••••••••</p>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {key.scopes.map((scope) => <span key={scope} className="rounded-md bg-primary-50 px-2 py-1 text-[10px] font-bold text-primary-800">{scope}</span>)}
                        </div>
                      </div>
                      <button type="button" disabled={!key.is_active || revoking === key.id} onClick={() => void revoke(key)} className="shrink-0 rounded-lg border border-red-200 px-3 py-2 text-xs font-bold text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-40">
                        {revoking === key.id ? 'กำลังเพิกถอน' : 'เพิกถอน'}
                      </button>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 border-t border-gray-100 pt-3 text-xs text-gray-500">
                      <span>สร้าง {formatDateTime(key.created_at)}</span>
                      <span>หมดอายุ {formatDateTime(key.expires_at)}</span>
                      <span>ใช้ล่าสุด {formatDateTime(key.last_used_at)}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>

      {created && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/70 p-4" role="presentation" onClick={() => setCreated(null)}>
          <div role="dialog" aria-modal="true" aria-labelledby="created-key-title" className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl" onClick={(event) => event.stopPropagation()}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-emerald-700">Created successfully</p>
                <h2 id="created-key-title" className="mt-2 text-xl font-bold text-gray-900">คัดลอก API Key ของคุณ</h2>
              </div>
              <button ref={closeButtonRef} type="button" aria-label="ปิด" onClick={() => setCreated(null)} className="rounded-lg p-2 text-gray-500 hover:bg-gray-100">✕</button>
            </div>
            <p className="mt-3 text-sm leading-6 text-gray-600">เก็บคีย์นี้ในที่จัดการความลับของคุณ ระบบจะแสดงครั้งเดียวเท่านั้น</p>
            <div className="mt-5 flex items-stretch gap-2">
              <code className="flex-1 break-all rounded-lg bg-gray-950 px-4 py-3 font-mono text-xs text-gray-100">{created.plain_key}</code>
              <button type="button" onClick={() => void copyKey()} className="rounded-lg bg-primary-700 px-4 text-sm font-bold text-white hover:bg-primary-800">คัดลอก</button>
            </div>
            <button type="button" onClick={() => setCreated(null)} className="mt-6 w-full rounded-lg bg-gray-950 px-4 py-3 text-sm font-bold text-white hover:bg-gray-800">ฉันคัดลอกแล้ว</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ApiKeysPage() {
  return <ProtectedRoute><ApiKeysContent /></ProtectedRoute>;
}
