import api from './axios'

export const chatApi = {
    // История сообщений
    listMessages: (contractId, params) =>
        api.get(`/contracts/${contractId}/messages`, { params }),

    // Отправить сообщение
    sendMessage: (contractId, data) =>
        api.post(`/contracts/${contractId}/messages`, data),

    // Отметить одно сообщение как прочитанное
    markAsRead: (messageId) =>
        api.patch(`/messages/${messageId}/read`),

    // Отметить все как прочитанные
    markAllAsRead: (contractId) =>
        api.patch(`/contracts/${contractId}/messages/read-all`),

    // Количество непрочитанных
    unreadCount: (contractId) =>
        api.get(`/contracts/${contractId}/messages/unread`),
}