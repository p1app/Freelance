<template>
  <v-container>
    <!-- Заголовок -->
    <div class="d-flex align-center justify-space-between mb-4">
      <h1 class="text-h4">Проекты</h1>

      <!-- Кнопка "Создать проект" только для заказчика -->
      <v-btn
        v-if="authStore.isClient"
        color="primary"
        prepend-icon="mdi-plus"
        :to="{ name: 'ProjectCreate' }"
      >
        Создать проект
      </v-btn>
    </div>

    <!-- Фильтры -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row density="compact">
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="localFilters.category"
              :items="categories"
              label="Категория"
              clearable
              density="compact"
              variant="outlined"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="localFilters.search"
              label="Поиск"
              prepend-inner-icon="mdi-magnify"
              clearable
              density="compact"
              variant="outlined"
              @keyup.enter="applyFilters"
            />
          </v-col>

          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model.number="localFilters.budget_min"
              label="Бюджет от"
              type="number"
              density="compact"
              variant="outlined"
            />
          </v-col>

          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model.number="localFilters.budget_max"
              label="Бюджет до"
              type="number"
              density="compact"
              variant="outlined"
            />
          </v-col>

          <v-col cols="12" md="2" class="d-flex gap-2">
            <v-btn color="primary" block @click="applyFilters">
              Применить
            </v-btn>
            <v-btn variant="text" @click="resetFilters">
              Сброс
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Ошибка -->
    <v-alert
      v-if="projectsStore.error"
      type="error"
      variant="tonal"
      class="mb-4"
      closable
      @click:close="projectsStore.clearError()"
    >
      {{ projectsStore.error }}
    </v-alert>

    <!-- Загрузка -->
    <v-row v-if="projectsStore.loading">
      <v-col v-for="n in 6" :key="n" cols="12" sm="6" md="4">
        <v-skeleton-loader type="card" />
      </v-col>
    </v-row>

    <!-- Пусто -->
    <v-empty-state
      v-else-if="projectsStore.projects.length === 0"
      icon="mdi-briefcase-off-outline"
      title="Проекты не найдены"
      text="Попробуйте изменить фильтры или зайти позже"
    />

    <!-- Список -->
    <v-row v-else>
      <v-col
        v-for="project in projectsStore.projects"
        :key="project.id"
        cols="12"
        sm="6"
        md="4"
      >
        <ProjectCard :project="project" />
      </v-col>
    </v-row>

    <!-- Пагинация -->
    <v-pagination
      v-if="projectsStore.pagination.pages > 1"
      :model-value="projectsStore.pagination.page"
      :length="projectsStore.pagination.pages"
      :total-visible="7"
      class="mt-6"
      @update:model-value="onPageChange"
    />
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import { useAuthStore } from '@/stores/auth'
import ProjectCard from '@/components/project/ProjectCard.vue'

const projectsStore = useProjectsStore()
const authStore = useAuthStore()

const categories = [
  { title: 'Разработка', value: 'development' },
  { title: 'Дизайн', value: 'design' },
  { title: 'Маркетинг', value: 'marketing' },
  { title: 'Тексты', value: 'writing' },
  { title: 'Другое', value: 'other' },
]

const localFilters = reactive({
  category: null,
  search: null,
  budget_min: null,
  budget_max: null,
})

function applyFilters() {
  projectsStore.setFilters(localFilters)
}

function resetFilters() {
  localFilters.category = null
  localFilters.search = null
  localFilters.budget_min = null
  localFilters.budget_max = null
  projectsStore.resetFilters()
}

function onPageChange(page) {
  projectsStore.setPage(page)
}

onMounted(() => {
  projectsStore.fetchProjects()
})
</script>