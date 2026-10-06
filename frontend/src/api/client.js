import axios from 'axios'

// The frontend only ever talks to our own FastAPI backend. The SerpApi
// key lives on the backend and is never exposed here.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://carriermind-ai.onrender.com/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach the auth token automatically if one is stored (used once the
// auth flow is wired up in a later step; harmless no-op until then).
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('cg_access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Normalize error shape so components can rely on `error.message` and
// optional `error.status` without inspecting Axios internals everywhere.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    const message =
      (typeof detail === 'string' && detail) ||
      error.message ||
      'Something went wrong talking to the CareerGraph AI backend.'
    return Promise.reject({ status, message, raw: error })
  }
)

export default apiClient
