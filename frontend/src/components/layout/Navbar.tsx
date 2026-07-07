'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { getMe } from '@/lib/api';

interface UserData {
  id: number; username: string; email: string; overall_elo: number; created_at: string;
}
import { getEloTier, formatElo } from '@/lib/utils';
import styles from './Navbar.module.css';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<UserData | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('token');
          router.push('/login');
        });
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  const tier = user ? getEloTier(user.overall_elo) : null;

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/dashboard', label: 'Học tập', icon: '📚' },
    { href: '/dashboard', label: 'AI Tutor', icon: '🤖' },
  ];

  return (
    <nav className={`${styles.navbar} glass`}>
      <div className={`${styles.navContent} container`}>
        {/* Logo */}
        <a href="/dashboard" className={styles.logo}>
          <div style={{ width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img src="/logo.png" alt="LearnAI Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          </div>
          <span className={styles.logoText}>
            Learn<span className="gradient-text">AI</span>
          </span>
        </a>

        {/* Desktop Nav Links */}
        <div className={styles.navLinks}>
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className={`${styles.navLink} ${pathname === link.href ? styles.navLinkActive : ''}`}
            >
              <span className={styles.navLinkIcon}>{link.icon}</span>
              {link.label}
            </a>
          ))}
        </div>

        {/* User Section */}
        <div className={styles.userSection}>
          {user && tier && (
            <div className={styles.eloWrapper}>
              <span
                className={styles.eloBadge}
                style={{
                  background: tier.bgColor,
                  color: tier.color,
                  borderColor: tier.borderColor,
                }}
              >
                {tier.icon} {tier.name} — {formatElo(user.overall_elo)}
              </span>
            </div>
          )}

          {user && (
            <div className={styles.userInfo}>
              <div className={styles.avatar}>
                {user.username.charAt(0).toUpperCase()}
              </div>
              <span className={styles.username}>{user.username}</span>
            </div>
          )}

          <button onClick={handleLogout} className={`btn btn-ghost ${styles.logoutBtn}`}>
            Đăng xuất
          </button>

          {/* Mobile Hamburger */}
          <button
            className={styles.hamburger}
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Menu"
          >
            <span className={`${styles.hamburgerLine} ${menuOpen ? styles.open : ''}`} />
            <span className={`${styles.hamburgerLine} ${menuOpen ? styles.open : ''}`} />
            <span className={`${styles.hamburgerLine} ${menuOpen ? styles.open : ''}`} />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className={styles.mobileMenu}>
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className={styles.mobileLink}
              onClick={() => setMenuOpen(false)}
            >
              <span>{link.icon}</span>
              {link.label}
            </a>
          ))}
          <button onClick={handleLogout} className={styles.mobileLogout}>
            🚪 Đăng xuất
          </button>
        </div>
      )}
    </nav>
  );
}
