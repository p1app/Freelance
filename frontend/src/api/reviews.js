import api from './axios'

export const reviewsApi = {
    // Создать отзыв по контракту
    create: (contractId, data) =>
        api.post(`/contracts/${contractId}/reviews`, data),

    // Отзывы по контракту
    listByContract: (contractId) =>
        api.get(`/contracts/${contractId}/reviews`),

    // Отзывы о пользователе
    listByUser: (userId, params) =>
        api.get(`/users/${userId}/reviews`, { params }),

    // Статистика отзывов
    statsByUser: (userId) =>
        api.get(`/users/${userId}/reviews/stats`),
}