import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi } from '@/api'
import { tokenUtils } from '@/utils/token'

export const useChatStore = defineStore('chat', () => {
    // ─────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────
    const messages = ref([])
    const unreadCount = ref(0)
    const loading = ref(false)
    const error = ref(null)
    const isConnected = ref(false)

    let ws = null
    let currentContractId = null
    let reconnectTimeout = null
    let reconnectAttempts = 0
    const MAX_RECONNECT_ATTEMPTS = 5
    const RECONNECT_DELAY = 3000

    // ─────────────────────────────────────────────
    // ЗАГРУЗКА ИСТОРИИ
    // ─────────────────────────────────────────────
    async function fetchMessages(contractId, params = {}) {
        loading.value = true
        error.value = null

        try {
            const { data } = await chatApi.listMessages(contractId, params)
            messages.value = data.items || data
            return messages.value
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки сообщений'
            return []
        } finally {
            loading.value = false
        }
    }

    // ─────────────────────────────────────────────
    // WEBSOCKET
    // ─────────────────────────────────────────────
    function connect(contractId) {
        // Если уже подключены к этому контракту — не переподключаемся
        if (
            ws &&
            currentContractId === contractId &&
            ws.readyState === WebSocket.OPEN
        ) {
            return
        }

        disconnect()
        currentContractId = contractId
        reconnectAttempts = 0

        _createConnection()
    }

    function _createConnection() {
        const token = tokenUtils.getAccessToken()
        if (!token) {
            return
        }

        // Определяем URL для WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        const apiUrl = import.meta.env.VITE_API_URL || '/api'

        let wsUrl
        if (apiUrl.startsWith('/')) {
            // Прокси: ws://localhost:5173/ws/chat/{id}?token=...
            wsUrl = `${protocol}//${host}/ws/chat/${currentContractId}?token=${token}`
        } else {
            // Прямой URL: ws://localhost:8000/ws/chat/{id}?token=...
            const url = new URL(apiUrl)
            url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
            wsUrl = `${url.origin}/ws/chat/${currentContractId}?token=${token}`
        }

        try {
            ws = new WebSocket(wsUrl)
        } catch (e) {
            console.error('WebSocket creation error:', e)
            _scheduleReconnect()
            return
        }

        ws.onopen = () => {
            isConnected.value = true
            reconnectAttempts = 0
            console.log('WebSocket connected')
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)

                if (data.type === 'new_message') {
                    // Проверяем, нет ли уже такого сообщения
                    const exists = messages.value.some((m) => m.id === data.id)
                    if (!exists) {
                        messages.value.push(data)
                    }
                } else if (data.type === 'error') {
                    console.error('WebSocket error:', data.detail)
                    error.value = data.detail
                }
            } catch (e) {
                console.error('WS message parse error:', e)
            }
        }

        ws.onclose = (event) => {
            isConnected.value = false
            ws = null

            // Если код 1008 — не переподключаемся (нет прав / токен истёк)
            if (event.code === 1008) {
                console.warn('WebSocket closed: policy violation (1008)')
                return
            }

            // Автопереподключение
            if (currentContractId) {
                _scheduleReconnect()
            }
        }

        ws.onerror = (e) => {
            console.error('WebSocket error:', e)
        }
    }

    function _scheduleReconnect() {
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            console.warn('Max reconnect attempts reached')
            return
        }

        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout)
        }

        reconnectAttempts++
        console.log(`Reconnecting... attempt ${reconnectAttempts}`)

        reconnectTimeout = setTimeout(() => {
            if (currentContractId) {
                _createConnection()
            }
        }, RECONNECT_DELAY)
    }

    function disconnect() {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout)
            reconnectTimeout = null
        }

        if (ws) {
            // Убираем onclose, чтобы не было переподключения
            ws.onclose = null
            ws.close()
            ws = null
        }

        isConnected.value = false
        currentContractId = null
    }

    // ─────────────────────────────────────────────
    // ОТПРАВКА СООБЩЕНИЯ
    // ─────────────────────────────────────────────
    function sendMessage(contractId, message) {
        error.value = null

        // Если WebSocket подключён — отправляем через него
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ message }))
            return true
        }

        // Иначе — через REST API (fallback)
        return _sendViaRest(contractId, message)
    }

    async function _sendViaRest(contractId, message) {
        try {
            const { data } = await chatApi.sendMessage(contractId, { message })
            messages.value.push(data)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка отправки'
            return null
        }
    }

    // ─────────────────────────────────────────────
    // ПРОЧЕЕ
    // ─────────────────────────────────────────────
    async function markAsRead(messageId) {
        try {
            await chatApi.markAsRead(messageId)
            const message = messages.value.find((m) => m.id === messageId)
            if (message) message.is_read = true
        } catch (e) {
            console.error(e)
        }
    }

    async function markAllAsRead(contractId) {
        try {
            await chatApi.markAllAsRead(contractId)
            messages.value.forEach((m) => (m.is_read = true))
            unreadCount.value = 0
        } catch (e) {
            console.error(e)
        }
    }

    async function fetchUnreadCount(contractId) {
        try {
            const { data } = await chatApi.unreadCount(contractId)
            unreadCount.value = data.count
            return data.count
        } catch (e) {
            return 0
        }
    }

    function clearError() {
        error.value = null
    }

    function reset() {
        disconnect()
        messages.value = []
        unreadCount.value = 0
        error.value = null
    }

    return {
        messages,
        unreadCount,
        loading,
        error,
        isConnected,
        fetchMessages,
        connect,
        disconnect,
        sendMessage,
        markAsRead,
        markAllAsRead,
        fetchUnreadCount,
        clearError,
        reset,
    }
})