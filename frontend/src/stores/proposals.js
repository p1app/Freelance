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

    // Отклик текущего фрилансера на открытый проект (нужен ProjectDetailView,
    // чтобы после перезагрузки страницы не показывать форму повторно)
    const myProposalForProject = ref(null)
    const myProposalChecked = ref(false)

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

    /**
     * Отклик текущего фрилансера на конкретный проект.
     * Бэкенд отдаёт 404, если отклика нет, — это нормальная ситуация, не ошибка.
     * Отозванный отклик не считаем: по правилам бэкенда после отзыва можно откликнуться снова.
     */
    async function fetchMyProposalForProject(projectId) {
        myProposalChecked.value = false
        myProposalForProject.value = null

        try {
            const { data } = await proposalsApi.myProposalByProject(projectId)
            myProposalForProject.value =
                data?.status === 'withdrawn' ? null : data
            return myProposalForProject.value
        } catch (e) {
            if (e.response?.status !== 404) {
                error.value =
                    e.response?.data?.detail || 'Ошибка загрузки отклика'
            }
            return null
        } finally {
            myProposalChecked.value = true
        }
    }

    function setMyProposalForProject(proposal) {
        myProposalForProject.value = proposal || null
        myProposalChecked.value = true
    }

    function clearMyProposalForProject() {
        myProposalForProject.value = null
        myProposalChecked.value = false
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
            if (myProposalForProject.value?.id === proposalId) {
                // Отозванный отклик не мешает откликнуться снова,
                // поэтому возвращаем форму отклика
                myProposalForProject.value = null
                myProposalChecked.value = true
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
        myProposalForProject.value = null
        myProposalChecked.value = false
    }

    return {
        proposals,
        loading,
        error,
        pagination,
        myProposalForProject,
        myProposalChecked,
        fetchByProject,
        fetchMyProposals,
        createProposal,
        fetchMyProposalForProject,
        setMyProposalForProject,
        clearMyProposalForProject,
        updateProposal,
        withdrawProposal,
        acceptProposal,
        rejectProposal,
        setPage,
        clearError,
        reset,
    }
})