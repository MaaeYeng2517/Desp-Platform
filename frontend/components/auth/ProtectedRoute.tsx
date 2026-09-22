'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';
import { ForbiddenState, LoadingState } from '@/components/ui/States';
import type { Role } from '@/lib/types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: Role[];
}

export default function ProtectedRoute({
  children,
  allowedRoles = ['member', 'admin'],
}: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      const next = `${pathname}${typeof window !== 'undefined' ? window.location.search : ''}`;
      router.replace(`/auth/login?next=${encodeURIComponent(next)}`);
    }
  }, [loading, user, router, pathname]);

  if (loading) return <LoadingState label="กำลังตรวจสอบสิทธิ์" />;
  if (!user) return null;

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <ForbiddenState />;
  }

  return children;
}
