'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';
import { Field, inputClassName } from '@/components/ui/FormField';
import { getErrorMessage } from '@/lib/api/client';

export default function LoginPage() {
  const { user, loading: authLoading, login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    if (!authLoading && user) router.replace('/dashboard');
  }, [authLoading, user, router]);

  const next = searchParams.get('next');
  const destination = next?.startsWith('/') && !next.startsWith('//') ? next : '/dashboard';

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(undefined);
    try {
      await login(email, password);
      router.replace(destination);
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'อีเมลหรือรหัสผ่านไม่ถูกต้อง'));
    } finally {
      setSubmitting(false);
    }
  };

  if (authLoading) {
    return <div className="flex min-h-[40rem] items-center justify-center"><div className="h-9 w-9 animate-spin rounded-full border-4 border-primary-200 border-t-primary-700" role="status" /></div>;
  }
  if (user) return null;

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto grid max-w-5xl overflow-hidden rounded-3xl bg-white shadow-xl sm:grid-cols-[1fr_0.85fr]">
        <div className="bg-gray-950 p-8 text-white sm:p-12 lg:p-14">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-400">Member Access</p>
          <h1 className="mt-5 text-3xl font-bold leading-tight sm:text-4xl">เข้าสู่พื้นที่ทำงานของคุณ</h1>
          <p className="mt-5 text-sm leading-6 text-gray-400">จัดการ API Keys ติดตามสมาชิก และเข้าถึงเครื่องมือสร้างแพลตฟอร์มความรู้</p>
          <ul className="mt-12 space-y-5 text-sm text-gray-300">
            {['จัดการสิทธิ์ API ด้วยตัวเอง', 'ติดตามแผนและการใช้งาน', 'เข้าถึงเครื่องมือผู้ดูแลตามบทบาท'].map((item) => (
              <li key={item} className="flex gap-3"><span className="text-primary-400">✓</span>{item}</li>
            ))}
          </ul>
        </div>
        <div className="p-8 sm:p-12">
          <p className="text-sm font-semibold text-gray-600">ยังไม่มีบัญชี? <Link href="/auth/register" className="font-bold text-primary-700 hover:underline">สมัครสมาชิก</Link></p>
          <form onSubmit={submit} className="mt-8 space-y-5">
            {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{error}</div>}
            <Field label="อีเมล">
              <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" className={inputClassName()} placeholder="name@company.com" />
            </Field>
            <Field label="รหัสผ่าน">
              <input required type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" className={inputClassName()} placeholder="รหัสผ่าน" />
            </Field>
            <button disabled={submitting} className="w-full rounded-lg bg-primary-700 px-5 py-3 text-sm font-bold text-white hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:cursor-wait disabled:opacity-60">
              {submitting ? 'กำลังเข้าสู่ระบบ' : 'เข้าสู่ระบบ'}
            </button>
          </form>
          <p className="mt-6 text-xs leading-5 text-gray-500">การเข้าสู่ระบบหมายถึงคุณยอมรับนโยบายการใช้งานของแพลตฟอร์ม</p>
        </div>
      </div>
    </div>
  );
}
