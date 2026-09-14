import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usersApi, reviewsApi } from '@/api'

export const useUserStore = defineStore('user', () => {
    // ─────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────
    const publicProfile = ref(null)
    const stats = ref(null)
    const reviews = ref([])
    const reviewsStats = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // ─────────────────────────────────────────────
    // ACTIONS
    // ─────────────────────────────────────────────
    async function fetchPublicProfile(userId) {
        loading.value = true
        error.value = null

        try {
            const { data } = await usersApi.getById(userId)
            publicProfile.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Пользователь не найден'
            return null
        } finally {
            loading.value = false
        }
    }

    async function fetchStats() {
        loading.value = true
        error.value = null

        try {
            const { data } = await usersApi.getStats()
            stats.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки статистики'
            return null
        } finally {
            loading.value = false
        }
    }

    async function fetchUserReviews(userId, params = {}) {
        try {
            const { data } = await reviewsApi.listByUser(userId, params)
            reviews.value = data.items
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки отзывов'
            return null
        }
    }

    async function fetchUserReviewsStats(userId) {
        try {
            const { data } = await reviewsApi.statsByUser(userId)
            reviewsStats.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки статистики отзывов'
            return null
        }
    }

    async function updateProfile(updateData) {
        loading.value = true
        error.value = null

        try {
            const { data } = await usersApi.updateProfile(updateData)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка обновления профиля'
            return null
        } finally {
            loading.value = false
        }
    }

    function clearError() {
        error.value = null
    }

    function reset() {
        publicProfile.value = null
        stats.value = null
        reviews.value = []
        reviewsStats.value = null
        error.value = null
    }

    return {
        publicProfile,
        stats,
        reviews,
        reviewsStats,
        loading,
        error,
        fetchPublicProfile,
        fetchStats,
        fetchUserReviews,
        fetchUserReviewsStats,
        updateProfile,
        clearError,
        reset,
    }
})