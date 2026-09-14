<template>
  <v-container>
    <h1 class="text-h4 mb-4">
      {{ authStore.isClient ? 'Мои проекты' : 'Проекты в работе' }}
    </h1>

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

    <template v-else>
      <!-- Заказчик: созданные проекты -->
      <template v-if="authStore.isClient">
        <v-empty-state
          v-if="projectsStore.myProjects.length === 0"
          icon="mdi-folder-outline"
          title="Нет созданных проектов"
          text="Создайте первый проект, чтобы он появился здесь"
        >
          <template #actions>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              :to="{ name: 'ProjectCreate' }"
            >
              Создать проект
            </v-btn>
          </template>
        </v-empty-state>

        <v-row v-else>
          <v-col
            v-for="project in projectsStore.myProjects"
            :key="project.id"
            cols="12"
            sm="6"
            md="4"
          >
            <ProjectCard :project="project" />
          </v-col>
        </v-row>

        <v-pagination
          v-if="projectsStore.myProjectsPagination.pages > 1"
          :model-value="projectsStore.myProjectsPagination.page"
          :length="projectsStore.myProjectsPagination.pages"
          class="mt-6"
          @update:model-value="projectsStore.fetchMyProjects"
        />
      </template>

      <!-- Фрилансер: проекты в работе -->
      <template v-else-if="authStore.isFreelancer">
        <v-empty-state
          v-if="projectsStore.workingProjects.length === 0"
          icon="mdi-briefcase-off-outline"
          title="Нет проектов в работе"
          text="Здесь появятся проекты, где вы исполнитель"
        />

        <v-row v-else>
          <v-col
            v-for="project in projectsStore.workingProjects"
            :key="project.id"
            cols="12"
            sm="6"
            md="4"
          >
            <ProjectCard :project="project" />
          </v-col>
        </v-row>

        <v-pagination
          v-if="projectsStore.workingPagination.pages > 1"
          :model-value="projectsStore.workingPagination.page"
          :length="projectsStore.workingPagination.pages"
          class="mt-6"
          @update:model-value="projectsStore.fetchWorkingProjects"
        />
      </template>
    </template>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import { useAuthStore } from '@/stores/auth'
import ProjectCard from '@/components/project/ProjectCard.vue'

const projectsStore = useProjectsStore()
const authStore = useAuthStore()

onMounted(() => {
  if (authStore.isClient) {
    projectsStore.fetchMyProjects()
  } else if (authStore.isFreelancer) {
    projectsStore.fetchWorkingProjects()
  }
})
</script>