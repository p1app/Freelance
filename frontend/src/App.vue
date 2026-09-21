<template>
  <v-app>
    <template v-if="!isAuthLayout">
      <AppBar @toggle-drawer="drawer = !drawer" />
      <AppDrawer v-if="authStore.isAuthenticated" v-model="drawer" />

      <v-main>
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-main>
    </template>

    <template v-else>
      <v-main>
        <router-view />
      </v-main>
    </template>

    <!-- Глобальный диалог подтверждения (замена нативному confirm) -->
    <ConfirmDialog />
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import AppBar from '@/components/layout/AppBar.vue'
import AppDrawer from '@/components/layout/AppDrawer.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const drawer = ref(true)

const isAuthLayout = computed(() => route.meta.layout === 'auth')

// Уведомления: живой канал /ws/me + редкий опрос как страховка
// (опрос можно убрать, когда сокет будет стабилен)
const NOTIFICATIONS_FALLBACK_POLL_MS = 120000
let notificationsTimer = null

function stopNotificationsPolling() {
  if (notificationsTimer) {
    clearInterval(notificationsTimer)
    notificationsTimer = null
  }
}

function startNotifications() {
  stopNotificationsPolling()
  notificationsStore.fetchNotifications()
  notificationsStore.connect()
  notificationsTimer = setInterval(
    () => notificationsStore.fetchNotifications(),
    NOTIFICATIONS_FALLBACK_POLL_MS
  )
}

function stopNotifications() {
  stopNotificationsPolling()
  notificationsStore.disconnect()
  notificationsStore.reset()
}

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      startNotifications()
    } else {
      stopNotifications()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchProfile()
  }
})

onUnmounted(stopNotifications)
</script>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>