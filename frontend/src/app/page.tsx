import LandingPage from './LandingPage';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'LearnAI - Học tập thông minh cùng AI',
  description: 'Hệ thống tự động điều chỉnh nội dung theo năng lực của bạn. Sử dụng thuật toán Elo Rating và Spaced Repetition.',
};

export default function Page() {
  return <LandingPage />;
}
