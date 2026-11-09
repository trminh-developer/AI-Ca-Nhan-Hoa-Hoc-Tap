'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function RoleGuard({
  children,
  allowedRoles,
  redirectTo = '/dashboard',
}: {
  children: React.ReactNode;
  allowedRoles: Array<'admin' | 'teacher' | 'student'>;
  redirectTo?: string;
}) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated || !user) {
      router.replace('/login');
      return;
    }
    if (!allowedRoles.includes(user.role as 'admin' | 'teacher' | 'student')) {
      router.replace(redirectTo);
    }
  }, [isLoading, isAuthenticated, user, allowedRoles, router, redirectTo]);

  if (isLoading || !user) return null;
  if (!allowedRoles.includes(user.role as 'admin' | 'teacher' | 'student')) return null;

  return <>{children}</>;
}
