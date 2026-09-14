<template>
  <v-container>
    <div class="d-flex align-center mb-6">
      <v-icon color="primary" size="36" class="mr-3">mdi-file-document-multiple</v-icon>
      <h1 class="text-h4 font-weight-bold">Мои контракты</h1>
    </div>

    <!-- Фильтры -->
    <v-card class="glass mb-6 fade-in">
      <v-card-text class="pa-5">
        <div class="d-flex gap-2 flex-wrap">
          <v-chip
            v-for="opt in statusOptions"
            :key="opt.value"
            :color="statusFilter === opt.value ? 'primary' : undefined"
            :variant="statusFilter === opt.value ? 'flat' : 'outlined'"
            class="status-chip"
            @click="setFilter(opt.value)"
          >
            {{ opt.title }}
          </v-chip>
        </div>
      </v-card-text>
    </v-card>

    <!-- Ошибка -->
    <v-alert
      v-if="contractsStore.error"
      type="error"
      variant="tonal"
      class="mb-4"
      closable
      @click:close="contractsStore.clearError()"
    >
      {{ contractsStore.error }}
    </v-alert>

    <!-- Загрузка -->
    <v-row v-if="contractsStore.loading">
      <v-col v-for="n in 6" :key="n" cols="12" sm="6" md="4">
        <v-skeleton-loader type="card" />
      </v-col>
    </v-row>

    <!-- Пусто -->
    <v-empty-state
      v-else-if="contractsStore.contracts.length === 0"
      icon="mdi-file-document-outline"
      title="Контрактов нет"
      text="Здесь появятся ваши контракты после принятия отклика"
    />

    <!-- Список -->
    <v-row v-else>
      <v-col
        v-for="contract in contractsStore.contracts"
        :key="contract.id"
        cols="12"
        sm="6"
        md="4"
      >
        <ContractCard :contract="contract" />
      </v-col>
    </v-row>

    <!-- Пагинация -->
    <v-pagination
      v-if="contractsStore.pagination.pages > 1"
      :model-value="contractsStore.pagination.page"
      :length="contractsStore.pagination.pages"
      class="mt-6"
      @update:model-value="contractsStore.setPage"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useContractsStore } from '@/stores/contracts'
import ContractCard from '@/components/contract/ContractCard.vue'

const contractsStore = useContractsStore()

const statusFilter = ref(null)

const statusOptions = [
  { title: 'Все', value: null },
  { title: 'Активные', value: 'active' },
  { title: 'Завершённые', value: 'completed' },
  { title: 'Отменённые', value: 'cancelled' },
]

function setFilter(value) {
  statusFilter.value = value
  loadContracts()
}

function loadContracts() {
  contractsStore.fetchMyContracts({
    status: statusFilter.value,
  })
}

onMounted(loadContracts)
</script>

<style scoped>
.status-chip {
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-chip:hover {
  transform: translateY(-2px);
}

.gap-2 {
  gap: 8px;
}
</style>