'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';

const publicLinks = [
  { href: '/', label: 'หน้าแรก' },
  { href: '/products', label: 'สินค้าและแผน' },
  { href: '/services', label: 'บริการ' },
  { href: '/articles', label: 'บทความ' },
  { href: '/about', label: 'เกี่ยวกับเรา' },
  { href: '/contact', label: 'ติดต่อเรา' },
];

function Brand() {
  return (
    <Link href="/" className="flex items-center gap-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary-600 to-primary-900 text-white shadow-sm" aria-hidden="true">
        <span className="text-sm font-black">K</span>
      </span>
      <span className="text-left">
        <span className="block text-sm font-bold leading-tight text-gray-900">Knowledge Platform</span>
        <span className="block text-[10px] font-medium uppercase tracking-wider text-gray-500">Knowledge Engineering</span>
      </span>
    </Link>
  );
}

function DesktopNavigation() {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();
  const [loggingOut, setLoggingOut] = useState(false);
  const memberLinks = [
    { href: '/dashboard', label: 'แดชบอร์ด' },
    { href: '/api-keys', label: 'API Keys' },
    { href: '/billing', label: 'การเรียกเก็บเงิน' },
  ];

  return (
    <nav aria-label="เมนูหลัก" className="hidden items-center gap-1 lg:flex">
      {publicLinks.map((link) => {
        const active = link.href === '/' ? pathname === '/' : pathname.startsWith(link.href);
        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={active ? 'page' : undefined}
            className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
              active
                ? 'bg-primary-50 text-primary-800'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }`}
          >
            {link.label}
          </Link>
        );
      })}
      {user ? (
        <>
          <span className="mx-2 h-6 w-px bg-gray-200" aria-hidden="true" />
          {memberLinks.map((link) => {
            const active = pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? 'page' : undefined}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                  active
                    ? 'bg-primary-50 text-primary-800'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
          {user.role === 'admin' && (
            <Link
              href="/admin"
              aria-current={pathname.startsWith('/admin') ? 'page' : undefined}
              className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                pathname.startsWith('/admin')
                  ? 'bg-primary-50 text-primary-800'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              ผู้ดูแลระบบ
            </Link>
          )}
          <button
            type="button"
            disabled={loggingOut}
            onClick={async () => {
              setLoggingOut(true);
              try {
                await logout();
              } finally {
                setLoggingOut(false);
              }
            }}
            className="ml-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-white hover:bg-gray-50 disabled:cursor-wait disabled:opacity-50"
          >
            {loggingOut ? 'กำลังออก' : 'ออกจากระบบ'}
          </button>
        </>
      ) : (
        <div className="ml-2 flex items-center gap-2">
          {loading ? (
            <span className="px-3 text-sm text-gray-500">กำลังโหลด</span>
          ) : (
            <>
              <Link href="/auth/login" className="rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100">
                เข้าสู่ระบบ
              </Link>
              <Link href="/auth/register" className="rounded-lg bg-primary-700 px-3 py-2 text-sm font-semibold text-white hover:bg-primary-800">
                สมัครสมาชิก
              </Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}

function MobileNavigation({ open }: { open: boolean }) {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
    } finally {
      setLoggingOut(false);
    }
  };

  return (
    <div id="mobile-menu" className={`lg:hidden ${open ? 'block' : 'hidden'}`}>
      <nav aria-label="เมนูมือถือ" className="space-y-1 border-t border-gray-200 px-4 py-4">
        {publicLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            aria-current={pathname === link.href ? 'page' : undefined}
            className={`block rounded-lg px-3 py-2.5 text-sm font-medium ${
              pathname === link.href ? 'bg-primary-50 text-primary-800' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            {link.label}
          </Link>
        ))}
        {user ? (
          <>
            <div className="my-3 border-t border-gray-200" />
            {[
              { href: '/dashboard', label: 'แดชบอร์ด' },
              { href: '/api-keys', label: 'API Keys' },
              { href: '/billing', label: 'การเรียกเก็บเงิน' },
            ].map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`block rounded-lg px-3 py-2.5 text-sm font-medium ${
                  pathname.startsWith(link.href) ? 'bg-primary-50 text-primary-800' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {link.label}
              </Link>
            ))}
            {user.role === 'admin' && (
              <Link
                href="/admin"
                className={`block rounded-lg px-3 py-2.5 text-sm font-medium ${
                  pathname.startsWith('/admin') ? 'bg-primary-50 text-primary-800' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                ผู้ดูแลระบบ
              </Link>
            )}
            <div className="my-3 border-t border-gray-200" />
            <div className="px-3 py-2">
              <p className="truncate text-sm font-medium text-gray-900">{user.full_name || user.email}</p>
              <p className="truncate text-xs text-gray-500">{user.email}</p>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              disabled={loggingOut}
              className="mt-2 w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 disabled:cursor-wait disabled:opacity-50"
            >
              {loggingOut ? 'กำลังออกจากระบบ' : 'ออกจากระบบ'}
            </button>
          </>
        ) : (
          <div className="grid grid-cols-2 gap-3 border-t border-gray-200 pt-4">
            <Link href="/auth/login" className="rounded-lg border border-gray-300 px-3 py-2.5 text-center text-sm font-semibold text-gray-700">
              เข้าสู่ระบบ
            </Link>
            <Link href="/auth/register" className="rounded-lg bg-primary-700 px-3 py-2.5 text-center text-sm font-semibold text-white">
              {loading ? 'กำลังโหลด' : 'สมัครสมาชิก'}
            </Link>
          </div>
        )}
      </nav>
    </div>
  );
}

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { user } = useAuth();

  useEffect(() => setOpen(false), [pathname]);

  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-8xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Brand />
        <DesktopNavigation />
        <div className="flex items-center gap-2 lg:hidden">
          <Link href={user ? '/dashboard' : '/auth/login'} className="rounded-lg px-3 py-2 text-sm font-semibold text-primary-700 hover:bg-primary-50">
            {user?.full_name || 'บัญชีของฉัน'}
          </Link>
          <button
            type="button"
            aria-label={open ? 'ปิดเมนู' : 'เปิดเมนู'}
            aria-controls="mobile-menu"
            aria-expanded={open}
            onClick={() => setOpen((value) => !value)}
            className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
              {open ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>
      <MobileNavigation open={open} />
    </header>
  );
}
