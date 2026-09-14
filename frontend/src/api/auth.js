import api from './axios'

export const authApi = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    refresh: (refreshToken) =>
        api.post('/auth/refresh', null, {
            headers: {
                Authorization: `Bearer ${refreshToken}`,
            },
        }),
    logout: () => api.post('/auth/logout'),
}