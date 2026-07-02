'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { login } from '@/lib/api';
import styles from './login.module.css';

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(form.username, form.password);
      localStorage.setItem('token', data.access_token);
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
        <Link href="/" className={styles.logo}>🧠 LearnAI</Link>
        <h1 className={styles.title}>Đăng nhập</h1>
        <p className={styles.subtitle}>Chào mừng bạn trở lại!</p>

        {error && <div className={styles.error}>⚠️ {error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Tên đăng nhập</label>
            <input
              type="text"
              className={styles.input}
              placeholder="Nhập tên đăng nhập"
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
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập →'}
          </button>
        </form>

        <p className={styles.switchText}>
          Chưa có tài khoản?{' '}
          <Link href="/register" className={styles.switchLink}>Đăng ký ngay</Link>
        </p>
      </div>
    </div>
  );
}
