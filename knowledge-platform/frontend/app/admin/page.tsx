'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Field, inputClassName } from '@/components/ui/FormField';
import { PageHeader } from '@/components/ui/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States';
import { api, getErrorMessage } from '@/lib/api/client';
import { formatDateTime, formatMoney, formatNumber } from '@/lib/format';
import type { AdminStats, AdminUserList, User } from '@/lib/types';

interface Filters {
  search: string;
  role: string;
  active: string;
}

const stats = [
  { label: 'ผู้ใช้งาน', get: (value: AdminStats) => value.total_users, format: formatNumber },
  { label: 'พื้นที่ทำงาน', get: (value: AdminStats) => value.total_tenants, format: formatNumber },
  { label: 'สมาชิกทั้งหมด', get: (value: AdminStats) => value.total_subscriptions, format: formatNumber },
  { label: 'สมาชิกใช้งานได้', get: (value: AdminStats) => value.active_subscriptions, format: formatNumber },
  { label: 'API Keys', get: (value: AdminStats) => `${value.active_api_keys}/${value.total_api_keys}`, format: (value: string) => value },
  { label: 'API calls วันนี้', get: (value: AdminStats) => value.total_api_calls_today, format: formatNumber },
  { label: 'API calls เดือนนี้', get: (value: AdminStats) => value.total_api_calls_month, format: formatNumber },
  { label: 'รายได้สะสม', get: (value: AdminStats) => formatMoney(value.revenue_cents, 'THB'), format: (value: string) => value },
  { label: 'ข้อความติดต่อ', get: (value: AdminStats) => value.contact_messages, format: formatNumber },
  { label: 'รอดำเนินการ', get: (value: AdminStats) => value.pending_contact_messages, format: formatNumber },
] as const;

export function AdminContent() {
  const [filters, setFilters] = useState<Filters>({ search: '', role: '', active: '' });
  const [page, setPage] = useState(1);
  const [statsData, setStatsData] = useState<AdminStats | null>(null);
  const [userList, setUserList] = useState<AdminUserList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [busyUser, setBusyUser] = useState<string>();

  const load = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '20',
      });
      if (filters.search) params.set('search', filters.search);
      if (filters.role) params.set('role', filters.role);
      if (filters.active) params.set('is_active', filters.active);

      const [statsResponse, usersResponse] = await Promise.all([
        api.get<AdminStats>('/api/v1/admin/stats'),
        api.get<AdminUserList>(`/api/v1/admin/users?${params}`),
      ]);
      setStatsData(statsResponse.data);
      setUserList(usersResponse.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [page, filters.role, filters.active]);

  const submitSearch = (event: React.FormEvent) => {
    event.preventDefault();
    setPage(1);
    void load();
  };

  const updateUser = async (user: User, active: boolean) => {
    setBusyUser(user.id);
    setError(undefined);
    try {
      await api.patch(`/api/v1/admin/users/${user.id}`, { is_active: active });
      setUserList((current) => current ? {
        ...current,
        users: current.users.map((item) => item.id === user.id ? { ...item, is_active: active } : item),
      } : current);
      await load();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusyUser(undefined);
    }
  };

  if (loading) return <LoadingState label="กำลังโหลดแดชบอร์ดผู้ดูแลระบบ" />;
  if (error && !statsData && !userList) return <ErrorState message={error} onRetry={load} />;

  const totalPages = userList ? Math.max(1, Math.ceil(userList.total / userList.page_size)) : 1;

  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader eyebrow="Administration" title="ภาพรวมแพลตฟอร์ม" description="ข้อมูลผู้ใช้งาน สมาชิก API และข้อความติดต่อจากแหล่งข้อมูลจริง" action={error && <button type="button" onClick={() => void load()} className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-semibold hover:bg-gray-50">ลองอีกครั้ง</button>} />
        {error && <div role="alert" className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 whitespace-pre-line text-sm text-red-800">{error}</div>}

        {statsData && (
          <section aria-label="สถิติแพลตฟอร์ม" className="mt-10 grid grid-cols-2 gap-4 lg:grid-cols-5">
            {stats.map((item) => (
              <article key={item.label} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
                <p className="text-xs font-medium text-gray-500">{item.label}</p>
                <p className="mt-2 text-xl font-bold text-gray-900 sm:text-2xl">{item.format(item.get(statsData))}</p>
              </article>
            ))}
          </section>
        )}

        <section className="mt-10 rounded-2xl bg-white p-6 shadow-sm sm:p-7">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <h2 className="text-xl font-bold text-gray-900">ผู้ใช้งาน</h2>
              <p className="mt-1 text-sm text-gray-600">{userList ? `ทั้งหมด ${formatNumber(userList.total)} บัญชี` : 'ไม่มีข้อมูล'}</p>
            </div>
            <form onSubmit={submitSearch} className="grid w-full gap-3 sm:grid-cols-[1fr_auto_auto_auto]">
              <Field label="ค้นหา">
                <input value={filters.search} onChange={(event) => setFilters((current) => ({ ...current, search: event.target.value }))} className={inputClassName()} placeholder="อีเมลหรือชื่อ" />
              </Field>
              <Field label="บทบาท">
                <select value={filters.role} onChange={(event) => setFilters((current) => ({ ...current, role: event.target.value }))} className={inputClassName()}>
                  <option value="">ทั้งหมด</option>
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                  <option value="guest">Guest</option>
                </select>
              </Field>
              <Field label="สถานะ">
                <select value={filters.active} onChange={(event) => setFilters((current) => ({ ...current, active: event.target.value }))} className={inputClassName()}>
                  <option value="">ทั้งหมด</option>
                  <option value="true">เปิดใช้งาน</option>
                  <option value="false">ปิดใช้งาน</option>
                </select>
              </Field>
              <button type="submit" className="mt-5 rounded-lg bg-primary-700 px-4 py-2.5 text-sm font-bold text-white hover:bg-primary-800 sm:mt-0">กรอง</button>
            </form>
          </div>

          {userList?.users.length === 0 ? (
            <div className="mt-8"><EmptyState title="ไม่พบผู้ใช้งาน" message="ลองเปลี่ยนคำค้นหาหรือตัวกรอง" /></div>
          ) : (
            <div className="mt-6 overflow-x-auto rounded-xl border border-gray-200">
              <table className="w-full min-w-[760px] divide-y divide-gray-200 text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
                  <tr>
                    <th className="px-4 py-3 font-semibold">ผู้ใช้งาน</th>
                    <th className="px-4 py-3 font-semibold">บทบาท</th>
                    <th className="px-4 py-3 font-semibold">พื้นที่ทำงาน</th>
                    <th className="px-4 py-3 font-semibold">สร้างเมื่อ</th>
                    <th className="px-4 py-3 font-semibold">สถานะ</th>
                    <th className="px-4 py-3 font-semibold"><span className="sr-only">ดำเนินการ</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 bg-white">
                  {userList?.users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <p className="font-semibold text-gray-900">{user.full_name || user.email}</p>
                        <p className="mt-0.5 text-xs text-gray-500">{user.email}</p>
                      </td>
                      <td className="px-4 py-3"><span className={`rounded-full px-2 py-1 text-[10px] font-bold uppercase ${user.role === 'admin' ? 'bg-primary-50 text-primary-800' : 'bg-gray-100 text-gray-700'}`}>{user.role}</span></td>
                      <td className="px-4 py-3 font-mono text-xs text-gray-600">{user.tenant_id.slice(0, 8)}…</td>
                      <td className="px-4 py-3 text-xs text-gray-600">{formatDateTime(user.created_at)}</td>
                      <td className="px-4 py-3"><span className={`rounded-full px-2 py-1 text-[10px] font-bold ${user.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-200 text-gray-600'}`}>{user.is_active ? 'active' : 'inactive'}</span></td>
                      <td className="px-4 py-3 text-right">
                        <button type="button" disabled={busyUser === user.id} onClick={() => void updateUser(user, !user.is_active)} className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-bold hover:bg-gray-50 disabled:cursor-wait disabled:opacity-50">
                          {busyUser === user.id ? 'บันทึก' : user.is_active ? 'ปิดใช้งาน' : 'เปิดใช้งาน'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {userList && totalPages > 1 && (
            <nav aria-label="หน้าผู้ใช้งาน" className="mt-6 flex items-center justify-center gap-2">
              <button type="button" disabled={page === 1} onClick={() => setPage((current) => Math.max(1, current - 1))} className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-semibold disabled:opacity-40">ก่อนหน้า</button>
              <span className="min-w-20 text-center text-sm text-gray-700">หน้า {page} จาก {totalPages}</span>
              <button type="button" disabled={page === totalPages} onClick={() => setPage((current) => Math.min(totalPages, current + 1))} className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-semibold disabled:opacity-40">ถัดไป</button>
            </nav>
          )}
        </section>
      </div>
    </div>
  );
}

export default function AdminPage() {
  return <ProtectedRoute allowedRoles={['admin']}><AdminContent /></ProtectedRoute>;
}
