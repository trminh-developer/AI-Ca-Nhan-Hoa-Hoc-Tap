import Link from 'next/link';
import styles from './admin.module.css';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <Link href="/admin" className={styles.logo}>
          🛡️ Admin Panel
        </Link>
        <nav className={styles.nav}>
          <Link href="/admin" className={`${styles.navLink} ${styles.navLinkActive}`}>
            📊 Dashboard
          </Link>
        </nav>
        <div className={styles.bottomNav}>
          <Link href="/dashboard" className={styles.navLink}>
            ← Quay lại Nyvora
          </Link>
        </div>
      </aside>
      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}
