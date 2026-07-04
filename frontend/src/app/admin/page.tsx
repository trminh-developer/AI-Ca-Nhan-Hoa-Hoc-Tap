'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getMe, getAdminStats, getAllUsers, updateUserRole } from '@/lib/api';
import styles from './admin.module.css';

interface AdminStats {
  total_users: number;
  total_subjects: number;
  total_topics: number;
  total_questions: number;
}

interface User {
  id: number;
  username: string;
  email: string;
  overall_elo: number;
  is_admin: boolean;
  created_at: string;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = useCallback(async () => {
    // Bước 1: Kiểm tra đã đăng nhập chưa
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) {
      router.push('/admin/login');
      return;
    }

    try {
      // Bước 2: Kiểm tra quyền Admin
      const currentUser = await getMe(adminToken);
      if (!currentUser.is_admin) {
        router.push('/admin/login');
        return;
      }

      // Bước 3: Load dữ liệu Admin
      const [statsData, usersData] = await Promise.all([
        getAdminStats(adminToken),
        getAllUsers(adminToken)
      ]);
      setStats(statsData);
      setUsers(usersData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Lỗi không xác định';
      if (message.includes('401') || message.includes('Token')) {
        // Token hết hạn hoặc không hợp lệ -> về trang đăng nhập admin
        localStorage.removeItem('admin_token');
        router.push('/admin/login');
      } else if (message.includes('403') || message.includes('Admin')) {
        // Không có quyền admin
        localStorage.removeItem('admin_token');
        router.push('/admin/login');
      } else {
        setError(`Lỗi kết nối API: ${message}. Hãy đảm bảo Backend đang chạy.`);
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const toggleRole = async (userId: number, currentRole: boolean) => {
    try {
      const adminToken = localStorage.getItem('admin_token') || undefined;
      await updateUserRole(userId, !currentRole, adminToken);
      setUsers(users.map(u => u.id === userId ? { ...u, is_admin: !currentRole } : u));
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message || 'Lỗi khi cập nhật quyền');
      } else {
        alert('Lỗi khi cập nhật quyền');
      }
    }
  };

  if (loading) return (
    <div className={styles.loadingPage}>
      <div className={styles.spinner}></div>
      <p>Đang kiểm tra quyền truy cập...</p>
    </div>
  );

  if (error) return (
    <div className={styles.errorPage}>
      <h2>⚠️ Lỗi</h2>
      <p>{error}</p>
      <button onClick={() => { setError(''); setLoading(true); void loadData(); }} className={styles.retryBtn}>
        🔄 Thử lại
      </button>
    </div>
  );

  if (!stats) return null;

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Tổng quan Hệ thống</h1>
        <p className={styles.subtitle}>Theo dõi các chỉ số quan trọng của LearnAI</p>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>👥</div>
          <div className={styles.statValue}>{stats.total_users}</div>
          <div className={styles.statLabel}>Học viên</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>📚</div>
          <div className={styles.statValue}>{stats.total_subjects}</div>
          <div className={styles.statLabel}>Môn học</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>📋</div>
          <div className={styles.statValue}>{stats.total_topics}</div>
          <div className={styles.statLabel}>Chủ đề</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>❓</div>
          <div className={styles.statValue}>{stats.total_questions}</div>
          <div className={styles.statLabel}>Câu hỏi AI</div>
        </div>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Quản lý Người Dùng</h2>
        {users.length === 0 ? (
          <p style={{ color: 'var(--color-text-secondary)', padding: '1rem' }}>Chưa có người dùng nào.</p>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Tên đăng nhập</th>
                  <th>Email</th>
                  <th>Điểm Elo</th>
                  <th>Phân quyền</th>
                  <th>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td>#{user.id}</td>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{Math.round(user.overall_elo)}</td>
                    <td>
                      <span className={user.is_admin ? styles.badgeAdmin : styles.badgeUser}>
                        {user.is_admin ? '🛡️ Admin' : '👤 Học viên'}
                      </span>
                    </td>
                    <td>
                      {user.username !== 'admin' && (
                        <button 
                          className={styles.actionBtn}
                          onClick={() => toggleRole(user.id, user.is_admin)}
                        >
                          {user.is_admin ? 'Hạ quyền' : 'Cấp Admin'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
