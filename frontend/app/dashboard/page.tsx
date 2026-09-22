'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { PageHeader } from '@/components/ui/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States';
import { api, getErrorMessage } from '@/lib/api/client';
import { formatDate, formatNumber } from '@/lib/format';
import type { Entitlement, Subscription } from '@/lib/types';

export function DashboardContent() {
  const [entitlement, setEntitlement] = useState<Entitlement | null>(null);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const load = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const [entitlementResponse, subscriptionResponse] = await Promise.all([
        api.get<Entitlement>('/api/v1/billing/entitlement'),
        api.get<Subscription | null>('/api/v1/billing/subscription'),
      ]);
      setEntitlement(entitlementResponse.data);
      setSubscription(subscriptionResponse.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  if (loading) return <LoadingState label="กำลังโหลดแดชบอร์ด" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!entitlement) return <EmptyState title="ยังไม่มีข้อมูลสมาชิก" message="ไม่พบสิทธิ์การใช้งานของบัญชีนี้ โปรดติดต่อทีมสนับสนุน" />;

  const activeStatuses = new Set(['active', 'trialing']);
  const statusLabel: Record<string, string> = {
    active: 'ใช้งานได้',
    trialing: 'ทดลองใช้งาน',
    past_due: 'ชำระเงินล่าช้า',
    unpaid: 'ยังไม่ชำระ',
    canceled: 'ยกเลิกแล้ว',
    incomplete: 'อยู่ระหว่างสร้าง',
    incomplete_expired: 'หมดอายุ',
    paused: 'พักการใช้งาน',
  };

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader
          eyebrow="Member Workspace"
          title={`สวัสดีคุณ ${entitlement.plan}`}
          description="ภาพรวมสมาชิก สิทธิ์การใช้งาน และเครื่องมือสำหรับพัฒนาแพลตฟอร์มความรู้"
          action={<Link href="/api-keys" className="inline-flex rounded-lg bg-primary-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800">สร้าง API Key</Link>}
        />

        <section aria-label="สถานะสมาชิก" className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: 'แผนปัจจุบัน', value: entitlement.plan, className: 'text-primary-700' },
            { label: 'สถานะ', value: statusLabel[entitlement.status] || entitlement.status, className: activeStatuses.has(entitlement.status) ? 'text-emerald-700' : 'text-amber-700' },
            { label: 'โควตา API', value: formatNumber(entitlement.api_calls_limit), suffix: 'calls / month', className: 'text-gray-700' },
            { label: 'ครบกำหนด', value: formatDate(entitlement.current_period_end), className: 'text-gray-700' },
          ].map((item) => (
            <article key={item.label} className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-medium text-gray-500">{item.label}</p>
              <p className={`mt-3 text-2xl font-bold ${item.className}`}>{item.value}</p>
              {item.suffix && <p className="mt-1 text-xs text-gray-500">{item.suffix}</p>}
            </article>
          ))}
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-3">
          <article className="rounded-2xl border border-gray-200 bg-white p-7 shadow-sm lg:col-span-2">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-gray-500">Current entitlement</p>
                <h2 className="mt-2 text-xl font-bold text-gray-900">สิทธิ์ที่พร้อมใช้งาน</h2>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-bold ${activeStatuses.has(entitlement.status) ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                {entitlement.status}
              </span>
            </div>
            <ul className="mt-6 grid gap-3 sm:grid-cols-2">
              {(entitlement.features.length ? entitlement.features : ['ไม่มีคุณสมบัติเพิ่มเติม']).map((feature) => (
                <li key={feature} className="flex items-center gap-3 rounded-xl bg-gray-50 p-4 text-sm text-gray-700">
                  <span className="text-primary-700">✓</span>{feature}
                </li>
              ))}
            </ul>
          </article>

          <article className="rounded-2xl bg-gray-950 p-7 text-white shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wider text-gray-400">Quick actions</p>
            <h2 className="mt-2 text-xl font-bold">จัดการทีมและ API</h2>
            <div className="mt-6 space-y-3">
              <Link href="/api-keys" className="flex items-center justify-between rounded-xl bg-white/10 p-4 text-sm font-semibold hover:bg-white/15">API Keys <span>→</span></Link>
              <Link href="/billing" className="flex items-center justify-between rounded-xl bg-white/10 p-4 text-sm font-semibold hover:bg-white/15">การเรียกเก็บเงิน <span>→</span></Link>
              <Link href="/contact" className="flex items-center justify-between rounded-xl bg-white/10 p-4 text-sm font-semibold hover:bg-white/15">ติดต่อสนับสนุน <span>→</span></Link>
            </div>
          </article>
        </section>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return <ProtectedRoute><DashboardContent /></ProtectedRoute>;
}
