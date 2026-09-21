<template>
  <v-app-bar
    class="glass elevation-0"
    density="comfortable"
    :style="{ borderBottom: '1px solid rgba(59, 130, 246, 0.1)' }"
  >
    <!-- Кнопка меню -->
    <v-app-bar-nav-icon
      v-if="authStore.isAuthenticated"
      @click="$emit('toggle-drawer')"
    />

    <!-- Логотип -->
    <v-app-bar-title>
      <router-link to="/" class="text-decoration-none d-flex align-center">
        <v-icon class="mr-2" color="primary" size="28">mdi-briefcase</v-icon>
        <span class="gradient-text font-weight-bold text-h6">
          Freelance LITE
        </span>
      </router-link>
    </v-app-bar-title>

    <v-spacer />

    <!-- Авторизованный -->
    <template v-if="authStore.isAuthenticated">
      <NotificationsMenu />

      <v-menu location="bottom end">
        <template #activator="{ props }">
          <v-btn icon v-bind="props" class="mr-2">
            <v-avatar color="primary" size="36">
              <span class="text-white font-weight-bold">
                {{ userInitials }}
              </span>
            </v-avatar>
          </v-btn>
        </template>

        <v-list min-width="220" class="glass">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              {{ authStore.user?.fullname }}
            </v-list-item-title>
            <v-list-item-subtitle>
              @{{ authStore.user?.username }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-divider />

          <v-list-item to="/profile" prepend-icon="mdi-account">
            <v-list-item-title>Профиль</v-list-item-title>
          </v-list-item>

          <v-list-item
            v-if="authStore.isAdmin"
            to="/admin"
            prepend-icon="mdi-shield-account"
          >
            <v-list-item-title>Админка</v-list-item-title>
          </v-list-item>

          <v-divider />

          <v-list-item prepend-icon="mdi-logout" @click="handleLogout">
            <v-list-item-title>Выйти</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>

    <!-- Гость -->
    <template v-else>
      <v-btn variant="text" to="/login" class="mr-2">Войти</v-btn>
      <v-btn color="primary" to="/register" class="btn-glow">Регистрация</v-btn>
    </template>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NotificationsMenu from '@/components/notification/NotificationsMenu.vue'

defineEmits(['toggle-drawer'])

const router = useRouter()
const authStore = useAuthStore()

const userInitials = computed(() => {
  const name = authStore.user?.fullname || authStore.user?.username || ''
  return name
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>