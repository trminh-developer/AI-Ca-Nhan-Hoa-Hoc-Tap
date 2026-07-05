import type { Metadata } from "next";
import { Inter, Bricolage_Grotesque, JetBrains_Mono } from "next/font/google";
import "@/app/globals.css";
import Chatbot from "@/components/chat/Chatbot";

const inter = Inter({ subsets: ["latin", "vietnamese"], weight: ["300", "400", "500", "600", "700", "800", "900"], variable: '--font-inter' });
const bricolage = Bricolage_Grotesque({ subsets: ["latin", "vietnamese"], weight: ["400", "500", "600", "700", "800"], variable: '--font-bricolage' });
const jetbrains = JetBrains_Mono({ subsets: ["latin", "vietnamese"], weight: ["400", "500", "600", "700"], variable: '--font-jetbrains' });

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
      <body className={`${inter.variable} ${bricolage.variable} ${jetbrains.variable} font-sans bg-background text-foreground`}>
        {children}
        <Chatbot />
      </body>
    </html>
  );
}
