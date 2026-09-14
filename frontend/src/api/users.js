import api from './axios'

export const usersApi = {
    // Свой профиль
    getProfile: () => api.get('/users/me'),
    updateProfile: (data) => api.put('/users/me', data),
    deleteProfile: () => api.delete('/users/me'),
    getStats: () => api.get('/users/me/stats'),

    // Публичные
    getById: (userId) => api.get(`/users/${userId}`),
    getFreelancers: (filters) =>
        api.get('/users/freelancers', { params: filters }),
}