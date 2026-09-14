import { defineStore } from 'pinia'
import { ref } from 'vue'
import { milestonesApi } from '@/api'

export const useMilestonesStore = defineStore('milestones', () => {
    // ─────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────
    const milestones = ref([])
    const loading = ref(false)
    const error = ref(null)

    // ─────────────────────────────────────────────
    // ACTIONS
    // ─────────────────────────────────────────────
    async function fetchByContract(contractId, params = {}) {
        loading.value = true
        error.value = null

        try {
            const { data } = await milestonesApi.listByContract(contractId, params)
            milestones.value = data.items || data
            return milestones.value
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки этапов'
            return []
        } finally {
            loading.value = false
        }
    }

    async function createMilestone(contractId, data) {
        loading.value = true
        error.value = null

        try {
            const response = await milestonesApi.create(contractId, data)
            milestones.value.push(response.data)
            return response.data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка создания этапа'
            return null
        } finally {
            loading.value = false
        }
    }

    async function updateMilestone(milestoneId, data) {
        loading.value = true
        error.value = null

        try {
            const response = await milestonesApi.update(milestoneId, data)
            updateInList(response.data)
            return response.data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка обновления'
            return null
        } finally {
            loading.value = false
        }
    }

    async function deleteMilestone(milestoneId) {
        loading.value = true
        error.value = null

        try {
            await milestonesApi.remove(milestoneId)
            milestones.value = milestones.value.filter((m) => m.id !== milestoneId)
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка удаления'
            return false
        } finally {
            loading.value = false
        }
    }

    async function completeMilestone(milestoneId) {
        try {
            const response = await milestonesApi.complete(milestoneId)
            updateInList(response.data)
            return response.data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка завершения'
            return null
        }
    }

    async function approveMilestone(milestoneId) {
        try {
            const response = await milestonesApi.approve(milestoneId)
            updateInList(response.data)
            return response.data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка утверждения'
            return null
        }
    }

    function updateInList(updated) {
        const index = milestones.value.findIndex((m) => m.id === updated.id)
        if (index !== -1) {
            milestones.value[index] = updated
        }
    }

    function clearError() {
        error.value = null
    }

    function reset() {
        milestones.value = []
        error.value = null
    }

    return {
        milestones,
        loading,
        error,
        fetchByContract,
        createMilestone,
        updateMilestone,
        deleteMilestone,
        completeMilestone,
        approveMilestone,
        clearError,
        reset,
    }
})