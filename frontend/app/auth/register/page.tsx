'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';
import { Field, inputClassName } from '@/components/ui/FormField';
import { getErrorMessage } from '@/lib/api/client';

export default function RegisterPage() {
  const { user, loading: authLoading, register } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    if (!authLoading && user) router.replace('/dashboard');
  }, [authLoading, user, router]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(undefined);
    try {
      await register(email, password, fullName);
      router.replace('/dashboard');
    } catch (requestError) {
      setError(getErrorMessage(requestError));
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
      <div className="mx-auto max-w-2xl">
        <div className="text-center">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-700">Create Account</p>
          <h1 className="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl">สร้างบัญชีใหม่</h1>
          <p className="mt-3 text-sm text-gray-600">เริ่มต้นด้วยแผนฟรีและอัปเกรดเมื่อทีมของคุณพร้อม</p>
        </div>
        <div className="mt-8 rounded-2xl bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-semibold text-gray-600">มีบัญชีแล้ว? <Link href="/auth/login" className="font-bold text-primary-700 hover:underline">เข้าสู่ระบบ</Link></p>
          <form onSubmit={submit} className="mt-8 space-y-5">
            {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{error}</div>}
            <Field label="ชื่อ" hint="ไม่บังคับ">
              <input value={fullName} onChange={(event) => setFullName(event.target.value)} maxLength={255} autoComplete="name" className={inputClassName()} placeholder="ชื่อของคุณ" />
            </Field>
            <Field label="อีเมล">
              <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" className={inputClassName()} placeholder="name@company.com" />
            </Field>
            <Field label="รหัสผ่าน" hint="8 ตัวอักษรขึ้นไป">
              <input required minLength={8} maxLength={128} type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" className={inputClassName()} placeholder="สร้างรหัสผ่าน" />
            </Field>
            <button disabled={submitting} className="w-full rounded-lg bg-primary-700 px-5 py-3 text-sm font-bold text-white hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:cursor-wait disabled:opacity-60">
              {submitting ? 'กำลังสร้างบัญชี' : 'สร้างบัญชี'}
            </button>
          </form>
          <p className="mt-6 text-xs leading-5 text-gray-500">บัญชีใหม่จะได้รับแผน Free และพื้นที่ทำงานอัตโนมัติ</p>
        </div>
      </div>
    </div>
  );
}
