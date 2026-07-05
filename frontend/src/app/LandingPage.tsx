"use client";
import { useState, useEffect, useRef } from "react";
import { motion, useInView } from "motion/react";
import {
  Brain, Target, Clock, MessageSquare, BarChart3, BookOpen, Zap,
  ArrowRight, Menu, X, Sparkles, Star, ChevronDown, CheckCircle2,
  TrendingUp, Users, Award, Shield, Lightbulb,
  Code2, Calculator, AtomIcon, Globe, Play,
  RotateCcw, Send, Cpu
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar
} from "recharts";
import * as Accordion from "@radix-ui/react-accordion";

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   HOOKS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function useCounter(end: number, duration: number, active: boolean) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!active) return;
    let t0: number | null = null;
    const tick = (now: number) => {
      if (!t0) t0 = now;
      const p = Math.min((now - t0) / duration, 1);
      setVal(Math.round(p * end));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [end, duration, active]);
  return val;
}

function useTypewriter(words: string[], speed = 80, pause = 2000) {
  const [idx, setIdx] = useState(0);
  const [char, setChar] = useState(0);
  const [deleting, setDeleting] = useState(false);
  useEffect(() => {
    const current = words[idx];
    const delay = deleting ? speed / 2 : char === current.length ? pause : speed;
    const t = setTimeout(() => {
      if (!deleting && char === current.length) {
        setDeleting(true);
      } else if (deleting && char === 0) {
        setDeleting(false);
        setIdx((i) => (i + 1) % words.length);
      } else {
        setChar((c) => c + (deleting ? -1 : 1));
      }
    }, delay);
    return () => clearTimeout(t);
  }, [char, deleting, idx, words, speed, pause]);
  return words[idx].slice(0, char);
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   BACKGROUND
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function KineticBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div className="absolute inset-0 bg-[#06060e]" />
      <div className="absolute -top-32 left-[15%] w-[600px] h-[600px] rounded-full bg-cyan-500/6 blur-[130px] animate-[pulse_9s_ease-in-out_infinite]" />
      <div className="absolute top-[30%] right-[10%] w-[480px] h-[480px] rounded-full bg-violet-600/7 blur-[110px] animate-[pulse_11s_ease-in-out_infinite_2s]" />
      <div className="absolute bottom-[5%] left-[30%] w-[360px] h-[360px] rounded-full bg-blue-500/5 blur-[100px] animate-[pulse_8s_ease-in-out_infinite_4s]" />
      <div className="absolute top-[60%] left-[5%] w-[280px] h-[280px] rounded-full bg-emerald-500/5 blur-[80px] animate-[pulse_13s_ease-in-out_infinite_1s]" />
      <div
        className="absolute inset-0 opacity-[0.022]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(34,211,238,1) 1px,transparent 1px),linear-gradient(90deg,rgba(34,211,238,1) 1px,transparent 1px)",
          backgroundSize: "64px 64px",
        }}
      />
      {/* Diagonal accent lines */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.04]" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        <line x1="0" y1="900" x2="400" y2="0" stroke="url(#gl1)" strokeWidth="1" />
        <line x1="1440" y1="0" x2="1100" y2="900" stroke="url(#gl2)" strokeWidth="1" />
        <defs>
          <linearGradient id="gl1" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#22d3ee" stopOpacity="0" />
            <stop offset="50%" stopColor="#22d3ee" stopOpacity="1" />
            <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="gl2" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#7c3aed" stopOpacity="0" />
            <stop offset="50%" stopColor="#7c3aed" stopOpacity="1" />
            <stop offset="100%" stopColor="#7c3aed" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   NAV
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function Nav({ scrolled }: { scrolled: boolean }) {
  const [open, setOpen] = useState(false);
  const links = [
    { label: "TĂ­nh nÄƒng", href: "#features" },
    { label: "Dashboard", href: "#dashboard" },
    { label: "MĂ´n há»c", href: "#subjects" },
    { label: "FAQ", href: "#faq" },
  ];

  return (
    <motion.header
      initial={{ y: -70, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "bg-[#06060e]/92 backdrop-blur-2xl border-b border-cyan-400/8"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center shadow-[0_0_18px_rgba(34,211,238,0.45)]">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <span className="font-['Bricolage_Grotesque',sans-serif] font-extrabold text-lg text-white tracking-tight">
            Learn<span className="text-cyan-400">AI</span>
          </span>
          <span className="hidden sm:block ml-1 px-1.5 py-0.5 text-[9px] font-medium bg-cyan-400/10 text-cyan-300 rounded font-['JetBrains_Mono',monospace] border border-cyan-400/20">
            BETA
          </span>
        </div>

        <nav className="hidden md:flex items-center gap-8">
          {links.map((l) => (
            <a key={l.label} href={l.href} className="text-sm text-[#7878a0] hover:text-cyan-300 transition-colors duration-200 font-medium">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <button className="text-sm text-[#7878a0] hover:text-white transition-colors px-4 py-2 font-medium">
            ÄÄƒng nháº­p
          </button>
          <button className="relative text-sm font-semibold px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-cyan-400 text-[#06060e] hover:from-cyan-400 hover:to-cyan-300 transition-all duration-200 shadow-[0_0_22px_rgba(34,211,238,0.35)] hover:shadow-[0_0_32px_rgba(34,211,238,0.55)]">
            Báº¯t Ä‘áº§u miá»…n phĂ­
          </button>
        </div>

        <button className="md:hidden text-[#7878a0] hover:text-white transition-colors" onClick={() => setOpen(!open)}>
          {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {open && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden bg-[#0b0b1e]/96 backdrop-blur-2xl border-b border-white/5 px-6 py-5 flex flex-col gap-4"
        >
          {links.map((l) => (
            <a key={l.label} href={l.href} onClick={() => setOpen(false)} className="text-sm text-[#7878a0] hover:text-cyan-300 transition-colors py-1 font-medium">
              {l.label}
            </a>
          ))}
          <button className="text-sm font-semibold px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-[#06060e] mt-1">
            Báº¯t Ä‘áº§u miá»…n phĂ­
          </button>
        </motion.div>
      )}
    </motion.header>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   HERO
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function Hero() {
  const typed = useTypewriter(["Elo Rating", "Spaced Repetition", "AI Chatbot", "Bloom Taxonomy"], 75, 2200);

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-16 overflow-hidden">
      {/* Hero image as subtle bg overlay */}
      <div
        className="absolute inset-0 opacity-[0.07] bg-cover bg-center"
        style={{ backgroundImage: "url(https://images.unsplash.com/photo-1757466762489-52fea38071ad?w=1800&h=1000&fit=crop&auto=format)" }}
        aria-hidden="true"
      />
      <div className="absolute inset-0 bg-gradient-to-b from-[#06060e]/40 via-[#06060e]/20 to-[#06060e]" />

      {/* Neural SVG */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.07] pointer-events-none" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice">
        {([
          [150,150,500,350],[500,350,900,180],[500,350,700,600],
          [150,150,350,480],[350,480,500,350],[900,180,1050,480],
          [1050,480,700,600],[700,600,500,350],[350,480,700,600],
        ] as [number,number,number,number][]).map(([x1,y1,x2,y2],i) => (
          <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(34,211,238,0.9)" strokeWidth="1.5" />
        ))}
        {([
          [150,150],[500,350],[900,180],[350,480],[700,600],[1050,480]
        ] as [number,number][]).map(([cx,cy],i) => (
          <g key={i}>
            <circle cx={cx} cy={cy} r="10" fill="rgba(34,211,238,0.08)" />
            <circle cx={cx} cy={cy} r="4" fill="rgba(34,211,238,0.7)" />
          </g>
        ))}
      </svg>

      <div className="relative z-10 max-w-5xl mx-auto text-center w-full">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.88 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-cyan-500/28 bg-cyan-500/7 text-cyan-300 text-xs font-semibold mb-8 backdrop-blur-md"
        >
          <Sparkles className="w-3.5 h-3.5 animate-pulse" />
          NghiĂªn cá»©u Khoa há»c Sinh viĂªn Â· 2024
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse ml-1" />
        </motion.div>

        {/* Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 36 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="font-['Bricolage_Grotesque',sans-serif] text-5xl sm:text-6xl md:text-[82px] font-extrabold text-white leading-[0.92] tracking-tight mb-6"
        >
          Há»c thĂ´ng minh hÆ¡n
          <br />
          <span className="relative">
            <span className="bg-gradient-to-r from-cyan-300 via-cyan-400 to-violet-400 bg-clip-text text-transparent">
              vá»›i {typed}
            </span>
            <span className="inline-block w-0.5 h-[0.9em] bg-cyan-400 ml-1 align-middle animate-[pulse_1s_step-end_infinite]" />
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.22 }}
          className="text-[#8080a8] text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-10"
        >
          Há»‡ thá»‘ng há»c táº­p tháº¿ há»‡ má»›i â€” cĂ¡ nhĂ¢n hĂ³a tá»«ng cĂ¢u há»i, tá»«ng lá»‹ch Ă´n, tá»«ng gá»£i Ă½. ÄÆ°á»£c xĂ¢y dá»±ng dá»±a trĂªn khoa há»c nháº­n thá»©c vĂ  trĂ­ tuá»‡ nhĂ¢n táº¡o.
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.32 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16"
        >
          <button className="group flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-[#06060e] font-semibold text-base hover:from-cyan-400 hover:to-cyan-300 transition-all duration-200 shadow-[0_0_32px_rgba(34,211,238,0.38)] hover:shadow-[0_0_48px_rgba(34,211,238,0.6)]">
            <Zap className="w-4 h-4" />
            Báº¯t Ä‘áº§u há»c ngay
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>
          <button className="group flex items-center gap-2 px-8 py-4 rounded-xl border border-white/10 bg-white/3 text-[#e0e0f0] font-medium text-base hover:border-cyan-500/30 hover:text-cyan-200 hover:bg-white/5 transition-all duration-200 backdrop-blur-sm">
            <Play className="w-4 h-4" />
            Xem demo
          </button>
        </motion.div>

        {/* Mini stat pills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.45 }}
          className="flex flex-wrap gap-3 justify-center"
        >
          {[
            { icon: Users, val: "500+", label: "sinh viĂªn" },
            { icon: BookOpen, val: "60+", label: "cĂ¢u há»i" },
            { icon: Award, val: "6", label: "cáº¥p Bloom" },
            { icon: Shield, val: "100%", label: "miá»…n phĂ­" },
          ].map(({ icon: Icon, val, label }, i) => (
            <div key={i} className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/4 border border-white/8 backdrop-blur-sm">
              <Icon className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-white text-sm font-semibold">{val}</span>
              <span className="text-[#7878a0] text-xs">{label}</span>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Scroll cue */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <div className="w-5 h-8 rounded-full border border-white/20 flex items-start justify-center p-1.5">
          <div className="w-1 h-1.5 rounded-full bg-cyan-400 animate-[bounce_2s_infinite]" />
        </div>
      </motion.div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   MARQUEE TICKER
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function Ticker() {
  const items = [
    "Elo Rating", "Spaced Repetition", "SM-2 Algorithm",
    "Bloom Taxonomy", "AI Tutor", "Adaptive Learning",
    "Cognitive Science", "Zone of Proximal Development",
    "Personalized Education", "Real-time Analytics",
    "Há»c Láº­p TrĂ¬nh", "ToĂ¡n Cao Cáº¥p", "Váº­t LĂ½ Äáº¡i CÆ°Æ¡ng",
  ];
  const doubled = [...items, ...items];
  return (
    <div className="relative z-10 py-5 overflow-hidden border-y border-white/5">
      <div className="flex animate-[marquee_30s_linear_infinite] whitespace-nowrap gap-0">
        {doubled.map((item, i) => (
          <span key={i} className="inline-flex items-center gap-3 px-6 text-sm text-[#6060a0] font-['JetBrains_Mono',monospace]">
            <span className="w-1 h-1 rounded-full bg-cyan-400/50" />
            {item}
          </span>
        ))}
      </div>
      <style>{`
        @keyframes marquee { from { transform: translateX(0) } to { transform: translateX(-50%) } }
        @keyframes marquee2 { from { transform: translateX(-50%) } to { transform: translateX(0) } }
      `}</style>
    </div>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   STATS + ELO CHART
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
const eloData = [
  { week: "T1", elo: 820 },
  { week: "T2", elo: 855 },
  { week: "T3", elo: 840 },
  { week: "T4", elo: 890 },
  { week: "T5", elo: 920 },
  { week: "T6", elo: 905 },
  { week: "T7", elo: 960 },
  { week: "T8", elo: 998 },
  { week: "T9", elo: 1032 },
  { week: "T10", elo: 1058 },
  { week: "T11", elo: 1044 },
  { week: "T12", elo: 1087 },
];

function Stats() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const s = useCounter(3, 1400, inView);
  const q = useCounter(60, 1700, inView);
  const b = useCounter(6, 1200, inView);
  const p = useCounter(500, 1900, inView);

  return (
    <section ref={ref} id="dashboard" className="relative z-10 py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <span className="font-['JetBrains_Mono',monospace] text-xs text-cyan-400 tracking-[0.2em] uppercase mb-3 block">
            {"//"} Ná»n táº£ng sá»‘ liá»‡u
          </span>
          <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold text-white">
            Con sá»‘{" "}
            <span className="bg-gradient-to-r from-cyan-300 to-violet-400 bg-clip-text text-transparent">
              biáº¿t nĂ³i
            </span>
          </h2>
        </motion.div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            { val: s, suffix: "+", label: "MĂ´n há»c", sub: "& má»Ÿ rá»™ng", color: "text-cyan-400", glow: "rgba(34,211,238,0.08)" },
            { val: q, suffix: "+", label: "CĂ¢u há»i", sub: "Ä‘a cáº¥p Ä‘á»™", color: "text-violet-400", glow: "rgba(124,58,237,0.08)" },
            { val: b, suffix: "", label: "Cáº¥p Bloom", sub: "taxonomy", color: "text-emerald-400", glow: "rgba(16,185,129,0.08)" },
            { val: p, suffix: "+", label: "Sinh viĂªn", sub: "Ä‘ang há»c", color: "text-orange-400", glow: "rgba(249,115,22,0.08)" },
          ].map(({ val, suffix, label, sub, color, glow }, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="rounded-2xl border border-white/7 bg-[#0b0b1e] p-6 flex flex-col hover:border-white/12 transition-colors"
              style={{ boxShadow: `inset 0 0 40px ${glow}` }}
            >
              <span className={`font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold ${color} tabular-nums`}>
                {val}{suffix}
              </span>
              <span className="text-white font-semibold mt-2 text-sm">{label}</span>
              <span className="text-[#7878a0] text-xs mt-0.5 font-['JetBrains_Mono',monospace]">{sub}</span>
            </motion.div>
          ))}
        </div>

        {/* Elo Chart */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="rounded-2xl border border-white/7 bg-[#0b0b1e] p-6 md:p-8"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <span className="text-white font-semibold">Elo Rating theo thá»i gian</span>
              </div>
              <p className="text-[#7878a0] text-xs font-['JetBrains_Mono',monospace]">Há»c viĂªn Ä‘iá»ƒn hĂ¬nh â€¢ 12 tuáº§n</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-2xl font-['Bricolage_Grotesque',sans-serif] font-extrabold text-cyan-400">+267</div>
                <div className="text-xs text-[#7878a0]">Ä‘iá»ƒm tÄƒng trÆ°á»Ÿng</div>
              </div>
              <div className="w-px h-10 bg-white/10" />
              <div className="text-right">
                <div className="text-2xl font-['Bricolage_Grotesque',sans-serif] font-extrabold text-emerald-400">82%</div>
                <div className="text-xs text-[#7878a0]">tá»· lá»‡ Ä‘Ăºng TB</div>
              </div>
            </div>
          </div>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={eloData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="eloGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.01} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="week" tick={{ fill: "#7878a0", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis domain={[800, 1100]} tick={{ fill: "#7878a0", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#0f0f20", border: "1px solid rgba(34,211,238,0.2)", borderRadius: 10, color: "#e0e0f0", fontSize: 12 }}
                  formatter={(v: any) => [`${v} Elo`, "Rating"]}
                />
                <Area type="monotone" dataKey="elo" stroke="#22d3ee" strokeWidth={2} fill="url(#eloGrad)" dot={{ fill: "#22d3ee", r: 3, strokeWidth: 0 }} activeDot={{ r: 5, fill: "#22d3ee" }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   FEATURES
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
const MiniSparkline = ({ data, color }: { data: number[]; color: string }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((v - min) / (max - min)) * 80 - 10;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full">
      <polyline points={points} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <polyline points={`0,100 ${points} 100,100`} fill={color} fillOpacity="0.1" stroke="none" />
    </svg>
  );
};

function Features() {
  const [active, setActive] = useState(0);

  const features = [
    {
      icon: Target,
      label: "Elo Rating",
      title: "Elo Rating ThĂ­ch á»¨ng",
      tagline: "LuĂ´n trong vĂ¹ng thĂ¡ch thá»©c tá»‘i Æ°u",
      desc: "Há»‡ thá»‘ng Elo Rating liĂªn tá»¥c hiá»‡u chá»‰nh Ä‘á»™ khĂ³ cĂ¢u há»i dá»±a trĂªn má»—i cĂ¢u tráº£ lá»i cá»§a báº¡n. Má»¥c tiĂªu duy trĂ¬ trong vĂ¹ng 70â€“85% tá»· lá»‡ Ä‘Ăºng â€” Ä‘Ă¢y lĂ  vĂ¹ng há»c táº­p hiá»‡u quáº£ nháº¥t theo nghiĂªn cá»©u khoa há»c nháº­n thá»©c.",
      bullets: [
        "Hiá»‡u chá»‰nh real-time sau má»—i cĂ¢u tráº£ lá»i",
        "So sĂ¡nh vá»›i chuáº©n há»c táº­p toĂ n há»‡ thá»‘ng",
        "PhĂ¢n tĂ­ch xu hÆ°á»›ng tiáº¿n bá»™ theo tuáº§n",
        "Cáº£nh bĂ¡o khi rÆ¡i vĂ o vĂ¹ng thoáº£i mĂ¡i",
      ],
      color: "from-cyan-500/12 to-blue-600/12",
      border: "border-cyan-500/22",
      glow: "0 0 50px rgba(34,211,238,0.07)",
      iconBg: "bg-cyan-500/12 group-hover:bg-cyan-500/20",
      iconColor: "text-cyan-400",
      tag: "bg-cyan-400/10 text-cyan-400",
      chart: [65, 72, 68, 79, 83, 80, 85, 82, 87, 84],
      chartColor: "#22d3ee",
    },
    {
      icon: Clock,
      label: "SM-2",
      title: "Spaced Repetition SM-2",
      tagline: "Chiáº¿n tháº¯ng Ä‘Æ°á»ng cong quĂªn lĂ£ng",
      desc: "Thuáº­t toĂ¡n SuperMemo SM-2 tĂ­nh toĂ¡n thá»i Ä‘iá»ƒm tá»‘i Æ°u Ä‘á»ƒ Ă´n láº¡i kiáº¿n thá»©c, dá»±a trĂªn Ä‘Æ°á»ng cong quĂªn lĂ£ng Ebbinghaus cĂ¡ nhĂ¢n cá»§a báº¡n. Há»c Ă­t hÆ¡n, nhá»› lĂ¢u hÆ¡n.",
      bullets: [
        "Lá»‹ch Ă´n cĂ¡ nhĂ¢n hĂ³a tá»± Ä‘á»™ng",
        "6 há»‡ sá»‘ dá»… theo tá»«ng ná»™i dung",
        "TĂ­ch há»£p vá»›i Elo Ä‘á»ƒ Æ°u tiĂªn Ä‘iá»ƒm yáº¿u",
        "Thá»‘ng kĂª retention rate tá»«ng tuáº§n",
      ],
      color: "from-violet-500/12 to-purple-600/12",
      border: "border-violet-500/22",
      glow: "0 0 50px rgba(124,58,237,0.07)",
      iconBg: "bg-violet-500/12 group-hover:bg-violet-500/20",
      iconColor: "text-violet-400",
      tag: "bg-violet-400/10 text-violet-400",
      chart: [40, 28, 55, 38, 70, 52, 80, 62, 88, 74],
      chartColor: "#7c3aed",
    },
    {
      icon: BarChart3,
      label: "Dashboard",
      title: "Analytics Dashboard",
      tagline: "Dá»¯ liá»‡u há»c táº­p toĂ n diá»‡n",
      desc: "Báº£ng Ä‘iá»u khiá»ƒn thá»i gian thá»±c hiá»ƒn thá»‹ Ä‘áº§y Ä‘á»§ hĂ nh trĂ¬nh há»c táº­p: xáº¿p háº¡ng Elo, báº£n Ä‘á»“ thĂ nh tháº¡o chá»§ Ä‘á», streak ngĂ y há»c, vĂ  phĂ¢n tĂ­ch session chi tiáº¿t.",
      bullets: [
        "Biá»ƒu Ä‘á»“ Elo theo thá»i gian thá»±c",
        "Báº£n Ä‘á»“ nhiá»‡t thĂ nh tháº¡o chá»§ Ä‘á»",
        "Streak vĂ  milestone gamification",
        "Export bĂ¡o cĂ¡o PDF cĂ¡ nhĂ¢n",
      ],
      color: "from-emerald-500/12 to-teal-600/12",
      border: "border-emerald-500/22",
      glow: "0 0 50px rgba(16,185,129,0.07)",
      iconBg: "bg-emerald-500/12 group-hover:bg-emerald-500/20",
      iconColor: "text-emerald-400",
      tag: "bg-emerald-400/10 text-emerald-400",
      chart: [50, 55, 62, 70, 75, 74, 82, 88, 86, 93],
      chartColor: "#10b981",
    },
    {
      icon: MessageSquare,
      label: "AI Tutor",
      title: "AI Tutor CĂ¡ NhĂ¢n",
      tagline: "Trá»£ lĂ½ thĂ´ng minh 24/7",
      desc: "Chatbot AI Ä‘Æ°á»£c Ä‘Ă o táº¡o trĂªn tĂ i liá»‡u khĂ³a há»c, cĂ³ thá»ƒ giáº£i thĂ­ch khĂ¡i niá»‡m, gá»£i Ă½ lá»™ trĂ¬nh há»c, vĂ  cung cáº¥p hints phĂ¹ há»£p Ä‘Ăºng vá»›i trĂ¬nh Ä‘á»™ Elo hiá»‡n táº¡i cá»§a báº¡n.",
      bullets: [
        "Tráº£ lá»i dá»±a trĂªn tĂ i liá»‡u khĂ³a há»c",
        "Hints thĂ­ch á»©ng theo cáº¥p Bloom",
        "Giáº£i thĂ­ch nhiá»u cĂ¡ch cho má»™t khĂ¡i niá»‡m",
        "Lá»‹ch sá»­ há»™i thoáº¡i lÆ°u trá»¯ Ä‘áº§y Ä‘á»§",
      ],
      color: "from-orange-500/12 to-rose-600/12",
      border: "border-orange-500/22",
      glow: "0 0 50px rgba(249,115,22,0.07)",
      iconBg: "bg-orange-500/12 group-hover:bg-orange-500/20",
      iconColor: "text-orange-400",
      tag: "bg-orange-400/10 text-orange-400",
      chart: [30, 38, 46, 52, 61, 68, 74, 79, 85, 90],
      chartColor: "#f97316",
    },
  ];

  const feat = features[active];
  const Icon = feat.icon;

  return (
    <section id="features" className="relative z-10 py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <span className="font-['JetBrains_Mono',monospace] text-xs text-cyan-400 tracking-[0.2em] uppercase mb-3 block">
            {"//"} TĂ­nh nÄƒng cá»‘t lĂµi
          </span>
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold text-white leading-tight">
              CĂ´ng nghá»‡ giĂ¡o dá»¥c{" "}
              <span className="bg-gradient-to-r from-cyan-300 to-violet-400 bg-clip-text text-transparent">
                tháº¿ há»‡ má»›i
              </span>
            </h2>
            <p className="text-[#7878a0] text-sm max-w-xs leading-relaxed">
              Bá»‘n trá»¥ cá»™t Ä‘Æ°á»£c xĂ¢y dá»±ng trĂªn ná»n táº£ng nghiĂªn cá»©u nháº­n thá»©c há»c vĂ  khoa há»c dá»¯ liá»‡u.
            </p>
          </div>
        </motion.div>

        {/* Feature tab pills */}
        <div className="flex flex-wrap gap-2 mb-8">
          {features.map((f, i) => {
            const FIcon = f.icon;
            return (
              <button
                key={i}
                onClick={() => setActive(i)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${
                  active === i
                    ? `bg-gradient-to-r ${f.color} ${f.border} text-white`
                    : "border-white/8 text-[#7878a0] hover:text-white hover:border-white/16"
                }`}
              >
                <FIcon className={`w-3.5 h-3.5 ${active === i ? f.iconColor : ""}`} />
                {f.label}
              </button>
            );
          })}
        </div>

        {/* Detail panel */}
        <motion.div
          key={active}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className={`rounded-2xl bg-gradient-to-br ${feat.color} border ${feat.border} p-6 md:p-8`}
          style={{ boxShadow: feat.glow }}
        >
          <div className="grid md:grid-cols-[1fr_280px] gap-8">
            <div>
              <div className="flex items-center gap-3 mb-5">
                <div className={`w-11 h-11 rounded-xl ${feat.iconBg} flex items-center justify-center transition-colors group`}>
                  <Icon className={`w-5 h-5 ${feat.iconColor}`} />
                </div>
                <div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${feat.tag} font-['JetBrains_Mono',monospace]`}>
                    feature_{String(active + 1).padStart(2, "0")}
                  </span>
                  <h3 className="font-['Bricolage_Grotesque',sans-serif] text-2xl font-bold text-white mt-0.5">{feat.title}</h3>
                </div>
              </div>
              <p className={`text-sm font-medium ${feat.iconColor} mb-3`}>{feat.tagline}</p>
              <p className="text-[#b0b0cc] leading-relaxed mb-6 text-sm">{feat.desc}</p>
              <ul className="grid sm:grid-cols-2 gap-2.5">
                {feat.bullets.map((b, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-[#e0e0f0]">
                    <CheckCircle2 className={`w-4 h-4 ${feat.iconColor} flex-shrink-0 mt-0.5`} />
                    {b}
                  </li>
                ))}
              </ul>
            </div>
            {/* Mini sparkline card */}
            <div className="rounded-xl bg-[#08080f]/60 border border-white/6 p-5 flex flex-col">
              <div className="text-xs text-[#7878a0] font-['JetBrains_Mono',monospace] mb-1">Hiá»‡u quáº£ há»c táº­p</div>
              <div className={`font-['Bricolage_Grotesque',sans-serif] text-3xl font-extrabold ${feat.iconColor} mb-4`}>
                {feat.chart[feat.chart.length - 1]}%
              </div>
              <div className="flex-1 min-h-[80px]">
                <MiniSparkline data={feat.chart} color={feat.chartColor} />
              </div>
              <div className="mt-3 text-xs text-[#7878a0] flex justify-between">
                <span>10 tuáº§n trÆ°á»›c</span>
                <span className={`${feat.iconColor} font-medium`}>HĂ´m nay</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   SUBJECTS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
const radarData = [
  { subject: "CÆ¡ báº£n", A: 90, B: 60, C: 75 },
  { subject: "á»¨ng dá»¥ng", A: 78, B: 85, C: 55 },
  { subject: "PhĂ¢n tĂ­ch", A: 65, B: 72, C: 88 },
  { subject: "Tá»•ng há»£p", A: 70, B: 58, C: 80 },
  { subject: "ÄĂ¡nh giĂ¡", A: 55, B: 90, C: 65 },
];

function Subjects() {
  const subjects = [
    {
      icon: Code2,
      name: "Láº­p TrĂ¬nh",
      code: "CS101",
      desc: "Thuáº­t toĂ¡n, cáº¥u trĂºc dá»¯ liá»‡u, láº­p trĂ¬nh hÆ°á»›ng Ä‘á»‘i tÆ°á»£ng vĂ  giáº£i quyáº¿t váº¥n Ä‘á» thá»±c táº¿.",
      topics: ["Thuáº­t toĂ¡n", "OOP", "Data Structures", "Complexity"],
      elo: 950,
      maxElo: 1200,
      questions: 24,
      color: "text-cyan-400",
      border: "border-cyan-500/20",
      bg: "bg-cyan-500/8",
      glow: "rgba(34,211,238,0.06)",
      bar: "bg-gradient-to-r from-cyan-500 to-cyan-400",
    },
    {
      icon: Calculator,
      name: "ToĂ¡n Cao Cáº¥p",
      code: "MATH201",
      desc: "Giáº£i tĂ­ch, Ä‘áº¡i sá»‘ tuyáº¿n tĂ­nh, xĂ¡c suáº¥t thá»‘ng kĂª vĂ  á»©ng dá»¥ng trong khoa há»c mĂ¡y tĂ­nh.",
      topics: ["Giáº£i tĂ­ch", "Ma tráº­n", "XĂ¡c suáº¥t", "Thá»‘ng kĂª"],
      elo: 1080,
      maxElo: 1200,
      questions: 22,
      color: "text-violet-400",
      border: "border-violet-500/20",
      bg: "bg-violet-500/8",
      glow: "rgba(124,58,237,0.06)",
      bar: "bg-gradient-to-r from-violet-500 to-violet-400",
    },
    {
      icon: AtomIcon,
      name: "Váº­t LĂ½ Äáº¡i CÆ°Æ¡ng",
      code: "PHY101",
      desc: "CÆ¡ há»c cá»• Ä‘iá»ƒn, Ä‘iá»‡n tá»« há»c, quang há»c vĂ  nhiá»‡t Ä‘á»™ng lá»±c há»c vá»›i bĂ i toĂ¡n thá»±c táº¿.",
      topics: ["CÆ¡ há»c", "Äiá»‡n tá»«", "Quang há»c", "Nhiá»‡t há»c"],
      elo: 820,
      maxElo: 1200,
      questions: 18,
      color: "text-emerald-400",
      border: "border-emerald-500/20",
      bg: "bg-emerald-500/8",
      glow: "rgba(16,185,129,0.06)",
      bar: "bg-gradient-to-r from-emerald-500 to-emerald-400",
    },
  ];

  return (
    <section id="subjects" className="relative z-10 py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-16 flex flex-col md:flex-row md:items-end justify-between gap-6"
        >
          <div>
            <span className="font-['JetBrains_Mono',monospace] text-xs text-violet-400 tracking-[0.2em] uppercase mb-3 block">
              {"//"} MĂ´n há»c hiá»‡n cĂ³
            </span>
            <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold text-white leading-tight">
              Ba mĂ´n há»c,{" "}
              <span className="bg-gradient-to-r from-violet-300 to-emerald-400 bg-clip-text text-transparent">
                vĂ´ háº¡n cĂ¢u há»i
              </span>
            </h2>
          </div>
          <p className="text-[#7878a0] text-sm max-w-xs leading-relaxed">
            Má»—i mĂ´n há»c Ä‘Æ°á»£c chia thĂ nh cĂ¡c chá»§ Ä‘á» nhá» vá»›i Ä‘á»™ khĂ³ riĂªng biá»‡t, Ä‘áº£m báº£o há»c táº­p toĂ n diá»‡n.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-5 mb-10">
          {subjects.map(({ icon: Icon, name, code, desc, topics, elo, maxElo, questions, color, border, bg, glow, bar }, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className={`rounded-2xl border ${border} bg-[#0b0b1e] p-6 flex flex-col hover:border-opacity-50 transition-all duration-300 group cursor-pointer`}
              style={{ boxShadow: `0 0 40px ${glow}` }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <span className={`font-['JetBrains_Mono',monospace] text-[10px] font-medium px-2 py-0.5 rounded ${bg} ${color} border ${border}`}>
                  {code}
                </span>
              </div>
              <h3 className="font-['Bricolage_Grotesque',sans-serif] text-xl font-bold text-white mb-2">{name}</h3>
              <p className="text-[#7878a0] text-sm leading-relaxed mb-5 flex-1">{desc}</p>

              {/* Topics */}
              <div className="flex flex-wrap gap-1.5 mb-5">
                {topics.map((t) => (
                  <span key={t} className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 border border-white/8 text-[#9090b8] font-['JetBrains_Mono',monospace]">
                    {t}
                  </span>
                ))}
              </div>

              {/* Elo bar */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#7878a0]">{questions} cĂ¢u há»i</span>
                  <span className={`text-sm font-bold font-['JetBrains_Mono',monospace] ${color}`}>{elo} Elo</span>
                </div>
                <div className="h-1.5 rounded-full bg-white/6 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${(elo / maxElo) * 100}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, ease: "easeOut", delay: i * 0.1 + 0.3 }}
                    className={`h-full rounded-full ${bar}`}
                  />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Radar chart: thĂ nh tháº¡o so sĂ¡nh */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="rounded-2xl border border-white/7 bg-[#0b0b1e] p-6 md:p-8"
        >
          <div className="flex flex-col md:flex-row gap-8 items-center">
            <div className="md:w-64 flex-shrink-0">
              <h3 className="font-['Bricolage_Grotesque',sans-serif] text-xl font-bold text-white mb-2">
                ThĂ nh tháº¡o theo cáº¥p Bloom
              </h3>
              <p className="text-[#7878a0] text-sm leading-relaxed mb-5">
                So sĂ¡nh má»©c Ä‘á»™ thĂ nh tháº¡o cá»§a ba mĂ´n há»c trĂªn thang Ä‘o 6 cáº¥p Ä‘á»™ nháº­n thá»©c.
              </p>
              <div className="space-y-2">
                {[
                  { label: "Láº­p TrĂ¬nh", color: "#22d3ee" },
                  { label: "ToĂ¡n Cao Cáº¥p", color: "#7c3aed" },
                  { label: "Váº­t LĂ½", color: "#10b981" },
                ].map(({ label, color }) => (
                  <div key={label} className="flex items-center gap-2">
                    <div className="w-3 h-1 rounded-full" style={{ backgroundColor: color }} />
                    <span className="text-xs text-[#9090b8]">{label}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex-1 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.06)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: "#7878a0", fontSize: 11 }} />
                  <Radar name="Láº­p TrĂ¬nh" dataKey="A" stroke="#22d3ee" fill="#22d3ee" fillOpacity={0.12} strokeWidth={1.5} />
                  <Radar name="ToĂ¡n" dataKey="B" stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.12} strokeWidth={1.5} />
                  <Radar name="Váº­t LĂ½" dataKey="C" stroke="#10b981" fill="#10b981" fillOpacity={0.12} strokeWidth={1.5} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   HOW IT WORKS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function HowItWorks() {
  const steps = [
    {
      num: "01", icon: Brain, color: "text-cyan-400", bg: "bg-cyan-400/10", border: "border-cyan-400/20",
      title: "ÄĂ¡nh giĂ¡ nÄƒng lá»±c ban Ä‘áº§u",
      desc: "HoĂ n thĂ nh bĂ i kiá»ƒm tra Ä‘áº§u vĂ o thĂ­ch á»©ng gá»“m 20 cĂ¢u há»i. Há»‡ thá»‘ng Elo phĂ¢n tĂ­ch pattern vĂ  xĂ¡c Ä‘á»‹nh trĂ¬nh Ä‘á»™ xuáº¥t phĂ¡t chĂ­nh xĂ¡c cho tá»«ng chá»§ Ä‘á».",
      detail: "~10 phĂºt",
    },
    {
      num: "02", icon: Cpu, color: "text-violet-400", bg: "bg-violet-400/10", border: "border-violet-400/20",
      title: "AI xĂ¢y dá»±ng báº£n Ä‘á»“ tri thá»©c",
      desc: "Thuáº­t toĂ¡n phĂ¢n tĂ­ch Ä‘iá»ƒm máº¡nh, Ä‘iá»ƒm yáº¿u, vĂ  xĂ¢y dá»±ng Ä‘á»“ thá»‹ tri thá»©c cĂ¡ nhĂ¢n. Má»—i concept Ä‘Æ°á»£c gáº¯n Elo riĂªng vĂ  lá»‹ch Ă´n SM-2.",
      detail: "Tá»± Ä‘á»™ng",
    },
    {
      num: "03", icon: Target, color: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/20",
      title: "Há»c theo lá»™ trĂ¬nh cĂ¡ nhĂ¢n",
      desc: "Nháº­n cĂ¢u há»i vĂ  tĂ i liá»‡u Ä‘Æ°á»£c Ä‘iá»u chá»‰nh liĂªn tá»¥c. AI tutor Ä‘á»“ng hĂ nh giáº£i Ä‘Ă¡p tháº¯c máº¯c. Elo cáº­p nháº­t sau má»—i cĂ¢u tráº£ lá»i.",
      detail: "LiĂªn tá»¥c",
    },
    {
      num: "04", icon: TrendingUp, color: "text-orange-400", bg: "bg-orange-400/10", border: "border-orange-400/20",
      title: "Theo dĂµi vĂ  tá»‘i Æ°u tiáº¿n bá»™",
      desc: "Dashboard thá»i gian thá»±c hiá»ƒn thá»‹ tiáº¿n bá»™, Ä‘iá»ƒm thĂ nh tháº¡o, vĂ  so sĂ¡nh vá»›i cá»™ng Ä‘á»“ng. Há»‡ thá»‘ng tá»± Ä‘iá»u chá»‰nh thuáº­t toĂ¡n khi phĂ¡t hiá»‡n plateau.",
      detail: "Real-time",
    },
  ];

  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-16 text-center"
        >
          <span className="font-['JetBrains_Mono',monospace] text-xs text-emerald-400 tracking-[0.2em] uppercase mb-3 block">
            {"//"} Quy trĂ¬nh há»c táº­p
          </span>
          <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold text-white leading-tight">
            Bá»‘n bÆ°á»›c Ä‘áº¿n{" "}
            <span className="bg-gradient-to-r from-emerald-300 to-cyan-400 bg-clip-text text-transparent">
              thĂ nh tháº¡o
            </span>
          </h2>
        </motion.div>

        <div className="relative">
          {/* Vertical connector */}
          <div className="absolute left-[27px] md:left-1/2 md:-translate-x-px top-8 bottom-8 w-px bg-gradient-to-b from-cyan-400/40 via-violet-400/40 to-orange-400/40 hidden sm:block" />

          <div className="space-y-6 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-16 md:gap-y-10">
            {steps.map(({ num, icon: Icon, color, bg, border, title, desc, detail }, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className={`flex gap-5 ${i % 2 === 1 ? "md:flex-row-reverse md:text-right" : ""}`}
              >
                <div className="relative flex-shrink-0">
                  <div className={`w-14 h-14 rounded-2xl ${bg} border ${border} flex flex-col items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${color} mb-0.5`} />
                    <span className={`font-['JetBrains_Mono',monospace] text-[9px] font-bold ${color}`}>{num}</span>
                  </div>
                </div>
                <div className={`pt-1 ${i % 2 === 1 ? "md:flex md:flex-col md:items-end" : ""}`}>
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <h3 className="font-['Bricolage_Grotesque',sans-serif] text-lg font-bold text-white">{title}</h3>
                    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${bg} ${color} border ${border} font-['JetBrains_Mono',monospace]`}>
                      {detail}
                    </span>
                  </div>
                  <p className="text-[#7878a0] text-sm leading-relaxed">{desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   AI CHATBOT DEMO
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function AIDemo() {
  const [messages, setMessages] = useState([
    { role: "ai" as const, text: "Xin chĂ o! TĂ´i lĂ  AI Tutor cá»§a LearnAI. HĂ´m nay báº¡n muá»‘n Ă´n táº­p chá»§ Ä‘á» nĂ o? Elo hiá»‡n táº¡i cá»§a báº¡n lĂ  950." },
    { role: "user" as const, text: "Giáº£i thĂ­ch cho tĂ´i vá» Big O notation?" },
    { role: "ai" as const, text: "Big O notation mĂ´ táº£ tá»‘c Ä‘á»™ tÄƒng trÆ°á»Ÿng cá»§a thuáº­t toĂ¡n khi input tÄƒng. VĂ­ dá»¥: O(n) nghÄ©a lĂ  thá»i gian cháº¡y tÄƒng tuyáº¿n tĂ­nh. Dá»±a trĂªn Elo cá»§a báº¡n, tĂ´i gá»£i Ă½ báº¯t Ä‘áº§u vá»›i O(1), O(n), O(nÂ²) trÆ°á»›c khi sang O(log n)." },
  ]);
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  const suggestions = ["O(log n) lĂ  gĂ¬?", "Giáº£i thĂ­ch thuáº­t toĂ¡n sáº¯p xáº¿p", "VĂ­ dá»¥ vá» O(nÂ²)"];

  const send = (text: string) => {
    if (!text.trim()) return;
    setMessages(m => [...m, { role: "user", text }]);
    setInput("");
    setTimeout(() => {
      setMessages(m => [...m, { role: "ai", text: "CĂ¢u há»i ráº¥t hay! Dá»±a trĂªn trĂ¬nh Ä‘á»™ Elo 950 cá»§a báº¡n, Ä‘Ă¢y lĂ  giáº£i thĂ­ch phĂ¹ há»£p nháº¥t: " + text.toLowerCase().includes("log") ? "O(log n) xuáº¥t hiá»‡n trong thuáº­t toĂ¡n Binary Search â€” má»—i bÆ°á»›c loáº¡i bá» ná»­a pháº§n tá»­, nĂªn chá»‰ cáº§n logâ‚‚(n) bÆ°á»›c." : "TĂ´i sáº½ cung cáº¥p gá»£i Ă½ phĂ¹ há»£p vá»›i trĂ¬nh Ä‘á»™ cá»§a báº¡n. HĂ£y thá»­ lĂ m bĂ i táº­p nhá» nĂ y trÆ°á»›c nhĂ©!" }]);
    }, 800);
  };

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-[1fr_480px] gap-12 items-start">
          {/* Left */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="lg:sticky lg:top-24"
          >
            <span className="font-['JetBrains_Mono',monospace] text-xs text-orange-400 tracking-[0.2em] uppercase mb-4 block">
              {"//"} AI Tutor
            </span>
            <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold text-white leading-tight mb-6">
              NgÆ°á»i hÆ°á»›ng dáº«n
              <br />
              <span className="bg-gradient-to-r from-orange-300 to-rose-400 bg-clip-text text-transparent">
                thĂ´ng minh
              </span>{" "}
              cá»§a báº¡n
            </h2>
            <p className="text-[#7878a0] leading-relaxed mb-8 text-sm">
              KhĂ´ng chá»‰ tráº£ lá»i â€” AI Tutor phĂ¢n tĂ­ch trĂ¬nh Ä‘á»™ Elo, lá»‹ch sá»­ há»c táº­p vĂ  Ä‘Æ°a ra gá»£i Ă½ tá»‘i Æ°u cho tá»«ng cĂ¢u há»i cá»§a báº¡n.
            </p>
            <div className="space-y-4">
              {[
                { icon: BookOpen, title: "ÄĂ o táº¡o trĂªn tĂ i liá»‡u", desc: "PhĂ¢n tĂ­ch sĂ¡ch giĂ¡o khoa, slide bĂ i giáº£ng vĂ  Ä‘á» thi" },
                { icon: Lightbulb, title: "Gá»£i Ă½ thĂ­ch á»©ng", desc: "Hints phĂ¹ há»£p cáº¥p Bloom tÆ°Æ¡ng á»©ng trĂ¬nh Ä‘á»™ Elo" },
                { icon: Globe, title: "Äa ngĂ´n ngá»¯", desc: "Há»— trá»£ tiáº¿ng Viá»‡t vĂ  tiáº¿ng Anh tá»± nhiĂªn" },
              ].map(({ icon: Icon, title, desc }) => (
                <div key={title} className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-orange-500/10 border border-orange-400/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Icon className="w-4 h-4 text-orange-400" />
                  </div>
                  <div>
                    <div className="text-white text-sm font-semibold">{title}</div>
                    <div className="text-[#7878a0] text-xs mt-0.5">{desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Chat UI */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="rounded-2xl border border-orange-500/18 bg-[#0b0b1e] overflow-hidden shadow-[0_0_70px_rgba(249,115,22,0.07)]"
          >
            {/* Header */}
            <div className="flex items-center gap-3 px-5 py-4 border-b border-white/5 bg-[#0e0e20]">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-orange-400 to-rose-500 flex items-center justify-center shadow-[0_0_12px_rgba(249,115,22,0.4)]">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-white">AI Tutor Â· Láº­p TrĂ¬nh</div>
                <div className="text-xs text-[#7878a0] font-['JetBrains_Mono',monospace]">Elo báº¡n: <span className="text-cyan-400">950</span></div>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Online
              </div>
            </div>

            {/* Messages */}
            <div className="p-5 space-y-4 h-72 overflow-y-auto scrollbar-thin">
              {messages.map((m, i) => (
                <div key={i} className={`flex gap-2.5 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                  {m.role === "ai" && (
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-orange-400 to-rose-500 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-3.5 h-3.5 text-white" />
                    </div>
                  )}
                  <div
                    className={`max-w-[82%] px-3.5 py-2.5 rounded-xl text-sm leading-relaxed ${
                      m.role === "user"
                        ? "bg-orange-500/18 text-orange-50 border border-orange-500/18 rounded-tr-sm"
                        : "bg-[#14142a] text-[#c0c0d8] border border-white/5 rounded-tl-sm"
                    }`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
              <div ref={endRef} />
            </div>

            {/* Suggestions */}
            <div className="px-4 pb-2 flex gap-2 overflow-x-auto">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="flex-shrink-0 text-xs px-3 py-1.5 rounded-full border border-white/8 bg-white/3 text-[#9090b8] hover:border-orange-400/30 hover:text-orange-200 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>

            {/* Input */}
            <div className="px-4 py-4 border-t border-white/5 flex gap-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send(input)}
                placeholder="Há»i AI Tutor báº¥t cá»© Ä‘iá»u gĂ¬..."
                className="flex-1 bg-[#14142a] border border-white/6 rounded-xl px-4 py-2.5 text-sm text-[#e0e0f0] placeholder:text-[#5050780] outline-none focus:border-orange-400/30 transition-colors"
              />
              <button
                onClick={() => send(input)}
                className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center flex-shrink-0 hover:from-orange-400 hover:to-rose-400 transition-colors shadow-[0_0_16px_rgba(249,115,22,0.3)]"
              >
                <Send className="w-4 h-4 text-white" />
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   TESTIMONIALS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function Testimonials() {
  const reviews = [
    {
      name: "Nguyá»…n Minh Tuáº¥n",
      role: "Sinh viĂªn nÄƒm 3 Â· CNTT",
      avatar: "NMT",
      color: "bg-cyan-500",
      rating: 5,
      text: "LearnAI thá»±c sá»± thay Ä‘á»•i cĂ¡ch tĂ´i há»c ToĂ¡n. TrÆ°á»›c Ä‘Ă¢y tĂ´i cá»© lĂ m láº¡i nhá»¯ng bĂ i dá»…, nhÆ°ng giá» há»‡ thá»‘ng luĂ´n Ä‘áº©y tĂ´i vĂ o Ä‘Ăºng vĂ¹ng thĂ¡ch thá»©c. Äiá»ƒm Elo tá»« 800 lĂªn 1050 sau 8 tuáº§n!",
    },
    {
      name: "Tráº§n Thá»‹ Lan",
      role: "Sinh viĂªn nÄƒm 2 Â· Khoa há»c mĂ¡y tĂ­nh",
      avatar: "TTL",
      color: "bg-violet-500",
      rating: 5,
      text: "AI Tutor giáº£i thĂ­ch ráº¥t tá»± nhiĂªn, khĂ´ng chá»‰ Ä‘Æ°a Ä‘Ă¡p Ă¡n mĂ  cĂ²n há»i ngÆ°á»£c láº¡i Ä‘á»ƒ tĂ´i suy nghÄ©. TĂ´i thĂ­ch nháº¥t lĂ  nĂ³ biáº¿t trĂ¬nh Ä‘á»™ cá»§a mĂ¬nh vĂ  khĂ´ng giáº£i thĂ­ch quĂ¡ Ä‘Æ¡n giáº£n hay quĂ¡ khĂ³.",
    },
    {
      name: "LĂª HoĂ ng PhĂºc",
      role: "Sinh viĂªn nÄƒm 4 Â· Ká»¹ thuáº­t pháº§n má»m",
      avatar: "LHP",
      color: "bg-emerald-500",
      rating: 5,
      text: "Dashboard ráº¥t trá»±c quan, tĂ´i tháº¥y rĂµ mĂ¬nh yáº¿u chá»§ Ä‘á» nĂ o vĂ  cáº§n Ă´n bĂ i gĂ¬. Spaced Repetition thá»±c sá»± hiá»‡u quáº£ â€” tĂ´i khĂ´ng cĂ²n quĂªn bĂ i ngay sau khi há»c ná»¯a.",
    },
  ];

  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-16 text-center"
        >
          <span className="font-['JetBrains_Mono',monospace] text-xs text-emerald-400 tracking-[0.2em] uppercase mb-3 block">
            {"//"} Cá»™ng Ä‘á»“ng nĂ³i gĂ¬
          </span>
          <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold text-white">
            Há»c viĂªn{" "}
            <span className="bg-gradient-to-r from-emerald-300 to-violet-400 bg-clip-text text-transparent">
              chia sáº»
            </span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-5">
          {reviews.map(({ name, role, avatar, color, rating, text }, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="rounded-2xl border border-white/7 bg-[#0b0b1e] p-6 flex flex-col hover:border-white/12 transition-colors group"
            >
              <div className="flex gap-0.5 mb-4">
                {Array(rating).fill(0).map((_, j) => (
                  <Star key={j} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-[#c0c0d8] text-sm leading-relaxed flex-1 mb-5">&quot;{text}&quot;</p>
              <div className="flex items-center gap-3 pt-4 border-t border-white/5">
                <div className={`w-9 h-9 rounded-full ${color} flex items-center justify-center text-white text-xs font-bold flex-shrink-0`}>
                  {avatar}
                </div>
                <div>
                  <div className="text-white text-sm font-semibold">{name}</div>
                  <div className="text-[#7878a0] text-xs">{role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   FAQ
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function FAQ() {
  const faqs = [
    {
      q: "Há»‡ thá»‘ng Elo Rating hoáº¡t Ä‘á»™ng nhÆ° tháº¿ nĂ o?",
      a: "Má»—i cĂ¢u há»i vĂ  má»—i há»c viĂªn Ä‘á»u cĂ³ Elo rating riĂªng. Khi báº¡n tráº£ lá»i Ä‘Ăºng cĂ¢u khĂ³, Elo cá»§a báº¡n tÄƒng nhiá»u; tráº£ lá»i sai cĂ¢u dá»…, Elo giáº£m Ă­t. Há»‡ thá»‘ng chá»n cĂ¢u há»i sao cho tá»· lá»‡ Ä‘Ăºng cá»§a báº¡n dao Ä‘á»™ng trong vĂ¹ng 70â€“85% â€” Ä‘iá»ƒm tá»‘i Æ°u cho há»c táº­p theo nghiĂªn cá»©u khoa há»c nháº­n thá»©c.",
    },
    {
      q: "SM-2 Spaced Repetition khĂ¡c gĂ¬ so vá»›i há»c bĂ¬nh thÆ°á»ng?",
      a: "Há»c bĂ¬nh thÆ°á»ng báº¡n Ă´n Ä‘á»u Ä‘áº·n má»—i ngĂ y, khĂ´ng phĂ¢n biá»‡t bĂ i nĂ o Ä‘Ă£ thuá»™c hay chÆ°a. SM-2 tĂ­nh toĂ¡n khoáº£ng cĂ¡ch tá»‘i Æ°u giá»¯a cĂ¡c láº§n Ă´n dá»±a trĂªn má»©c Ä‘á»™ ghi nhá»› cá»§a báº¡n â€” bĂ i Ä‘Ă£ thuá»™c sáº½ Ă´n sau 1 tuáº§n, bĂ i chÆ°a thuá»™c Ă´n sau 1 ngĂ y. Káº¿t quáº£ lĂ  há»c Ă­t hÆ¡n 40% thá»i gian mĂ  nhá»› lĂ¢u hÆ¡n gáº¥p Ä‘Ă´i.",
    },
    {
      q: "AI Tutor Ä‘Æ°á»£c Ä‘Ă o táº¡o trĂªn dá»¯ liá»‡u gĂ¬?",
      a: "AI Tutor Ä‘Æ°á»£c fine-tune trĂªn tĂ i liá»‡u tá»«ng khĂ³a há»c: sĂ¡ch giĂ¡o khoa, slide bĂ i giáº£ng, Ä‘á» thi cÅ© vĂ  bĂ i táº­p máº«u. Khi tráº£ lá»i, nĂ³ cÅ©ng tham chiáº¿u Elo rating hiá»‡n táº¡i cá»§a báº¡n Ä‘á»ƒ Ä‘iá»u chá»‰nh Ä‘á»™ phá»©c táº¡p cá»§a giáº£i thĂ­ch â€” khĂ´ng quĂ¡ Ä‘Æ¡n giáº£n, khĂ´ng quĂ¡ khĂ³.",
    },
    {
      q: "Bloom Taxonomy Ä‘Æ°á»£c tĂ­ch há»£p nhÆ° tháº¿ nĂ o?",
      a: "Má»—i cĂ¢u há»i Ä‘Æ°á»£c phĂ¢n loáº¡i theo 6 cáº¥p Ä‘á»™ nháº­n thá»©c cá»§a Bloom: Nhá»›, Hiá»ƒu, á»¨ng dá»¥ng, PhĂ¢n tĂ­ch, ÄĂ¡nh giĂ¡, SĂ¡ng táº¡o. Há»‡ thá»‘ng khĂ´ng chá»‰ Ä‘áº£m báº£o báº¡n nhá»› kiáº¿n thá»©c, mĂ  cĂ²n phĂ¡t triá»ƒn kháº£ nÄƒng á»©ng dá»¥ng vĂ  tÆ° duy phĂª phĂ¡n â€” Ä‘iá»u mĂ  há»c váº¹t khĂ´ng lĂ m Ä‘Æ°á»£c.",
    },
    {
      q: "TĂ´i cĂ³ thá»ƒ xem tiáº¿n bá»™ cá»§a mĂ¬nh nhÆ° tháº¿ nĂ o?",
      a: "Dashboard cung cáº¥p Ä‘áº§y Ä‘á»§: biá»ƒu Ä‘á»“ Elo theo thá»i gian, báº£n Ä‘á»“ nhiá»‡t thĂ nh tháº¡o tá»«ng chá»§ Ä‘á», thá»‘ng kĂª session há»c táº­p, streak ngĂ y há»c liĂªn tiáº¿p, vĂ  so sĂ¡nh vá»›i trung bĂ¬nh cá»™ng Ä‘á»“ng. Báº¡n cĂ³ thá»ƒ export bĂ¡o cĂ¡o PDF Ä‘á»ƒ chia sáº» vá»›i giĂ¡o viĂªn hoáº·c mentor.",
    },
    {
      q: "LearnAI cĂ³ miá»…n phĂ­ khĂ´ng?",
      a: "HoĂ n toĂ n miá»…n phĂ­ trong giai Ä‘oáº¡n beta. Táº¥t cáº£ tĂ­nh nÄƒng â€” Elo Rating, Spaced Repetition, Dashboard analytics, AI Tutor vĂ  toĂ n bá»™ ngĂ¢n hĂ ng cĂ¢u há»i â€” Ä‘á»u Ä‘Æ°á»£c má»Ÿ khĂ´ng giá»›i háº¡n cho sinh viĂªn Ä‘Äƒng kĂ½.",
    },
  ];

  return (
    <section id="faq" className="relative z-10 py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <span className="font-['JetBrains_Mono',monospace] text-xs text-cyan-400 tracking-[0.2em] uppercase mb-3 block">
            {"//"} CĂ¢u há»i thÆ°á»ng gáº·p
          </span>
          <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-5xl font-extrabold text-white">
            CĂ³ tháº¯c máº¯c?{" "}
            <span className="bg-gradient-to-r from-cyan-300 to-violet-400 bg-clip-text text-transparent">
              ChĂºng tĂ´i giáº£i Ä‘Ă¡p
            </span>
          </h2>
        </motion.div>

        <Accordion.Root type="single" collapsible className="space-y-3">
          {faqs.map(({ q, a }, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
            >
              <Accordion.Item
                value={`item-${i}`}
                className="rounded-xl border border-white/7 bg-[#0b0b1e] overflow-hidden hover:border-white/12 transition-colors"
              >
                <Accordion.Header>
                  <Accordion.Trigger className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left group">
                    <span className="text-sm font-semibold text-white group-hover:text-cyan-200 transition-colors">
                      {q}
                    </span>
                    <ChevronDown className="w-4 h-4 text-[#7878a0] flex-shrink-0 transition-transform duration-200 group-data-[state=open]:rotate-180" />
                  </Accordion.Trigger>
                </Accordion.Header>
                <Accordion.Content className="overflow-hidden data-[state=open]:animate-[slideDown_0.2s_ease] data-[state=closed]:animate-[slideUp_0.2s_ease]">
                  <p className="px-5 pb-5 text-sm text-[#8888a8] leading-relaxed">{a}</p>
                </Accordion.Content>
              </Accordion.Item>
            </motion.div>
          ))}
        </Accordion.Root>
        <style>{`
          @keyframes slideDown { from { height: 0 } to { height: var(--radix-accordion-content-height) } }
          @keyframes slideUp { from { height: var(--radix-accordion-content-height) } to { height: 0 } }
        `}</style>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   CTA
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function CTA() {
  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.65 }}
          className="relative rounded-3xl border border-white/8 overflow-hidden text-center"
        >
          {/* BG */}
          <div className="absolute inset-0 bg-[#0b0b1e]" />
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/8 via-transparent to-violet-500/10" />
          <div
            className="absolute inset-0 opacity-[0.08] bg-cover bg-center"
            style={{ backgroundImage: "url(https://images.unsplash.com/photo-1579567761406-4684ee0c75b6?w=1400&h=600&fit=crop&auto=format)" }}
            aria-hidden="true"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-[#0b0b1e]/30 via-[#0b0b1e]/50 to-[#0b0b1e]/80" />
          {/* Top/bottom glows */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-80 h-px bg-gradient-to-r from-transparent via-cyan-400/60 to-transparent" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-80 h-px bg-gradient-to-r from-transparent via-violet-400/60 to-transparent" />

          <div className="relative z-10 px-8 py-16 md:py-20">
            <span className="font-['JetBrains_Mono',monospace] text-xs text-cyan-400 tracking-[0.2em] uppercase mb-4 block">
              {"//"} Báº¯t Ä‘áº§u hĂ nh trĂ¬nh
            </span>
            <h2 className="font-['Bricolage_Grotesque',sans-serif] text-4xl md:text-6xl font-extrabold text-white mb-6 leading-tight">
              Sáºµn sĂ ng há»c thĂ´ng minh hÆ¡n
              <br />
              <span className="bg-gradient-to-r from-cyan-300 via-cyan-400 to-violet-400 bg-clip-text text-transparent">
                cĂ¹ng AI?
              </span>
            </h2>
            <p className="text-[#8080a8] text-lg mb-10 max-w-xl mx-auto leading-relaxed">
              Tham gia cĂ¹ng 500+ sinh viĂªn Ä‘ang tráº£i nghiá»‡m há»c táº­p cĂ¡ nhĂ¢n hĂ³a thá»±c sá»±. HoĂ n toĂ n miá»…n phĂ­ â€” khĂ´ng cáº§n tháº» tĂ­n dá»¥ng.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-10">
              <button className="group flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-[#06060e] font-semibold text-base hover:from-cyan-400 hover:to-cyan-300 transition-all duration-200 shadow-[0_0_40px_rgba(34,211,238,0.4)] hover:shadow-[0_0_56px_rgba(34,211,238,0.62)]">
                <Zap className="w-4 h-4" />
                ÄÄƒng kĂ½ miá»…n phĂ­
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </button>
              <button className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl border border-white/12 text-[#e0e0f0] font-medium hover:border-violet-400/30 hover:text-violet-200 hover:bg-violet-500/5 transition-all duration-200">
                <RotateCcw className="w-4 h-4" />
                Xem láº¡i demo
              </button>
            </div>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-[#7878a0]">
              {[
                { icon: Shield, text: "Miá»…n phĂ­ 100%" },
                { icon: Users, text: "500+ sinh viĂªn" },
                { icon: Award, text: "Äá» tĂ i NCKH 2024" },
              ].map(({ icon: Icon, text }) => (
                <div key={text} className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-cyan-400" />
                  {text}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   FOOTER
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function Footer() {
  const links = {
    "Sáº£n pháº©m": ["TĂ­nh nÄƒng", "Dashboard", "AI Tutor", "MĂ´n há»c"],
    "NghiĂªn cá»©u": ["Elo Rating", "Spaced Repetition", "Bloom Taxonomy", "Cognition"],
    "LiĂªn há»‡": ["Vá» dá»± Ă¡n", "Äá»™i ngÅ©", "GitHub", "BĂ¡o lá»—i"],
  };

  return (
    <footer className="relative z-10 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6 py-14">
        <div className="grid grid-cols-2 md:grid-cols-[2fr_1fr_1fr_1fr] gap-10 mb-12">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center shadow-[0_0_16px_rgba(34,211,238,0.4)]">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <span className="font-['Bricolage_Grotesque',sans-serif] font-extrabold text-lg text-white">
                Learn<span className="text-cyan-400">AI</span>
              </span>
            </div>
            <p className="text-[#7878a0] text-sm leading-relaxed max-w-xs mb-5">
              Há»c táº­p cĂ¡ nhĂ¢n hĂ³a thá»±c sá»±, Ä‘Æ°á»£c xĂ¢y dá»±ng trĂªn ná»n táº£ng khoa há»c nháº­n thá»©c vĂ  trĂ­ tuá»‡ nhĂ¢n táº¡o.
            </p>
            <div className="flex gap-3">
              {["Gh", "Fb", "Em"].map((s) => (
                <a key={s} href="#" className="w-8 h-8 rounded-lg border border-white/8 bg-white/3 flex items-center justify-center text-xs text-[#7878a0] hover:border-cyan-400/30 hover:text-cyan-300 transition-colors font-['JetBrains_Mono',monospace]">
                  {s}
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <div className="text-xs font-semibold text-white mb-4 tracking-widest uppercase font-['JetBrains_Mono',monospace]">
                {category}
              </div>
              <ul className="space-y-2.5">
                {items.map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm text-[#7878a0] hover:text-cyan-300 transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="pt-6 border-t border-white/5 flex flex-col md:flex-row justify-between gap-3">
          <p className="text-xs text-[#5050780] font-['JetBrains_Mono',monospace]">
            Â© 2024 LearnAI Â· Äá» tĂ i NghiĂªn cá»©u Khoa há»c Sinh viĂªn
          </p>
          <div className="flex gap-5">
            {["Äiá»u khoáº£n", "Báº£o máº­t", "Cookie"].map((t) => (
              <a key={t} href="#" className="text-xs text-[#505070] hover:text-[#9090b8] transition-colors">
                {t}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   ROOT
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
export default function App() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  return (
    <div className="relative min-h-screen overflow-x-hidden" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <KineticBackground />
      <Nav scrolled={scrolled} />
      <main>
        <Hero />
        <Ticker />
        <Stats />
        <Features />
        <Subjects />
        <HowItWorks />
        <AIDemo />
        <Testimonials />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}

