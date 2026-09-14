<template>
  <v-card class="glass chat-card">
    <!-- Заголовок -->
    <v-card-title
      class="pa-4 d-flex align-center"
      style="border-bottom: 1px solid rgba(59, 130, 246, 0.1)"
    >
      <v-icon color="primary" class="mr-2">mdi-message-text</v-icon>
      <span class="font-weight-bold">Чат</span>

      <v-chip
        v-if="chatStore.messages.length > 0"
        size="small"
        variant="tonal"
        color="primary"
        class="ml-2"
      >
        {{ chatStore.messages.length }}
      </v-chip>

      <v-spacer />

      <!-- Статус -->
      <v-chip
        v-if="isContractClosed"
        size="small"
        variant="tonal"
        color="error"
        prepend-icon="mdi-lock"
      >
        Закрыт
      </v-chip>
      <v-chip
        v-else
        size="small"
        variant="tonal"
        :color="chatStore.isConnected ? 'success' : 'warning'"
        :prepend-icon="
          chatStore.isConnected ? 'mdi-circle' : 'mdi-circle-outline'
        "
      >
        {{ chatStore.isConnected ? 'Онлайн' : 'Подключение...' }}
      </v-chip>
    </v-card-title>

    <!-- Список сообщений -->
    <v-card-text ref="messagesContainer" class="messages-container pa-4">
      <div
        v-if="chatStore.loading && chatStore.messages.length === 0"
        class="text-center py-4"
      >
        <v-progress-circular indeterminate color="primary" size="32" />
      </div>

      <v-empty-state
        v-else-if="chatStore.messages.length === 0"
        icon="mdi-message-outline"
        title="Сообщений нет"
        text="Начните общение первым"
      />

      <MessageItem
        v-for="message in chatStore.messages"
        :key="message.id"
        :message="message"
      />
    </v-card-text>

    <v-divider style="border-color: rgba(59, 130, 246, 0.1)" />

    <!-- Форма отправки -->
    <v-card-actions class="pa-3">
      <v-text-field
        v-model="newMessage"
        placeholder="Написать сообщение..."
        variant="outlined"
        density="comfortable"
        rounded="lg"
        hide-details
        :disabled="chatStore.loading || isContractClosed"
        @keyup.enter="handleSend"
      >
        <template #prepend-inner>
          <v-icon color="primary" size="20">mdi-emoticon-outline</v-icon>
        </template>

        <template #append-inner>
          <v-btn
            icon
            size="small"
            color="primary"
            variant="flat"
            :disabled="!newMessage.trim() || isContractClosed"
            :loading="sending"
            @click="handleSend"
          >
            <v-icon>mdi-send</v-icon>
          </v-btn>
        </template>
      </v-text-field>
    </v-card-actions>

    <!-- Закрытый контракт -->
    <v-alert
      v-if="isContractClosed"
      type="info"
      variant="tonal"
      density="compact"
      class="ma-3"
      prepend-icon="mdi-information"
    >
      Контракт завершён. Чат закрыт.
    </v-alert>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useContractsStore } from '@/stores/contracts'
import MessageItem from './MessageItem.vue'

const props = defineProps({
  contractId: {
    type: Number,
    required: true,
  },
})

const chatStore = useChatStore()
const contractsStore = useContractsStore()

const newMessage = ref('')
const sending = ref(false)
const messagesContainer = ref(null)

const isContractClosed = computed(
  () => contractsStore.currentContract?.status !== 'active'
)

async function loadMessages() {
  await chatStore.fetchMessages(props.contractId)
  await chatStore.markAllAsRead(props.contractId)
  scrollToBottom()
}

async function handleSend() {
  const text = newMessage.value.trim()
  if (!text) return

  sending.value = true
  await chatStore.sendMessage(props.contractId, text)
  sending.value = false

  newMessage.value = ''
  await nextTick()
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    const el = messagesContainer.value?.$el || messagesContainer.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

// Автоскролл при новых сообщениях
watch(
  () => chatStore.messages.length,
  () => scrollToBottom()
)

onMounted(async () => {
  await loadMessages()
  chatStore.connect(props.contractId)
})

onUnmounted(() => {
  chatStore.disconnect()
  chatStore.reset()
})
</script>

<style scoped>
.chat-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  overflow: hidden;
}

.messages-container {
  max-height: 450px;
  min-height: 250px;
  overflow-y: auto;
  background: radial-gradient(
    ellipse at top,
    rgba(30, 64, 175, 0.05) 0%,
    transparent 70%
  );
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.3);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.5);
}
</style>