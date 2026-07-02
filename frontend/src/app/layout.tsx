import type { Metadata } from "next";
import "@/styles/globals.css";
import Chatbot from "@/components/chat/Chatbot";

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
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </head>
      <body>
        {children}
        <Chatbot />
      </body>
    </html>
  );
}
