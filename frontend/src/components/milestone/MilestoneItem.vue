<template>
  <div class="milestone-wrapper d-flex fade-in">
    <!-- Timeline-линия -->
    <div class="timeline-col">
      <div class="timeline-dot" :style="{ background: statusColor }">
        <v-icon size="16" color="white">{{ statusIcon }}</v-icon>
      </div>
      <div class="timeline-line" />
    </div>

    <!-- Карточка этапа -->
    <v-card class="glass milestone-card flex-grow-1 mb-4">
      <v-card-item class="pa-5">
        <v-card-title class="text-h6 font-weight-bold">
          {{ milestone.title }}
        </v-card-title>

        <v-card-subtitle class="d-flex align-center mt-2">
          <v-chip :color="statusColor" size="small" variant="flat">
            {{ statusLabel }}
          </v-chip>
          <span class="ml-3 text-caption" style="color: #9CA3AF">
            <v-icon size="14" class="mr-1">mdi-calendar</v-icon>
            {{ formatDate(milestone.due_date) }}
          </span>
        </v-card-subtitle>
      </v-card-item>

      <v-card-text v-if="milestone.description" class="pa-5 pt-0">
        <p class="text-body-2" style="color: #D1D5DB">
          {{ milestone.description }}
        </p>
      </v-card-text>

      <!-- Действия (только для активного контракта) -->
      <v-card-actions v-if="contractStatus === 'active'" class="pa-5 pt-0">
        <!-- Фрилансер: завершить -->
        <v-btn
          v-if="isFreelancer && milestone.status === 'pending'"
          color="primary"
          variant="flat"
          prepend-icon="mdi-check"
          :loading="loading"
          class="btn-glow"
          @click="$emit('complete', milestone.id)"
        >
          Завершить
        </v-btn>

        <!-- Заказчик: утвердить -->
        <v-btn
          v-if="isCustomer && milestone.status === 'completed'"
          color="success"
          variant="flat"
          prepend-icon="mdi-check-circle"
          :loading="loading"
          class="btn-glow"
          @click="$emit('approve', milestone.id)"
        >
          Утвердить
        </v-btn>

        <!-- Фрилансер: редактировать / удалить -->
        <template v-if="isFreelancer && milestone.status === 'pending'">
          <v-spacer />
          <v-btn
            icon
            variant="text"
            size="small"
            @click="$emit('edit', milestone)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="error"
            @click="$emit('delete', milestone.id)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  milestone: { type: Object, required: true },
  contractStatus: { type: String, default: 'active' },
  isFreelancer: { type: Boolean, default: false },
  isCustomer: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

defineEmits(['complete', 'approve', 'edit', 'delete'])

const statusMap = {
  pending: { label: 'Ожидает', color: 'orange', icon: 'mdi-clock-outline' },
  completed: { label: 'Завершён', color: 'blue', icon: 'mdi-check' },
  approved: { label: 'Утверждён', color: 'green', icon: 'mdi-check-circle' },
}

const statusLabel = computed(() => statusMap[props.milestone.status]?.label || '')
const statusColor = computed(() => statusMap[props.milestone.status]?.color || 'grey')
const statusIcon = computed(() => statusMap[props.milestone.status]?.icon || 'mdi-help')

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<style scoped>
.milestone-wrapper {
  position: relative;
}

.timeline-col {
  width: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex-shrink: 0;
}

.timeline-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  margin-top: 8px;
}

.timeline-line {
  flex-grow: 1;
  width: 2px;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.3), transparent);
  margin-top: 4px;
}

.milestone-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  transition: all 0.2s ease;
}

.milestone-card:hover {
  border-color: rgba(59, 130, 246, 0.4) !important;
  transform: translateX(4px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.1);
}
</style>