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
    // Для какого контракта загружен список (чтобы не показывать чужие этапы)
    const loadedContractId = ref(null)

    // ─────────────────────────────────────────────
    // ACTIONS
    // ─────────────────────────────────────────────
    function isLoaded(contractId) {
        return (
            loadedContractId.value !== null &&
            Number(loadedContractId.value) === Number(contractId)
        )
    }

    async function fetchByContract(contractId, { force = false } = {}) {
        if (!force && isLoaded(contractId)) {
            return milestones.value
        }

        loading.value = true
        error.value = null
        // Пока грузится другой контракт, старый список не показываем
        loadedContractId.value = null

        try {
            const { data } = await milestonesApi.listByContract(contractId)
            milestones.value = data.items || data
            loadedContractId.value = contractId
            return milestones.value
        } catch (e) {
            milestones.value = []
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
        loadedContractId.value = null
    }

    return {
        milestones,
        loading,
        error,
        loadedContractId,
        isLoaded,
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