import { defineStore } from 'pinia'
import { ref } from 'vue'
import { proposalsApi } from '@/api'

export const useProposalsStore = defineStore('proposals', () => {
    // ─────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────
    const proposals = ref([])
    const loading = ref(false)
    const error = ref(null)

    const pagination = ref({
        page: 1,
        pageSize: 12,
        total: 0,
        pages: 0,
    })

    // ─────────────────────────────────────────────
    // ACTIONS
    // ─────────────────────────────────────────────
    async function fetchByProject(projectId, params = {}) {
        loading.value = true
        error.value = null

        try {
            const { data } = await proposalsApi.listByProject(projectId, params)
            proposals.value = data.items || data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки откликов'
            return null
        } finally {
            loading.value = false
        }
    }

    async function fetchMyProposals(params = {}) {
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

            const { data } = await proposalsApi.myProposals(requestParams)

            proposals.value = data.items
            pagination.value = {
                page: data.page,
                pageSize: data.page_size,
                total: data.total,
                pages: data.pages,
            }
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки откликов'
            return null
        } finally {
            loading.value = false
        }
    }

    async function createProposal(projectId, proposalData) {
        loading.value = true
        error.value = null

        try {
            const { data } = await proposalsApi.create(projectId, proposalData)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка создания отклика'
            return null
        } finally {
            loading.value = false
        }
    }

    async function updateProposal(proposalId, data) {
        loading.value = true
        error.value = null

        try {
            const { data: updated } = await proposalsApi.update(proposalId, data)
            const index = proposals.value.findIndex((p) => p.id === proposalId)
            if (index !== -1) {
                proposals.value[index] = updated
            }
            return updated
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка обновления'
            return null
        } finally {
            loading.value = false
        }
    }

    async function withdrawProposal(proposalId) {
        try {
            const { data } = await proposalsApi.withdraw(proposalId)
            const index = proposals.value.findIndex((p) => p.id === proposalId)
            if (index !== -1) {
                proposals.value[index] = data
            }
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка отзыва'
            return null
        }
    }

    async function acceptProposal(proposalId) {
        try {
            const { data } = await proposalsApi.accept(proposalId)
            proposals.value = proposals.value.map((p) => {
                if (p.id === proposalId) return { ...p, status: 'accepted' }
                if (p.status === 'pending') return { ...p, status: 'rejected' }
                return p
            })
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка принятия отклика'
            return null
        }
    }

    async function rejectProposal(proposalId) {
        try {
            const { data } = await proposalsApi.reject(proposalId)
            const index = proposals.value.findIndex((p) => p.id === proposalId)
            if (index !== -1) {
                proposals.value[index] = data
            }
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка отклонения'
            return null
        }
    }

    function setPage(page) {
        pagination.value.page = page
    }

    function clearError() {
        error.value = null
    }

    function reset() {
        proposals.value = []
        error.value = null
    }

    return {
        proposals,
        loading,
        error,
        pagination,
        fetchByProject,
        fetchMyProposals,
        createProposal,
        updateProposal,
        withdrawProposal,
        acceptProposal,
        rejectProposal,
        setPage,
        clearError,
        reset,
    }
})