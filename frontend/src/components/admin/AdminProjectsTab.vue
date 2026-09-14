<template>
  <div>
    <!-- Фильтры -->
    <v-card class="glass mb-4 fade-in">
      <v-card-text class="pa-5">
        <v-row dense>
          <v-col cols="12" sm="4">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="Статус"
              clearable
              density="compact"
              variant="outlined"
              rounded="lg"
              prepend-inner-icon="mdi-progress-check"
              @update:model-value="loadProjects"
            />
          </v-col>
          <v-col cols="12" sm="4" class="d-flex align-center">
            <v-chip
              size="small"
              color="primary"
              variant="tonal"
              prepend-icon="mdi-briefcase"
            >
              Всего: {{ adminStore.projectsPagination.total }}
            </v-chip>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Загрузка -->
    <v-skeleton-loader v-if="adminStore.loading" type="table" />

    <!-- Таблица -->
    <v-card v-else class="glass fade-in">
      <v-data-table
        :headers="headers"
        :items="adminStore.projects"
        :items-per-page="-1"
        hide-default-footer
        class="admin-table"
        hover
        @click:row="handleRowClick"
      >
        <template #item.title="{ item }">
          <span class="font-weight-medium" style="color: #60A5FA">
            {{ item.title }}
          </span>
        </template>

        <template #item.status="{ item }">
          <v-chip :color="statusColor(item.status)" size="small" variant="flat">
            {{ statusLabel(item.status) }}
          </v-chip>
        </template>

        <template #item.budget="{ item }">
          <span class="font-weight-bold gradient-text">
            {{ formatBudget(item.budget) }}
          </span>
        </template>

        <template #item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon
            size="small"
            variant="text"
            color="primary"
            @click.stop="viewProject(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>

          <v-btn
            icon
            size="small"
            variant="text"
            color="error"
            @click.stop="handleDelete(item)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Пагинация -->
    <v-pagination
      v-if="adminStore.projectsPagination.pages > 1"
      :model-value="adminStore.projectsPagination.page"
      :length="adminStore.projectsPagination.pages"
      class="mt-4"
      @update:model-value="onPageChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const router = useRouter()
const adminStore = useAdminStore()

const statusFilter = ref(null)

const statusOptions = [
  { title: 'Черновик', value: 'draft' },
  { title: 'Открыт', value: 'open' },
  { title: 'В работе', value: 'in_progress' },
  { title: 'Завершён', value: 'completed' },
  { title: 'Отменён', value: 'cancelled' },
]

const headers = [
  { title: 'ID', key: 'id', sortable: false },
  { title: 'Название', key: 'title' },
  { title: 'Статус', key: 'status' },
  { title: 'Бюджет', key: 'budget' },
  { title: 'Заказчик', key: 'customer_name' },
  { title: 'Дата', key: 'created_at' },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' },
]

function statusLabel(status) {
  const labels = {
    draft: 'Черновик',
    open: 'Открыт',
    in_progress: 'В работе',
    completed: 'Завершён',
    cancelled: 'Отменён',
  }
  return labels[status] || status
}

function statusColor(status) {
  const colors = {
    draft: 'grey',
    open: 'green',
    in_progress: 'blue',
    completed: 'purple',
    cancelled: 'red',
  }
  return colors[status] || 'grey'
}

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
    year: 'numeric',
  })
}

function loadProjects() {
  adminStore.fetchProjects({ status: statusFilter.value })
}

function onPageChange(page) {
  adminStore.projectsPagination.page = page
  loadProjects()
}

function handleRowClick(event, { item }) {
  viewProject(item)
}

function viewProject(item) {
  router.push({ name: 'ProjectDetail', params: { id: item.id } })
}

async function handleDelete(item) {
  if (!confirm(`Удалить проект "${item.title}"?`)) return
  await adminStore.deleteProject(item.id)
}

onMounted(loadProjects)
</script>

<style scoped>
:deep(.admin-table) {
  background: transparent !important;
}

:deep(.admin-table thead) {
  background: rgba(59, 130, 246, 0.05);
}

:deep(.admin-table tbody tr) {
  cursor: pointer;
  transition: background 0.2s ease;
}

:deep(.admin-table tbody tr:hover) {
  background: rgba(59, 130, 246, 0.08) !important;
}
</style>