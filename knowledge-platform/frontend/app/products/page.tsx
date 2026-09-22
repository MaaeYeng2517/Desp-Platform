'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/ui/PageHeader';
import { ErrorState, LoadingState } from '@/components/ui/States';
import { useAuth } from '@/components/providers/AuthProvider';
import { api, getErrorMessage } from '@/lib/api/client';
import { formatMoney, formatNumber } from '@/lib/format';
import type { MembershipPlan } from '@/lib/types';

export default function ProductsPage() {
  const [plans, setPlans] = useState<MembershipPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [checkoutPlan, setCheckoutPlan] = useState<string>();
  const [checkoutError, setCheckoutError] = useState<string>();
  const { user } = useAuth();
  const router = useRouter();

  const loadPlans = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const response = await api.get<MembershipPlan[]>('/api/v1/billing/plans');
      setPlans(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadPlans();
  }, []);

  const choosePlan = (plan: MembershipPlan) => {
    if (!user) {
      router.push(`/auth/login?next=${encodeURIComponent('/billing')}`);
      return;
    }
    void startCheckout(plan);
  };

  const startCheckout = async (plan: MembershipPlan) => {
    setCheckoutPlan(plan.id);
    setCheckoutError(undefined);
    try {
      const response = await api.post<{ checkout_url?: string; message?: string }>('/api/v1/billing/checkout', {
        plan_id: plan.id,
        success_url: `${window.location.origin}/billing?checkout=success`,
        cancel_url: `${window.location.origin}/billing?checkout=cancelled`,
      });
      if (response.data.checkout_url) {
        window.location.assign(response.data.checkout_url);
      } else {
        setCheckoutError(response.data.message || 'ไม่สามารถสร้างการชำระเงินได้');
      }
    } catch (requestError) {
      setCheckoutError(getErrorMessage(requestError));
    } finally {
      setCheckoutPlan(undefined);
    }
  };

  if (loading) return <div className="mx-auto max-w-8xl px-4 py-12 sm:px-6 lg:px-8"><LoadingState label="กำลังโหลดแผนการใช้งาน" /></div>;
  if (error) return <div className="mx-auto max-w-8xl px-4 py-12 sm:px-6 lg:px-8"><ErrorState message={error} onRetry={loadPlans} /></div>;

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader
          eyebrow="Membership"
          title="เลือกแผนที่เติบโตไปกับทีม"
          description="เริ่มต้นฟรีและอัปเกรดเมื่องานของคุณพร้อม ข้อมูลแผนและราคาแสดงจากบริการการเรียกเก็บเงินจริง"
          action={<Link href="/billing" className="inline-flex rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50">จัดการสมาชิกของฉัน</Link>}
        />

        {checkoutError && (
          <div role="alert" className="mt-8 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {checkoutError}
          </div>
        )}

        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          {plans.map((plan, index) => {
            const featured = plan.code === 'pro' || index === 1;
            return (
              <article key={plan.id} className={`flex h-full flex-col rounded-2xl bg-white p-7 ${featured ? 'ring-2 ring-primary-700 shadow-xl' : 'border border-gray-200 shadow-sm'}`}>
                {featured && <p className="text-xs font-bold uppercase tracking-wider text-primary-700">แนะนำ</p>}
                <div className="mt-2 flex items-baseline justify-between gap-3">
                  <h2 className="text-xl font-bold text-gray-900">{plan.name}</h2>
                  <span className="rounded-full bg-gray-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-gray-600">{plan.code}</span>
                </div>
                <p className="mt-4 flex items-baseline gap-1">
                  <span className="text-4xl font-bold tracking-tight text-gray-900">{formatMoney(plan.price_cents, plan.currency)}</span>
                  <span className="text-sm text-gray-500">/{plan.interval === 'year' ? 'ปี' : 'เดือน'}</span>
                </p>
                <p className="mt-4 min-h-12 text-sm leading-6 text-gray-600">{plan.description || 'แผนการใช้งานสำหรับทีมที่ต้องการสร้างและให้บริการความรู้'}</p>
                <dl className="mt-6 flex-1 space-y-3 border-t border-gray-100 pt-6 text-sm">
                  <div className="flex justify-between gap-4">
                    <dt className="text-gray-500">API calls</dt>
                    <dd className="font-semibold text-gray-900">{formatNumber(plan.api_calls_per_month)} / เดือน</dd>
                  </div>
                  <div className="flex justify-between gap-4">
                    <dt className="text-gray-500">รอบบริการ</dt>
                    <dd className="font-semibold text-gray-900">{plan.interval === 'year' ? 'รายปี' : 'รายเดือน'}</dd>
                  </div>
                </dl>
                <ul className="mt-6 space-y-2.5 text-sm text-gray-700">
                  {(plan.features.length ? plan.features : ['จัดการ API Keys', 'Hybrid Search', 'Role-based access']).map((feature) => (
                    <li key={feature} className="flex gap-2.5">
                      <span className="mt-0.5 text-primary-700">✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  type="button"
                  onClick={() => choosePlan(plan)}
                  disabled={checkoutPlan === plan.id}
                  className={`mt-8 w-full rounded-lg px-4 py-3 text-sm font-bold transition focus:outline-none focus:ring-4 ${featured ? 'bg-primary-700 text-white hover:bg-primary-800 focus:ring-primary-200' : 'bg-gray-950 text-white hover:bg-gray-800 focus:ring-gray-200'} disabled:cursor-wait disabled:opacity-60`}
                >
                  {checkoutPlan === plan.id ? 'กำลังเตรียมการชำระเงิน' : user ? 'เลือกแผนนี้' : 'เริ่มต้นใช้งาน'}
                </button>
              </article>
            );
          })}
        </div>
        {plans.length === 0 && <p className="mt-10 rounded-xl border border-gray-200 bg-white p-8 text-center text-sm text-gray-600">ยังไม่มีแผนการใช้งานที่เปิดให้บริการ</p>}
      </div>
    </div>
  );
}
