<template>
  <div>
    <v-skeleton-loader v-if="adminStore.loading && !stats" type="article" />

    <template v-else-if="stats">
      <!-- Карточки -->
      <v-row>
        <v-col cols="12" sm="6" md="3">
          <v-card color="blue" variant="tonal">
            <v-card-text>
              <div class="text-caption">Пользователей</div>
              <div class="text-h4 font-weight-bold">{{ stats.total_users }}</div>
              <div class="text-caption">
                Заказчиков: {{ stats.clients_count }} |
                Фрилансеров: {{ stats.freelancers_count }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="green" variant="tonal">
            <v-card-text>
              <div class="text-caption">Проектов</div>
              <div class="text-h4 font-weight-bold">{{ stats.total_projects }}</div>
              <div class="text-caption">
                Открыто: {{ stats.open_projects }} |
                В работе: {{ stats.in_progress_projects }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="purple" variant="tonal">
            <v-card-text>
              <div class="text-caption">Контрактов</div>
              <div class="text-h4 font-weight-bold">{{ stats.total_contracts }}</div>
              <div class="text-caption">
                Активных: {{ stats.active_contracts }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="amber" variant="tonal">
            <v-card-text>
              <div class="text-caption">Средний рейтинг</div>
              <div class="text-h4 font-weight-bold">
                {{ stats.average_rating?.toFixed(2) || '0.00' }}
              </div>
              <div class="text-caption">
                Завершено: {{ stats.completed_projects }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Детали -->
      <v-card class="mt-4">
        <v-card-title>Детали</v-card-title>
        <v-list>
          <v-list-item>
            <v-list-item-title>Всего пользователей</v-list-item-title>
            <template #append>{{ stats.total_users }}</template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Заказчики</v-list-item-title>
            <template #append>{{ stats.clients_count }}</template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Фрилансеры</v-list-item-title>
            <template #append>{{ stats.freelancers_count }}</template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Всего проектов</v-list-item-title>
            <template #append>{{ stats.total_projects }}</template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Завершённых проектов</v-list-item-title>
            <template #append>{{ stats.completed_projects }}</template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Удалённых проектов</v-list-item-title>
            <template #append>{{ stats.deleted_projects ?? 0 }}</template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Всего контрактов</v-list-item-title>
            <template #append>{{ stats.total_contracts }}</template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Активных контрактов</v-list-item-title>
            <template #append>{{ stats.active_contracts }}</template>
          </v-list-item>
        </v-list>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()

const stats = computed(() => adminStore.stats)

onMounted(() => {
  adminStore.fetchStats()
})
</script>