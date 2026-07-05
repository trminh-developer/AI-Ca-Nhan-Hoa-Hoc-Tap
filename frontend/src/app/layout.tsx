import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import "@/app/globals.css";
import Chatbot from "@/components/chat/Chatbot";

const inter = Inter({ subsets: ["latin", "vietnamese"], weight: ["300", "400", "500", "600", "700", "800", "900"] });

export const metadata: Metadata = {
  title: "LearnAI - Học tập thông minh với AI",
  description: "Nền tảng học tập thích ứng sử dụng AI để cá nhân hóa nội dung theo năng lực người học. Elo Rating, SM-2 Spaced Repetition, Bloom's Taxonomy.",
  keywords: "AI, học tập, cá nhân hóa, adaptive learning, Elo rating, NCKH",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className={inter.className}>
        {children}
        <Chatbot />
      </body>
    </html>
  );
}
