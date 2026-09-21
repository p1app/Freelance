import api from './axios'

export const notificationsApi = {
    // Уведомления текущего пользователя.
    // Бэкенд отдаёт 404, если уведомлений нет — это нормальный случай, не ошибка.
    list: () => api.get('/users/me/notifications'),

    // Отметить прочитанным: одно / все
    read: (notificationId) => api.patch(`/notifications/${notificationId}`),
    readAll: () => api.patch('/users/me/notifications'),

    // Удалить: одно / все
    remove: (notificationId) => api.delete(`/notifications/${notificationId}`),
    removeAll: () => api.delete('/users/me/notifications'),
}
