/* eslint-disable */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { 
  getMe, getAdminStats, getAllUsers, updateUserRole, assignTeacher,
  getAdminQuestions, deleteAdminQuestion, deleteAdminUser, QuestionData
} from '@/lib/api';
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
  role: string;
  teacher_id: number | null;
  created_at: string;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [questions, setQuestions] = useState<(QuestionData & { id: number, created_by_id: number | null })[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'users' | 'quizzes'>('users');

  const loadData = useCallback(async () => {
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) {
      router.push('/admin/login');
      return;
    }

    try {
      const me = await getMe(adminToken);
      if (me.role !== 'admin' && me.role !== 'teacher') {
        router.push('/admin/login');
        return;
      }
      setCurrentUser(me);

      const [statsData, usersData, questionsData] = await Promise.all([
        getAdminStats(adminToken),
        getAllUsers(adminToken),
        getAdminQuestions(adminToken)
      ]);
      setStats(statsData);
      setUsers(usersData);
      setQuestions(questionsData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Lỗi không xác định';
      if (message.includes('401') || message.includes('Token') || message.includes('403')) {
        localStorage.removeItem('admin_token');
        router.push('/admin/login');
      } else {
        setError(`Lỗi kết nối API: ${message}`);
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const handleChangeRole = async (userId: number, newRole: string) => {
    try {
      const adminToken = localStorage.getItem('admin_token') || undefined;
      await updateUserRole(userId, newRole, adminToken);
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi cập nhật quyền');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Bạn có chắc chắn muốn xóa người dùng này?')) return;
    try {
      const adminToken = localStorage.getItem('admin_token') || undefined;
      await deleteAdminUser(userId, adminToken);
      setUsers(users.filter(u => u.id !== userId));
      
      // Update stats manually
      if (stats) {
        setStats({
          ...stats,
          total_users: stats.total_users - 1
        });
      }
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi xóa người dùng');
    }
  };

  const handleDeleteQuestion = async (qId: number) => {
    if (!confirm('Bạn có chắc chắn muốn xóa câu hỏi này?')) return;
    try {
      const adminToken = localStorage.getItem('admin_token') || undefined;
      await deleteAdminQuestion(qId, adminToken);
      setQuestions(questions.filter(q => q.id !== qId));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi xóa câu hỏi');
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

  if (!stats || !currentUser) return null;

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Quản trị Hệ thống</h1>
        <p className={styles.subtitle}>
          Xin chào, {currentUser.username} ({currentUser.role === 'admin' ? '🛡️ Admin' : '👨‍🏫 Giảng Viên'})
        </p>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>👥</div>
          <div className={styles.statValue}>{stats.total_users}</div>
          <div className={styles.statLabel}>Học viên quản lý</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>❓</div>
          <div className={styles.statValue}>{stats.total_questions}</div>
          <div className={styles.statLabel}>Câu hỏi của bạn</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>📋</div>
          <div className={styles.statValue}>{stats.total_topics}</div>
          <div className={styles.statLabel}>Tổng Chủ đề (Hệ thống)</div>
        </div>
      </div>

      <div className={styles.tabs}>
        <button 
          className={`${styles.tabBtn} ${activeTab === 'users' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Quản lý Học Viên
        </button>
        <button 
          className={`${styles.tabBtn} ${activeTab === 'quizzes' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('quizzes')}
        >
          Quản lý Bài Quiz
        </button>
      </div>

      <div className={styles.section}>
        {activeTab === 'users' && (
          <>
            <h2 className={styles.sectionTitle}>Danh sách Người dùng</h2>
            {users.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>Không có dữ liệu.</p>
            ) : (
              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Tên đăng nhập</th>
                      <th>Phân quyền</th>
                      {currentUser.role === 'admin' && <th>Thao tác (Admin)</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(user => (
                      <tr key={user.id}>
                        <td>#{user.id}</td>
                        <td>{user.username}</td>
                        <td>
                          <span className={user.role === 'admin' ? styles.badgeAdmin : (user.role === 'teacher' ? styles.badgeTeacher : styles.badgeUser)}>
                            {user.role === 'admin' ? '🛡️ Admin' : (user.role === 'teacher' ? '👨‍🏫 Giảng viên' : '👤 Học viên')}
                          </span>
                        </td>
                        {currentUser.role === 'admin' && (
                          <td>
                            {user.username !== currentUser.username && (
                              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                <select 
                                  value={user.role} 
                                  onChange={(e) => handleChangeRole(user.id, e.target.value)}
                                  className={styles.roleSelect}
                                >
                                  <option value="student">Học viên</option>
                                  <option value="teacher">Giảng viên</option>
                                  <option value="admin">Admin</option>
                                </select>
                                <button className={styles.deleteBtn} onClick={() => handleDeleteUser(user.id)}>
                                  Xóa
                                </button>
                              </div>
                            )}
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}

        {activeTab === 'quizzes' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className={styles.sectionTitle}>Danh sách Câu hỏi / Quiz</h2>
              {/* Nút thêm câu hỏi (có thể phát triển form thêm mới sau) */}
              <button className={styles.actionBtn} onClick={() => alert('Tính năng Thêm mới đang hoàn thiện')}>
                + Thêm Câu hỏi
              </button>
            </div>
            
            {questions.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>Bạn chưa tạo câu hỏi nào.</p>
            ) : (
              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Nội dung</th>
                      <th>Độ khó (Elo)</th>
                      <th>Bloom</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {questions.map(q => (
                      <tr key={q.id}>
                        <td>#{q.id}</td>
                        <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {q.question_text}
                        </td>
                        <td>{q.difficulty_elo}</td>
                        <td>Mức {q.bloom_level}</td>
                        <td>
                          <button className={styles.deleteBtn} onClick={() => handleDeleteQuestion(q.id)}>
                            Xóa
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
