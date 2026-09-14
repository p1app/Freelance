import api from './axios'

export const proposalsApi = {
    // Список откликов на проект (только заказчик)
    listByProject: (projectId, params) =>
        api.get(`/projects/${projectId}/proposals`, { params }),

    // Мои отклики (только фрилансер)
    myProposals: (params) => api.get('/proposals/me', { params }),

    // Создать отклик
    create: (projectId, data) =>
        api.post(`/projects/${projectId}/proposals`, data),

    // Обновить / отозвать
    update: (proposalId, data) => api.put(`/proposals/${proposalId}`, data),
    withdraw: (proposalId) => api.delete(`/proposals/${proposalId}`),

    // Принять / отклонить
    accept: (proposalId) => api.patch(`/proposals/${proposalId}/accept`),
    reject: (proposalId) => api.patch(`/proposals/${proposalId}/reject`),
}