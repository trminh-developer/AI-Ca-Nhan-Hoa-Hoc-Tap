'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register, login } from '@/lib/api';
import styles from '../login/login.module.css';

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp');
      return;
    }
    if (form.password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự');
      return;
    }

    setLoading(true);
    try {
      await register(form.username, form.email, form.password);
      // Auto-login sau khi đăng ký
      const data = await login(form.username, form.password);
      localStorage.setItem('token', data.access_token);
      router.push('/dashboard');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Đăng ký thất bại';
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
        <Link href="/" className={styles.logo}>🧠 Nyvora</Link>
        <h1 className={styles.title}>Đăng ký tài khoản</h1>
        <p className={styles.subtitle}>Bắt đầu hành trình học tập thông minh</p>

        {error && <div className={styles.error}>⚠️ {error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Tên đăng nhập</label>
            <input type="text" className={styles.input} placeholder="Nhập tên đăng nhập"
              value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Email</label>
            <input type="email" className={styles.input} placeholder="example@email.com"
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Mật khẩu</label>
            <input type="password" className={styles.input} placeholder="Tối thiểu 6 ký tự"
              value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Xác nhận mật khẩu</label>
            <input type="password" className={styles.input} placeholder="Nhập lại mật khẩu"
              value={form.confirmPassword} onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })} required />
          </div>
          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? 'Đang tạo tài khoản...' : 'Tạo tài khoản →'}
          </button>
        </form>

        <p className={styles.switchText}>
          Đã có tài khoản?{' '}
          <Link href="/login" className={styles.switchLink}>Đăng nhập</Link>
        </p>
      </div>
    </div>
  );
}
