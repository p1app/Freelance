import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LoginView.vue'),
        meta: { guest: true, layout: 'auth' },
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/RegisterView.vue'),
        meta: { guest: true, layout: 'auth' },
    },
    {
        path: '/',
        name: 'Projects',
        component: () => import('@/views/ProjectsView.vue'),
    },
    {
        path: '/projects/create',
        name: 'ProjectCreate',
        component: () => import('@/views/ProjectCreateView.vue'),
        meta: { requiresAuth: true, requiresClient: true },
    },
    {
        path: '/projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/ProjectDetailView.vue'),
    },
    {
        path: '/my-projects',
        name: 'MyProjects',
        component: () => import('@/views/MyProjectsView.vue'),
        meta: { requiresAuth: true, requiresParticipant: true },
    },
    {
        path: '/my-proposals',
        name: 'MyProposals',
        component: () => import('@/views/MyProposalsView.vue'),
        meta: { requiresAuth: true, requiresFreelancer: true },
    },
    {
        path: '/contracts',
        name: 'Contracts',
        component: () => import('@/views/ContractsView.vue'),
        meta: { requiresAuth: true, requiresParticipant: true },
    },
    {
        path: '/contracts/:id',
        name: 'ContractDetail',
        component: () => import('@/views/ContractDetailView.vue'),
        meta: { requiresAuth: true, requiresParticipant: true },
    },
    {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { requiresAuth: true },
    },
    {
        path: '/users/:id',
        name: 'UserPublic',
        component: () => import('@/views/UserPublicView.vue'),
    },
    {
        path: '/admin',
        name: 'Admin',
        component: () => import('@/views/AdminView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFoundView.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        return { top: 0 }
    },
})

router.beforeEach((to) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        return { name: 'Login', query: { redirect: to.fullPath } }
    }

    if (to.meta.requiresAdmin && !authStore.isAdmin) {
        return { name: 'Projects' }
    }

    if (to.meta.requiresClient && !authStore.isClient) {
        return { name: 'Projects' }
    }

    if (to.meta.requiresFreelancer && !authStore.isFreelancer) {
        return { name: 'Projects' }
    }

    if (to.meta.requiresParticipant && authStore.isAdmin) {
        return { name: 'Projects' }
    }

    if (to.meta.guest && authStore.isAuthenticated) {
        return { name: 'Projects' }
    }
})

export default router