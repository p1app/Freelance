// Тип уведомления → иконка, цвет и подпись
const TYPES = {
    proposal: { icon: 'mdi-send', color: 'primary', label: 'Отклик' },
    message: { icon: 'mdi-message-text', color: 'info', label: 'Сообщение' },
    contract: { icon: 'mdi-file-document-outline', color: 'success', label: 'Контракт' },
    milestone: { icon: 'mdi-flag-checkered', color: 'warning', label: 'Этап' },
    review: { icon: 'mdi-star', color: 'amber', label: 'Отзыв' },
    system: { icon: 'mdi-information-outline', color: 'grey', label: 'Система' },
}

export function notificationMeta(type) {
    return (
        TYPES[type] || {
            icon: 'mdi-bell-outline',
            color: 'grey',
            label: 'Уведомление',
        }
    )
}

// Куда ведём по клику (null — уведомление без перехода)
export function notificationRoute(notification) {
    switch (notification?.type) {
        case 'proposal':
            return notification.project_id
                ? { name: 'ProjectDetail', params: { id: notification.project_id } }
                : null
        case 'contract':
        case 'milestone':
        case 'message':
            return notification.contract_id
                ? { name: 'ContractDetail', params: { id: notification.contract_id } }
                : null
        case 'review':
            return { name: 'Profile' }
        default:
            return null
    }
}

// created_at может прийти ISO-строкой или числом (секунды/миллисекунды)
export function formatNotificationTime(value) {
    if (value === null || value === undefined || value === '') return ''

    const date =
        typeof value === 'number'
            ? new Date(value > 1e12 ? value : value * 1000)
            : new Date(value)

    if (Number.isNaN(date.getTime())) return ''

    const diffSec = Math.round((Date.now() - date.getTime()) / 1000)

    if (diffSec < 60) return 'только что'
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)} мин назад`
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} ч назад`
    if (diffSec < 604800) return `${Math.floor(diffSec / 86400)} дн назад`

    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
    })
}
