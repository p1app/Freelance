<template>
  <v-container>
    <div class="d-flex align-center mb-6">
      <v-icon color="primary" size="36" class="mr-3">mdi-send</v-icon>
      <h1 class="text-h4 font-weight-bold">Мои отклики</h1>
    </div>

    <!-- Фильтры -->
    <v-card class="glass mb-6 fade-in">
      <v-card-text class="pa-5">
        <div class="d-flex gap-2 flex-wrap">
          <v-chip
            v-for="opt in statusOptions"
            :key="opt.value ?? 'all'"
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
      v-if="proposalsStore.error"
      type="error"
      variant="tonal"
      class="mb-4"
      closable
      @click:close="proposalsStore.clearError()"
    >
      {{ proposalsStore.error }}
    </v-alert>

    <!-- Загрузка -->
    <v-row v-if="proposalsStore.loading">
      <v-col v-for="n in 6" :key="n" cols="12" sm="6" md="4">
        <v-skeleton-loader type="card" />
      </v-col>
    </v-row>

    <!-- Пусто -->
    <v-empty-state
      v-else-if="proposalsStore.proposals.length === 0"
      icon="mdi-send-outline"
      title="Откликов нет"
      text="Здесь появятся ваши отклики на проекты"
    >
      <template #actions>
        <v-btn color="primary" to="/" prepend-icon="mdi-briefcase">
          Найти проекты
        </v-btn>
      </template>
    </v-empty-state>

    <!-- Список -->
    <v-row v-else>
      <v-col
        v-for="proposal in proposalsStore.proposals"
        :key="proposal.id"
        cols="12"
        sm="6"
        md="4"
      >
        <MyProposalCard :proposal="proposal" />
      </v-col>
    </v-row>

    <!-- Пагинация -->
    <v-pagination
      v-if="proposalsStore.pagination.pages > 1"
      :model-value="proposalsStore.pagination.page"
      :length="proposalsStore.pagination.pages"
      class="mt-6"
      @update:model-value="onPageChange"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProposalsStore } from '@/stores/proposals'
import MyProposalCard from '@/components/proposal/MyProposalCard.vue'

const proposalsStore = useProposalsStore()

const statusFilter = ref(null)

const statusOptions = [
  { title: 'Все', value: null },
  { title: 'Ожидают', value: 'pending' },
  { title: 'Приняты', value: 'accepted' },
  { title: 'Отклонены', value: 'rejected' },
  { title: 'Отозваны', value: 'withdrawn' },
]

function setFilter(value) {
  statusFilter.value = value
  loadProposals()
}

function loadProposals() {
  proposalsStore.fetchMyProposals({
    status: statusFilter.value,
  })
}

function onPageChange(page) {
  proposalsStore.setPage(page)
  loadProposals()
}

onMounted(loadProposals)
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