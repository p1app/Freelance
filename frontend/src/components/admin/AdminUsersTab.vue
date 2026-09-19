<template>
  <div>
    <!-- Фильтры -->
    <v-card class="glass mb-4 fade-in">
      <v-card-text class="pa-5">
        <v-row dense>
          <v-col cols="12" sm="4">
            <v-select
              v-model="roleFilter"
              :items="roleOptions"
              label="Роль"
              clearable
              density="compact"
              variant="outlined"
              rounded="lg"
              prepend-inner-icon="mdi-account-tag"
              @update:model-value="loadUsers"
            />
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="Статус"
              clearable
              density="compact"
              variant="outlined"
              rounded="lg"
              prepend-inner-icon="mdi-check-circle"
              @update:model-value="loadUsers"
            />
          </v-col>
          <v-col cols="12" sm="4" class="d-flex align-center">
            <v-chip
              size="small"
              color="primary"
              variant="tonal"
              prepend-icon="mdi-account-multiple"
            >
              Всего: {{ adminStore.usersPagination.total }}
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
        :items="adminStore.users"
        :items-per-page="-1"
        hide-default-footer
        class="admin-table"
        hover
        @click:row="handleRowClick"
      >
        <template #item.username="{ item }">
          <span class="font-weight-medium" style="color: #60A5FA">
            {{ item.username }}
          </span>
        </template>

        <template #item.role="{ item }">
          <v-chip :color="roleColor(item.role)" size="small" variant="flat">
            {{ roleLabel(item.role) }}
          </v-chip>
        </template>

        <template #item.is_active="{ item }">
          <v-chip
            :color="item.is_active ? 'green' : 'red'"
            size="small"
            variant="flat"
            :prepend-icon="item.is_active ? 'mdi-check-circle' : 'mdi-block-helper'"
          >
            {{ item.is_active ? 'Активен' : 'Заблокирован' }}
          </v-chip>
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
            @click.stop="viewProfile(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>

          <v-btn
            v-if="item.is_active"
            icon
            size="small"
            variant="text"
            color="error"
            @click.stop="handleBlock(item)"
          >
            <v-icon>mdi-block-helper</v-icon>
          </v-btn>
          <v-btn
            v-else
            icon
            size="small"
            variant="text"
            color="success"
            @click.stop="handleUnblock(item)"
          >
            <v-icon>mdi-check-circle</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Пагинация -->
    <v-pagination
      v-if="adminStore.usersPagination.pages > 1"
      :model-value="adminStore.usersPagination.page"
      :length="adminStore.usersPagination.pages"
      class="mt-4"
      @update:model-value="onPageChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useConfirm } from '@/composables/useConfirm'

const router = useRouter()
const adminStore = useAdminStore()
const { confirm } = useConfirm()

const roleFilter = ref(null)
const statusFilter = ref(null)

const roleOptions = [
  { title: 'Заказчик', value: 'client' },
  { title: 'Фрилансер', value: 'freelancer' },
  { title: 'Администратор', value: 'admin' },
]

const statusOptions = [
  { title: 'Активные', value: true },
  { title: 'Заблокированные', value: false },
]

const headers = [
  { title: 'ID', key: 'id', sortable: false },
  { title: 'Username', key: 'username' },
  { title: 'Email', key: 'email' },
  { title: 'Имя', key: 'fullname' },
  { title: 'Роль', key: 'role' },
  { title: 'Статус', key: 'is_active' },
  { title: 'Дата', key: 'created_at' },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' },
]

function roleLabel(role) {
  const labels = { client: 'Заказчик', freelancer: 'Фрилансер', admin: 'Админ' }
  return labels[role] || role
}

function roleColor(role) {
  const colors = { client: 'blue', freelancer: 'green', admin: 'red' }
  return colors[role] || 'grey'
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function loadUsers() {
  adminStore.fetchUsers({
    role: roleFilter.value,
    is_active: statusFilter.value,
  })
}

function onPageChange(page) {
  adminStore.usersPagination.page = page
  loadUsers()
}

function handleRowClick(event, { item }) {
  viewProfile(item)
}

function viewProfile(item) {
  router.push({ name: 'UserPublic', params: { id: item.id } })
}

async function handleBlock(item) {
  const agreed = await confirm({
    title: `Заблокировать ${item.username}?`,
    text: 'Пользователь не сможет войти и пользоваться API до разблокировки.',
    confirmText: 'Заблокировать',
    color: 'error',
  })
  if (!agreed) return

  await adminStore.blockUser(item.id)
}

async function handleUnblock(item) {
  await adminStore.unblockUser(item.id)
}

onMounted(loadUsers)
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