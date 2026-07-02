/**
 * Format a date string to Vietnamese locale
 */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * Format a short date
 */
export function formatShortDate(dateStr: string): string {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
  }).format(date);
}

/**
 * Format Elo rating with comma separator
 */
export function formatElo(elo: number): string {
  return Math.round(elo).toLocaleString('vi-VN');
}

/**
 * Get Bloom's Taxonomy level label in Vietnamese
 */
export function getBloomLabel(level: number): string {
  const labels: Record<number, string> = {
    1: 'Nhớ',
    2: 'Hiểu',
    3: 'Vận dụng',
    4: 'Phân tích',
    5: 'Đánh giá',
    6: 'Sáng tạo',
  };
  return labels[level] || 'Chưa xác định';
}

/**
 * Get color for Bloom's Taxonomy level
 */
export function getBloomColor(level: number): string {
  const colors: Record<number, string> = {
    1: '#10b981', // Green - Remember
    2: '#06b6d4', // Cyan - Understand
    3: '#3b82f6', // Blue - Apply
    4: '#8b5cf6', // Purple - Analyze
    5: '#ec4899', // Pink - Evaluate
    6: '#f59e0b', // Orange - Create
  };
  return colors[level] || '#94a3b8';
}

/**
 * Get badge class for Bloom level
 */
export function getBloomBadgeClass(level: number): string {
  const classes: Record<number, string> = {
    1: 'badge-green',
    2: 'badge-cyan',
    3: 'badge-blue',
    4: 'badge-purple',
    5: 'badge-red',
    6: 'badge-orange',
  };
  return classes[level] || 'badge-blue';
}

/**
 * Elo tier definition
 */
export interface EloTier {
  name: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
  minElo: number;
}

/**
 * Map Elo rating to a tier
 */
export function getEloTier(elo: number): EloTier {
  if (elo >= 2400) {
    return {
      name: 'Thách đấu',
      color: '#f59e0b',
      bgColor: 'rgba(245, 158, 11, 0.15)',
      borderColor: 'rgba(245, 158, 11, 0.3)',
      icon: '👑',
      minElo: 2400,
    };
  }
  if (elo >= 2000) {
    return {
      name: 'Kim cương',
      color: '#06b6d4',
      bgColor: 'rgba(6, 182, 212, 0.15)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      icon: '💎',
      minElo: 2000,
    };
  }
  if (elo >= 1600) {
    return {
      name: 'Bạch kim',
      color: '#a3e635',
      bgColor: 'rgba(163, 230, 53, 0.15)',
      borderColor: 'rgba(163, 230, 53, 0.3)',
      icon: '⚜️',
      minElo: 1600,
    };
  }
  if (elo >= 1200) {
    return {
      name: 'Vàng',
      color: '#fbbf24',
      bgColor: 'rgba(251, 191, 36, 0.15)',
      borderColor: 'rgba(251, 191, 36, 0.3)',
      icon: '🏅',
      minElo: 1200,
    };
  }
  if (elo >= 800) {
    return {
      name: 'Bạc',
      color: '#94a3b8',
      bgColor: 'rgba(148, 163, 184, 0.15)',
      borderColor: 'rgba(148, 163, 184, 0.3)',
      icon: '🥈',
      minElo: 800,
    };
  }
  return {
    name: 'Đồng',
    color: '#cd7f32',
    bgColor: 'rgba(205, 127, 50, 0.15)',
    borderColor: 'rgba(205, 127, 50, 0.3)',
    icon: '🥉',
    minElo: 0,
  };
}

/**
 * Calculate accuracy percentage
 */
export function calculateAccuracy(correct: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((correct / total) * 100);
}

/**
 * Format seconds to mm:ss
 */
export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Clamp a number between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Generate a greeting based on time of day
 */
export function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Chào buổi sáng';
  if (hour < 18) return 'Chào buổi chiều';
  return 'Chào buổi tối';
}
