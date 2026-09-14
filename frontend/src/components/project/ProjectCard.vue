<template>
  <v-card
    class="h-100 d-flex flex-column card-glow hover-lift"
    :to="{ name: 'ProjectDetail', params: { id: project.id } }"
    :style="{ borderLeft: `4px solid ${statusColor}` }"
  >
    <v-card-item>
      <template #prepend>
        <v-avatar :color="categoryColor" size="40" variant="tonal">
          <v-icon>{{ categoryIcon }}</v-icon>
        </v-avatar>
      </template>

      <v-card-title class="text-truncate">
        {{ project.title }}
      </v-card-title>

      <v-card-subtitle>
        <v-chip :color="statusColor" size="small" variant="tonal">
          {{ statusLabel }}
        </v-chip>
      </v-card-subtitle>
    </v-card-item>

    <v-card-text class="flex-grow-1">
      <p class="text-body-2 text-truncate-3" style="color: #9CA3AF">
        {{ project.description }}
      </p>
    </v-card-text>

    <v-divider style="border-color: rgba(59, 130, 246, 0.1)" />

    <v-card-actions>
      <v-icon size="small" class="mr-1" color="primary">mdi-currency-usd</v-icon>
      <span class="font-weight-bold">{{ formatBudget(project.budget) }}</span>

      <v-spacer />

      <v-icon size="small" class="mr-1" color="primary">mdi-calendar</v-icon>
      <span class="text-caption">{{ formatDate(project.deadline) }}</span>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  project: { type: Object, required: true },
})

const categoryMap = {
  development: { label: 'Разработка', color: 'blue', icon: 'mdi-code-tags' },
  design: { label: 'Дизайн', color: 'purple', icon: 'mdi-palette' },
  marketing: { label: 'Маркетинг', color: 'orange', icon: 'mdi-bullhorn' },
  writing: { label: 'Тексты', color: 'green', icon: 'mdi-pencil' },
  other: { label: 'Другое', color: 'grey', icon: 'mdi-dots-horizontal' },
}

const statusMap = {
  draft: { label: 'Черновик', color: 'grey' },
  open: { label: 'Открыт', color: 'green' },
  in_progress: { label: 'В работе', color: 'blue' },
  completed: { label: 'Завершён', color: 'purple' },
  cancelled: { label: 'Отменён', color: 'red' },
}

const categoryLabel = computed(() => categoryMap[props.project.category]?.label || '')
const categoryColor = computed(() => categoryMap[props.project.category]?.color || 'grey')
const categoryIcon = computed(() => categoryMap[props.project.category]?.icon || 'mdi-help')

const statusLabel = computed(() => statusMap[props.project.status]?.label || '')
const statusColor = computed(() => statusMap[props.project.status]?.color || 'grey')

function formatBudget(value) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(value)
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
  })
}
</script>

<style scoped>
.text-truncate-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>