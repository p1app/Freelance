import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reviewsApi } from '@/api'

export const useReviewsStore = defineStore('reviews', () => {
    const reviews = ref([])
    const stats = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const pagination = ref({
        page: 1,
        pageSize: 10,
        total: 0,
        pages: 0,
    })

    async function fetchByUser(userId, params = {}) {
        loading.value = true
        error.value = null

        try {
            const requestParams = {
                page: pagination.value.page,
                page_size: pagination.value.pageSize,
                ...params,
            }

            Object.keys(requestParams).forEach((key) => {
                if (requestParams[key] === null || requestParams[key] === '') {
                    delete requestParams[key]
                }
            })

            const { data } = await reviewsApi.listByUser(userId, requestParams)
            reviews.value = data.items
            pagination.value = {
                page: data.page,
                pageSize: data.page_size,
                total: data.total,
                pages: data.pages,
            }
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки отзывов'
        } finally {
            loading.value = false
        }
    }

    async function fetchStatsByUser(userId) {
        loading.value = true
        error.value = null

        try {
            const { data } = await reviewsApi.statsByUser(userId)
            stats.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки статистики'
            return null
        } finally {
            loading.value = false
        }
    }

    async function fetchByContract(contractId) {
        loading.value = true
        error.value = null

        try {
            const { data } = await reviewsApi.listByContract(contractId)
            reviews.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки отзывов'
            return []
        } finally {
            loading.value = false
        }
    }

    async function createReview(contractId, reviewData) {
        loading.value = true
        error.value = null

        try {
            const { data } = await reviewsApi.create(contractId, reviewData)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка создания отзыва'
            return null
        } finally {
            loading.value = false
        }
    }

    async function updateReview(reviewId, data) {
        loading.value = true
        error.value = null

        try {
            const { data: updated } = await reviewsApi.update(reviewId, data)
            const index = reviews.value.findIndex((r) => r.id === reviewId)
            if (index !== -1) reviews.value[index] = updated
            return updated
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка обновления'
            return null
        } finally {
            loading.value = false
        }
    }

    async function deleteReview(reviewId) {
        loading.value = true
        error.value = null

        try {
            await reviewsApi.remove(reviewId)
            reviews.value = reviews.value.filter((r) => r.id !== reviewId)
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка удаления'
            return false
        } finally {
            loading.value = false
        }
    }

    function setPage(page) {
        pagination.value.page = page
    }

    function clearError() {
        error.value = null
    }

    function reset() {
        reviews.value = []
        stats.value = null
        error.value = null
    }

    return {
        reviews,
        stats,
        loading,
        error,
        pagination,
        fetchByUser,
        fetchStatsByUser,
        fetchByContract,
        createReview,
        updateReview,
        deleteReview,
        setPage,
        clearError,
        reset,
    }
})