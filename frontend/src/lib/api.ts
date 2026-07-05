const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Generic API request helper
 * Tự động attach JWT token từ localStorage
 */
async function apiRequest<T>(endpoint: string, options: {
  method?: string;
  body?: unknown;
  contentType?: string;
  customToken?: string | null;
} = {}): Promise<T> {
  const { method = 'GET', body, contentType = 'application/json', customToken } = options;
  const defaultToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const token = customToken !== undefined ? customToken : defaultToken;

  const headers: Record<string, string> = {};
  if (contentType) headers['Content-Type'] = contentType;
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const config: RequestInit = { method, headers };
  if (body && method !== 'GET') {
    config.body = contentType === 'application/json' ? JSON.stringify(body) : body as string;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Lỗi ${response.status}`);
  }

  if (response.status === 204) return {} as T;
  return response.json();
}

/* ══════════════ AUTH ══════════════ */

export async function register(username: string, email: string, password: string) {
  return apiRequest<{ id: number; username: string }>('/auth/register', {
    method: 'POST',
    body: { username, email, password },
  });
}

export async function login(username: string, password: string) {
  // Backend auth dùng form-urlencoded (OAuth2 standard)
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Đăng nhập thất bại');
  }

  return response.json() as Promise<{ access_token: string; token_type: string }>;
}

export async function getMe(token?: string) {
  return apiRequest<{
    id: number; username: string; email: string; overall_elo: number; role: string; teacher_id: number | null; created_at: string;
  }>('/auth/me', { customToken: token });
}

export async function updateMe(data: { email?: string; password?: string }) {
  return apiRequest<{
    id: number; username: string; email: string; overall_elo: number; role: string; teacher_id: number | null; created_at: string;
  }>('/auth/me', {
    method: 'PUT',
    body: data,
  });
}

/* ══════════════ CONTENT ══════════════ */

export async function getSubjects() {
  return apiRequest<Array<{
    id: number; name: string; description: string; icon_emoji: string;
  }>>('/subjects');
}

export async function getTopics(subjectId: number) {
  return apiRequest<Array<{
    id: number; name: string; description: string; bloom_level: number;
  }>>(`/subjects/${subjectId}/topics`);
}

/* ══════════════ LEARNING ══════════════ */

export async function submitAnswer(questionId: number, selectedAnswer: string, timeSpentMs: number) {
  return apiRequest<{
    is_correct: boolean; correct_answer: string; explanation: string;
    elo_change: number; new_elo: number; xp_earned: number;
  }>('/learning/answer', {
    method: 'POST',
    body: { question_id: questionId, selected_answer: selectedAnswer, time_spent_ms: timeSpentMs },
  });
}

export async function getNextQuestion(topicId?: number) {
  const query = topicId ? `?topic_id=${topicId}` : '';
  return apiRequest<{
    id: number; question_text: string; option_a: string; option_b: string;
    option_c: string; option_d: string; difficulty_elo: number; bloom_level: number;
  }>(`/learning/next-question${query}`);
}

export async function getProgress() {
  return apiRequest<{
    overall_elo: number; total_questions_answered: number; accuracy_rate: number;
    current_streak: number; topics_mastery: Array<{
      topic_id: number; topic_name: string; mastery_score: number; elo_rating: number;
      bloom_level: number; total_attempts: number; correct_attempts: number;
    }>;
  }>('/learning/progress');
}

export async function getMastery() {
  return apiRequest<Array<{
    topic_id: number; topic_name: string; mastery_score: number;
    elo_rating: number; bloom_level: number;
  }>>('/learning/mastery');
}

export async function getReviewQueue() {
  return apiRequest<Array<{
    id: number; question_text: string; next_review: string;
  }>>('/learning/review-queue');
}

/* ══════════════ QUIZ ══════════════ */

export async function startQuiz(topicId: number, numQuestions: number = 10) {
  return apiRequest<Array<{
    id: number; question_text: string; option_a: string; option_b: string;
    option_c: string; option_d: string; difficulty_elo: number; bloom_level: number;
  }>>('/quiz/start', {
    method: 'POST',
    body: { topic_id: topicId, num_questions: numQuestions },
  });
}

/* ══════════════ CHATBOT ══════════════ */

export async function sendMessageToBot(message: string) {
  return apiRequest<{ reply: string }>('/chat/', {
    method: 'POST',
    body: { message },
  });
}

export interface ChatHistoryItem {
  id: number;
  role: string;
  message: string;
  created_at: string;
}

export async function getChatHistory() {
  return apiRequest<ChatHistoryItem[]>('/chat/history');
}

/* ══════════════ ADMIN ══════════════ */

export async function getAdminStats(token?: string) {
  return apiRequest<{
    total_users: number; total_subjects: number; total_topics: number; total_questions: number;
  }>('/admin/stats', { customToken: token });
}

export async function getAllUsers(token?: string) {
  return apiRequest<Array<{
    id: number; username: string; email: string; overall_elo: number; role: string; teacher_id: number | null; created_at: string;
  }>>('/admin/users', { customToken: token });
}

export async function updateUserRole(userId: number, role: string, token?: string) {
  return apiRequest<{
    id: number; username: string; email: string; overall_elo: number; role: string; teacher_id: number | null; created_at: string;
  }>(`/admin/users/${userId}/role`, {
    method: 'PUT',
    body: { role },
    customToken: token
  });
}

export async function assignTeacher(userId: number, teacherId: number | null, token?: string) {
  return apiRequest<{
    id: number; username: string; email: string; overall_elo: number; role: string; teacher_id: number | null; created_at: string;
  }>(`/admin/users/${userId}/teacher`, {
    method: 'PUT',
    body: { teacher_id: teacherId },
    customToken: token
  });
}

export async function deleteAdminUser(userId: number, token?: string) {
  return apiRequest<{ message: string }>(`/admin/users/${userId}`, {
    method: 'DELETE',
    customToken: token
  });
}

export interface QuestionData {
  id?: number;
  topic_id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: string;
  explanation?: string;
  difficulty_elo: number;
  bloom_level: number;
}

export async function getAdminQuestions(token?: string) {
  return apiRequest<Array<QuestionData & { id: number, created_by_id: number | null }>>('/admin/questions', { customToken: token });
}

export async function createAdminQuestion(data: QuestionData, token?: string) {
  return apiRequest<QuestionData & { id: number, created_by_id: number | null }>('/admin/questions', {
    method: 'POST',
    body: data,
    customToken: token
  });
}

export async function updateAdminQuestion(id: number, data: QuestionData, token?: string) {
  return apiRequest<QuestionData & { id: number, created_by_id: number | null }>(`/admin/questions/${id}`, {
    method: 'PUT',
    body: data,
    customToken: token
  });
}

export async function deleteAdminQuestion(id: number, token?: string) {
  return apiRequest<{ message: string }>(`/admin/questions/${id}`, {
    method: 'DELETE',
    customToken: token
  });
}
