const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

export function getStoredAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token') || localStorage.getItem('admin_token');
}

export function getStoredRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('refresh_token');
}

export function saveAuthTokens(accessToken: string, refreshToken?: string | null, role?: string | null) {
  if (typeof window === 'undefined') return;
  localStorage.setItem('token', accessToken);
  if (role === 'admin' || role === 'teacher') {
    localStorage.setItem('admin_token', accessToken);
  }
  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken);
  }
}

export function clearAuthTokens() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('token');
  localStorage.removeItem('admin_token');
  localStorage.removeItem('refresh_token');
}

async function tryRefreshToken(): Promise<string | null> {
  const rt = getStoredRefreshToken();
  if (!rt) return null;

  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: rt }),
      });
      if (!res.ok) {
        clearAuthTokens();
        return null;
      }
      const data = await res.json();
      if (data?.access_token) {
        saveAuthTokens(data.access_token, data.refresh_token, data.role);
        return data.access_token as string;
      }
      return null;
    } catch {
      return null;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Generic API request helper
 * Tự động đính kèm JWT Access Token và tự động làm mới bằng Refresh Token khi gặp 401.
 */
async function apiRequest<T>(
  endpoint: string,
  options: {
    method?: string;
    body?: unknown;
    contentType?: string;
    customToken?: string | null;
    skipRefresh?: boolean;
  } = {}
): Promise<T> {
  const {
    method = 'GET',
    body,
    contentType = 'application/json',
    customToken,
    skipRefresh = false,
  } = options;

  const defaultToken = getStoredAccessToken();
  const token = customToken !== undefined ? customToken : defaultToken;

  const headers: Record<string, string> = {};
  if (contentType) headers['Content-Type'] = contentType;
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const config: RequestInit = { method, headers };
  if (body && method !== 'GET') {
    config.body = contentType === 'application/json' ? JSON.stringify(body) : (body as string);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${endpoint}`, config);
  } catch {
    throw new Error(
      'Không thể kết nối tới máy chủ Nyvora Backend (cổng 8000). Vui lòng kiểm tra dịch vụ FastAPI đang chạy.'
    );
  }

  if (response.status === 401 && !skipRefresh && token) {
    const refreshedAccess = await tryRefreshToken();
    if (refreshedAccess) {
      headers['Authorization'] = `Bearer ${refreshedAccess}`;
      response = await fetch(`${API_BASE}${endpoint}`, { method, headers, body: config.body });
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || `Lỗi ${response.status}`);
  }

  if (response.status === 204) return {} as T;
  return response.json();
}

/* ══════════════ AUTH ══════════════ */

export interface AuthTokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
  expires_in?: number;
  role?: string | null;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  overall_elo: number;
  role: string;
  teacher_id: number | null;
  created_at: string;
}

export async function register(username: string, email: string, password: string) {
  return apiRequest<UserProfile>('/auth/register', {
    method: 'POST',
    body: { username: username.trim(), email: email.trim(), password },
    skipRefresh: true,
  });
}

export async function login(username: string, password: string): Promise<AuthTokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', username.trim());
  formData.append('password', password);

  let response: Response;
  try {
    response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
  } catch {
    throw new Error(
      'Không thể kết nối tới máy chủ Nyvora Backend (http://localhost:8000). Vui lòng khởi chạy Backend trước khi đăng nhập.'
    );
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Tên đăng nhập hoặc mật khẩu không đúng');
  }

  const data = (await response.json()) as AuthTokenResponse;
  saveAuthTokens(data.access_token, data.refresh_token, data.role);
  return data;
}

export async function logoutUser() {
  const rt = getStoredRefreshToken();
  try {
    if (rt) {
      await apiRequest('/auth/logout', {
        method: 'POST',
        body: { refresh_token: rt },
        skipRefresh: true,
      });
    }
  } catch {
    // Bỏ qua lỗi mạng khi đăng xuất
  } finally {
    clearAuthTokens();
  }
}

export async function getMe(token?: string) {
  return apiRequest<UserProfile>('/auth/me', { customToken: token });
}

export async function updateMe(data: { email?: string; password?: string }) {
  return apiRequest<UserProfile>('/auth/me', {
    method: 'PUT',
    body: data,
  });
}

/* ══════════════ CONTENT ══════════════ */

export interface SubjectItem {
  id: number;
  name: string;
  description: string;
  icon_emoji: string;
  topic_count?: number;
}

export interface TopicItem {
  id: number;
  subject_id: number;
  name: string;
  description: string;
  bloom_level: number;
  order_index: number;
  prerequisites: number[];
  question_count: number;
}

export async function getSubjects() {
  return apiRequest<SubjectItem[]>('/subjects');
}

export async function getTopics(subjectId: number) {
  return apiRequest<TopicItem[]>(`/subjects/${subjectId}/topics`);
}

/* ══════════════ LEARNING & ANALYTICS ══════════════ */

export interface AnswerSubmissionResult {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  elo_change: number;
  new_elo: number;
  xp_earned: number;
  sm2_quality?: number;
  next_review_days?: number;
  easiness_factor?: number;
}

export interface EloHistoryPoint {
  index: number;
  elo: number;
  change: number;
  delta?: number;
  is_correct: boolean;
  timestamp: string;
}

export interface BloomRadarPoint {
  bloom_level: number;
  level: number;
  label: string;
  mastery_percent: number;
  mastery: number;
  unlocked: boolean;
  questions_attempted: number;
}

export interface TopicMasteryItem {
  topic_id: number;
  topic_name: string;
  subject_id?: number;
  subject_name?: string;
  mastery_score: number;
  elo_rating: number;
  bloom_level: number;
  total_attempts: number;
  correct_attempts: number;
  accuracy: number;
  last_practiced?: string | null;
}

export interface ProgressData {
  overall_elo: number;
  total_questions_answered: number;
  accuracy_rate: number;
  current_streak: number;
  due_reviews_count: number;
  topics_mastery: TopicMasteryItem[];
  elo_history: EloHistoryPoint[];
  bloom_radar: BloomRadarPoint[];
}

export interface SpacedReviewCard {
  id: number;
  topic_id: number;
  topic_name: string;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  difficulty_elo: number;
  bloom_level: number;
  repetitions: number;
  interval_days: number;
  easiness_factor: number;
  next_review: string | null;
}

export async function submitAnswer(
  questionId: number,
  selectedAnswer: string,
  timeSpentMs: number,
  hintsUsed: number = 0
) {
  return apiRequest<AnswerSubmissionResult>('/learning/answer', {
    method: 'POST',
    body: {
      question_id: questionId,
      selected_answer: selectedAnswer,
      time_spent_ms: timeSpentMs,
      hints_used: hintsUsed,
    },
  });
}

export async function getNextQuestion(topicId?: number) {
  const query = topicId ? `?topic_id=${topicId}` : '';
  return apiRequest<{
    id: number;
    topic_id: number;
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    difficulty_elo: number;
    bloom_level: number;
    recommendation_reason: string;
  }>(`/learning/next-question${query}`);
}

export async function getProgress() {
  return apiRequest<ProgressData>('/learning/progress');
}

export async function getMastery() {
  return apiRequest<TopicMasteryItem[]>('/learning/mastery');
}

export async function getReviewQueue() {
  return apiRequest<
    Array<{
      id: number;
      topic_id: number;
      question_text: string;
      option_a: string;
      option_b: string;
      option_c: string;
      option_d: string;
      difficulty_elo: number;
      bloom_level: number;
    }>
  >('/learning/review-queue');
}

export async function getDueSpacedReviews() {
  return apiRequest<SpacedReviewCard[]>('/spaced-review/due');
}

export async function submitSpacedReviewAnswer(
  questionId: number,
  selectedAnswer: string,
  timeSpentMs: number,
  hintsUsed: number = 0
) {
  return apiRequest<AnswerSubmissionResult>('/spaced-review/answer', {
    method: 'POST',
    body: {
      question_id: questionId,
      selected_answer: selectedAnswer,
      time_spent_ms: timeSpentMs,
      hints_used: hintsUsed,
    },
  });
}

/* ══════════════ QUIZ ══════════════ */

export async function startQuiz(topicId: number, numQuestions: number = 10) {
  return apiRequest<
    Array<{
      id: number;
      topic_id: number;
      question_text: string;
      option_a: string;
      option_b: string;
      option_c: string;
      option_d: string;
      difficulty_elo: number;
      bloom_level: number;
    }>
  >('/quiz/start', {
    method: 'POST',
    body: { topic_id: topicId, num_questions: numQuestions },
  });
}

/* ══════════════ CHATBOT (PYTHON 3.14.x BACKEND) ══════════════ */

export interface ChatbotRuntimeInfo {
  service: string;
  language: string;
  python_version: string;
  python_series: string;
  sdk: string;
  model: string;
  ai_configured: boolean;
}

export interface ChatbotReply {
  reply: string;
  python_version?: string;
  engine?: string;
}

export async function getChatbotRuntime() {
  return apiRequest<ChatbotRuntimeInfo>('/chat/runtime');
}

export async function sendMessageToBot(message: string, customToken?: string | null) {
  return apiRequest<ChatbotReply>('/chat/', {
    method: 'POST',
    body: { message },
    customToken,
  });
}

export async function sendDemoMessageToBot(
  message: string,
  learnerElo: number = 950,
  history: Array<{ role: string; message: string }> = []
) {
  return apiRequest<ChatbotReply>('/chat/demo', {
    method: 'POST',
    body: {
      message,
      learner_elo: learnerElo,
      history,
    },
    customToken: null,
    skipRefresh: true,
  });
}

export interface ChatHistoryItem {
  id: number;
  role: string;
  message: string;
  created_at: string;
}

export async function getChatHistory(customToken?: string | null) {
  return apiRequest<ChatHistoryItem[]>('/chat/history', { customToken });
}

/* ══════════════ ADMIN & TEACHER HUB ══════════════ */

export async function getAdminStats(token?: string) {
  return apiRequest<{
    total_users: number;
    total_subjects: number;
    total_topics: number;
    total_questions: number;
  }>('/admin/stats', { customToken: token });
}

export async function getAllUsers(token?: string) {
  return apiRequest<UserProfile[]>('/admin/users', { customToken: token });
}

export async function updateUserRole(userId: number, role: string, token?: string) {
  return apiRequest<UserProfile>(`/admin/users/${userId}/role`, {
    method: 'PUT',
    body: { role },
    customToken: token,
  });
}

export async function assignTeacher(userId: number, teacherId: number | null, token?: string) {
  return apiRequest<UserProfile>(`/admin/users/${userId}/teacher`, {
    method: 'PUT',
    body: { teacher_id: teacherId },
    customToken: token,
  });
}

export async function deleteAdminUser(userId: number, token?: string) {
  return apiRequest<{ message: string }>(`/admin/users/${userId}`, {
    method: 'DELETE',
    customToken: token,
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
  return apiRequest<Array<QuestionData & { id: number; created_by_id: number | null }>>(
    '/admin/questions',
    { customToken: token }
  );
}

export async function createAdminQuestion(data: QuestionData, token?: string) {
  return apiRequest<QuestionData & { id: number; created_by_id: number | null }>(
    '/admin/questions',
    {
      method: 'POST',
      body: data,
      customToken: token,
    }
  );
}

export async function updateAdminQuestion(id: number, data: QuestionData, token?: string) {
  return apiRequest<QuestionData & { id: number; created_by_id: number | null }>(
    `/admin/questions/${id}`,
    {
      method: 'PUT',
      body: data,
      customToken: token,
    }
  );
}

export async function deleteAdminQuestion(id: number, token?: string) {
  return apiRequest<{ message: string }>(`/admin/questions/${id}`, {
    method: 'DELETE',
    customToken: token,
  });
}

export interface AlgorithmConfig {
  k_learner: number;
  k_item: number;
  zpd_lower_prob: number;
  zpd_upper_prob: number;
}

export async function getAlgorithmConfig(token?: string) {
  return apiRequest<AlgorithmConfig>('/admin/config', { customToken: token });
}

export async function updateAlgorithmConfig(config: AlgorithmConfig, token?: string) {
  return apiRequest<AlgorithmConfig>('/admin/config', {
    method: 'PUT',
    body: config,
    customToken: token,
  });
}

export async function triggerAdminSeed(token?: string) {
  return apiRequest<{
    message: string;
    summary: { subjects: number; topics: number; questions: number };
  }>('/admin/seed', {
    method: 'POST',
    customToken: token,
  });
}
