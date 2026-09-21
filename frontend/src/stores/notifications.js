import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsApi } from '@/api'
import { tokenUtils } from '@/utils/token'

export const useNotificationsStore = defineStore('notifications', () => {
    const items = ref([])
    const loading = ref(false)
    const error = ref(null)
    const isConnected = ref(false)

    let ws = null
    let reconnectTimeout = null
    let reconnectAttempts = 0
    const MAX_RECONNECT_ATTEMPTS = 5
    const RECONNECT_DELAY = 3000
    // Пинг, чтобы nginx/прокси не закрывали простаивающее соединение
    let heartbeatTimer = null
    const HEARTBEAT_MS = 30000

    // Пока бэкенд не отдаёт is_read, непрочитанными считаются все —
    // после «прочитать» состояние меняем локально (оптимистично)
    const unreadCount = computed(
        () => items.value.filter((n) => !n.is_read).length
    )

    // Свежие сверху: id монотонный, поэтому сортируем по нему, без разбора дат
    function sortNewestFirst(list) {
        return [...list].sort((a, b) => (b.id ?? 0) - (a.id ?? 0))
    }

    async function fetchNotifications() {
        loading.value = true
        error.value = null

        try {
            const { data } = await notificationsApi.list()
            items.value = sortNewestFirst(data || [])
            return items.value
        } catch (e) {
            if (e.response?.status === 404) {
                // Бэкенд отдаёт 404 вместо пустого списка
                items.value = []
                return items.value
            }
            error.value =
                e.response?.data?.detail || 'Ошибка загрузки уведомлений'
            return []
        } finally {
            loading.value = false
        }
    }

    async function markRead(notificationId) {
        const item = items.value.find((n) => n.id === notificationId)
        if (!item || item.is_read) return true

        item.is_read = true // оптимистично
        try {
            await notificationsApi.read(notificationId)
            return true
        } catch (e) {
            item.is_read = false
            error.value =
                e.response?.data?.detail || 'Ошибка отметки уведомления'
            return false
        }
    }

    async function markAllRead() {
        const snapshot = items.value.map((n) => !!n.is_read)
        items.value.forEach((n) => {
            n.is_read = true
        })

        try {
            await notificationsApi.readAll()
            return true
        } catch (e) {
            items.value.forEach((n, index) => {
                n.is_read = snapshot[index]
            })
            error.value =
                e.response?.data?.detail || 'Ошибка отметки уведомлений'
            return false
        }
    }

    async function remove(notificationId) {
        const index = items.value.findIndex((n) => n.id === notificationId)
        if (index === -1) return true

        const [removed] = items.value.splice(index, 1) // оптимистично
        try {
            await notificationsApi.remove(notificationId)
            return true
        } catch (e) {
            items.value.splice(index, 0, removed)
            error.value =
                e.response?.data?.detail || 'Ошибка удаления уведомления'
            return false
        }
    }

    async function removeAll() {
        const snapshot = items.value
        items.value = []

        try {
            await notificationsApi.removeAll()
            return true
        } catch (e) {
            items.value = snapshot
            error.value =
                e.response?.data?.detail || 'Ошибка очистки уведомлений'
            return false
        }
    }

    function clearError() {
        error.value = null
    }

    // ─────────────────────────────────────────────
    // WEBSOCKET: /ws/me — уведомления в реальном времени
    // ─────────────────────────────────────────────
    function buildSocketUrl() {
        const token = tokenUtils.getAccessToken()
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        const apiUrl = import.meta.env.VITE_API_URL || '/api'

        if (apiUrl.startsWith('/')) {
            // Через дев-прокси: ws://localhost:5173/ws/me?token=...
            return `${protocol}//${host}/ws/me?token=${token}`
        }

        const url = new URL(apiUrl)
        url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
        return `${url.origin}/ws/me?token=${token}`
    }

    function addIncoming(notification) {
        if (!notification?.id) return
        // Дедуп: тот же кадр мог прийти повторно после реконнекта
        if (items.value.some((n) => n.id === notification.id)) return
        items.value = [notification, ...items.value]
    }

    // Бэкенд может прислать уведомление в нескольких видах, поддерживаем все:
    //   {"event": "notification", "payload": {...}}   — конверт с вложенным payload
    //   {"event": "notification", "type": "message", "id": 1, ...} — плоский кадр
    //   {"type": "notification", "payload": {...}}    — прежний вариант маркера
    //   {"type": "message", "id": 1, ...}             — маркер потерян из-за коллизии ключей
    function extractNotification(frame) {
        if (!frame || typeof frame !== 'object') return null

        if (frame.payload && typeof frame.payload === 'object') {
            return frame.payload
        }

        if (frame.event === 'notification') {
            // Убираем только служебный ключ: поле type — это тип уведомления
            const { event, ...notification } = frame
            return notification
        }

        if (frame.type === 'notification') {
            const { type, ...notification } = frame
            return notification
        }

        if (frame.id && frame.description && frame.to_user_id) {
            return frame
        }

        return null
    }

    function handleFrame(raw) {
        let frame
        try {
            frame = JSON.parse(raw)
        } catch (e) {
            return
        }

        const notification = extractNotification(frame)
        if (notification?.id) {
            addIncoming(notification)
            return
        }

        // Кадр непонятного формата — не гадаем, просто перечитываем список
        fetchNotifications()
    }

    function startHeartbeat() {
        stopHeartbeat()
        heartbeatTimer = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ event: 'ping' }))
            }
        }, HEARTBEAT_MS)
    }

    function stopHeartbeat() {
        if (heartbeatTimer) {
            clearInterval(heartbeatTimer)
            heartbeatTimer = null
        }
    }

    function connect() {
        if (!tokenUtils.getAccessToken()) return
        if (
            ws &&
            (ws.readyState === WebSocket.OPEN ||
                ws.readyState === WebSocket.CONNECTING)
        ) {
            return
        }

        try {
            ws = new WebSocket(buildSocketUrl())
        } catch (e) {
            scheduleReconnect()
            return
        }

        ws.onopen = () => {
            isConnected.value = true
            reconnectAttempts = 0
            startHeartbeat()
        }

        ws.onmessage = (event) => handleFrame(event.data)

        ws.onclose = (event) => {
            isConnected.value = false
            ws = null
            stopHeartbeat()
            // 1008 — нет прав/токен истёк, переподключаться бессмысленно
            if (event.code !== 1008) scheduleReconnect()
        }

        ws.onerror = () => {}
    }

    function scheduleReconnect() {
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) return
        if (reconnectTimeout) clearTimeout(reconnectTimeout)

        reconnectAttempts += 1
        reconnectTimeout = setTimeout(() => {
            if (tokenUtils.getAccessToken()) connect()
        }, RECONNECT_DELAY)
    }

    function disconnect() {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout)
            reconnectTimeout = null
        }
        stopHeartbeat()
        if (ws) {
            ws.onclose = null
            ws.close()
            ws = null
        }
        reconnectAttempts = 0
        isConnected.value = false
    }

    function reset() {
        items.value = []
        error.value = null
    }

    return {
        items,
        loading,
        error,
        isConnected,
        unreadCount,
        fetchNotifications,
        markRead,
        markAllRead,
        remove,
        removeAll,
        connect,
        disconnect,
        clearError,
        reset,
    }
})
