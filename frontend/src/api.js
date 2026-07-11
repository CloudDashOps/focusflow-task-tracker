import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Get all tasks
export const fetchTasks = async () => {
  try {
    const response = await apiClient.get('/tasks');
    return response.data;
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw error;
  }
};

// Create a new task
export const createTask = async (task) => {
  try {
    const response = await apiClient.post('/tasks', task);
    return response.data;
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
};

// Update a task (toggle completion or update title)
export const updateTask = async (taskId, updates) => {
  try {
    const response = await apiClient.put(`/tasks/${taskId}`, updates);
    return response.data;
  } catch (error) {
    console.error('Error updating task:', error);
    throw error;
  }
};

// Delete a task
export const deleteTask = async (taskId) => {
  try {
    const response = await apiClient.delete(`/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting task:', error);
    throw error;
  }
};
