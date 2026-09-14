import api from './axios'

export const projectsApi = {
    // Список с фильтрами
    list: (filters) => api.get('/projects', { params: filters }),

    // Детали
    getById: (projectId) => api.get(`/projects/${projectId}`),

    // CRUD (только заказчик)
    create: (data) => api.post('/projects', data),
    update: (projectId, data) => api.put(`/projects/${projectId}`, data),
    remove: (projectId) => api.delete(`/projects/${projectId}`),

    // Статусы
    publish: (projectId) => api.patch(`/projects/${projectId}/publish`),
    cancel: (projectId) => api.patch(`/projects/${projectId}/cancel`),
    assign: (projectId, freelancerId) =>
        api.patch(`/projects/${projectId}/assign`, null, {
            params: { freelancer_id: freelancerId },
        }),

    // Мои проекты
    myProjects: (params) => api.get('/projects/me', { params }),
    workingProjects: (params) => api.get('/projects/me/working', { params }),
}