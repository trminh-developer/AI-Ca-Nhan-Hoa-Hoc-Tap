'use client';

import { useState, useRef, useEffect } from 'react';
import {
  sendMessageToBot,
  sendDemoMessageToBot,
  getChatHistory,
  getChatbotRuntime,
} from '@/lib/api';
import styles from './chatbot.module.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
}

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [pythonVersion, setPythonVersion] = useState('3.14');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Chào bạn! Mình là Trợ giảng Ảo Nyvora (vận hành trên Python 3.14). Bạn cần mình hỗ trợ bài học nào hôm nay?',
      sender: 'bot',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const hasLoadedHistoryRef = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    getChatbotRuntime()
      .then((info) => {
        if (info?.python_version) {
          setPythonVersion(info.python_version);
        }
      })
      .catch(() => {
        // Giữ nhãn mặc định Python 3.14 nếu Backend chưa bật
      });

    const activeToken =
      typeof window !== 'undefined'
        ? localStorage.getItem('token') || localStorage.getItem('admin_token')
        : null;

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
          // Không ghi đè tin nhắn chào mừng nếu phiên đăng nhập hết hạn
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
    const recentHistory = messages.slice(-8).map((m) => ({
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
      const activeToken =
        typeof window !== 'undefined'
          ? localStorage.getItem('token') || localStorage.getItem('admin_token')
          : null;

      const res = activeToken
        ? await sendMessageToBot(userText, activeToken)
        : await sendDemoMessageToBot(userText, 1200, recentHistory);

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
          text: '⚠️ Không thể kết nối tới máy chủ Chatbot Python 3.14. Vui lòng kiểm tra Backend FastAPI (cổng 8000) đã khởi chạy chưa nhé!',
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
              <h3 className={styles.title}>🧠 Trợ giảng AI</h3>
              <span className={styles.runtimeBadge}>🐍 Python {pythonVersion}</span>
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
                {msg.text}
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
              placeholder="Hỏi Trợ giảng AI (Python 3.14)..."
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
          aria-label="Mở Trợ giảng AI Python 3.14"
        >
          💬
        </button>
      )}
    </div>
  );
}
