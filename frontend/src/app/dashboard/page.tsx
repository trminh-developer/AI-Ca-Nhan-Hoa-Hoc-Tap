'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getMe, getSubjects, getProgress } from '@/lib/api';
import { getEloTier, getBloomLabel } from '@/lib/utils';
import styles from './dashboard.module.css';

interface UserData {
  id: number; username: string; email: string; overall_elo: number; role: string; teacher_id: number | null;
}
interface Subject {
  id: number; name: string; icon_emoji: string; description: string;
}
interface MasteryItem {
  topic_id: number; topic_name: string; mastery_score: number; elo_rating: number; bloom_level: number; total_attempts: number; correct_attempts: number;
}
interface Progress {
  overall_elo: number; total_questions_answered: number; accuracy_rate: number; current_streak: number;
  topics_mastery: MasteryItem[];
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    Promise.all([getMe(), getSubjects(), getProgress()])
      .then(([u, s, p]) => { setUser(u); setSubjects(s); setProgress(p); })
      .catch(() => { localStorage.removeItem('token'); router.push('/login'); })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return (
    <div className={styles.loadingPage}>
      <div className={styles.spinner}></div>
      <p>Đang tải dữ liệu...</p>
    </div>
  );
  if (!user) return null;

  const tier = getEloTier(user.overall_elo);

  return (
    <div className={styles.page}>
      {/* Navbar */}
      <nav className={styles.navbar}>
        <div className={styles.navContent}>
          <Link href="/" className={styles.logo}>🧠 Nyvora</Link>
          <div className={styles.navRight}>
            <span className={styles.userInfo}>
              <span className={styles.tierBadge} style={{ background: tier.color }}>{tier.name}</span>
              {user.username}
            </span>
            <Link href="/profile" className={styles.logoutBtn} style={{ background: 'rgba(255,255,255,0.1)' }}>Hồ sơ</Link>
            {user.role === 'admin' && (
              <Link href="/admin" className={styles.logoutBtn} style={{ background: 'var(--color-primary)' }}>Admin</Link>
            )}
            <button className={styles.logoutBtn} onClick={() => { localStorage.removeItem('token'); router.push('/'); }}>
              Đăng xuất
            </button>
          </div>
        </div>
      </nav>

      <main className={styles.main}>
        {/* Welcome */}
        <section className={styles.welcome}>
          <h1>Xin chào, <span className={styles.gradientText}>{user.username}</span>! 👋</h1>
          <p className={styles.welcomeSub}>Tiếp tục hành trình học tập của bạn</p>
        </section>

        {/* Stats Cards */}
        <section className={styles.statsGrid}>
          {[
            { icon: '⚡', label: 'Elo Rating', value: Math.round(user.overall_elo), color: 'var(--accent-blue)' },
            { icon: '🎯', label: 'Độ chính xác', value: `${Math.round(progress?.accuracy_rate || 0)}%`, color: 'var(--accent-green)' },
            { icon: '📝', label: 'Câu đã trả lời', value: progress?.total_questions_answered || 0, color: 'var(--accent-purple)' },
            { icon: '🔥', label: 'Streak hiện tại', value: progress?.current_streak || 0, color: 'var(--accent-orange)' },
          ].map((s, i) => (
            <div key={i} className={styles.statCard}>
              <span className={styles.statIcon}>{s.icon}</span>
              <div className={styles.statValue} style={{ color: s.color }}>{s.value}</div>
              <div className={styles.statLabel}>{s.label}</div>
            </div>
          ))}
        </section>

        {/* Subjects */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>📚 Môn học</h2>
          <div className={styles.subjectGrid}>
            {subjects.map((s) => (
              <div key={s.id} className={styles.subjectCard}>
                <span className={styles.subjectIcon}>{s.icon_emoji}</span>
                <h3 className={styles.subjectName}>{s.name}</h3>
                <p className={styles.subjectDesc}>{s.description}</p>
                <Link href={`/quiz/${s.id}`} className={styles.startBtn}>
                  Bắt đầu học →
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* Topic Mastery */}
        {progress?.topics_mastery && progress.topics_mastery.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>📊 Mức thành thạo theo chủ đề</h2>
            <div className={styles.masteryGrid}>
              {progress.topics_mastery.map((m, i) => (
                <div key={i} className={styles.masteryCard}>
                  <div className={styles.masteryHeader}>
                    <span className={styles.masteryName}>{m.topic_name}</span>
                    <span className={styles.bloomBadge}>{getBloomLabel(m.bloom_level)}</span>
                  </div>
                  <div className={styles.progressBar}>
                    <div className={styles.progressFill} style={{ width: `${Math.round(m.mastery_score * 100)}%` }}></div>
                  </div>
                  <div className={styles.masteryStats}>
                    <span>Elo: {Math.round(m.elo_rating)}</span>
                    <span>{m.correct_attempts}/{m.total_attempts} đúng</span>
                    <span>{Math.round(m.mastery_score * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
