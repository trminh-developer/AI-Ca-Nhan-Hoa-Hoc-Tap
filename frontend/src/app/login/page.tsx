'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import styles from './login.module.css';

const DEMO_ACCOUNTS = [
  { label: '👤 Học viên', user: 'student', pass: 'student123' },
  { label: '👨‍🏫 Giảng viên', user: 'teacher', pass: 'teacher123' },
  { label: '🛡️ Admin', user: 'admin', pass: 'admin123' },
  { label: '⚡ trminhdev', user: 'trminhdev', pass: '123456' },
];

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.username, form.password);
      router.push('/dashboard');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Đăng nhập thất bại';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.decorOrb1}></div>
      <div className={styles.decorOrb2}></div>
      <div className={styles.card}>
        <Link href="/" className={styles.logo}>
          🧠 Nyvora
        </Link>
        <h1 className={styles.title}>Đăng nhập</h1>
        <p className={styles.subtitle}>Hệ thống Học tập Thích ứng AI (JWT + Refresh Rotation)</p>

        {error && <div className={styles.error}>⚠️ {error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Tên đăng nhập hoặc Email</label>
            <input
              type="text"
              className={styles.input}
              placeholder="Nhập tên đăng nhập (vd: student, trminhdev)"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Mật khẩu</label>
            <input
              type="password"
              className={styles.input}
              placeholder="Nhập mật khẩu"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>
          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? 'Đang xác thực JWT...' : 'Đăng nhập →'}
          </button>
        </form>

        <div className="mt-5 pt-4 border-t border-white/10">
          <p className="text-xs text-slate-400 mb-2 text-center">
            Tài khoản mẫu NCKH (Click để điền nhanh):
          </p>
          <div className="grid grid-cols-2 gap-1.5">
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.user}
                type="button"
                onClick={() => {
                  setError('');
                  setForm({ username: acc.user, password: acc.pass });
                }}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium bg-white/5 hover:bg-indigo-500/20 border border-white/10 hover:border-indigo-500/40 text-slate-300 transition cursor-pointer text-left truncate"
              >
                {acc.label}: <span className="font-mono text-indigo-300">{acc.user}</span>
              </button>
            ))}
          </div>
        </div>

        <p className={styles.switchText}>
          Chưa có tài khoản?{' '}
          <Link href="/register" className={styles.switchLink}>
            Đăng ký ngay
          </Link>
        </p>
      </div>
    </div>
  );
}
