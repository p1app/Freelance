<template>
  <v-card
    v-if="proposal && proposal.project_id"
    class="glass proposal-card h-100 d-flex flex-column fade-in"
    :to="{ name: 'ProjectDetail', params: { id: proposal.project_id } }"
  >
    <v-card-item class="pa-5">
      <template #prepend>
        <v-avatar :color="statusColor" variant="tonal" size="48">
          <v-icon>{{ statusIcon }}</v-icon>
        </v-avatar>
      </template>

      <v-card-title class="text-truncate font-weight-bold">
        {{ proposal.project_title || `Проект #${proposal.project_id}` }}
      </v-card-title>

      <v-card-subtitle>
        <v-chip :color="statusColor" size="small" variant="flat">
          {{ statusLabel }}
        </v-chip>
      </v-card-subtitle>
    </v-card-item>

    <v-card-text class="flex-grow-1 pa-5 pt-0">
      <p class="text-body-2 mb-3 text-truncate-3" style="color: #9ca3af">
        {{ proposal.cover_letter }}
      </p>

      <v-row dense>
        <v-col cols="6">
          <div class="text-caption" style="color: #9ca3af">Цена</div>
          <div class="text-h6 font-weight-bold gradient-text">
            {{ formatBudget(proposal.bid_amount) }}
          </div>
        </v-col>
        <v-col cols="6">
          <div class="text-caption" style="color: #9ca3af">Срок</div>
          <div class="font-weight-bold">{{ proposal.estimated_days }} дней</div>
        </v-col>
      </v-row>
    </v-card-text>

    <v-divider style="border-color: rgba(59, 130, 246, 0.1)" />

    <v-card-actions class="pa-5">
      <v-icon size="small" class="mr-1" color="primary">mdi-calendar</v-icon>
      <span class="text-caption" style="color: #9ca3af">
        {{ formatDate(proposal.created_at) }}
      </span>

      <v-spacer />

      <v-btn
        v-if="proposal.status === 'pending'"
        icon
        size="small"
        variant="text"
        color="error"
        @click.stop="handleWithdraw"
      >
        <v-icon>mdi-cancel</v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useProposalsStore } from '@/stores/proposals'

const props = defineProps({
  proposal: { type: Object, required: true },
})

const proposalsStore = useProposalsStore()

const statusMap = {
  pending: { label: 'Ожидает', color: 'orange', icon: 'mdi-clock-outline' },
  accepted: { label: 'Принят', color: 'green', icon: 'mdi-check-circle' },
  rejected: { label: 'Отклонён', color: 'red', icon: 'mdi-close-circle' },
  withdrawn: { label: 'Отозван', color: 'grey', icon: 'mdi-cancel' },
}

const statusLabel = computed(() => {
  if (!props.proposal?.status) return ''
  return statusMap[props.proposal.status]?.label || ''
})

const statusColor = computed(() => {
  if (!props.proposal?.status) return 'grey'
  return statusMap[props.proposal.status]?.color || 'grey'
})

const statusIcon = computed(() => {
  if (!props.proposal?.status) return 'mdi-help'
  return statusMap[props.proposal.status]?.icon || 'mdi-help'
})

function formatBudget(value) {
  if (!value) return '0 ₽'
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
    year: 'numeric',
  })
}

async function handleWithdraw() {
  if (!confirm('Отозвать отклик?')) return
  await proposalsStore.withdrawProposal(props.proposal.id)
}
</script>

<style scoped>
.proposal-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  transition: all 0.2s ease;
}

.proposal-card:hover {
  border-color: rgba(59, 130, 246, 0.4) !important;
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.15);
}

.text-truncate-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>