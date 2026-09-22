'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Field, inputClassName } from '@/components/ui/FormField';
import { PageHeader } from '@/components/ui/PageHeader';
import { api, getErrorMessage } from '@/lib/api/client';

interface ContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}

const initialForm: ContactForm = {
  name: '',
  email: '',
  subject: '',
  message: '',
};

export default function ContactPage() {
  const searchParams = useSearchParams();
  const [form, setForm] = useState<ContactForm>(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>();
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const subject = searchParams.get('subject');
    if (subject) setForm((current) => ({ ...current, subject }));
  }, [searchParams]);

  const update = (field: keyof ContactForm, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(undefined);
    setSuccess(false);
    try {
      await api.post('/api/v1/contact', form);
      setForm(initialForm);
      setSuccess(true);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto grid max-w-8xl gap-12 px-4 sm:px-6 lg:grid-cols-[0.8fr_1.2fr] lg:px-8">
        <div>
          <PageHeader eyebrow="Contact" title="เริ่มสนทนากัน" description="ส่งโจทย์ของทีมมาทีมงานจะติดต่อกลับเพื่อช่วยกำหนดขั้นตอนถัดไป" />
          <div className="mt-10 space-y-6 rounded-2xl bg-white p-6 shadow-sm">
            <div>
              <p className="text-sm font-bold text-gray-900">ช่องทางติดต่อ</p>
              <p className="mt-2 text-sm text-gray-600">contact@knowledge-platform.example</p>
            </div>
            <div>
              <p className="text-sm font-bold text-gray-900">เวลาทำการ</p>
              <p className="mt-2 text-sm text-gray-600">จันทร์–ศุกร์ 09:00–18:00 น.</p>
            </div>
            <p className="rounded-xl bg-primary-50 p-4 text-sm leading-6 text-primary-900">สำหรับข้อความที่มีข้อมูลส่วนตัวหรือความลับ โปรดไม่ส่งรหัสผ่านหรือ API Key ผ่านแบบฟอร์มนี้</p>
          </div>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-sm sm:p-8">
          {success ? (
            <div role="status" className="flex min-h-[28rem] flex-col items-center justify-center text-center">
              <span className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-2xl font-bold text-emerald-700">✓</span>
              <h2 className="mt-5 text-2xl font-bold text-gray-900">ส่งข้อความแล้ว</h2>
              <p className="mt-3 max-w-md text-sm leading-6 text-gray-600">ขอบคุณที่ติดต่อมา เราได้รับข้อความของคุณแล้วและจะติดต่อกลับโดยเร็ว</p>
              <button type="button" onClick={() => setSuccess(false)} className="mt-6 rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold hover:bg-gray-50">ส่งข้อความอีกข้อความ</button>
            </div>
          ) : (
            <form onSubmit={submit} className="space-y-5">
              {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{error}</div>}
              <div className="grid gap-5 sm:grid-cols-2">
                <Field label="ชื่อและนามสกุล">
                  <input required maxLength={100} value={form.name} onChange={(event) => update('name', event.target.value)} autoComplete="name" className={inputClassName()} placeholder="ชื่อของคุณ" />
                </Field>
                <Field label="อีเมล">
                  <input required type="email" maxLength={320} value={form.email} onChange={(event) => update('email', event.target.value)} autoComplete="email" className={inputClassName()} placeholder="name@company.com" />
                </Field>
              </div>
              <Field label="หัวข้อ">
                <input required maxLength={200} value={form.subject} onChange={(event) => update('subject', event.target.value)} className={inputClassName()} placeholder="สิ่งที่คุณต้องการให้ช่วย" />
              </Field>
              <Field label="รายละเอียด" hint={`${form.message.length} / 10,000`}>
                <textarea required maxLength={10000} rows={7} value={form.message} onChange={(event) => update('message', event.target.value)} className={`${inputClassName()} resize-y`} placeholder="เล่าถึงข้อมูล ผู้ใช้ เป้าหมาย และข้อจำกัดของโครงการ" />
              </Field>
              <button type="submit" disabled={submitting} className="w-full rounded-lg bg-primary-700 px-5 py-3.5 text-sm font-bold text-white transition hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:cursor-wait disabled:opacity-60">
                {submitting ? 'กำลังส่งข้อความ' : 'ส่งข้อความ'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
