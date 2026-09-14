<template>
  <div
    class="message-row d-flex mb-3 fade-in"
    :class="isOwn ? 'justify-end' : 'justify-start'"
  >
    <!-- Аватар (слева для чужих) -->
    <v-avatar
      v-if="!isOwn"
      size="36"
      class="mr-2 flex-shrink-0"
      :color="avatarColor"
    >
      <span class="text-white text-caption font-weight-bold">
        {{ initials }}
      </span>
    </v-avatar>

    <div class="message-content">
      <!-- Имя отправителя (только для чужих) -->
      <div
        v-if="!isOwn"
        class="text-caption font-weight-medium mb-1 ml-2"
        style="color: #9CA3AF"
      >
        <router-link
          :to="{ name: 'UserPublic', params: { id: message.sender_id } }"
          class="text-decoration-none"
          style="color: #9CA3AF"
        >
          {{ message.sender_name }}
        </router-link>
      </div>

      <!-- Пузырь -->
      <div
        class="message-bubble pa-3 rounded-lg"
        :class="isOwn ? 'bubble-own' : 'bubble-other'"
      >
        <div class="text-body-2">{{ message.message }}</div>

        <div class="d-flex align-center justify-end mt-1 gap-1">
          <span
            class="text-caption"
            :style="{ color: isOwn ? 'rgba(255,255,255,0.7)' : '#9CA3AF' }"
          >
            {{ formatTime(message.created_at) }}
          </span>

          <!-- Галочки прочтения (только для своих) -->
          <v-icon
            v-if="isOwn"
            size="14"
            :color="message.is_read ? '#60A5FA' : 'rgba(255,255,255,0.5)'"
          >
            {{ message.is_read ? 'mdi-check-all' : 'mdi-check' }}
          </v-icon>
        </div>
      </div>
    </div>

    <!-- Аватар (справа для своих) -->
    <v-avatar
      v-if="isOwn"
      size="36"
      class="ml-2 flex-shrink-0"
      :color="avatarColor"
    >
      <span class="text-white text-caption font-weight-bold">
        {{ initials }}
      </span>
    </v-avatar>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
})

const authStore = useAuthStore()

const isOwn = computed(
  () => props.message.sender_id === authStore.user?.id
)

const initials = computed(() => {
  const name = props.message.sender_name || 'U'
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const avatarColor = computed(() => {
  if (isOwn.value) return 'primary'
  // Цвет по sender_id (стабильный)
  const colors = ['#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4']
  const index = (props.message.sender_id || 0) % colors.length
  return colors[index]
})

function formatTime(value) {
  if (!value) return ''
  return new Date(value).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.message-row {
  animation: fadeIn 0.3s ease-out;
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  word-break: break-word;
  position: relative;
  transition: transform 0.2s ease;
}

.message-bubble:hover {
  transform: translateY(-1px);
}

.bubble-own {
  background: linear-gradient(135deg, #3B82F6, #1E40AF);
  color: #FFFFFF;
  border-bottom-right-radius: 4px !important;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.bubble-other {
  background: #1F2937;
  color: #F9FAFB;
  border-bottom-left-radius: 4px !important;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.gap-1 {
  gap: 4px;
}
</style>