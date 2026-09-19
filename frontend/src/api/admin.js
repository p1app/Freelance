import api from './axios'

export const adminApi = {
    // Пользователи
    listUsers: (params) => api.get('/admin/users', { params }),
    getUser: (userId) => api.get(`/admin/users/${userId}`),
    blockUser: (userId) =>
        api.patch(`/admin/users/${userId}/block`),
    unblockUser: (userId) =>
        api.patch(`/admin/users/${userId}/unblock`),

    // Проекты
    listProjects: (params) => api.get('/admin/projects', { params }),
    deleteProject: (projectId) =>
        api.delete(`/admin/projects/${projectId}`),
    restoreProject: (projectId) =>
        api.patch(`/admin/projects/${projectId}/restore`),

    // Статистика
    stats: () => api.get('/admin/stats'),
}