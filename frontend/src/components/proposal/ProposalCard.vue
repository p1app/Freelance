<template>
  <v-card class="glass proposal-card mb-3 fade-in">
    <v-card-item class="pa-5">
      <template #prepend>
        <v-avatar :color="avatarColor" size="48">
          <span class="text-white font-weight-bold">
            {{ initials }}
          </span>
        </v-avatar>
      </template>

      <v-card-title class="text-h6 font-weight-bold">
        <router-link
          :to="{ name: 'UserPublic', params: { id: proposal.freelancer_id } }"
          class="text-decoration-none"
          style="color: inherit"
        >
          {{ proposal.freelancer_name }}
        </router-link>
      </v-card-title>

      <v-card-subtitle>
        <v-chip :color="statusColor" size="small" variant="flat">
          {{ statusLabel }}
        </v-chip>
      </v-card-subtitle>
    </v-card-item>

    <v-card-text class="pa-5 pt-0">
      <p class="text-body-2 mb-4" style="color: #D1D5DB">
        {{ proposal.cover_letter }}
      </p>

      <v-row dense>
        <v-col cols="6">
          <div class="metric-box">
            <v-icon color="primary" size="20">mdi-currency-usd</v-icon>
            <div>
              <div class="text-caption" style="color: #9CA3AF">Цена</div>
              <div class="font-weight-bold">{{ formatBudget(proposal.bid_amount) }}</div>
            </div>
          </div>
        </v-col>
        <v-col cols="6">
          <div class="metric-box">
            <v-icon color="primary" size="20">mdi-clock-outline</v-icon>
            <div>
              <div class="text-caption" style="color: #9CA3AF">Срок</div>
              <div class="font-weight-bold">{{ proposal.estimated_days }} дней</div>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>

    <!-- Действия для заказчика -->
    <v-card-actions
      v-if="canManage && proposal.status === 'pending'"
      class="pa-5 pt-0"
    >
      <v-btn
        color="success"
        variant="flat"
        prepend-icon="mdi-check"
        :loading="loading"
        class="btn-glow flex-grow-1"
        @click="$emit('accept', proposal.id)"
      >
        Принять
      </v-btn>

      <v-btn
        color="error"
        variant="outlined"
        prepend-icon="mdi-close"
        :loading="loading"
        class="flex-grow-1"
        @click="$emit('reject', proposal.id)"
      >
        Отклонить
      </v-btn>
    </v-card-actions>

    <!-- Действия для фрилансера -->
    <v-card-actions
      v-if="isOwner && proposal.status === 'pending'"
      class="pa-5 pt-0"
    >
      <v-btn
        variant="outlined"
        color="error"
        prepend-icon="mdi-cancel"
        @click="$emit('withdraw', proposal.id)"
      >
        Отозвать отклик
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  proposal: { type: Object, required: true },
  projectCustomerId: { type: Number, required: true },
  loading: { type: Boolean, default: false },
})

defineEmits(['accept', 'reject', 'withdraw'])

const authStore = useAuthStore()

const initials = computed(() => {
  const name = props.proposal.freelancer_name || 'U'
  return name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)
})

const avatarColor = computed(() => {
  const colors = ['#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4']
  const index = (props.proposal.freelancer_id || 0) % colors.length
  return colors[index]
})

const isOwner = computed(
  () => props.proposal.freelancer_id === authStore.user?.id
)

const canManage = computed(
  () => props.projectCustomerId === authStore.user?.id
)

const statusMap = {
  pending: { label: 'На рассмотрении', color: 'orange' },
  accepted: { label: 'Принят', color: 'green' },
  rejected: { label: 'Отклонён', color: 'red' },
  withdrawn: { label: 'Отозван', color: 'grey' },
}

const statusLabel = computed(() => statusMap[props.proposal.status]?.label || '')
const statusColor = computed(() => statusMap[props.proposal.status]?.color || 'grey')

function formatBudget(value) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(value)
}
</script>

<style scoped>
.proposal-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  transition: all 0.2s ease;
}

.proposal-card:hover {
  border-color: rgba(59, 130, 246, 0.4) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
}

.metric-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.1);
}
</style>