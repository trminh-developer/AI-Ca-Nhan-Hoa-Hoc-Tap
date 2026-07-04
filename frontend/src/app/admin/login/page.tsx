'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login, getMe } from '@/lib/api';
import styles from './login.module.css';

export default function AdminLogin() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // 1. Đăng nhập để lấy token
      const res = await login(username, password);
      const token = res.access_token;
      
      // 2. Lấy thông tin user để kiểm tra quyền admin
      const user = await getMe(token);
      
      if (user.role !== 'admin' && user.role !== 'teacher') {
        setError('Tài khoản này không có quyền Quản trị hoặc Giảng viên!');
        setIsLoading(false);
        return;
      }

      // 3. Nếu là Admin, lưu token riêng cho trang quản trị
      localStorage.setItem('admin_token', token);
      
      // 4. Chuyển hướng vào trang Admin Dashboard
      router.push('/admin');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'Tài khoản hoặc mật khẩu không chính xác');
      } else {
        setError('Tài khoản hoặc mật khẩu không chính xác');
      }
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.loginBox}>
        <div className={styles.header}>
          <div className={styles.icon}>🛡️</div>
          <h1 className={styles.title}>Admin Panel</h1>
          <p className={styles.subtitle}>Đăng nhập dành riêng cho Quản trị viên</p>
        </div>
        
        {error && <div className={styles.errorAlert}>{error}</div>}
        
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputGroup}>
            <label htmlFor="username">Tên đăng nhập</label>
            <input 
              id="username"
              type="text" 
              placeholder="Nhập tài khoản admin..."
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          
          <div className={styles.inputGroup}>
            <label htmlFor="password">Mật khẩu</label>
            <input 
              id="password"
              type="password" 
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          
          <button 
            type="submit" 
            className={styles.loginBtn}
            disabled={isLoading || !username || !password}
          >
            {isLoading ? 'Đang xác thực...' : 'Đăng nhập vào Quản trị'}
          </button>
        </form>

        <button 
          onClick={() => router.push('/login')} 
          className={styles.backBtn}
        >
          ← Quay lại Đăng nhập Học viên
        </button>
      </div>
    </div>
  );
}
