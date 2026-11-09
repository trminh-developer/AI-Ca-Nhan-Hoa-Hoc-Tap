'use client';

import { useState, useRef, useEffect } from 'react';
import {
  sendMessageToBot,
  sendDemoMessageToBot,
  getChatHistory,
  getChatbotRuntime,
  getStoredAccessToken,
} from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import MathText from '@/components/ui/MathText';
import styles from './chatbot.module.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
}

export default function Chatbot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [pythonVersion, setPythonVersion] = useState('3.14.0');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Chào bạn! Mình là **Trợ giảng Socratic AI Nyvora** (vận hành trên **Python 3.14** & `google-genai`). Mình sẽ gợi mở tư duy từng bước theo điểm Elo của bạn. Bạn đang thắc mắc bài toán hay đoạn code nào?',
      sender: 'bot',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const hasLoadedHistoryRef = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const learnerElo = user?.overall_elo ?? 1200;
  const socraticTier =
    learnerElo < 1200
      ? 'Cơ bản (Scaffolding)'
      : learnerElo <= 1800
      ? 'Trung cấp (Socratic)'
      : 'Chuyên sâu (Hàn lâm)';

  useEffect(() => {
    if (!isOpen) return;

    getChatbotRuntime()
      .then((info) => {
        if (info?.python_version) {
          setPythonVersion(info.python_version);
        }
      })
      .catch(() => {
        // Giữ nhãn mặc định Python 3.14.0
      });

    const activeToken = getStoredAccessToken();

    if (activeToken && !hasLoadedHistoryRef.current) {
      hasLoadedHistoryRef.current = true;
      getChatHistory(activeToken)
        .then((history) => {
          if (history && history.length > 0) {
            const formatted: Message[] = history.map((h) => ({
              id: h.id.toString(),
              text: h.message,
              sender: h.role === 'user' ? 'user' : 'bot',
            }));
            setMessages(formatted);
          }
        })
        .catch(() => {
          // Giữ tin nhắn chào mừng nếu chưa có lịch sử
        });
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    const recentHistory = messages.slice(-10).map((m) => ({
      role: m.sender === 'user' ? 'user' : 'model',
      message: m.text,
    }));

    setInput('');
    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), text: userText, sender: 'user' },
    ]);
    setIsLoading(true);

    try {
      const activeToken = getStoredAccessToken();

      const res = activeToken
        ? await sendMessageToBot(userText, activeToken)
        : await sendDemoMessageToBot(userText, learnerElo, recentHistory);

      if (res.python_version) {
        setPythonVersion(res.python_version);
      }

      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), text: res.reply, sender: 'bot' },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          text: '⚠️ Không thể kết nối tới máy chủ Socratic AI Python 3.14. Vui lòng kiểm tra Backend FastAPI (cổng 8000) đã khởi chạy chưa nhé!',
          sender: 'bot',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatbotWrapper}>
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.header}>
            <div className={styles.headerInfo}>
              <h3 className={styles.title}>🧠 Socratic AI Tutor</h3>
              <span className={styles.runtimeBadge}>
                🐍 Py {pythonVersion} • {socraticTier}
              </span>
            </div>
            <button
              type="button"
              className={styles.closeBtn}
              onClick={() => setIsOpen(false)}
              aria-label="Đóng khung chat"
            >
              ✕
            </button>
          </div>

          <div className={styles.messages}>
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`${styles.message} ${
                  msg.sender === 'user' ? styles.userMessage : styles.botMessage
                }`}
              >
                <MathText content={msg.text} block />
              </div>
            ))}

            {isLoading && (
              <div className={styles.loading}>
                <div className={styles.dot}></div>
                <div className={styles.dot}></div>
                <div className={styles.dot}></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className={styles.inputArea} onSubmit={handleSend}>
            <input
              type="text"
              className={styles.input}
              placeholder={`Hỏi Socratic Tutor (Elo ${Math.round(learnerElo)})...`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className={styles.sendBtn}
              disabled={!input.trim() || isLoading}
              aria-label="Gửi tin nhắn"
            >
              ↑
            </button>
          </form>
        </div>
      )}

      {!isOpen && (
        <button
          type="button"
          className={styles.floatingBtn}
          onClick={() => setIsOpen(true)}
          aria-label="Mở Trợ giảng Socratic AI Python 3.14"
        >
          💬
        </button>
      )}
    </div>
  );
}
