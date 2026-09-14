<template>
  <v-container>
    <h1 class="text-h4 mb-4">
      <v-icon color="primary" size="32" class="mr-2">mdi-shield-account</v-icon>
      Админ-панель
    </h1>

    <!-- Вкладки -->
    <v-tabs v-model="tab" class="mb-4">
      <v-tab value="stats" prepend-icon="mdi-chart-box-outline">
        Статистика
      </v-tab>
      <v-tab value="users" prepend-icon="mdi-account-multiple-outline">
        Пользователи
      </v-tab>
      <v-tab value="projects" prepend-icon="mdi-briefcase-outline">
        Проекты
      </v-tab>
    </v-tabs>

    <!-- Ошибка -->
    <v-alert
      v-if="adminStore.error"
      type="error"
      variant="tonal"
      class="mb-4"
      closable
      @click:close="adminStore.clearError()"
    >
      {{ adminStore.error }}
    </v-alert>

    <!-- Контент вкладок -->
    <v-window v-model="tab">
      <v-window-item value="stats">
        <AdminStatsTab />
      </v-window-item>

      <v-window-item value="users">
        <AdminUsersTab />
      </v-window-item>

      <v-window-item value="projects">
        <AdminProjectsTab />
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import AdminStatsTab from '@/components/admin/AdminStatsTab.vue'
import AdminUsersTab from '@/components/admin/AdminUsersTab.vue'
import AdminProjectsTab from '@/components/admin/AdminProjectsTab.vue'

const adminStore = useAdminStore()
const authStore = useAuthStore()
const router = useRouter()

const tab = ref('stats')

onMounted(() => {
  if (!authStore.isAdmin) {
    router.push('/')
  }
})
</script>