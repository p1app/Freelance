<template>
  <v-menu v-model="menu" location="bottom end" :close-on-content-click="false" max-width="380">
    <template #activator="{ props }">
      <v-btn icon variant="text" v-bind="props" class="mr-1">
        <v-badge
          :content="unreadCount"
          :model-value="unreadCount > 0"
          color="error"
          offset-x="6"
          offset-y="6"
        >
          <v-icon>mdi-bell-outline</v-icon>
        </v-badge>
      </v-btn>
    </template>

    <v-card class="glass notifications-card">
      <div class="d-flex align-center pa-4 pb-2">
        <span class="font-weight-bold">Уведомления</span>
        <v-chip
          v-if="unreadCount > 0"
          size="x-small"
          color="error"
          variant="flat"
          class="ml-2"
        >
          {{ unreadCount }}
        </v-chip>

        <v-spacer />

        <v-btn
          v-if="store.items.length"
          size="small"
          variant="text"
          color="primary"
          :disabled="unreadCount === 0"
          @click="store.markAllRead()"
        >
          Прочитать все
        </v-btn>
      </div>

      <v-divider />

      <div class="notifications-list">
        <div
          v-if="store.loading && store.items.length === 0"
          class="text-center pa-6"
        >
          <v-progress-circular indeterminate color="primary" size="28" />
        </div>

        <div
          v-else-if="store.items.length === 0"
          class="text-center pa-6 text-body-2"
          style="color: #9ca3af"
        >
          Уведомлений нет
        </div>

        <template v-else>
          <div
            v-for="notification in store.items"
            :key="notification.id"
            class="notification-item d-flex pa-3"
            :class="{ 'notification-item--unread': !notification.is_read }"
            @click="openNotification(notification)"
          >
            <v-icon
              :color="notificationMeta(notification.type).color"
              size="22"
              class="mr-3 mt-1"
            >
              {{ notificationMeta(notification.type).icon }}
            </v-icon>

            <div class="flex-grow-1">
              <div class="text-body-2">{{ notification.description }}</div>
              <div class="text-caption mt-1" style="color: #6b7280">
                {{ notificationMeta(notification.type).label }} ·
                {{ formatNotificationTime(notification.created_at) }}
              </div>
            </div>

            <v-btn
              icon
              size="x-small"
              variant="text"
              class="ml-1"
              title="Удалить уведомление"
              @click.stop="store.remove(notification.id)"
            >
              <v-icon size="16">mdi-close</v-icon>
            </v-btn>
          </div>
        </template>
      </div>

      <template v-if="store.items.length">
        <v-divider />
        <div class="d-flex justify-end pa-2">
          <v-btn
            size="small"
            variant="text"
            color="error"
            prepend-icon="mdi-delete-sweep-outline"
            @click="store.removeAll()"
          >
            Очистить все
          </v-btn>
        </div>
      </template>

      <v-alert
        v-if="store.error"
        type="error"
        variant="tonal"
        density="compact"
        class="ma-3"
        closable
        @click:close="store.clearError()"
      >
        {{ store.error }}
      </v-alert>
    </v-card>
  </v-menu>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import {
    notificationMeta,
    notificationRoute,
    formatNotificationTime,
} from '@/utils/notification'

const router = useRouter()
const store = useNotificationsStore()

const menu = ref(false)
const unreadCount = computed(() => store.unreadCount)

async function openNotification(notification) {
  await store.markRead(notification.id)

  const target = notificationRoute(notification)
  if (!target) return

  menu.value = false
  router.push(target)
}

onMounted(() => {
  if (store.items.length === 0) store.fetchNotifications()
})
</script>

<style scoped>
.notifications-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  overflow: hidden;
}

.notifications-list {
  max-height: 380px;
  overflow-y: auto;
}

.notification-item {
  cursor: pointer;
  border-bottom: 1px solid rgba(59, 130, 246, 0.08);
  transition: background 0.2s ease;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background: rgba(59, 130, 246, 0.08);
}

.notification-item--unread {
  background: rgba(59, 130, 246, 0.06);
}
</style>
