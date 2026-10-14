import axios from 'axios';

const defaultBase = typeof window !== 'undefined' && window.location?.hostname
  ? `http://${window.location.hostname}:8000`
  : 'http://localhost:8000';
const rawBase = import.meta.env.VITE_API_BASE_URL || defaultBase;
const cleanBase = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase;
export const API_BASE_URL = cleanBase.endsWith('/api/v1') ? cleanBase : `${cleanBase}/api/v1`;
export const ROOT_URL = cleanBase.replace(/\/api\/v1$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Attach Authorization Bearer token to all outgoing requests if stored
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // If 401 Unauthorized occurs on an authenticated route, clear stored session
    if (error.response?.status === 401 && !error.config.url.includes('/auth/login')) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }

    const errorDetails = {
      message:
        error.response?.data?.detail ||
        error.message ||
        'An unexpected network error occurred',
      status: error.response?.status,
      data: error.response?.data,
    };
    return Promise.reject(errorDetails);
  }
);

export const authApi = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  getMe: () => apiClient.get('/auth/me'),
  logout: () => apiClient.post('/auth/logout'),
};

export const userApi = {
  list: (params) => apiClient.get('/users', { params }),
  get: (id) => apiClient.get(`/users/${id}`),
  updateRole: (id, role) => apiClient.patch(`/users/${id}/role`, { role }),
  updateStatus: (id, isActive) => apiClient.patch(`/users/${id}/status`, { is_active: isActive }),
  delete: (id) => apiClient.delete(`/users/${id}`),
};

export const healthApi = {
  checkHealth: async () => {
    const res = await axios.get(`${ROOT_URL}/health`);
    return res.data;
  },
  checkReady: async () => {
    const res = await axios.get(`${ROOT_URL}/ready`);
    return res.data;
  },
};

export const feedbackApi = {
  list: (params) => apiClient.get('/feedback', { params }),
  get: (id) => apiClient.get(`/feedback/${id}`),
  create: (data) => apiClient.post('/feedback', data),
  update: (id, data) => apiClient.patch(`/feedback/${id}`, data),
  delete: (id) => apiClient.delete(`/feedback/${id}`),
  analyze: (id) => apiClient.post(`/feedback/${id}/analyze`),
  batchAnalyze: (params) => apiClient.post('/feedback/batch-analyze', null, { params }),
  analyzeAsync: (id) => apiClient.post(`/feedback/${id}/analyze-async`),
  batchAnalyzeAsync: (params) => apiClient.post('/feedback/batch-analyze-async', null, { params }),
};

export const tasksApi = {
  getStatus: (taskId) => apiClient.get(`/tasks/${taskId}`),
};

export const analyticsApi = {
  getOverview: () => apiClient.get('/analytics/overview'),
  getSentiment: () => apiClient.get('/analytics/sentiment'),
  getCategories: () => apiClient.get('/analytics/categories'),
  getTrends: (params) => apiClient.get('/analytics/trends', { params }),
};
