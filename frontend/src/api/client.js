// =====================================================
// src/api/client.js — Axios API client
// =====================================================
// Yeh ek central place hai saari API calls ke liye.
// Token automatically har request mein add hoga.

import axios from "axios";

// Backend ka URL
const API_URL = "http://localhost:8000";

// Axios instance — default config ke saath
const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — har request se pehle token add karo
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — 401 aane par logout karo
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ---- Auth APIs ----
export const authAPI = {
  login: (data) => api.post("/auth/login", data),
  register: (data) => api.post("/auth/register", data),
  me: () => api.get("/auth/me"),
};

// ---- Document APIs ----
export const documentAPI = {
  upload: (formData) =>
    api.post("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  list: () => api.get("/documents/"),
  delete: (id) => api.delete(`/documents/${id}`),
  reprocess: (id) => api.post(`/documents/${id}/reprocess`),
  assignPermission: (data) => api.post("/documents/permissions", data),
  getPermissions: (docId) => api.get(`/documents/${docId}/permissions`),
  revokePermission: (permId) => api.delete(`/documents/permissions/${permId}`),
};

// ---- Chat APIs ----
export const chatAPI = {
  ask: (data) => api.post("/chat/ask", data),
  conversations: () => api.get("/chat/conversations"),
  messages: (convId) => api.get(`/chat/conversations/${convId}/messages`),
  deleteConversation: (id) => api.delete(`/chat/conversations/${id}`),
};

// ---- Admin APIs ----
export const adminAPI = {
  stats: () => api.get("/admin/stats"),
  users: () => api.get("/admin/users"),
  createUser: (data) => api.post("/admin/users", data),
  toggleUser: (id) => api.put(`/admin/users/${id}/toggle`),
  groups: () => api.get("/admin/groups"),
  createGroup: (data) => api.post("/admin/groups", data),
  addMember: (groupId, data) => api.post(`/admin/groups/${groupId}/members`, data),
  activity: () => api.get("/admin/activity"),
};

export default api;
