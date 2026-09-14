import { defineStore } from 'pinia'
import { ref } from 'vue'
import { adminApi } from '@/api'

export const useAdminStore = defineStore('admin', () => {
    // ─────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────
    const users = ref([])
    const projects = ref([])
    const stats = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const usersPagination = ref({
        page: 1,
        pageSize: 20,
        total: 0,
        pages: 0,
    })

    const projectsPagination = ref({
        page: 1,
        pageSize: 20,
        total: 0,
        pages: 0,
    })

    // ─────────────────────────────────────────────
    // USERS
    // ─────────────────────────────────────────────
    async function fetchUsers(params = {}) {
        loading.value = true
        error.value = null

        try {
            const requestParams = {
                page: usersPagination.value.page,
                page_size: usersPagination.value.pageSize,
                ...params,
            }

            Object.keys(requestParams).forEach((key) => {
                if (requestParams[key] === null || requestParams[key] === '') {
                    delete requestParams[key]
                }
            })

            const { data } = await adminApi.listUsers(requestParams)
            users.value = data.items
            usersPagination.value = {
                page: data.page,
                pageSize: data.page_size,
                total: data.total,
                pages: data.pages,
            }
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки пользователей'
        } finally {
            loading.value = false
        }
    }

    async function blockUser(userId) {
        try {
            await adminApi.blockUser(userId)
            const user = users.value.find((u) => u.id === userId)
            if (user) user.is_active = false
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка блокировки'
            return false
        }
    }

    async function unblockUser(userId) {
        try {
            await adminApi.unblockUser(userId)
            const user = users.value.find((u) => u.id === userId)
            if (user) user.is_active = true
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка разблокировки'
            return false
        }
    }

    // ─────────────────────────────────────────────
    // PROJECTS
    // ─────────────────────────────────────────────
    async function fetchProjects(params = {}) {
        loading.value = true
        error.value = null

        try {
            const requestParams = {
                page: projectsPagination.value.page,
                page_size: projectsPagination.value.pageSize,
                ...params,
            }

            Object.keys(requestParams).forEach((key) => {
                if (requestParams[key] === null || requestParams[key] === '') {
                    delete requestParams[key]
                }
            })

            const { data } = await adminApi.listProjects(requestParams)
            projects.value = data.items
            projectsPagination.value = {
                page: data.page,
                pageSize: data.page_size,
                total: data.total,
                pages: data.pages,
            }
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки проектов'
        } finally {
            loading.value = false
        }
    }

    async function deleteProject(projectId) {
        try {
            await adminApi.deleteProject(projectId)
            projects.value = projects.value.filter((p) => p.id !== projectId)
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка удаления'
            return false
        }
    }

    // ─────────────────────────────────────────────
    // STATS
    // ─────────────────────────────────────────────
    async function fetchStats() {
        loading.value = true
        error.value = null

        try {
            const { data } = await adminApi.stats()
            stats.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки статистики'
            return null
        } finally {
            loading.value = false
        }
    }

    function clearError() {
        error.value = null
    }

    return {
        users,
        projects,
        stats,
        loading,
        error,
        usersPagination,
        projectsPagination,
        fetchUsers,
        blockUser,
        unblockUser,
        fetchProjects,
        deleteProject,
        fetchStats,
        clearError,
    }
})