'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { PageHeader } from '@/components/ui/PageHeader';
import { ErrorState, LoadingState } from '@/components/ui/States';
import { api, getErrorMessage } from '@/lib/api/client';
import { formatDate, formatMoney } from '@/lib/format';
import type { MembershipPlan, Subscription } from '@/lib/types';

export function BillingContent() {
  const searchParams = useSearchParams();
  const [plans, setPlans] = useState<MembershipPlan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [busyPlan, setBusyPlan] = useState<string>();
  const [portalLoading, setPortalLoading] = useState(false);
  const [actionError, setActionError] = useState<string>();
  const checkoutMessage = searchParams.get('checkout');

  const load = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const [plansResponse, subscriptionResponse] = await Promise.all([
        api.get<MembershipPlan[]>('/api/v1/billing/plans'),
        api.get<Subscription | null>('/api/v1/billing/subscription'),
      ]);
      setPlans(plansResponse.data);
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

  const checkout = async (plan: MembershipPlan) => {
    setBusyPlan(plan.id);
    setActionError(undefined);
    try {
      const response = await api.post<{ checkout_url?: string; message?: string }>('/api/v1/billing/checkout', {
        plan_id: plan.id,
        success_url: `${window.location.origin}/billing?checkout=success`,
        cancel_url: `${window.location.origin}/billing?checkout=cancelled`,
      });
      if (response.data.checkout_url) {
        window.location.assign(response.data.checkout_url);
      } else {
        setActionError(response.data.message || 'ไม่สามารถเริ่มการชำระเงินได้');
      }
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setBusyPlan(undefined);
    }
  };

  const openPortal = async () => {
    setPortalLoading(true);
    setActionError(undefined);
    try {
      const response = await api.post<{ portal_url: string }>('/api/v1/billing/portal', {
        return_url: `${window.location.origin}/billing`,
      });
      window.location.assign(response.data.portal_url);
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
      setPortalLoading(false);
    }
  };

  if (loading) return <LoadingState label="กำลังโหลดข้อมูลการเรียกเก็บเงิน" />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  const currentPlan = plans.find((plan) => plan.id === subscription?.plan_id);
  const activeStatuses = new Set(['active', 'trialing']);

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader eyebrow="Billing" title="การเรียกเก็บเงินและสมาชิก" description="ตรวจสอบสมาชิกปัจจุบัน เปลี่ยนแผน และจัดการการชำระเงินผ่านบริการจริง" action={<Link href="/products" className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold hover:bg-gray-50">เทียบแผนทั้งหมด</Link>} />

        {checkoutMessage === 'success' && <div role="status" className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-900">การชำระเงินเสร็จสิ้น กรุณารอสักครู่ให้ระบบอัปเดตสถานะ</div>}
        {checkoutMessage === 'cancelled' && <div role="status" className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm font-medium text-amber-900">คุณยกเลิกการชำระเงิน สามารถเลือกแผนใหม่ได้ตลอดเวลา</div>}
        {actionError && <div role="alert" className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{actionError}</div>}

        <section className="mt-10 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-gray-500">Current subscription</p>
              <h2 className="mt-2 text-2xl font-bold text-gray-900">{currentPlan?.name || 'ยังไม่มีสมาชิกแบบชำระเงิน'}</h2>
              <p className="mt-1 text-sm text-gray-600">{subscription ? `สถานะ ${subscription.status}` : 'ลงทะเบียนด้วยแผน Free'}</p>
            </div>
            {subscription?.stripe_subscription_id && (
              <button type="button" disabled={portalLoading} onClick={() => void openPortal()} className="rounded-lg border border-gray-300 px-4 py-3 text-sm font-bold hover:bg-gray-50 disabled:cursor-wait disabled:opacity-60">
                {portalLoading ? 'กำลังเปิด' : 'จัดการการชำระเงิน'}
              </button>
            )}
          </div>
          {subscription && (
            <dl className="mt-7 grid gap-5 border-t border-gray-100 pt-6 sm:grid-cols-3">
              <div><dt className="text-xs text-gray-500">สถานะ</dt><dd className="mt-1 text-sm font-bold">{subscription.status}</dd></div>
              <div><dt className="text-xs text-gray-500">เริ่มรอบบริการ</dt><dd className="mt-1 text-sm font-bold">{formatDate(subscription.current_period_start)}</dd></div>
              <div><dt className="text-xs text-gray-500">ครบกำหนด</dt><dd className="mt-1 text-sm font-bold">{formatDate(subscription.current_period_end)}</dd></div>
            </dl>
          )}
        </section>

        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          {plans.map((plan) => {
            const selected = plan.id === subscription?.plan_id && activeStatuses.has(subscription.status);
            return (
              <article key={plan.id} className={`flex h-full flex-col rounded-2xl bg-white p-7 ${selected ? 'ring-2 ring-primary-700 shadow-xl' : 'border border-gray-200 shadow-sm'}`}>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gray-900">{plan.name}</h2>
                  {selected && <span className="rounded-full bg-primary-50 px-2.5 py-1 text-[10px] font-bold text-primary-800">ปัจจุบัน</span>}
                </div>
                <p className="mt-4 text-3xl font-bold tracking-tight text-gray-900">{formatMoney(plan.price_cents, plan.currency)}<span className="ml-1 text-sm font-normal text-gray-500">/{plan.interval}</span></p>
                <p className="mt-3 min-h-12 text-sm leading-6 text-gray-600">{plan.description || 'เลือกแผนนี้เพื่อเริ่มใช้งาน'}</p>
                <ul className="mt-5 flex-1 space-y-2 text-sm text-gray-700">
                  {(plan.features.length ? plan.features : ['API access', 'Knowledge search', 'Member dashboard']).map((feature) => (
                    <li key={feature} className="flex gap-2"><span className="text-primary-700">✓</span>{feature}</li>
                  ))}
                </ul>
                <button type="button" disabled={selected || busyPlan === plan.id} onClick={() => void checkout(plan)} className="mt-7 w-full rounded-lg bg-gray-950 px-4 py-3 text-sm font-bold text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50">
                  {selected ? 'แผนปัจจุบัน' : busyPlan === plan.id ? 'กำลังประมวลผล' : plan.price_cents === 0 ? 'ใช้แผนฟรี' : 'อัปเกรดแผนนี้'}
                </button>
              </article>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function BillingPage() {
  return <ProtectedRoute><BillingContent /></ProtectedRoute>;
}
