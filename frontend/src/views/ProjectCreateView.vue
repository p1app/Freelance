<template>
  <v-container>
    <v-btn
      variant="text"
      prepend-icon="mdi-arrow-left"
      class="mb-4"
      to="/my-projects"
    >
      Назад
    </v-btn>

    <ProjectForm
      :loading="loading"
      :error="projectsStore.error"
      @submit="handleSubmit"
      @cancel="$router.push('/my-projects')"
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import ProjectForm from '@/components/project/ProjectForm.vue'

const router = useRouter()
const projectsStore = useProjectsStore()

const loading = ref(false)

async function handleSubmit(data) {
  loading.value = true
  const result = await projectsStore.createProject(data)
  loading.value = false

  if (result) {
    router.push(`/projects/${result.id}`)
  }
}
</script>