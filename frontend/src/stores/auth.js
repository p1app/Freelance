import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, usersApi } from '@/api'
import { tokenUtils } from '@/utils/token'

export const useAuthStore = defineStore('auth', () => {
    // ─────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────
    const user = ref(null)
    const accessToken = ref(tokenUtils.getAccessToken())
    const refreshToken = ref(tokenUtils.getRefreshToken())
    const loading = ref(false)
    const error = ref(null)

    // ─────────────────────────────────────────────
    // GETTERS
    // ─────────────────────────────────────────────
    const isAuthenticated = computed(() => !!accessToken.value)
    const isAdmin = computed(() => user.value?.role === 'admin')
    const isClient = computed(() => user.value?.role === 'client')
    const isFreelancer = computed(() => user.value?.role === 'freelancer')

    // ─────────────────────────────────────────────
    // ACTIONS
    // ─────────────────────────────────────────────
    async function login(username, password) {
        loading.value = true
        error.value = null

        try {
            const { data } = await authApi.login({ username, password })

            accessToken.value = data.access_token
            refreshToken.value = data.refresh_token
            tokenUtils.setTokens(data.access_token, data.refresh_token)

            await fetchProfile()
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка входа'
            return false
        } finally {
            loading.value = false
        }
    }

    async function register(userData) {
        loading.value = true
        error.value = null

        try {
            const { data } = await authApi.register(userData)

            accessToken.value = data.access_token
            refreshToken.value = data.refresh_token
            tokenUtils.setTokens(data.access_token, data.refresh_token)

            await fetchProfile()
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка регистрации'
            return false
        } finally {
            loading.value = false
        }
    }

    async function fetchProfile() {
        if (!accessToken.value) return

        try {
            const { data } = await usersApi.getProfile()
            user.value = data
        } catch (e) {
            logout()
        }
    }

    async function updateProfile(updateData) {
        loading.value = true
        error.value = null

        try {
            const { data } = await usersApi.updateProfile(updateData)
            user.value = data
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка обновления'
            return false
        } finally {
            loading.value = false
        }
    }

    async function deleteAccount() {
        loading.value = true
        error.value = null

        try {
            await usersApi.deleteProfile()

            user.value = null
            accessToken.value = null
            refreshToken.value = null
            tokenUtils.clearTokens()
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка удаления профиля'
            return false
        } finally {
            loading.value = false
        }
    }

    async function logout() {
        try {
            await authApi.logout()
        } catch (e) {
            // Игнорируем
        }

        user.value = null
        accessToken.value = null
        refreshToken.value = null
        tokenUtils.clearTokens()
    }

    function clearError() {
        error.value = null
    }

    return {
        // State
        user,
        accessToken,
        refreshToken,
        loading,
        error,
        // Getters
        isAuthenticated,
        isAdmin,
        isClient,
        isFreelancer,
        // Actions
        login,
        register,
        fetchProfile,
        updateProfile,
        deleteAccount,
        logout,
        clearError,
    }
})