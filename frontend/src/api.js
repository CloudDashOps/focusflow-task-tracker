import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let authToken = '';
if (typeof window !== 'undefined' && window.localStorage) {
  authToken = localStorage.getItem('taskTrackerToken') || '';
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  if (authToken) {
        config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

export const setAuthToken = (token) => {
  authToken = token;
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }
  if (token) {
    localStorage.setItem('taskTrackerToken', token);
  } else {
    localStorage.removeItem('taskTrackerToken');
  }
};

export const signup = async ({ email, password }) => {
  const response = await apiClient.post('/auth/signup', { email, password });
  return response.data;
};

export const login = async ({ email, password }) => {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
};

export const fetchTasks = async () => {
  const response = await apiClient.get('/tasks');
  return response.data;
};

export const createTask = async (task) => {
  const response = await apiClient.post('/tasks', task);
  return response.data;
};

export const updateTask = async (taskId, updates) => {
  const response = await apiClient.put(`/tasks/${taskId}`, updates);
  return response.data;
};

export const deleteTask = async (taskId) => {
  const response = await apiClient.delete(`/tasks/${taskId}`);
  return response.data;
};

