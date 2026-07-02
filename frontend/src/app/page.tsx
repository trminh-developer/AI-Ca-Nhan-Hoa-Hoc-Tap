'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './page.module.css';

export default function LandingPage() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className={styles.page}>
      {/* Navbar */}
      <nav className={styles.navbar}>
        <div className={styles.navContent}>
          <Link href="/" className={styles.logo}>
            <span className={styles.logoIcon}>🧠</span>
            <span className={styles.logoText}>LearnAI</span>
          </Link>
          <div className={styles.navLinks}>
            <Link href="/login" className={styles.navBtn}>Đăng nhập</Link>
            <Link href="/register" className={styles.navBtnPrimary}>Bắt đầu miễn phí</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className={`${styles.hero} ${isVisible ? styles.heroVisible : ''}`}>
        <div className={styles.heroDecor}>
          <div className={styles.orb1}></div>
          <div className={styles.orb2}></div>
          <div className={styles.orb3}></div>
        </div>
        <div className={styles.heroContent}>
          <span className={styles.heroBadge}>🎓 Nền tảng học tập AI thế hệ mới</span>
          <h1 className={styles.heroTitle}>
            Học tập <span className={styles.gradientText}>thông minh</span> với AI
          </h1>
          <p className={styles.heroDesc}>
            Hệ thống tự động điều chỉnh nội dung theo năng lực của bạn. 
            Sử dụng thuật toán Elo Rating và Spaced Repetition để tối ưu hóa 
            quá trình học tập cá nhân.
          </p>
          <div className={styles.heroBtns}>
            <Link href="/register" className={styles.btnPrimary}>
              Bắt đầu học ngay →
            </Link>
            <Link href="/login" className={styles.btnSecondary}>
              Đã có tài khoản
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className={styles.features}>
        <h2 className={styles.sectionTitle}>Tính năng nổi bật</h2>
        <div className={styles.featureGrid}>
          {[
            { icon: '🧠', title: 'Cá nhân hóa theo năng lực', desc: 'Thuật toán Elo Rating đánh giá trình độ và đề xuất nội dung phù hợp trong Zone of Proximal Development (70-85% thành công).' },
            { icon: '🔄', title: 'Ôn tập thông minh', desc: 'SM-2 Spaced Repetition tự động lên lịch ôn tập tối ưu, giúp ghi nhớ lâu dài và hiệu quả.' },
            { icon: '📊', title: 'Theo dõi tiến độ', desc: 'Dashboard trực quan hiển thị Elo Rating, mức thành thạo từng chủ đề, và lịch sử học tập.' },
            { icon: '🤖', title: 'AI Tutor', desc: 'Chatbot AI giải đáp thắc mắc dựa trên tài liệu học, cung cấp gợi ý cá nhân hóa theo mức độ hiểu.' },
          ].map((f, i) => (
            <div key={i} className={styles.featureCard} style={{ animationDelay: `${i * 0.1}s` }}>
              <span className={styles.featureIcon}>{f.icon}</span>
              <h3 className={styles.featureTitle}>{f.title}</h3>
              <p className={styles.featureDesc}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className={styles.howItWorks}>
        <h2 className={styles.sectionTitle}>Cách hoạt động</h2>
        <div className={styles.steps}>
          {[
            { num: '01', title: 'Làm bài đánh giá', desc: 'Trả lời các câu hỏi để hệ thống đánh giá năng lực ban đầu của bạn.' },
            { num: '02', title: 'AI phân tích năng lực', desc: 'Thuật toán Elo tính toán trình độ và xác định điểm mạnh, điểm yếu.' },
            { num: '03', title: 'Học tập cá nhân hóa', desc: 'Nội dung tự động điều chỉnh theo trình độ, đảm bảo hiệu quả tối đa.' },
          ].map((s, i) => (
            <div key={i} className={styles.step}>
              <div className={styles.stepNum}>{s.num}</div>
              <h3 className={styles.stepTitle}>{s.title}</h3>
              <p className={styles.stepDesc}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className={styles.stats}>
        {[
          { value: '3+', label: 'Môn học' },
          { value: '60+', label: 'Câu hỏi' },
          { value: '6', label: 'Cấp độ Bloom' },
          { value: '∞', label: 'Cá nhân hóa' },
        ].map((s, i) => (
          <div key={i} className={styles.statItem}>
            <div className={styles.statValue}>{s.value}</div>
            <div className={styles.statLabel}>{s.label}</div>
          </div>
        ))}
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerLogo}>🧠 LearnAI</div>
          <p className={styles.footerText}>
            Đề tài NCKH: AI trong giáo dục — Cá nhân hóa nội dung học tập theo năng lực người học
          </p>
          <p className={styles.footerCopy}>© 2024 LearnAI. Nghiên cứu khoa học sinh viên.</p>
        </div>
      </footer>
    </div>
  );
}
