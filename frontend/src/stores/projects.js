import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectsApi } from '@/api'

export const useProjectsStore = defineStore('projects', () => {
    // ─────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────
    const projects = ref([])
    const currentProject = ref(null)
    const myProjects = ref([])
    const workingProjects = ref([])
    const loading = ref(false)
    const error = ref(null)

    const pagination = ref({
        page: 1,
        pageSize: 12,
        total: 0,
        pages: 0,
    })

    const myProjectsPagination = ref({
        page: 1,
        pageSize: 12,
        total: 0,
        pages: 0,
    })

    const workingPagination = ref({
        page: 1,
        pageSize: 12,
        total: 0,
        pages: 0,
    })

    const filters = ref({
        category: null,
        status: null,
        budget_min: null,
        budget_max: null,
        search: null,
    })

    // ─────────────────────────────────────────────
    // ACTIONS
    // ─────────────────────────────────────────────
    async function fetchProjects(customFilters = null) {
        loading.value = true
        error.value = null

        try {
            const params = {
                page: pagination.value.page,
                page_size: pagination.value.pageSize,
                ...(customFilters || filters.value),
            }

            Object.keys(params).forEach((key) => {
                if (params[key] === null || params[key] === '') {
                    delete params[key]
                }
            })

            const { data } = await projectsApi.list(params)

            projects.value = data.items
            pagination.value = {
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

    async function fetchProjectById(id) {
        loading.value = true
        error.value = null

        try {
            const { data } = await projectsApi.getById(id)
            currentProject.value = data
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Проект не найден'
            return null
        } finally {
            loading.value = false
        }
    }

    async function fetchMyProjects(page = 1) {
        loading.value = true
        error.value = null

        try {
            const { data } = await projectsApi.myProjects({
                page,
                page_size: myProjectsPagination.value.pageSize,
            })

            myProjects.value = data.items
            myProjectsPagination.value = {
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

    async function fetchWorkingProjects(page = 1) {
        loading.value = true
        error.value = null

        try {
            const { data } = await projectsApi.workingProjects({
                page,
                page_size: workingPagination.value.pageSize,
            })

            workingProjects.value = data.items
            workingPagination.value = {
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

    async function createProject(projectData) {
        loading.value = true
        error.value = null

        try {
            const { data } = await projectsApi.create(projectData)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка создания проекта'
            return null
        } finally {
            loading.value = false
        }
    }

    async function updateProject(id, projectData) {
        loading.value = true
        error.value = null

        try {
            const { data } = await projectsApi.update(id, projectData)
            if (currentProject.value?.id === id) {
                currentProject.value = data
            }
            updateInList(data)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка обновления'
            return null
        } finally {
            loading.value = false
        }
    }

    async function deleteProject(id) {
        loading.value = true
        error.value = null

        try {
            await projectsApi.remove(id)
            projects.value = projects.value.filter((p) => p.id !== id)
            myProjects.value = myProjects.value.filter((p) => p.id !== id)
            return true
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка удаления'
            return false
        } finally {
            loading.value = false
        }
    }

    async function publishProject(id) {
        try {
            const { data } = await projectsApi.publish(id)
            currentProject.value = data
            updateInList(data)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка публикации'
            return null
        }
    }

    async function cancelProject(id) {
        try {
            const { data } = await projectsApi.cancel(id)
            currentProject.value = data
            updateInList(data)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка отмены'
            return null
        }
    }

    async function assignFreelancer(projectId, freelancerId) {
        try {
            const { data } = await projectsApi.assign(projectId, freelancerId)
            currentProject.value = data
            updateInList(data)
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || 'Ошибка назначения'
            return null
        }
    }

    function updateInList(updatedProject) {
        const index = projects.value.findIndex((p) => p.id === updatedProject.id)
        if (index !== -1) projects.value[index] = updatedProject

        const myIndex = myProjects.value.findIndex((p) => p.id === updatedProject.id)
        if (myIndex !== -1) myProjects.value[myIndex] = updatedProject

        const workIndex = workingProjects.value.findIndex(
            (p) => p.id === updatedProject.id
        )
        if (workIndex !== -1) workingProjects.value[workIndex] = updatedProject
    }

    function setPage(page) {
        pagination.value.page = page
        fetchProjects()
    }

    function setFilters(newFilters) {
        filters.value = { ...filters.value, ...newFilters }
        pagination.value.page = 1
        fetchProjects()
    }

    function resetFilters() {
        filters.value = {
            category: null,
            status: null,
            budget_min: null,
            budget_max: null,
            search: null,
        }
        pagination.value.page = 1
        fetchProjects()
    }

    function clearError() {
        error.value = null
    }

    return {
        // State
        projects,
        currentProject,
        myProjects,
        workingProjects,
        loading,
        error,
        pagination,
        myProjectsPagination,
        workingPagination,
        filters,
        // Actions
        fetchProjects,
        fetchProjectById,
        fetchMyProjects,
        fetchWorkingProjects,
        createProject,
        updateProject,
        deleteProject,
        publishProject,
        cancelProject,
        assignFreelancer,
        setPage,
        setFilters,
        resetFilters,
        clearError,
    }
})