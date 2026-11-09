'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { startQuiz, submitAnswer, AnswerSubmissionResult } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { getBloomLabel } from '@/lib/utils';
import MathText from '@/components/ui/MathText';
import styles from './quiz.module.css';

interface Question {
  id: number;
  topic_id?: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  difficulty_elo: number;
  bloom_level: number;
}

interface QuizTurnRecord {
  question: Question;
  selected: string;
  result: AnswerSubmissionResult;
  timeMs: number;
  hintsUsed: number;
}

export default function QuizPage({ params }: { params: Promise<{ topicId: string }> }) {
  const { topicId } = use(params);
  const router = useRouter();
  const { user, refreshUser } = useAuth();

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [answerResult, setAnswerResult] = useState<AnswerSubmissionResult | null>(null);
  const [results, setResults] = useState<QuizTurnRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [finished, setFinished] = useState(false);

  // Timer & Socratic Hints
  const [elapsedSec, setElapsedSec] = useState(0);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [showHint, setShowHint] = useState(false);

  useEffect(() => {
    const numTopicId = parseInt(topicId, 10);
    if (Number.isNaN(numTopicId)) {
      router.replace('/dashboard');
      return;
    }

    startQuiz(numTopicId, 10)
      .then((q) => {
        setQuestions(q);
      })
      .catch(() => router.replace('/dashboard'))
      .finally(() => setLoading(false));
  }, [topicId, router]);

  useEffect(() => {
    if (loading || finished || selected) return;
    const timer = setInterval(() => {
      setElapsedSec((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [loading, finished, selected, currentIdx]);

  const handleRequestHint = () => {
    if (!showHint) {
      setShowHint(true);
      setHintsUsed((prev) => prev + 1);
    }
  };

  const handleSelect = async (answer: string) => {
    if (selected || submitting) return;
    setSelected(answer);
    setSubmitting(true);

    const timeMs = Math.max(1000, (elapsedSec + 1) * 1000);
    try {
      const result = await submitAnswer(questions[currentIdx].id, answer, timeMs, hintsUsed);
      setAnswerResult(result);
      setResults((prev) => [
        ...prev,
        { question: questions[currentIdx], selected: answer, result, timeMs, hintsUsed },
      ]);
      void refreshUser();
    } catch {
      setAnswerResult({
        is_correct: false,
        correct_answer: 'a',
        explanation: 'Không thể đồng bộ kết quả với máy chủ.',
        elo_change: 0,
        new_elo: user?.overall_elo || 1500,
        xp_earned: 0,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (currentIdx + 1 >= questions.length) {
      setFinished(true);
    } else {
      setCurrentIdx((prev) => prev + 1);
      setSelected(null);
      setAnswerResult(null);
      setHintsUsed(0);
      setShowHint(false);
      setElapsedSec(0);
    }
  };

  if (loading) {
    return (
      <div className={styles.loadingPage}>
        <div className={styles.spinner}></div>
        <p>Đang khởi tạo câu hỏi trong vùng phát triển gần nhất (ZPD)...</p>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className={styles.loadingPage}>
        <p>Không có câu hỏi nào cho chủ đề này</p>
        <Link href="/dashboard" className={styles.backBtn}>
          ← Quay lại Dashboard
        </Link>
      </div>
    );
  }

  if (finished) {
    const correct = results.filter((r) => r.result.is_correct).length;
    const totalEloChange = results.reduce((sum, r) => sum + r.result.elo_change, 0);
    const totalXp = results.reduce((sum, r) => sum + r.result.xp_earned, 0);
    return (
      <div className={styles.page}>
        <div className={styles.resultCard}>
          <h1 className={styles.resultTitle}>🎉 Hoàn thành Phiên Học Thích Ứng!</h1>
          <div className={styles.scoreCircle}>
            <span className={styles.scoreNum}>{correct}</span>
            <span className={styles.scoreTotal}>/{results.length}</span>
          </div>
          <div className={styles.resultStats}>
            <div className={styles.resultStat}>
              <span className={styles.resultStatLabel}>Độ chính xác</span>
              <span className={styles.resultStatValue}>
                {Math.round((correct / results.length) * 100)}%
              </span>
            </div>
            <div className={styles.resultStat}>
              <span className={styles.resultStatLabel}>Biến thiên Elo</span>
              <span
                className={styles.resultStatValue}
                style={{
                  color: totalEloChange >= 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                }}
              >
                {totalEloChange >= 0 ? '+' : ''}
                {Math.round(totalEloChange * 10) / 10}
              </span>
            </div>
            <div className={styles.resultStat}>
              <span className={styles.resultStatLabel}>Tổng XP nhận được</span>
              <span className={styles.resultStatValue} style={{ color: '#f59e0b' }}>
                +{totalXp} XP
              </span>
            </div>
          </div>
          <div className={styles.resultList}>
            {results.map((r, i) => (
              <div
                key={i}
                className={`${styles.resultItem} ${
                  r.result.is_correct ? styles.resultCorrect : styles.resultWrong
                }`}
              >
                <span className={styles.resultIcon}>{r.result.is_correct ? '✅' : '❌'}</span>
                <span className={styles.resultQ}>
                  Câu {i + 1} • Bloom {r.question.bloom_level} • {(r.timeMs / 1000).toFixed(1)}s
                </span>
                <span
                  className={styles.resultElo}
                  style={{
                    color: r.result.elo_change >= 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                  }}
                >
                  {r.result.elo_change >= 0 ? '+' : ''}
                  {Math.round(r.result.elo_change * 10) / 10} Elo
                </span>
              </div>
            ))}
          </div>
          <Link href="/dashboard" className={styles.backBtn}>
            ← Quay lại Dashboard & Xem Biểu Đồ Elo
          </Link>
        </div>
      </div>
    );
  }

  const q = questions[currentIdx];
  const options = [
    { key: 'a', text: q.option_a },
    { key: 'b', text: q.option_b },
    { key: 'c', text: q.option_c },
    { key: 'd', text: q.option_d },
  ];
  const progress = ((currentIdx + 1) / questions.length) * 100;

  return (
    <div className={styles.page}>
      {/* Distraction-free Header */}
      <div className={styles.quizHeader}>
        <Link href="/dashboard" className={styles.quizBack}>
          ← Thoát
        </Link>
        <div className={styles.quizProgress}>
          <div className="flex items-center justify-between w-full mb-1">
            <span className={styles.quizCounter}>
              Câu {currentIdx + 1}/{questions.length}
            </span>
            <span className="text-xs font-mono text-cyan-400">⏱️ {elapsedSec}s</span>
          </div>
          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${progress}%` }}></div>
          </div>
        </div>
      </div>

      {/* Question Card */}
      <div className={styles.quizBody}>
        <div className={styles.questionCard}>
          <div className={styles.questionMeta}>
            <span className={styles.bloomTag}>
              Bloom {q.bloom_level}: {getBloomLabel(q.bloom_level)}
            </span>
            <span className={styles.eloTag}>Độ khó Elo: {Math.round(q.difficulty_elo)}</span>
            {!selected && (
              <button
                type="button"
                onClick={handleRequestHint}
                className="ml-auto px-3 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs font-semibold transition cursor-pointer"
              >
                💡 Gợi ý Socratic {hintsUsed > 0 ? `(Đã mở)` : ''}
              </button>
            )}
          </div>

          {showHint && !selected && (
            <div className="mb-4 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs sm:text-sm text-amber-200">
              <strong>🧭 Gợi mở Socratic:</strong> Câu hỏi này ở mức nhận thức{' '}
              <em>{getBloomLabel(q.bloom_level)}</em>. Hãy phân tích kỹ các khái niệm cốt lõi hoặc
              thay thử giá trị biên vào biểu thức trước khi chọn đáp án!
            </div>
          )}

          <div className={styles.questionText}>
            <MathText content={q.question_text} block />
          </div>

          <div className={styles.options}>
            {options.map((opt) => {
              let optClass = styles.option;
              if (selected) {
                if (opt.key === answerResult?.correct_answer) optClass += ` ${styles.optionCorrect}`;
                else if (opt.key === selected && !answerResult?.is_correct)
                  optClass += ` ${styles.optionWrong}`;
                else optClass += ` ${styles.optionDisabled}`;
              }
              return (
                <button
                  key={opt.key}
                  className={optClass}
                  onClick={() => handleSelect(opt.key)}
                  disabled={!!selected}
                >
                  <span className={styles.optionKey}>{opt.key.toUpperCase()}</span>
                  <span className={styles.optionText}>
                    <MathText content={opt.text} />
                  </span>
                </button>
              );
            })}
          </div>

          {/* Real-time Dual Elo & SM-2 Feedback */}
          {answerResult && (
            <div
              className={`${styles.feedback} ${
                answerResult.is_correct ? styles.feedbackCorrect : styles.feedbackWrong
              }`}
            >
              <div className={styles.feedbackHeader}>
                <span>
                  {answerResult.is_correct
                    ? '✅ Chính xác! Tư duy rất sắc bén!'
                    : `❌ Chưa chính xác (Đáp án đúng: ${answerResult.correct_answer.toUpperCase()})`}
                </span>
                <span
                  className={styles.eloChange}
                  style={{
                    color: answerResult.elo_change >= 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                  }}
                >
                  Elo: {answerResult.elo_change >= 0 ? '+' : ''}
                  {Math.round(answerResult.elo_change * 10) / 10} (→ {Math.round(answerResult.new_elo)}) | +
                  {answerResult.xp_earned} XP
                </span>
              </div>
              {answerResult.explanation && (
                <div className={styles.explanation}>
                  <MathText content={answerResult.explanation} block />
                </div>
              )}
              <div className="flex flex-wrap items-center justify-between gap-2 mt-3 pt-3 border-t border-white/10 text-xs text-slate-400 font-mono">
                <span>
                  🧠 SM-2 Quality: q={answerResult.sm2_quality ?? 4}/5 • Chu kỳ ôn lại:{' '}
                  {answerResult.next_review_days ?? 1} ngày (EF={answerResult.easiness_factor ?? 2.5})
                </span>
                <button className={styles.nextBtn} onClick={handleNext}>
                  {currentIdx + 1 >= questions.length ? 'Xem tổng kết →' : 'Câu tiếp theo →'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
