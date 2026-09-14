<template>
  <v-card
    class="glass contract-card h-100 d-flex flex-column fade-in"
    :to="{ name: 'ContractDetail', params: { id: contract.id } }"
  >
    <!-- Цветная полоса слева -->
    <div class="status-bar" :style="{ background: statusColor }" />

    <v-card-item class="pa-5">
      <template #prepend>
        <v-avatar :color="statusColor" variant="tonal" size="48">
          <v-icon>{{ statusIcon }}</v-icon>
        </v-avatar>
      </template>

      <v-card-title class="text-truncate font-weight-bold">
        {{ contract.project_title || `Контракт #${contract.id}` }}
      </v-card-title>

      <v-card-subtitle>
        <v-chip :color="statusColor" size="small" variant="flat">
          {{ statusLabel }}
        </v-chip>
      </v-card-subtitle>
    </v-card-item>

    <v-card-text class="flex-grow-1 pa-5 pt-0">
      <v-row dense>
        <v-col cols="6">
          <div class="text-caption" style="color: #9CA3AF">Сумма</div>
          <div class="text-h6 font-weight-bold gradient-text">
            {{ formatBudget(contract.final_price) }}
          </div>
        </v-col>
        <v-col cols="6">
          <div class="text-caption" style="color: #9CA3AF">Начало</div>
          <div class="font-weight-bold">{{ formatDate(contract.start_date) }}</div>
        </v-col>
      </v-row>
    </v-card-text>

    <v-divider style="border-color: rgba(59, 130, 246, 0.1)" />

    <v-card-actions class="pa-5">
      <v-avatar size="28" :color="avatarColor" class="mr-2">
        <span class="text-white text-caption font-weight-bold">
          {{ counterpartInitials }}
        </span>
      </v-avatar>
      <span class="text-caption" style="color: #9CA3AF">
        {{ isFreelancer ? 'Заказчик' : 'Исполнитель' }}:
      </span>
      <span class="text-body-2 font-weight-medium ml-1">
        {{ counterpartName }}
      </span>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  contract: { type: Object, required: true },
})

const authStore = useAuthStore()

const isFreelancer = computed(
  () => props.contract.freelancer_id === authStore.user?.id
)

const counterpartName = computed(() => {
  if (isFreelancer.value) {
    return props.contract.customer_name || '—'
  }
  return props.contract.freelancer_name || '—'
})

const counterpartInitials = computed(() => {
  const name = counterpartName.value
  if (name === '—') return '?'
  return name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)
})

const avatarColor = computed(() => {
  const colors = ['#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4']
  const id = isFreelancer.value ? props.contract.customer_id : props.contract.freelancer_id
  const index = (id || 0) % colors.length
  return colors[index]
})

const statusMap = {
  active: { label: 'Активен', color: 'green', icon: 'mdi-progress-clock' },
  completed: { label: 'Завершён', color: 'purple', icon: 'mdi-check-all' },
  cancelled: { label: 'Отменён', color: 'red', icon: 'mdi-cancel' },
  disputed: { label: 'Спор', color: 'orange', icon: 'mdi-alert' },
}

const statusLabel = computed(() => statusMap[props.contract.status]?.label || '')
const statusColor = computed(() => statusMap[props.contract.status]?.color || 'grey')
const statusIcon = computed(() => statusMap[props.contract.status]?.icon || 'mdi-help')

function formatBudget(value) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(value)
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
  })
}
</script>

<style scoped>
.contract-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  position: relative;
  overflow: hidden;
  transition: all 0.2s ease;
}

.contract-card:hover {
  border-color: rgba(59, 130, 246, 0.4) !important;
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.15);
}

.status-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}
</style>