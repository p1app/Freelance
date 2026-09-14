import api from './axios'

export const milestonesApi = {
    // Список этапов контракта
    listByContract: (contractId, params) =>
        api.get(`/contracts/${contractId}/milestones`, { params }),

    // Создать этап
    create: (contractId, data) =>
        api.post(`/contracts/${contractId}/milestones`, data),

    // Получить этап
    getById: (milestoneId) => api.get(`/milestones/${milestoneId}`),

    // Обновить / удалить
    update: (milestoneId, data) =>
        api.put(`/milestones/${milestoneId}`, data),
    remove: (milestoneId) =>
        api.delete(`/milestones/${milestoneId}`),

    // Статусы
    complete: (milestoneId) =>
        api.patch(`/milestones/${milestoneId}/complete`),
    approve: (milestoneId) =>
        api.patch(`/milestones/${milestoneId}/approve`),
}