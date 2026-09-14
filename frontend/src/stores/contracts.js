import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contractsApi } from '@/api'

export const useContractsStore = defineStore('contracts', () => {
    const contracts = ref([])
    const currentContract = ref(null)
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
    async function fetchMyContracts(params = {}) {
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

            const { data } = await contractsApi.myContracts(requestParams)

            contracts.value = data.items
            pagination.value = {
                page: data.page,
                pageSize: data.page_size,
                total: data.total,
                pages: data.pages,
            }
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка загрузки контрактов'
        } finally {
            loading.value = false
        }
    }

    async function fetchContractById(id) {
        loading.value = true
        error.value = null

        try {
            const { data } = await contractsApi.getById(id)
            currentContract.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Контракт не найден'
            return null
        } finally {
            loading.value = false
        }
    }

    async function completeContract(id) {
        loading.value = true

        try {
            const { data } = await contractsApi.complete(id)
            currentContract.value = data
            updateInList(data)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка завершения'
            return null
        } finally {
            loading.value = false
        }
    }

    async function cancelContract(id) {
        loading.value = true

        try {
            const { data } = await contractsApi.cancel(id)
            currentContract.value = data
            updateInList(data)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка отмены'
            return null
        } finally {
            loading.value = false
        }
    }

    function updateInList(updated) {
        const index = contracts.value.findIndex((c) => c.id === updated.id)
        if (index !== -1) {
            contracts.value[index] = updated
        }
    }

    function setPage(page) {
        pagination.value.page = page
        fetchMyContracts()
    }

    function clearError() {
        error.value = null
    }

    return {
        contracts,
        currentContract,
        loading,
        error,
        pagination,
        fetchMyContracts,
        fetchContractById,
        completeContract,
        cancelContract,
        setPage,
        clearError,
    }
})