import api from './axios'

export const contractsApi = {
    // Мои контракты (роль определяется автоматически)
    myContracts: (params) => api.get('/contracts/me', { params }),

    // Детали контракта
    getById: (contractId) => api.get(`/contracts/${contractId}`),

    // Действия
    complete: (contractId) =>
        api.patch(`/contracts/${contractId}/complete`),
    cancel: (contractId) =>
        api.patch(`/contracts/${contractId}/cancel`),
}