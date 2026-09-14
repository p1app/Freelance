import axios from 'axios'
import { tokenUtils } from '@/utils/token'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 15000,
})

// ─────────────────────────────────────────────
// REQUEST INTERCEPTOR
// ─────────────────────────────────────────────
api.interceptors.request.use(
    (config) => {
        const token = tokenUtils.getAccessToken()
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// ─────────────────────────────────────────────
// RESPONSE INTERCEPTOR — авто-refresh
// ─────────────────────────────────────────────
let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error)
        } else {
            prom.resolve(token)
        }
    })
    failedQueue = []
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        // НЕ рефрешим для login/register/refresh
        const skipUrls = ['/auth/login', '/auth/register', '/auth/refresh']
        const shouldSkip = skipUrls.some((url) => originalRequest.url?.includes(url))

        // Если 401 и это не запрос на login/register/refresh
        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !shouldSkip
        ) {
            // Если уже идёт refresh — ждём
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject })
                })
                    .then((token) => {
                        originalRequest.headers.Authorization = `Bearer ${token}`
                        return api(originalRequest)
                    })
                    .catch((err) => Promise.reject(err))
            }

            originalRequest._retry = true
            isRefreshing = true

            const refreshToken = tokenUtils.getRefreshToken()

            if (!refreshToken) {
                tokenUtils.clearTokens()
                window.location.href = '/login'
                return Promise.reject(error)
            }

            try {
                // Вариант 1: refresh-токен в заголовке
                const response = await axios.post(
                    `${import.meta.env.VITE_API_URL || '/api'}/auth/refresh`,
                    null,
                    {
                        headers: {
                            Authorization: `Bearer ${refreshToken}`,
                        },
                    }
                )

                const { access_token, refresh_token: newRefresh } = response.data

                tokenUtils.setTokens(access_token, newRefresh)
                api.defaults.headers.common.Authorization = `Bearer ${access_token}`
                originalRequest.headers.Authorization = `Bearer ${access_token}`

                processQueue(null, access_token)
                return api(originalRequest)
            } catch (refreshError) {
                processQueue(refreshError, null)
                tokenUtils.clearTokens()
                window.location.href = '/login'
                return Promise.reject(refreshError)
            } finally {
                isRefreshing = false
            }
        }

        return Promise.reject(error)
    }
)

export default api