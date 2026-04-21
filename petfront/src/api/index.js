// src/api/index.js
// Все вызовы к нашему FastAPI бэкенду

import api from './client'

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (email, password, username) =>
    api.post('/auth/register', { email, password, username }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  logout: () =>
    api.post('/auth/logout'),
  me: () =>
    api.get('/auth/me'),
}

// ── Pets ─────────────────────────────────────────────────────────────────────
export const petsApi = {
  list: () =>
    api.get('/pets/'),
  get: (id) =>
    api.get(`/pets/${id}`),
  create: (data) =>
    api.post('/pets/', data),
  update: (id, data) =>
    api.put(`/pets/${id}`, data),
  delete: (id) =>
    api.delete(`/pets/${id}`),

  // Медкарта
  getHealth: (petId, params = {}) =>
    api.get(`/pets/${petId}/health`, { params }),
  addHealth: (petId, data) =>
    api.post(`/pets/${petId}/health`, data),
  deleteHealth: (petId, recId) =>
    api.delete(`/pets/${petId}/health/${recId}`),

  // Дневник поведения
  getBehaviour: (petId, days = 30) =>
    api.get(`/pets/${petId}/behaviour`, { params: { days } }),
  addBehaviour: (petId, data) =>
    api.post(`/pets/${petId}/behaviour`, data),
}

// ── Forum ────────────────────────────────────────────────────────────────────
export const forumApi = {
  list: (params = {}) =>
    api.get('/forum/', { params }),
  get: (id) =>
    api.get(`/forum/${id}`),
  create: (data) =>
    api.post('/forum/', data),
  delete: (id) =>
    api.delete(`/forum/${id}`),
  like: (id) =>
    api.post(`/forum/${id}/like`),

  // Комментарии
  getComments: (postId) =>
    api.get(`/forum/${postId}/comments`),
  addComment: (postId, body, parentId = null) =>
    api.post(`/forum/${postId}/comments`, { body, parent_id: parentId }),
  deleteComment: (postId, commentId) =>
    api.delete(`/forum/${postId}/comments/${commentId}`),
}

// ── AI ───────────────────────────────────────────────────────────────────────
export const aiApi = {
  send: (message, petId = null) =>
    api.post('/ai/chat', { message, pet_id: petId }),
  history: (petId = null, limit = 50) =>
    api.get('/ai/chat', { params: { pet_id: petId, limit } }),
  clear: (petId = null) =>
    api.delete('/ai/chat', { params: { pet_id: petId } }),
  hints: (species = null) =>
    api.get('/ai/hints', { params: { species } }),
}
