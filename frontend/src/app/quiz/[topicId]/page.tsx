'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { startQuiz, submitAnswer } from '@/lib/api';
import styles from './quiz.module.css';

interface Question {
  id: number; question_text: string; option_a: string; option_b: string; option_c: string; option_d: string; difficulty_elo: number; bloom_level: number;
}
interface AnswerResult {
  is_correct: boolean; correct_answer: string; explanation: string; elo_change: number; new_elo: number; xp_earned: number;
}
interface QuizResult {
  question: Question; selected: string; result: AnswerResult; timeMs: number;
}

export default function QuizPage({ params }: { params: Promise<{ topicId: string }> }) {
  const { topicId } = use(params);
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [answerResult, setAnswerResult] = useState<AnswerResult | null>(null);
  const [results, setResults] = useState<QuizResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [startTime, setStartTime] = useState(Date.now());
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    startQuiz(parseInt(topicId), 10)
      .then((qs) => { setQuestions(qs); setStartTime(Date.now()); })
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false));
  }, [topicId, router]);

  const handleSelect = async (answer: string) => {
    if (selected || submitting) return;
    setSelected(answer);
    setSubmitting(true);

    const timeMs = Date.now() - startTime;
    try {
      const result = await submitAnswer(questions[currentIdx].id, answer, timeMs);
      setAnswerResult(result);
      setResults(prev => [...prev, { question: questions[currentIdx], selected: answer, result, timeMs }]);
    } catch {
      setAnswerResult({ is_correct: false, correct_answer: '?', explanation: 'Lỗi kết nối', elo_change: 0, new_elo: 0, xp_earned: 0 });
    }
    setSubmitting(false);
  };

  const handleNext = () => {
    if (currentIdx + 1 >= questions.length) {
      setFinished(true);
    } else {
      setCurrentIdx(prev => prev + 1);
      setSelected(null);
      setAnswerResult(null);
      setStartTime(Date.now());
    }
  };

  if (loading) return (
    <div className={styles.loadingPage}><div className={styles.spinner}></div><p>Đang tải câu hỏi...</p></div>
  );

  if (questions.length === 0) return (
    <div className={styles.loadingPage}><p>Không có câu hỏi nào cho chủ đề này</p><Link href="/dashboard" className={styles.backBtn}>← Quay lại</Link></div>
  );

  // Results Screen
  if (finished) {
    const correct = results.filter(r => r.result.is_correct).length;
    const totalEloChange = results.reduce((sum, r) => sum + r.result.elo_change, 0);
    return (
      <div className={styles.page}>
        <div className={styles.resultCard}>
          <h1 className={styles.resultTitle}>🎉 Hoàn thành!</h1>
          <div className={styles.scoreCircle}>
            <span className={styles.scoreNum}>{correct}</span>
            <span className={styles.scoreTotal}>/{results.length}</span>
          </div>
          <div className={styles.resultStats}>
            <div className={styles.resultStat}>
              <span className={styles.resultStatLabel}>Độ chính xác</span>
              <span className={styles.resultStatValue}>{Math.round(correct/results.length*100)}%</span>
            </div>
            <div className={styles.resultStat}>
              <span className={styles.resultStatLabel}>Elo thay đổi</span>
              <span className={styles.resultStatValue} style={{ color: totalEloChange >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                {totalEloChange >= 0 ? '+' : ''}{Math.round(totalEloChange)}
              </span>
            </div>
          </div>
          <div className={styles.resultList}>
            {results.map((r, i) => (
              <div key={i} className={`${styles.resultItem} ${r.result.is_correct ? styles.resultCorrect : styles.resultWrong}`}>
                <span className={styles.resultIcon}>{r.result.is_correct ? '✅' : '❌'}</span>
                <span className={styles.resultQ}>Câu {i+1}</span>
                <span className={styles.resultElo} style={{ color: r.result.elo_change >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                  {r.result.elo_change >= 0 ? '+' : ''}{Math.round(r.result.elo_change)}
                </span>
              </div>
            ))}
          </div>
          <Link href="/dashboard" className={styles.backBtn}>← Quay lại Dashboard</Link>
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
      {/* Header */}
      <div className={styles.quizHeader}>
        <Link href="/dashboard" className={styles.quizBack}>← Thoát</Link>
        <div className={styles.quizProgress}>
          <span className={styles.quizCounter}>Câu {currentIdx + 1}/{questions.length}</span>
          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${progress}%` }}></div>
          </div>
        </div>
      </div>

      {/* Question */}
      <div className={styles.quizBody}>
        <div className={styles.questionCard}>
          <div className={styles.questionMeta}>
            <span className={styles.bloomTag}>Bloom {q.bloom_level}</span>
            <span className={styles.eloTag}>Elo {Math.round(q.difficulty_elo)}</span>
          </div>
          <h2 className={styles.questionText}>{q.question_text}</h2>

          <div className={styles.options}>
            {options.map((opt) => {
              let optClass = styles.option;
              if (selected) {
                if (opt.key === answerResult?.correct_answer) optClass += ` ${styles.optionCorrect}`;
                else if (opt.key === selected && !answerResult?.is_correct) optClass += ` ${styles.optionWrong}`;
                else optClass += ` ${styles.optionDisabled}`;
              }
              return (
                <button key={opt.key} className={optClass} onClick={() => handleSelect(opt.key)} disabled={!!selected}>
                  <span className={styles.optionKey}>{opt.key.toUpperCase()}</span>
                  <span className={styles.optionText}>{opt.text}</span>
                </button>
              );
            })}
          </div>

          {/* Feedback */}
          {answerResult && (
            <div className={`${styles.feedback} ${answerResult.is_correct ? styles.feedbackCorrect : styles.feedbackWrong}`}>
              <div className={styles.feedbackHeader}>
                <span>{answerResult.is_correct ? '✅ Chính xác!' : '❌ Chưa đúng!'}</span>
                <span className={styles.eloChange} style={{ color: answerResult.elo_change >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                  Elo: {answerResult.elo_change >= 0 ? '+' : ''}{Math.round(answerResult.elo_change)} | +{answerResult.xp_earned} XP
                </span>
              </div>
              <p className={styles.explanation}>{answerResult.explanation}</p>
              <button className={styles.nextBtn} onClick={handleNext}>
                {currentIdx + 1 >= questions.length ? 'Xem kết quả →' : 'Câu tiếp theo →'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
