'use client';

import { useState, useRef, useEffect } from 'react';
import { sendMessageToBot } from '@/lib/api';
import styles from './chatbot.module.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
}

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'Chào bạn! Mình là Trợ giảng Ảo LearnAI. Bạn cần giúp gì nào?', sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { id: Date.now().toString(), text: userText, sender: 'user' }]);
    setIsLoading(true);

    try {
      // Call backend
      const res = await sendMessageToBot(userText);
      setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), text: res.reply, sender: 'bot' }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        id: (Date.now() + 1).toString(), 
        text: 'Xin lỗi, hệ thống đang bận hoặc bạn chưa đăng nhập. Vui lòng thử lại sau!', 
        sender: 'bot' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatbotWrapper}>
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.header}>
            <h3 className={styles.title}>🧠 Trợ giảng AI</h3>
            <button className={styles.closeBtn} onClick={() => setIsOpen(false)}>✕</button>
          </div>
          
          <div className={styles.messages}>
            {messages.map((msg) => (
              <div 
                key={msg.id} 
                className={`${styles.message} ${msg.sender === 'user' ? styles.userMessage : styles.botMessage}`}
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
              placeholder="Nhập câu hỏi..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" className={styles.sendBtn} disabled={!input.trim() || isLoading}>
              ↑
            </button>
          </form>
        </div>
      )}

      {!isOpen && (
        <button className={styles.floatingBtn} onClick={() => setIsOpen(true)}>
          💬
        </button>
      )}
    </div>
  );
}
