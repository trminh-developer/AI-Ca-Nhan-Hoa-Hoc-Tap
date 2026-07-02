'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getMe, updateMe } from '@/lib/api';
import styles from './profile.module.css';

interface User {
  id: number;
  username: string;
  email: string;
  overall_elo: number;
  is_admin: boolean;
  created_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
  // Edit form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadUser = useCallback(async () => {
    try {
      const data = await getMe();
      setUser(data);
      setEmail(data.email);
    } catch (err) {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void loadUser();
  }, [loadUser]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password && password !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp');
      return;
    }

    if (password && password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự');
      return;
    }

    setSaving(true);
    try {
      const updateData: { email?: string; password?: string } = {};
      if (email !== user?.email) updateData.email = email;
      if (password) updateData.password = password;

      if (Object.keys(updateData).length > 0) {
        const updatedUser = await updateMe(updateData);
        setUser(updatedUser);
        setSuccess('Cập nhật thông tin thành công!');
        setPassword('');
        setConfirmPassword('');
      }
      setIsEditing(false);
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message || 'Cập nhật thất bại');
      } else {
        setError('Cập nhật thất bại');
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className={styles.page}><div className="loading">Đang tải...</div></div>;
  }

  if (!user) return null;

  return (
    <div className={styles.page}>
      <Link href="/dashboard" className={styles.backLink}>← Quay lại Dashboard</Link>
      
      <div className={styles.container}>
        <h1 className={styles.title}>Hồ Sơ Cá Nhân</h1>
        
        {error && <div className={styles.error}>⚠️ {error}</div>}
        {success && <div className={styles.success}>✅ {success}</div>}

        {!isEditing ? (
          <>
            <div className={styles.infoGroup}>
              <span className={styles.label}>Tên đăng nhập</span>
              <span className={styles.value}>{user.username} {user.is_admin ? '(Admin)' : ''}</span>
            </div>
            
            <div className={styles.infoGroup}>
              <span className={styles.label}>Email</span>
              <span className={styles.value}>{user.email}</span>
            </div>

            <div className={styles.infoGroup}>
              <span className={styles.label}>Trình độ hiện tại (Elo)</span>
              <span className={styles.value}>{Math.round(user.overall_elo)}</span>
            </div>

            <div className={styles.infoGroup}>
              <span className={styles.label}>Ngày tham gia</span>
              <span className={styles.value}>{new Date(user.created_at).toLocaleDateString('vi-VN')}</span>
            </div>

            <button className={styles.editBtn} onClick={() => setIsEditing(true)}>
              Chỉnh sửa thông tin
            </button>
          </>
        ) : (
          <form onSubmit={handleSave}>
            <div className={styles.infoGroup}>
              <span className={styles.label}>Tên đăng nhập</span>
              <span className={styles.value} style={{ opacity: 0.5 }}>{user.username} (Không thể đổi)</span>
            </div>
            
            <div className={styles.infoGroup}>
              <label className={styles.label}>Email mới</label>
              <input 
                type="email" 
                className={styles.input} 
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>

            <div className={styles.infoGroup}>
              <label className={styles.label}>Đổi mật khẩu mới (Để trống nếu không muốn đổi)</label>
              <input 
                type="password" 
                className={styles.input} 
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Tối thiểu 6 ký tự"
              />
            </div>

            {password && (
              <div className={styles.infoGroup}>
                <label className={styles.label}>Xác nhận mật khẩu mới</label>
                <input 
                  type="password" 
                  className={styles.input} 
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  required={!!password}
                />
              </div>
            )}

            <button type="submit" className={styles.saveBtn} disabled={saving}>
              {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
            </button>
            <button type="button" className={styles.cancelBtn} onClick={() => setIsEditing(false)}>
              Hủy
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
