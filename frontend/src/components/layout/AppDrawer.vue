<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    permanent
    class="drawer-gradient"
    @click="rail = false"
  >
    <!-- Мини-профиль -->
    <v-list-item
      v-if="authStore.user"
      :prepend-avatar="avatarUrl"
      :title="authStore.user.full_name || authStore.user.username"
      :subtitle="roleLabel"
      nav
      class="ma-2 rounded-lg"
    >
      <template #append>
        <v-btn
          :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
          variant="text"
          size="small"
          @click.stop="rail = !rail"
        />
      </template>
    </v-list-item>

    <v-divider class="my-2" />

    <!-- Меню -->
    <v-list density="compact" nav class="px-2">
      <v-list-item
        v-for="item in menuItems"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        :value="item.to"
        rounded="lg"
        class="mb-1 menu-item"
      >
        <template v-if="item.badge" #append>
          <v-badge
            v-if="item.badge > 0"
            :content="item.badge"
            color="error"
            inline
          />
        </template>
      </v-list-item>
    </v-list>

    <v-divider class="my-2" />

    <!-- Дополнительно -->
    <v-list density="compact" nav class="px-2">
      <v-list-item
        prepend-icon="mdi-help-circle-outline"
        title="Помощь"
        rounded="lg"
        class="mb-1 menu-item"
        @click="showHelpDialog = true"
      />
      <v-list-item
        prepend-icon="mdi-information-outline"
        title="О проекте"
        rounded="lg"
        class="mb-1 menu-item"
        @click="showAboutDialog = true"
      />
    </v-list>

    <template #append>
      <div class="pa-3 text-caption text-center" style="color: #9CA3AF">
        v1.0.0
      </div>
    </template>
  </v-navigation-drawer>

  <!-- Помощь -->
  <v-dialog v-model="showHelpDialog" max-width="600">
    <v-card class="glass">
      <v-card-title class="gradient-text">Помощь</v-card-title>
      <v-card-text>
        <h3 class="text-h6 mb-2">Как пользоваться платформой?</h3>
        <p><strong>Заказчик:</strong></p>
        <ul>
          <li>Создайте проект в разделе "Мои проекты"</li>
          <li>Опубликуйте его, чтобы фрилансеры могли откликнуться</li>
          <li>Примите подходящий отклик</li>
        </ul>
        <p><strong>Фрилансер:</strong></p>
        <ul>
          <li>Найдите проект в разделе "Проекты"</li>
          <li>Оставьте отклик с ценой и сроком</li>
          <li>Следите за своими откликами в разделе "Мои отклики"</li>
        </ul>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="showHelpDialog = false">Понятно</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- О проекте -->
  <v-dialog v-model="showAboutDialog" max-width="600">
    <v-card class="glass">
      <v-card-title class="gradient-text">О проекте</v-card-title>
      <v-card-text>
        <h3 class="text-h6 mb-2">Freelance LITE</h3>
        <p>Платформа для поиска и выполнения фриланс-проектов.</p>
        <p><strong>Версия:</strong> 1.0.0</p>
        <p><strong>Стек:</strong> Vue 3, Vuetify 3, FastAPI, PostgreSQL</p>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="showAboutDialog = false">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'

const props = defineProps({
  modelValue: { type: Boolean, default: true },
})

const emit = defineEmits(['update:modelValue'])

const authStore = useAuthStore()
const chatStore = useChatStore()

const drawer = ref(props.modelValue)
const rail = ref(false)
const showHelpDialog = ref(false)
const showAboutDialog = ref(false)

watch(() => props.modelValue, (val) => {
  drawer.value = val
})

watch(drawer, (val) => {
  emit('update:modelValue', val)
})

const avatarUrl = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.username || 'User'
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3B82F6&color=fff`
})

const roleLabel = computed(() => {
  const roles = {
    admin: 'Администратор',
    client: 'Заказчик',
    freelancer: 'Фрилансер',
  }
  return roles[authStore.user?.role] || 'Пользователь'
})

const menuItems = computed(() => {
  const items = [
    {
      to: '/',
      title: 'Проекты',
      icon: 'mdi-briefcase-outline',
    },
  ]

  if (authStore.isClient) {
    items.push({
      to: '/my-projects',
      title: 'Мои проекты',
      icon: 'mdi-folder-outline',
    })
  }

  if (authStore.isFreelancer) {
    items.push(
      {
        to: '/my-projects',
        title: 'Проекты в работе',
        icon: 'mdi-briefcase-check-outline',
      },
      {
        to: '/my-proposals',
        title: 'Мои отклики',
        icon: 'mdi-send-outline',
      },
    )
  }

  if (authStore.isClient || authStore.isFreelancer) {
    items.push({
      to: '/contracts',
      title: 'Контракты',
      icon: 'mdi-file-document-outline',
      badge: chatStore.unreadCount,
    })
  }

  if (authStore.isAdmin) {
    items.push({
      to: '/admin',
      title: 'Админка',
      icon: 'mdi-shield-account-outline',
    })
  }

  return items
})
</script>

<style scoped>
.drawer-gradient {
  background: linear-gradient(180deg, #0f172a 0%, #0a0e1a 100%) !important;
  border-right: 1px solid rgba(59, 130, 246, 0.1);
}

.menu-item {
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: rgba(59, 130, 246, 0.1) !important;
  transform: translateX(4px);
}
</style>