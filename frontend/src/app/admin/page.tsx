'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getAdminStats, getAllUsers, updateUserRole } from '@/lib/api';
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

  const loadData = useCallback(async () => {
    try {
      const [statsData, usersData] = await Promise.all([
        getAdminStats(),
        getAllUsers()
      ]);
      setStats(statsData);
      setUsers(usersData);
    } catch (error) {
      // Nếu không có quyền admin (403), văng về dashboard
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const toggleRole = async (userId: number, currentRole: boolean) => {
    try {
      await updateUserRole(userId, !currentRole);
      setUsers(users.map(u => u.id === userId ? { ...u, is_admin: !currentRole } : u));
    } catch (error: unknown) {
      if (error instanceof Error) {
        alert(error.message || 'Lỗi khi cập nhật quyền');
      } else {
        alert('Lỗi khi cập nhật quyền');
      }
    }
  };

  if (loading) return <div style={{ padding: '2rem' }}>Đang tải dữ liệu...</div>;
  if (!stats) return null;

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Tổng quan Hệ thống</h1>
        <p className={styles.subtitle}>Theo dõi các chỉ số quan trọng của LearnAI</p>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{stats.total_users}</div>
          <div className={styles.statLabel}>Học viên</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{stats.total_subjects}</div>
          <div className={styles.statLabel}>Môn học</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{stats.total_topics}</div>
          <div className={styles.statLabel}>Chủ đề</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{stats.total_questions}</div>
          <div className={styles.statLabel}>Câu hỏi AI</div>
        </div>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Quản lý Người Dùng</h2>
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
                    {user.is_admin ? 'Admin' : 'Học viên'}
                  </span>
                </td>
                <td>
                  {user.username !== 'admin' && ( // Không cho phép đổi quyền tài khoản root
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
    </div>
  );
}
