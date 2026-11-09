'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  getMe,
  getAdminStats,
  getAllUsers,
  updateUserRole,
  assignTeacher,
  getAdminQuestions,
  createAdminQuestion,
  updateAdminQuestion,
  deleteAdminQuestion,
  deleteAdminUser,
  getSubjects,
  getTopics,
  getAlgorithmConfig,
  updateAlgorithmConfig,
  triggerAdminSeed,
  getStoredAccessToken,
  QuestionData,
  UserProfile,
  SubjectItem,
  TopicItem,
  AlgorithmConfig,
} from '@/lib/api';
import { getBloomLabel } from '@/lib/utils';
import MathText from '@/components/ui/MathText';
import styles from './admin.module.css';

interface AdminStats {
  total_users: number;
  total_subjects: number;
  total_topics: number;
  total_questions: number;
}

const EMPTY_QUESTION_FORM: QuestionData = {
  topic_id: 1,
  question_text: '',
  option_a: '',
  option_b: '',
  option_c: '',
  option_d: '',
  correct_answer: 'a',
  explanation: '',
  difficulty_elo: 1350,
  bloom_level: 2,
};

export default function AdminDashboard() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [questions, setQuestions] = useState<
    Array<QuestionData & { id: number; created_by_id: number | null }>
  >([]);
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [algoConfig, setAlgoConfig] = useState<AlgorithmConfig>({
    k_learner: 32,
    k_item: 16,
    zpd_lower_prob: 0.6,
    zpd_upper_prob: 0.75,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'users' | 'quizzes' | 'config'>('users');

  // Filters
  const [userSearch, setUserSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | 'student' | 'teacher' | 'admin'>('all');
  const [questionSearch, setQuestionSearch] = useState('');

  // Question CRUD Modal/Drawer state
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [editingQuestionId, setEditingQuestionId] = useState<number | null>(null);
  const [qForm, setQForm] = useState<QuestionData>(EMPTY_QUESTION_FORM);
  const [savingQuestion, setSavingQuestion] = useState(false);
  const [statusBanner, setStatusBanner] = useState<string>('');

  const loadData = useCallback(async () => {
    const activeToken = getStoredAccessToken();
    if (!activeToken) {
      router.push('/admin/login');
      return;
    }

    try {
      const me = await getMe(activeToken);
      if (me.role !== 'admin' && me.role !== 'teacher') {
        router.push('/admin/login');
        return;
      }
      setCurrentUser(me);

      const [statsData, usersData, questionsData, subjData, cfgData] = await Promise.all([
        getAdminStats(activeToken),
        getAllUsers(activeToken),
        getAdminQuestions(activeToken),
        getSubjects(),
        getAlgorithmConfig(activeToken).catch(() => ({
          k_learner: 32,
          k_item: 16,
          zpd_lower_prob: 0.6,
          zpd_upper_prob: 0.75,
        })),
      ]);
      setStats(statsData);
      setUsers(usersData);
      setQuestions(questionsData);
      setSubjects(subjData);
      setAlgoConfig(cfgData);

      // Load all topics across subjects for the Question Bank selector
      const topicLists = await Promise.all(
        subjData.map((s) => getTopics(s.id).catch(() => [] as TopicItem[]))
      );
      const allTopics = topicLists.flat();
      setTopics(allTopics);
      if (allTopics.length > 0) {
        setQForm((prev) => ({ ...prev, topic_id: allTopics[0].id }));
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Lỗi không xác định';
      if (message.includes('401') || message.includes('Token') || message.includes('403')) {
        router.push('/admin/login');
      } else {
        setError(`Lỗi kết nối API: ${message}`);
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void Promise.resolve().then(() => loadData());
  }, [loadData]);

  const handleChangeRole = async (userId: number, newRole: string) => {
    try {
      const token = getStoredAccessToken() || undefined;
      await updateUserRole(userId, newRole, token);
      setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u)));
      setStatusBanner(`✅ Đã cập nhật vai trò người dùng #${userId} thành ${newRole}`);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi cập nhật quyền');
    }
  };

  const handleAssignTeacher = async (userId: number, teacherIdStr: string) => {
    try {
      const token = getStoredAccessToken() || undefined;
      const teacherId = teacherIdStr ? parseInt(teacherIdStr, 10) : null;
      await assignTeacher(userId, teacherId, token);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, teacher_id: teacherId } : u))
      );
      setStatusBanner(`✅ Đã phân công giảng viên cho học viên #${userId}`);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi phân công giảng viên');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    try {
      const token = getStoredAccessToken() || undefined;
      await deleteAdminUser(userId, token);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
      if (stats) {
        setStats({ ...stats, total_users: Math.max(0, stats.total_users - 1) });
      }
      setStatusBanner(`🗑️ Đã xóa tài khoản #${userId}`);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi xóa người dùng');
    }
  };

  const handleOpenCreateQuestion = () => {
    setEditingQuestionId(null);
    setQForm({
      ...EMPTY_QUESTION_FORM,
      topic_id: topics[0]?.id || 1,
    });
    setShowQuestionForm(true);
  };

  const handleOpenEditQuestion = (
    q: QuestionData & { id: number; created_by_id: number | null }
  ) => {
    setEditingQuestionId(q.id);
    setQForm({
      topic_id: q.topic_id,
      question_text: q.question_text,
      option_a: q.option_a,
      option_b: q.option_b,
      option_c: q.option_c,
      option_d: q.option_d,
      correct_answer: q.correct_answer,
      explanation: q.explanation || '',
      difficulty_elo: q.difficulty_elo,
      bloom_level: q.bloom_level,
    });
    setShowQuestionForm(true);
  };

  const handleSaveQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingQuestion(true);
    try {
      const token = getStoredAccessToken() || undefined;
      if (editingQuestionId !== null) {
        const updated = await updateAdminQuestion(editingQuestionId, qForm, token);
        setQuestions((prev) => prev.map((q) => (q.id === editingQuestionId ? updated : q)));
        setStatusBanner(`✅ Đã cập nhật câu hỏi #${editingQuestionId}`);
      } else {
        const created = await createAdminQuestion(qForm, token);
        setQuestions((prev) => [created, ...prev]);
        if (stats) {
          setStats({ ...stats, total_questions: stats.total_questions + 1 });
        }
        setStatusBanner(`✅ Đã thêm câu hỏi mới #${created.id}`);
      }
      setShowQuestionForm(false);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi lưu câu hỏi');
    } finally {
      setSavingQuestion(false);
    }
  };

  const handleDeleteQuestion = async (qId: number) => {
    try {
      const token = getStoredAccessToken() || undefined;
      await deleteAdminQuestion(qId, token);
      setQuestions((prev) => prev.filter((q) => q.id !== qId));
      if (stats) {
        setStats({ ...stats, total_questions: Math.max(0, stats.total_questions - 1) });
      }
      setStatusBanner(`🗑️ Đã xóa câu hỏi #${qId}`);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi xóa câu hỏi');
    }
  };

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = getStoredAccessToken() || undefined;
      const saved = await updateAlgorithmConfig(algoConfig, token);
      setAlgoConfig(saved);
      setStatusBanner('✅ Đã lưu cấu hình thuật toán Dual Elo & ZPD thành công!');
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi cập nhật cấu hình');
    }
  };

  const handleTriggerSeed = async () => {
    try {
      const token = getStoredAccessToken() || undefined;
      const res = await triggerAdminSeed(token);
      setStatusBanner(
        `✅ ${res.message} (${res.summary.subjects} môn, ${res.summary.topics} chủ đề, ${res.summary.questions} câu hỏi)`
      );
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Lỗi đồng bộ dữ liệu mẫu');
    }
  };

  if (loading) {
    return (
      <div className={styles.loadingPage}>
        <div className={styles.spinner}></div>
        <p>Đang kiểm tra quyền truy cập RBAC...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorPage}>
        <h2>⚠️ Lỗi</h2>
        <p>{error}</p>
        <button
          onClick={() => {
            setError('');
            setLoading(true);
            void loadData();
          }}
          className={styles.retryBtn}
        >
          🔄 Thử lại
        </button>
      </div>
    );
  }

  if (!stats || !currentUser) return null;

  const teachers = users.filter((u) => u.role === 'teacher' || u.role === 'admin');
  const topicNameById: Record<number, string> = {};
  for (const t of topics) {
    const subj = subjects.find((s) => s.id === t.subject_id);
    topicNameById[t.id] = `${subj ? subj.icon_emoji + ' ' : ''}${t.name}`;
  }

  const filteredUsers = users.filter((u) => {
    const matchesRole = roleFilter === 'all' || u.role === roleFilter;
    const matchesSearch =
      u.username.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email.toLowerCase().includes(userSearch.toLowerCase());
    return matchesRole && matchesSearch;
  });

  const filteredQuestions = questions.filter((q) =>
    q.question_text.toLowerCase().includes(questionSearch.toLowerCase())
  );

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Trung tâm Quản trị & Học thuật Nyvora</h1>
        <p className={styles.subtitle}>
          Xin chào, <strong>{currentUser.username}</strong> (
          {currentUser.role === 'admin' ? '🛡️ Quản trị viên Toàn hệ thống' : '👨‍🏫 Giảng viên Hướng dẫn'})
        </p>
      </div>

      {statusBanner && (
        <div className="mb-6 p-3.5 rounded-xl bg-indigo-500/15 border border-indigo-500/40 text-indigo-200 text-sm flex items-center justify-between">
          <span>{statusBanner}</span>
          <button
            type="button"
            onClick={() => setStatusBanner('')}
            className="text-xs text-slate-400 hover:text-white cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>👥</div>
          <div className={styles.statValue}>{stats.total_users}</div>
          <div className={styles.statLabel}>Tài khoản quản lý</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>📚</div>
          <div className={styles.statValue}>{stats.total_subjects}</div>
          <div className={styles.statLabel}>Môn học chuẩn NCKH</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>📋</div>
          <div className={styles.statValue}>{stats.total_topics}</div>
          <div className={styles.statLabel}>Chủ đề (6 bậc Bloom)</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>❓</div>
          <div className={styles.statValue}>{stats.total_questions}</div>
          <div className={styles.statLabel}>Ngân hàng Câu hỏi</div>
        </div>
      </div>

      <div className={styles.tabs}>
        <button
          className={`${styles.tabBtn} ${activeTab === 'users' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👥 Quản lý Người dùng & Phân quyền ({users.length})
        </button>
        <button
          className={`${styles.tabBtn} ${activeTab === 'quizzes' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('quizzes')}
        >
          📝 Ngân hàng Câu hỏi LaTeX ({questions.length})
        </button>
        {currentUser.role === 'admin' && (
          <button
            className={`${styles.tabBtn} ${activeTab === 'config' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('config')}
          >
            ⚙️ Cấu hình Thuật toán Elo/ZPD
          </button>
        )}
      </div>

      <div className={styles.section}>
        {/* TAB 1: USERS & RBAC */}
        {activeTab === 'users' && (
          <>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
              <h2 className={styles.sectionTitle} style={{ marginBottom: 0 }}>
                Danh sách Tài khoản & Phân công Giảng viên
              </h2>
              <div className="flex flex-wrap items-center gap-2">
                <input
                  type="text"
                  placeholder="Tìm kiếm username, email..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-[#0d0d14] border border-[#252538] text-sm text-white"
                />
                <select
                  value={roleFilter}
                  onChange={(e) =>
                    setRoleFilter(e.target.value as 'all' | 'student' | 'teacher' | 'admin')
                  }
                  className={styles.roleSelect}
                >
                  <option value="all">Tất cả vai trò</option>
                  <option value="student">Học viên</option>
                  <option value="teacher">Giảng viên</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>

            {filteredUsers.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>Không tìm thấy người dùng phù hợp.</p>
            ) : (
              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Tài khoản</th>
                      <th>Điểm Elo</th>
                      <th>Vai trò RBAC</th>
                      {currentUser.role === 'admin' && <th>Giảng viên hướng dẫn</th>}
                      {currentUser.role === 'admin' && <th>Thao tác</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((u) => (
                      <tr key={u.id}>
                        <td className="font-mono">#{u.id}</td>
                        <td>
                          <div className="font-semibold text-white">{u.username}</div>
                          <div className="text-xs text-slate-400">{u.email}</div>
                        </td>
                        <td className="font-mono text-cyan-300 font-semibold">
                          {Math.round(u.overall_elo)}
                        </td>
                        <td>
                          <span
                            className={
                              u.role === 'admin'
                                ? styles.badgeAdmin
                                : u.role === 'teacher'
                                ? styles.badgeTeacher
                                : styles.badgeUser
                            }
                          >
                            {u.role === 'admin'
                              ? '🛡️ Admin'
                              : u.role === 'teacher'
                              ? '👨‍🏫 Giảng viên'
                              : '👤 Học viên'}
                          </span>
                        </td>
                        {currentUser.role === 'admin' && (
                          <td>
                            {u.role === 'student' ? (
                              <select
                                value={u.teacher_id ?? ''}
                                onChange={(e) => handleAssignTeacher(u.id, e.target.value)}
                                className={styles.roleSelect}
                              >
                                <option value="">-- Chưa gán --</option>
                                {teachers.map((t) => (
                                  <option key={t.id} value={t.id}>
                                    {t.username} (#{t.id})
                                  </option>
                                ))}
                              </select>
                            ) : (
                              <span className="text-xs text-slate-500">—</span>
                            )}
                          </td>
                        )}
                        {currentUser.role === 'admin' && (
                          <td>
                            {u.username !== currentUser.username && (
                              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                <select
                                  value={u.role}
                                  onChange={(e) => handleChangeRole(u.id, e.target.value)}
                                  className={styles.roleSelect}
                                >
                                  <option value="student">Học viên</option>
                                  <option value="teacher">Giảng viên</option>
                                  <option value="admin">Admin</option>
                                </select>
                                <button
                                  className={styles.deleteBtn}
                                  onClick={() => handleDeleteUser(u.id)}
                                >
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

        {/* TAB 2: QUESTION BANK CRUD + LIVE LATEX PREVIEW */}
        {activeTab === 'quizzes' && (
          <>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
              <h2 className={styles.sectionTitle} style={{ marginBottom: 0 }}>
                Ngân hàng Câu hỏi Thích ứng (Hỗ trợ LaTeX $...$ & Code)
              </h2>
              <div className="flex flex-wrap items-center gap-2">
                <input
                  type="text"
                  placeholder="Tìm nội dung câu hỏi..."
                  value={questionSearch}
                  onChange={(e) => setQuestionSearch(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-[#0d0d14] border border-[#252538] text-sm text-white"
                />
                <button className={styles.actionBtn} onClick={handleOpenCreateQuestion}>
                  + Tạo Câu hỏi Mới
                </button>
              </div>
            </div>

            {showQuestionForm && (
              <form
                onSubmit={handleSaveQuestion}
                className="mb-8 p-6 rounded-2xl bg-[#0d0d14] border border-indigo-500/40 space-y-4"
              >
                <div className="flex items-center justify-between border-b border-[#252538] pb-3">
                  <h3 className="text-lg font-bold text-white">
                    {editingQuestionId !== null
                      ? `✏️ Chỉnh sửa Câu hỏi #${editingQuestionId}`
                      : '✨ Tạo Câu hỏi Trắc nghiệm Chuẩn NCKH'}
                  </h3>
                  <button
                    type="button"
                    onClick={() => setShowQuestionForm(false)}
                    className="text-sm text-slate-400 hover:text-white cursor-pointer"
                  >
                    Đóng ✕
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Chủ đề học tập</label>
                    <select
                      value={qForm.topic_id}
                      onChange={(e) =>
                        setQForm({ ...qForm, topic_id: parseInt(e.target.value, 10) })
                      }
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                    >
                      {topics.map((t) => (
                        <option key={t.id} value={t.id}>
                          {topicNameById[t.id] || t.name} (Bloom {t.bloom_level})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">
                      Độ khó khởi tạo Elo (800 – 2400)
                    </label>
                    <input
                      type="number"
                      min={600}
                      max={2600}
                      step={10}
                      value={qForm.difficulty_elo}
                      onChange={(e) =>
                        setQForm({ ...qForm, difficulty_elo: parseFloat(e.target.value) || 1500 })
                      }
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white font-mono"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">
                      Cấp độ Nhận thức Bloom (1–6)
                    </label>
                    <select
                      value={qForm.bloom_level}
                      onChange={(e) =>
                        setQForm({ ...qForm, bloom_level: parseInt(e.target.value, 10) })
                      }
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                    >
                      {[1, 2, 3, 4, 5, 6].map((lvl) => (
                        <option key={lvl} value={lvl}>
                          Bậc {lvl}: {getBloomLabel(lvl)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Nội dung câu hỏi (Dùng `$công_thức$` cho LaTeX hoặc `` `code` `` cho mã nguồn)
                  </label>
                  <textarea
                    rows={3}
                    value={qForm.question_text}
                    onChange={(e) => setQForm({ ...qForm, question_text: e.target.value })}
                    placeholder="Ví dụ: Tính đạo hàm của hàm số $f(x) = x^3 - 3x + 1$ tại $x = 2$"
                    className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                    required
                  />
                </div>

                {/* Live LaTeX & Code Preview */}
                {qForm.question_text && (
                  <div className="p-3.5 rounded-xl bg-[#141422] border border-cyan-500/30">
                    <div className="text-xs font-mono text-cyan-400 mb-1">
                      👁️ Xem trước hiển thị KaTeX & Code:
                    </div>
                    <div className="text-sm text-white">
                      <MathText content={qForm.question_text} block />
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Đáp án A</label>
                    <input
                      type="text"
                      value={qForm.option_a}
                      onChange={(e) => setQForm({ ...qForm, option_a: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Đáp án B</label>
                    <input
                      type="text"
                      value={qForm.option_b}
                      onChange={(e) => setQForm({ ...qForm, option_b: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Đáp án C</label>
                    <input
                      type="text"
                      value={qForm.option_c}
                      onChange={(e) => setQForm({ ...qForm, option_c: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Đáp án D</label>
                    <input
                      type="text"
                      value={qForm.option_d}
                      onChange={(e) => setQForm({ ...qForm, option_d: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Đáp án Đúng</label>
                    <select
                      value={qForm.correct_answer}
                      onChange={(e) => setQForm({ ...qForm, correct_answer: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white font-bold uppercase"
                    >
                      <option value="a">Đáp án A</option>
                      <option value="b">Đáp án B</option>
                      <option value="c">Đáp án C</option>
                      <option value="d">Đáp án D</option>
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-xs text-slate-400 mb-1">
                      Lời giải thích khoa học (Hiển thị sau khi học sinh nộp bài)
                    </label>
                    <input
                      type="text"
                      value={qForm.explanation || ''}
                      onChange={(e) => setQForm({ ...qForm, explanation: e.target.value })}
                      placeholder="Giải thích công thức hoặc quy tắc..."
                      className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-sm text-white"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowQuestionForm(false)}
                    className="px-4 py-2 rounded-lg bg-white/5 text-slate-300 text-sm cursor-pointer"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    disabled={savingQuestion}
                    className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold cursor-pointer"
                  >
                    {savingQuestion ? 'Đang lưu...' : '💾 Lưu Câu hỏi'}
                  </button>
                </div>
              </form>
            )}

            {filteredQuestions.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>Không có câu hỏi nào.</p>
            ) : (
              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Chủ đề</th>
                      <th>Nội dung câu hỏi (Render LaTeX)</th>
                      <th>Độ khó Elo</th>
                      <th>Bloom</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredQuestions.map((q) => (
                      <tr key={q.id}>
                        <td className="font-mono">#{q.id}</td>
                        <td className="text-xs text-slate-300">
                          {topicNameById[q.topic_id] || `Topic #${q.topic_id}`}
                        </td>
                        <td style={{ maxWidth: '420px' }}>
                          <div className="text-sm text-white line-clamp-2">
                            <MathText content={q.question_text} />
                          </div>
                        </td>
                        <td className="font-mono text-cyan-300">{Math.round(q.difficulty_elo)}</td>
                        <td>
                          <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                            Bậc {q.bloom_level}: {getBloomLabel(q.bloom_level)}
                          </span>
                        </td>
                        <td>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => handleOpenEditQuestion(q)}
                              className="px-2.5 py-1 rounded bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 text-xs font-semibold cursor-pointer"
                            >
                              Sửa
                            </button>
                            <button
                              type="button"
                              className={styles.deleteBtn}
                              onClick={() => handleDeleteQuestion(q.id)}
                            >
                              Xóa
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}

        {/* TAB 3: ALGORITHM CONFIG & SEED DB */}
        {activeTab === 'config' && currentUser.role === 'admin' && (
          <div className="space-y-8">
            <div>
              <h2 className={styles.sectionTitle}>
                ⚙️ Cấu hình Tham số Toán học Dual Elo & Vùng ZPD
              </h2>
              <form
                onSubmit={handleSaveConfig}
                className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-3xl"
              >
                <div className="p-4 rounded-xl bg-[#0d0d14] border border-[#252538]">
                  <label className="block text-xs text-slate-400 mb-1">
                    Hệ số $K_L$ khởi tạo cho Học viên (`k_learner`)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="4"
                    max="128"
                    value={algoConfig.k_learner}
                    onChange={(e) =>
                      setAlgoConfig({ ...algoConfig, k_learner: parseFloat(e.target.value) || 32 })
                    }
                    className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-white font-mono"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Mặc định: 32.0 cho học viên mới, tự động co giãn về 16.0 khi ổn định.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-[#0d0d14] border border-[#252538]">
                  <label className="block text-xs text-slate-400 mb-1">
                    Hệ số $K_I$ hiệu chuẩn Độ khó Câu hỏi (`k_item`)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="2"
                    max="64"
                    value={algoConfig.k_item}
                    onChange={(e) =>
                      setAlgoConfig({ ...algoConfig, k_item: parseFloat(e.target.value) || 16 })
                    }
                    className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-white font-mono"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Mặc định: 16.0 để độ khó ngân hàng câu hỏi hội tụ ổn định.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-[#0d0d14] border border-[#252538]">
                  <label className="block text-xs text-slate-400 mb-1">
                    Ngưỡng xác suất ZPD dưới (`zpd_lower_prob`)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.35"
                    max="0.75"
                    value={algoConfig.zpd_lower_prob}
                    onChange={(e) =>
                      setAlgoConfig({
                        ...algoConfig,
                        zpd_lower_prob: parseFloat(e.target.value) || 0.6,
                      })
                    }
                    className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-white font-mono"
                  />
                </div>

                <div className="p-4 rounded-xl bg-[#0d0d14] border border-[#252538]">
                  <label className="block text-xs text-slate-400 mb-1">
                    Ngưỡng xác suất ZPD trên (`zpd_upper_prob`)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.60"
                    max="0.90"
                    value={algoConfig.zpd_upper_prob}
                    onChange={(e) =>
                      setAlgoConfig({
                        ...algoConfig,
                        zpd_upper_prob: parseFloat(e.target.value) || 0.75,
                      })
                    }
                    className="w-full px-3 py-2 rounded-lg bg-[#141422] border border-[#252538] text-white font-mono"
                  />
                </div>

                <div className="md:col-span-2">
                  <button type="submit" className={styles.actionBtn}>
                    💾 Lưu Cấu hình Thuật toán
                  </button>
                </div>
              </form>
            </div>

            <div className="pt-6 border-t border-[#252538]">
              <h3 className="text-base font-bold text-white mb-2">
                🌱 Đồng bộ Ngân hàng Dữ liệu Mẫu NCKH (Seed Database)
              </h3>
              <p className="text-sm text-slate-400 mb-4">
                Đảm bảo cơ sở dữ liệu có đủ 3 môn học, 12 chủ đề trải dài 6 cấp độ Bloom, 120 câu
                hỏi tích hợp công thức LaTeX & Code cùng 4 tài khoản RBAC mẫu.
              </p>
              <button
                type="button"
                onClick={handleTriggerSeed}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition cursor-pointer"
              >
                🔄 Kiểm tra & Đồng bộ 120 Câu hỏi Chuẩn NCKH
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
