// src/api/client.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,  // нужно для refresh cookie
})

// ── Читаем токен из zustand persist (localStorage) ──────────────────────────
function getToken() {
  try {
    const raw = localStorage.getItem('pc-auth')
    return JSON.parse(raw)?.state?.token ?? null
  } catch { return null }
}

function setToken(token) {
  try {
    const raw = localStorage.getItem('pc-auth')
    if (!raw) return
    const parsed = JSON.parse(raw)
    parsed.state.token = token
    localStorage.setItem('pc-auth', JSON.stringify(parsed))
  } catch {}
}

// ── Добавляем Bearer-токен к каждому запросу ────────────────────────────────
api.interceptors.request.use(cfg => {
  const token = getToken()
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// ── Авторефреш при 401 ───────────────────────────────────────────────────────
let refreshing = null

api.interceptors.response.use(
  r => r,
  async err => {
    const orig = err.config
    if (
      err.response?.status !== 401 ||
      orig._retry ||
      orig.url?.includes('/auth/')
    ) return Promise.reject(err)

    orig._retry = true

    if (!refreshing) {
      refreshing = axios
        .post('/api/v1/auth/refresh', {}, { withCredentials: true })
        .then(({ data }) => { setToken(data.access_token); return data.access_token })
        .catch(() => { window.location.href = '/login'; return null })
        .finally(() => { refreshing = null })
    }

    const token = await refreshing
    if (!token) return Promise.reject(err)
    orig.headers.Authorization = `Bearer ${token}`
    return api(orig)
  }
)

// Парсим ошибки FastAPI → читаемая строка
export function errMsg(err) {
  const d = err?.response?.data
  if (!d) return 'Нет соединения с сервером'
  if (Array.isArray(d.detail)) return d.detail.map(e => e.msg).join(', ')
  if (typeof d.detail === 'string') return d.detail
  return 'Что-то пошло не так'
}

export default api
