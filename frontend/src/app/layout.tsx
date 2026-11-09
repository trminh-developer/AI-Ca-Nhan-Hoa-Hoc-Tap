import type { Metadata } from "next";
import { Inter, Bricolage_Grotesque, JetBrains_Mono } from "next/font/google";
import "@/app/globals.css";
import { AuthProvider } from "@/context/AuthContext";
import Chatbot from "@/components/chat/Chatbot";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-inter",
});
const bricolage = Bricolage_Grotesque({
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-bricolage",
});
const jetbrains = JetBrains_Mono({
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-jetbrains",
});

export const metadata: Metadata = {
  title: "Nyvora — Nền tảng Học tập Thích ứng AI (NCKH)",
  description:
    "Nền tảng học tập thích ứng sử dụng AI để cá nhân hóa nội dung theo năng lực người học: Dual Elo Rating, ZPD, SM-2 Spaced Repetition, Bloom's Taxonomy & Socratic AI Tutor trên Python 3.14.",
  keywords:
    "Nyvora, AI, học tập thích ứng, adaptive learning, Dual Elo, SM-2, ZPD, Bloom Taxonomy, NCKH, Python 3.14",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css"
          crossOrigin="anonymous"
        />
      </head>
      <body
        className={`${inter.variable} ${bricolage.variable} ${jetbrains.variable} font-sans bg-background text-foreground`}
      >
        <AuthProvider>
          {children}
          <Chatbot />
        </AuthProvider>
      </body>
    </html>
  );
}
