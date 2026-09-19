<template>
  <v-container>
    <v-skeleton-loader v-if="projectsStore.loading" type="article" />

    <v-empty-state
      v-else-if="!project"
      icon="mdi-briefcase-off-outline"
      title="Проект не найден"
      text="Возможно, он был удалён или отменён"
    >
      <template #actions>
        <v-btn color="primary" to="/">Вернуться к проектам</v-btn>
      </template>
    </v-empty-state>

    <template v-else>
      <v-btn
        variant="text"
        prepend-icon="mdi-arrow-left"
        class="mb-4"
        to="/"
      >
        Назад к проектам
      </v-btn>

      <!-- Основная карточка -->
      <v-card class="glass project-card mb-4 fade-in">
        <div class="project-header pa-6">
          <div class="d-flex align-center gap-2 mb-3">
            <v-chip :color="categoryColor" variant="flat" :prepend-icon="categoryIcon">
              {{ categoryLabel }}
            </v-chip>
            <v-chip :color="statusColor" variant="flat" :prepend-icon="statusIcon">
              {{ statusLabel }}
            </v-chip>
          </div>

          <h1 class="text-h4 font-weight-bold mb-3">{{ project.title }}</h1>

          <div class="d-flex align-center flex-wrap gap-4 text-body-2" style="color: #9ca3af">
            <div class="d-flex align-center">
              <v-icon size="18" class="mr-1">mdi-account</v-icon>
              <router-link
                :to="{ name: 'UserPublic', params: { id: project.customer_id } }"
                class="text-decoration-none"
                style="color: #60a5fa"
              >
                {{ project.customer_name || '—' }}
              </router-link>
            </div>
            <div class="d-flex align-center">
              <v-icon size="18" class="mr-1">mdi-clock-outline</v-icon>
              {{ formatDate(project.deadline) }}
            </div>
          </div>
        </div>

        <v-divider style="border-color: rgba(59, 130, 246, 0.15)" />

        <v-card-text class="pa-6">
          <h3 class="text-h6 font-weight-bold mb-3">Описание</h3>
          <p class="text-body-1 mb-6">{{ project.description }}</p>

          <v-row>
            <v-col cols="12" sm="4">
              <div class="info-card">
                <v-icon color="primary" size="32" class="mb-2">mdi-wallet-outline</v-icon>
                <div class="text-caption" style="color: #9ca3af">Бюджет</div>
                <div class="text-h5 font-weight-bold gradient-text">
                  {{ formatBudget(project.budget) }}
                </div>
              </div>
            </v-col>

            <v-col cols="12" sm="4">
              <div class="info-card">
                <v-icon color="primary" size="32" class="mb-2">mdi-calendar-clock</v-icon>
                <div class="text-caption" style="color: #9ca3af">Дедлайн</div>
                <div class="text-h6 font-weight-bold">{{ formatDate(project.deadline) }}</div>
              </div>
            </v-col>

            <v-col cols="12" sm="4">
              <div class="info-card">
                <v-icon color="primary" size="32" class="mb-2">mdi-send</v-icon>
                <div class="text-caption" style="color: #9ca3af">Откликов</div>
                <div class="text-h5 font-weight-bold">{{ project.proposal_count || 0 }}</div>
              </div>
            </v-col>
          </v-row>

          <v-alert
            v-if="project.freelancer_name"
            type="info"
            variant="tonal"
            class="mt-4"
            prepend-icon="mdi-account-check"
          >
            Исполнитель:
            <router-link
              :to="{ name: 'UserPublic', params: { id: project.freelancer_id } }"
              class="text-decoration-none font-weight-bold"
              style="color: #60a5fa"
            >
              {{ project.freelancer_name }}
            </router-link>
          </v-alert>
        </v-card-text>

        <v-card-actions v-if="isCustomer" class="pa-6 pt-0">
          <v-btn
            v-if="project.status === 'draft'"
            color="primary"
            size="large"
            prepend-icon="mdi-publish"
            :loading="actionLoading"
            class="btn-glow"
            @click="handlePublish"
          >
            Опубликовать
          </v-btn>

          <v-btn
            v-if="['open', 'in_progress'].includes(project.status)"
            color="error"
            variant="outlined"
            size="large"
            prepend-icon="mdi-cancel"
            :loading="actionLoading"
            @click="handleCancel"
          >
            Отменить проект
          </v-btn>
        </v-card-actions>
      </v-card>

      <!-- Форма отклика -->
      <template v-if="canPropose">
        <ProposalForm
          :loading="proposalsStore.loading"
          :error="proposalsStore.error"
          @submit="handleProposalSubmit"
        />
      </template>

      <!-- Свой отклик на этот проект (после отправки или перезагрузки страницы) -->
      <template v-else-if="ownProposal">
        <div class="d-flex align-center mt-6 mb-3">
          <v-icon color="primary" size="28" class="mr-2">mdi-send</v-icon>
          <h2 class="text-h5 font-weight-bold">Ваш отклик</h2>
        </div>
        <MyProposalCard :proposal="ownProposal" />
      </template>

      <!-- Отклики для заказчика -->
      <template v-if="isCustomer && proposalsStore.proposals.length > 0">
        <div class="d-flex align-center mt-6 mb-4">
          <v-icon color="primary" size="28" class="mr-2">mdi-send</v-icon>
          <h2 class="text-h5 font-weight-bold">Отклики</h2>
          <v-chip size="small" color="primary" variant="tonal" class="ml-2">
            {{ proposalsStore.proposals.length }}
          </v-chip>
        </div>

        <v-alert
          v-if="project.status !== 'open'"
          type="info"
          variant="tonal"
          density="compact"
          class="mb-3"
        >
          Проект не открыт для приёма откликов — принять или отклонить отклик
          больше нельзя.
        </v-alert>

        <ProposalCard
          v-for="proposal in proposalsStore.proposals"
          :key="proposal.id"
          :proposal="proposal"
          :project-customer-id="project.customer_id"
          :project-status="project.status"
          :loading="actionLoading"
          @accept="handleAccept"
          @reject="handleReject"
        />
      </template>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useProposalsStore } from '@/stores/proposals'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import ProposalForm from '@/components/proposal/ProposalForm.vue'
import ProposalCard from '@/components/proposal/ProposalCard.vue'
import MyProposalCard from '@/components/proposal/MyProposalCard.vue'

const route = useRoute()
const projectsStore = useProjectsStore()
const proposalsStore = useProposalsStore()
const authStore = useAuthStore()
const { confirm } = useConfirm()

const actionLoading = ref(false)

const project = computed(() => projectsStore.currentProject)

const isCustomer = computed(
  () =>
    !!authStore.user?.id && project.value?.customer_id === authStore.user.id
)

// Отклик текущего фрилансера на этот проект: берём с бэкенда,
// чтобы после перезагрузки страницы форма отклика не показывалась снова
const ownProposal = computed(() =>
  authStore.isFreelancer ? proposalsStore.myProposalForProject : null
)

const canPropose = computed(
  () =>
    authStore.isFreelancer &&
    project.value?.status === 'open' &&
    project.value?.customer_id !== authStore.user?.id &&
    proposalsStore.myProposalChecked &&
    !ownProposal.value
)

const categoryMap = {
  development: { label: 'Разработка', color: 'blue', icon: 'mdi-code-tags' },
  design: { label: 'Дизайн', color: 'purple', icon: 'mdi-palette' },
  marketing: { label: 'Маркетинг', color: 'orange', icon: 'mdi-bullhorn' },
  writing: { label: 'Тексты', color: 'green', icon: 'mdi-pencil' },
  other: { label: 'Другое', color: 'grey', icon: 'mdi-dots-horizontal' },
}

const statusMap = {
  draft: { label: 'Черновик', color: 'grey', icon: 'mdi-file-outline' },
  open: { label: 'Открыт', color: 'green', icon: 'mdi-check-circle' },
  in_progress: { label: 'В работе', color: 'blue', icon: 'mdi-progress-clock' },
  completed: { label: 'Завершён', color: 'purple', icon: 'mdi-check-all' },
  cancelled: { label: 'Отменён', color: 'red', icon: 'mdi-cancel' },
}

const categoryLabel = computed(() => categoryMap[project.value?.category]?.label || '')
const categoryColor = computed(() => categoryMap[project.value?.category]?.color || 'grey')
const categoryIcon = computed(() => categoryMap[project.value?.category]?.icon || 'mdi-help')

const statusLabel = computed(() => statusMap[project.value?.status]?.label || '')
const statusColor = computed(() => statusMap[project.value?.status]?.color || 'grey')
const statusIcon = computed(() => statusMap[project.value?.status]?.icon || 'mdi-help')

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
    month: 'long',
    year: 'numeric',
  })
}

async function loadProject() {
  await projectsStore.fetchProjectById(route.params.id)

  if (!project.value) return

  if (project.value.customer_id === authStore.user?.id) {
    // Отклики грузим только для заказчика этого проекта
    proposalsStore.clearMyProposalForProject()
    await proposalsStore.fetchByProject(route.params.id)
  } else if (authStore.isFreelancer) {
    // Фрилансеру нужно знать, откликался ли он уже на этот проект
    await proposalsStore.fetchMyProposalForProject(route.params.id)
  } else {
    // Гость или другой пользователь: чужой отклик показывать нельзя
    proposalsStore.clearMyProposalForProject()
  }
}

async function handlePublish() {
  actionLoading.value = true
  await projectsStore.publishProject(route.params.id)
  await loadProject()
  actionLoading.value = false
}

async function handleCancel() {
  const agreed = await confirm({
    title: 'Отменить проект?',
    text: 'Проект закроется для новых откликов, ожидающие отклики будут отклонены. Действие необратимо.',
    confirmText: 'Отменить проект',
    color: 'error',
  })
  if (!agreed) return

  actionLoading.value = true
  await projectsStore.cancelProject(route.params.id)
  await loadProject()
  actionLoading.value = false
}

async function handleProposalSubmit(data) {
  const result = await proposalsStore.createProposal(route.params.id, data)

  if (result) {
    proposalsStore.setMyProposalForProject(result)
    return
  }

  // Отклик не создан: возможно, он уже существует (409) — перечитываем состояние
  await proposalsStore.fetchMyProposalForProject(route.params.id)
}

async function handleAccept(proposalId) {
  const agreed = await confirm({
    title: 'Принять отклик?',
    text: 'Будет создан контракт с этим фрилансером, остальные отклики отклонятся.',
    confirmText: 'Принять',
    color: 'success',
  })
  if (!agreed) return

  actionLoading.value = true
  await proposalsStore.acceptProposal(proposalId)
  await loadProject()
  actionLoading.value = false
}

async function handleReject(proposalId) {
  const agreed = await confirm({
    title: 'Отклонить отклик?',
    text: 'Фрилансер получит отказ, повторно откликнуться на этот проект он не сможет.',
    confirmText: 'Отклонить',
    color: 'error',
  })
  if (!agreed) return

  actionLoading.value = true
  await proposalsStore.rejectProposal(proposalId)
  await loadProject()
  actionLoading.value = false
}

onMounted(loadProject)
watch(() => route.params.id, loadProject)

// Профиль пользователя подгружается асинхронно (см. App.vue), поэтому роль
// может стать известна уже после первого рендера — тогда добираем свой отклик
watch(
  () => authStore.user?.id,
  (userId) => {
    if (!userId || !authStore.isFreelancer) return
    if (proposalsStore.myProposalChecked) return
    proposalsStore.fetchMyProposalForProject(route.params.id)
  }
)
</script>

<style scoped>
.project-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  overflow: hidden;
}

.project-header {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, transparent 100%);
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.info-card {
  padding: 20px;
  border-radius: 16px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.15);
  text-align: center;
  transition: all 0.2s ease;
  height: 100%;
}

.info-card:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.gap-2 {
  gap: 8px;
}

.gap-4 {
  gap: 16px;
}
</style>