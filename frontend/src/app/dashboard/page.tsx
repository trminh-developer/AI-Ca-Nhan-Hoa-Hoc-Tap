'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  getSubjects,
  getTopics,
  getProgress,
  getDueSpacedReviews,
  submitSpacedReviewAnswer,
  SubjectItem,
  TopicItem,
  TopicMasteryItem,
  ProgressData,
  SpacedReviewCard,
  AnswerSubmissionResult,
} from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { getEloTier, getBloomLabel } from '@/lib/utils';
import MathText from '@/components/ui/MathText';
import styles from './dashboard.module.css';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading, logout, refreshUser } = useAuth();

  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [topicsBySubject, setTopicsBySubject] = useState<Record<number, TopicItem[]>>({});
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [dueCards, setDueCards] = useState<SpacedReviewCard[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [activeTab, setActiveTab] = useState<'zpd' | 'sm2'>('zpd');

  // SM-2 Flashcard interactive state
  const [cardIndex, setCardIndex] = useState(0);
  const [selectedOpt, setSelectedOpt] = useState<string | null>(null);
  const [reviewResult, setReviewResult] = useState<AnswerSubmissionResult | null>(null);
  const [submittingReview, setSubmittingReview] = useState(false);

  const loadDashboardData = useCallback(async () => {
    try {
      const [subjList, progData, dueList] = await Promise.all([
        getSubjects(),
        getProgress(),
        getDueSpacedReviews().catch(() => [] as SpacedReviewCard[]),
      ]);
      setSubjects(subjList);
      setProgress(progData);
      setDueCards(dueList);

      const topicEntries = await Promise.all(
        subjList.map(async (s) => {
          const t = await getTopics(s.id).catch(() => [] as TopicItem[]);
          return [s.id, t] as const;
        })
      );
      const map: Record<number, TopicItem[]> = {};
      for (const [sid, list] of topicEntries) {
        map[sid] = list;
      }
      setTopicsBySubject(map);
    } catch {
      // Nếu lỗi xác thực thì đẩy về trang login
      router.replace('/login');
    } finally {
      setLoadingData(false);
    }
  }, [router]);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace('/login');
      return;
    }
    void Promise.resolve().then(() => loadDashboardData());
  }, [authLoading, user, router, loadDashboardData]);

  const handleReviewAnswer = async (optKey: string) => {
    if (selectedOpt || submittingReview || !dueCards[cardIndex]) return;
    setSelectedOpt(optKey);
    setSubmittingReview(true);
    try {
      const res = await submitSpacedReviewAnswer(dueCards[cardIndex].id, optKey, 6000, 0);
      setReviewResult(res);
      await refreshUser();
      const updatedProg = await getProgress();
      setProgress(updatedProg);
    } catch {
      setReviewResult({
        is_correct: false,
        correct_answer: 'a',
        explanation: 'Không thể gửi kết quả ôn tập SM-2.',
        elo_change: 0,
        new_elo: user?.overall_elo || 1500,
        xp_earned: 0,
      });
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleNextReviewCard = () => {
    setSelectedOpt(null);
    setReviewResult(null);
    if (cardIndex + 1 < dueCards.length) {
      setCardIndex((prev) => prev + 1);
    } else {
      setDueCards([]);
      setCardIndex(0);
    }
  };

  if (authLoading || loadingData) {
    return (
      <div className={styles.loadingPage}>
        <div className={styles.spinner}></div>
        <p>Đang đồng bộ không gian học tập thích ứng Nyvora...</p>
      </div>
    );
  }

  if (!user) return null;

  const currentElo = progress?.overall_elo ?? user.overall_elo;
  const tier = getEloTier(currentElo);
  const zpdLow = Math.round(currentElo - 85);
  const zpdHigh = Math.round(currentElo + 170);
  const accuracyPct = Math.round((progress?.accuracy_rate || 0) * 100);

  const masteryByTopicId: Record<number, TopicMasteryItem> = {};
  for (const m of progress?.topics_mastery || []) {
    masteryByTopicId[m.topic_id] = m;
  }

  const eloChartData =
    progress?.elo_history && progress.elo_history.length > 0
      ? progress.elo_history
      : [{ index: 0, elo: Math.round(currentElo), change: 0, is_correct: true, timestamp: 'Hiện tại' }];

  const bloomChartData =
    progress?.bloom_radar && progress.bloom_radar.length > 0
      ? progress.bloom_radar
      : [
          { bloom_level: 1, level: 1, label: 'Nhớ', mastery_percent: 50, mastery: 50, unlocked: true, questions_attempted: 0 },
          { bloom_level: 2, level: 2, label: 'Hiểu', mastery_percent: 35, mastery: 35, unlocked: true, questions_attempted: 0 },
          { bloom_level: 3, level: 3, label: 'Áp dụng', mastery_percent: 20, mastery: 20, unlocked: false, questions_attempted: 0 },
          { bloom_level: 4, level: 4, label: 'Phân tích', mastery_percent: 10, mastery: 10, unlocked: false, questions_attempted: 0 },
          { bloom_level: 5, level: 5, label: 'Đánh giá', mastery_percent: 5, mastery: 5, unlocked: false, questions_attempted: 0 },
          { bloom_level: 6, level: 6, label: 'Sáng tạo', mastery_percent: 0, mastery: 0, unlocked: false, questions_attempted: 0 },
        ];

  const activeCard = dueCards[cardIndex];

  return (
    <div className={styles.page}>
      {/* Navbar */}
      <nav className={styles.navbar}>
        <div className={styles.navContent}>
          <Link href="/" className={styles.logo}>
            🧠 Nyvora
          </Link>
          <div className={styles.navRight}>
            <span className={styles.userInfo}>
              <span className={styles.tierBadge} style={{ background: tier.color }}>
                {tier.name} • {Math.round(currentElo)}
              </span>
              {user.username}
            </span>
            <Link
              href="/profile"
              className={styles.logoutBtn}
              style={{ background: 'rgba(255,255,255,0.08)' }}
            >
              Hồ sơ
            </Link>
            {(user.role === 'admin' || user.role === 'teacher') && (
              <Link
                href="/admin"
                className={styles.logoutBtn}
                style={{ background: 'var(--color-primary)' }}
              >
                {user.role === 'admin' ? '🛡️ Admin Hub' : '👨‍🏫 Giảng viên'}
              </Link>
            )}
            <button
              className={styles.logoutBtn}
              onClick={async () => {
                await logout();
                router.push('/');
              }}
            >
              Đăng xuất
            </button>
          </div>
        </div>
      </nav>

      <main className={styles.main}>
        {/* Welcome Banner */}
        <section className={styles.welcome}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1>
                Xin chào, <span className={styles.gradientText}>{user.username}</span>! 👋
              </h1>
              <p className={styles.welcomeSub}>
                Vùng phát triển gần nhất (ZPD 60%–75%): Độ khó câu hỏi tối ưu từ{' '}
                <span className="font-mono text-indigo-400 font-semibold">
                  {zpdLow} – {zpdHigh} Elo
                </span>
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setActiveTab('zpd')}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition cursor-pointer ${
                  activeTab === 'zpd'
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                    : 'bg-[#141422] text-slate-300 border border-[#252538]'
                }`}
              >
                🎯 Lộ trình ZPD ({subjects.length} môn)
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('sm2')}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition cursor-pointer flex items-center gap-2 ${
                  activeTab === 'sm2'
                    ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/30'
                    : 'bg-[#141422] text-slate-300 border border-[#252538]'
                }`}
              >
                🧠 Ôn tập SM-2
                <span className="px-2 py-0.5 rounded-full text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono">
                  {dueCards.length}
                </span>
              </button>
            </div>
          </div>
        </section>

        {/* Stats Cards */}
        <section className={styles.statsGrid}>
          {[
            {
              icon: '⚡',
              label: `Elo Rating (${tier.name})`,
              value: Math.round(currentElo),
              sub: `ZPD: ${zpdLow}..${zpdHigh}`,
              color: 'var(--accent-blue)',
            },
            {
              icon: '🎯',
              label: 'Độ chính xác tích lũy',
              value: `${accuracyPct}%`,
              sub: `${progress?.total_questions_answered || 0} lượt tương tác`,
              color: 'var(--accent-green)',
            },
            {
              icon: '🔥',
              label: 'Chuỗi đúng liên tiếp',
              value: progress?.current_streak || 0,
              sub: 'Flow State Streak',
              color: 'var(--accent-orange)',
            },
            {
              icon: '⏱️',
              label: 'Cần ôn tập hôm nay (SM-2)',
              value: dueCards.length,
              sub: 'Chống quên Ebbinghaus',
              color: 'var(--accent-purple)',
            },
          ].map((s, i) => (
            <div key={i} className={styles.statCard}>
              <span className={styles.statIcon}>{s.icon}</span>
              <div className={styles.statValue} style={{ color: s.color }}>
                {s.value}
              </div>
              <div className={styles.statLabel}>{s.label}</div>
              <div className="text-xs text-slate-500 mt-1 font-mono">{s.sub}</div>
            </div>
          ))}
        </section>

        {/* Analytics Charts: Elo History & Bloom Taxonomy Radar */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
          {/* Elo History Chart */}
          <div className="p-6 rounded-2xl bg-[#12121a] border border-[#222232]">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white">📈 Biến thiên Năng lực Dual Elo</h2>
                <p className="text-xs text-slate-400">
                  <MathText content="Cập nhật thời gian thực $O(1)$ theo mô hình $R_L^{(new)} = R_L + K_L(S - E_L)$" />
                </p>
              </div>
              <span className="px-2.5 py-1 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-xs font-mono text-indigo-300">
                Hiện tại: {Math.round(currentElo)}
              </span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={eloChartData}>
                  <defs>
                    <linearGradient id="eloGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.45} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222232" />
                  <XAxis dataKey="timestamp" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} domain={['auto', 'auto']} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      borderColor: '#2e2e42',
                      borderRadius: '12px',
                      color: '#f8fafc',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="elo"
                    stroke="#6366f1"
                    strokeWidth={2.5}
                    fill="url(#eloGradient)"
                    name="Điểm Elo"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bloom's Revised Taxonomy 6-Level Radar Chart */}
          <div className="p-6 rounded-2xl bg-[#12121a] border border-[#222232]">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white">
                  🧭 Thang đo Nhận thức Bloom (6 Cấp độ)
                </h2>
                <p className="text-xs text-slate-400">
                  <MathText content="Điều kiện mở khóa cấp độ $k$: đạt Mastery $\ge 70\%$ ở cấp độ $k-1$" />
                </p>
              </div>
              <span className="px-2.5 py-1 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-xs font-mono text-cyan-300">
                Bloom Radar
              </span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={bloomChartData}>
                  <PolarGrid stroke="#252538" />
                  <PolarAngleAxis dataKey="label" tick={{ fill: '#cbd5e1', fontSize: 11 }} />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    tick={{ fill: '#64748b', fontSize: 10 }}
                  />
                  <Radar
                    name="Mức thành thạo (%)"
                    dataKey="mastery_percent"
                    stroke="#06b6d4"
                    fill="#06b6d4"
                    fillOpacity={0.35}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      borderColor: '#2e2e42',
                      borderRadius: '12px',
                      color: '#f8fafc',
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* Tab 2: SM-2 Spaced Repetition Smart Flashcards */}
        {activeTab === 'sm2' && (
          <section className="mb-10 p-6 rounded-2xl bg-[#12121a] border border-cyan-500/30">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
              <div>
                <h2 className="text-xl font-bold text-white">
                  🧠 Hàng đợi Ôn tập Ngắt quãng SuperMemo-2 (SM-2)
                </h2>
                <p className="text-sm text-slate-400">
                  <MathText content="Công thức $EF^{(new)} = \max(1.3, EF + (0.1 - (5-q)(0.08 + (5-q)\cdot 0.02)))$ • Chống đường cong quên lãng Ebbinghaus" />
                </p>
              </div>
              <span className="px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-300 text-xs font-mono">
                {dueCards.length > 0
                  ? `Thẻ ${cardIndex + 1} / ${dueCards.length}`
                  : 'Đã hoàn thành hôm nay'}
              </span>
            </div>

            {!activeCard ? (
              <div className="p-8 rounded-xl bg-[#0d0d14] border border-[#222232] text-center">
                <div className="text-4xl mb-3">🎉</div>
                <h3 className="text-lg font-semibold text-white mb-1">
                  Tuyệt vời! Bạn đã hoàn tất toàn bộ thẻ nhớ SM-2 đến hạn hôm nay.
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  Hãy chuyển sang lộ trình ZPD để chinh phục các chủ đề mới và tích lũy thêm thẻ ôn tập dài hạn.
                </p>
                <button
                  type="button"
                  onClick={() => setActiveTab('zpd')}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition cursor-pointer"
                >
                  Chuyển sang Bài học Thử thách ZPD →
                </button>
              </div>
            ) : (
              <div className="p-6 rounded-xl bg-[#0d0d14] border border-[#252538]">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 text-xs font-semibold">
                      {activeCard.topic_name || `Chủ đề #${activeCard.topic_id}`}
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-amber-500/20 text-amber-300 text-xs font-mono">
                      {getBloomLabel(activeCard.bloom_level)}
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 text-xs font-mono">
                      Độ khó: {Math.round(activeCard.difficulty_elo)} Elo
                    </span>
                  </div>
                  <div className="text-xs font-mono text-cyan-300">
                    Lặp: {activeCard.repetitions} lần • Chu kỳ: {activeCard.interval_days} ngày • EF:{' '}
                    {activeCard.easiness_factor}
                  </div>
                </div>

                <div className="text-base sm:text-lg font-medium text-white mb-5 leading-relaxed">
                  <MathText content={activeCard.question_text} block />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    { key: 'a', val: activeCard.option_a },
                    { key: 'b', val: activeCard.option_b },
                    { key: 'c', val: activeCard.option_c },
                    { key: 'd', val: activeCard.option_d },
                  ].map((opt) => {
                    const isCorrect = reviewResult && opt.key === reviewResult.correct_answer;
                    const isWrongSelected =
                      reviewResult && selectedOpt === opt.key && !reviewResult.is_correct;
                    return (
                      <button
                        key={opt.key}
                        type="button"
                        disabled={Boolean(selectedOpt)}
                        onClick={() => handleReviewAnswer(opt.key)}
                        className={`p-3.5 rounded-xl border text-left transition flex items-start gap-3 cursor-pointer ${
                          isCorrect
                            ? 'bg-emerald-500/20 border-emerald-500 text-emerald-200'
                            : isWrongSelected
                            ? 'bg-rose-500/20 border-rose-500 text-rose-200'
                            : 'bg-[#141422] hover:bg-[#1b1b2e] border-[#252538] text-slate-200'
                        }`}
                      >
                        <span className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center font-mono text-xs font-bold uppercase shrink-0">
                          {opt.key}
                        </span>
                        <span className="text-sm leading-relaxed">
                          <MathText content={opt.val} />
                        </span>
                      </button>
                    );
                  })}
                </div>

                {reviewResult && (
                  <div className="mt-5 p-4 rounded-xl bg-[#141422] border border-[#2e2e42]">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <span className="font-bold text-sm">
                        {reviewResult.is_correct ? '✅ Ghi nhớ chính xác!' : '❌ Cần củng cố lại!'}
                      </span>
                      <span className="font-mono text-xs text-cyan-300">
                        Elo: {reviewResult.elo_change >= 0 ? '+' : ''}
                        {reviewResult.elo_change} • Chất lượng nhớ q={reviewResult.sm2_quality ?? 4} • Hẹn ôn lại sau{' '}
                        {reviewResult.next_review_days ?? 1} ngày (EF={reviewResult.easiness_factor ?? 2.5})
                      </span>
                    </div>
                    {reviewResult.explanation && (
                      <div className="text-sm text-slate-300 mb-3">
                        <MathText content={reviewResult.explanation} block />
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={handleNextReviewCard}
                      className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition cursor-pointer"
                    >
                      {cardIndex + 1 < dueCards.length ? 'Thẻ SM-2 tiếp theo →' : 'Hoàn tất phiên ôn tập ✓'}
                    </button>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {/* Tab 1: Subjects & Topics ZPD Curriculum */}
        {activeTab === 'zpd' && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>📚 Môn học & Lộ trình Chủ đề Thích ứng (ZPD)</h2>
            <div className="space-y-8">
              {subjects.map((s) => {
                const subjectTopics = topicsBySubject[s.id] || [];
                const firstTopicId = subjectTopics[0]?.id || s.id;
                return (
                  <div
                    key={s.id}
                    className="p-6 rounded-2xl bg-[#12121a] border border-[#222232] shadow-lg"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-5 mb-5 border-b border-[#222232]">
                      <div className="flex items-start gap-4">
                        <span className="text-4xl">{s.icon_emoji}</span>
                        <div>
                          <h3 className="text-xl font-bold text-white">{s.name}</h3>
                          <p className="text-sm text-slate-400 mt-1">{s.description}</p>
                        </div>
                      </div>
                      <Link
                        href={`/quiz/${firstTopicId}`}
                        className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition shrink-0 text-center"
                      >
                        ⚡ Luyện nhanh ZPD →
                      </Link>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {subjectTopics.map((topic) => {
                        const mastery = masteryByTopicId[topic.id];
                        const masteryPct = mastery ? Math.round(mastery.mastery_score * 100) : 0;
                        const topicElo = mastery ? Math.round(mastery.elo_rating) : 1500;
                        return (
                          <div
                            key={topic.id}
                            className="p-4 rounded-xl bg-[#0d0d14] border border-[#252538] hover:border-indigo-500/50 transition flex flex-col justify-between gap-3"
                          >
                            <div>
                              <div className="flex items-center justify-between gap-2 mb-1.5">
                                <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                                  Bloom {topic.bloom_level}: {getBloomLabel(topic.bloom_level)}
                                </span>
                                <span className="text-xs font-mono text-slate-400">
                                  {topic.question_count} câu hỏi • Elo {topicElo}
                                </span>
                              </div>
                              <h4 className="text-base font-bold text-white">{topic.name}</h4>
                              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                                {topic.description}
                              </p>
                            </div>

                            <div className="pt-2">
                              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                                <span>
                                  Mức thành thạo ({mastery?.correct_attempts || 0}/
                                  {mastery?.total_attempts || 0} đúng)
                                </span>
                                <span className="font-mono font-semibold text-cyan-300">
                                  {masteryPct}%
                                </span>
                              </div>
                              <div className="w-full h-2 rounded-full bg-[#1b1b2e] overflow-hidden mb-3">
                                <div
                                  className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-500"
                                  style={{ width: `${masteryPct}%` }}
                                />
                              </div>
                              <Link
                                href={`/quiz/${topic.id}`}
                                className="block w-full py-2 rounded-lg bg-white/5 hover:bg-indigo-600 text-slate-200 hover:text-white text-xs font-semibold text-center border border-white/10 hover:border-indigo-500 transition"
                              >
                                Vào phòng Quiz Thích ứng ZPD →
                              </Link>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
