<template>
  <v-container>
    <v-skeleton-loader v-if="contractsStore.loading && !contract" type="article" />

    <v-empty-state
      v-else-if="!contract"
      icon="mdi-file-document-outline"
      title="Контракт не найден"
    >
      <template #actions>
        <v-btn color="primary" to="/contracts">К контрактам</v-btn>
      </template>
    </v-empty-state>

    <template v-else>
      <v-btn
        variant="text"
        prepend-icon="mdi-arrow-left"
        class="mb-3"
        to="/contracts"
      >
        Назад к контрактам
      </v-btn>

      <!-- Ошибка операции -->
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

      <!-- Основная карточка -->
      <v-card class="mb-4">
        <v-card-item>
          <v-card-title class="text-h5">
            {{ contract.project_title || `Контракт #${contract.id}` }}
          </v-card-title>
          <v-card-subtitle>
            <v-chip :color="statusColor" size="small" variant="tonal">
              {{ statusLabel }}
            </v-chip>
          </v-card-subtitle>
        </v-card-item>

        <v-card-text>
          <v-row>
            <v-col cols="12" sm="3">
              <div class="text-caption text-medium-emphasis">Сумма</div>
              <div class="text-h6">{{ formatBudget(contract.final_price) }}</div>
            </v-col>
            <v-col cols="12" sm="3">
              <div class="text-caption text-medium-emphasis">Начало</div>
              <div class="text-h6">{{ formatDate(contract.start_date) }}</div>
            </v-col>
            <v-col cols="12" sm="3">
              <div class="text-caption text-medium-emphasis">Окончание</div>
              <div class="text-h6">{{ formatDate(contract.end_date) }}</div>
            </v-col>
            <v-col cols="12" sm="3">
              <div class="text-caption text-medium-emphasis">Участники</div>
              <div class="text-body-2">
                <div>
                  Заказчик:
                  <router-link
                    :to="{ name: 'UserPublic', params: { id: contract.customer_id } }"
                    class="text-primary text-decoration-none"
                  >
                    {{ contract.customer_name }}
                  </router-link>
                </div>
                <div>
                  Фрилансер:
                  <router-link
                    :to="{ name: 'UserPublic', params: { id: contract.freelancer_id } }"
                    class="text-primary text-decoration-none"
                  >
                    {{ contract.freelancer_name }}
                  </router-link>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>

        <!-- Действия -->
        <v-card-actions v-if="contract.status === 'active'" class="flex-wrap gap-2">
          <v-btn
            v-if="isCustomer"
            color="success"
            prepend-icon="mdi-check-circle"
            :loading="contractsStore.loading"
            :disabled="!allMilestonesApproved"
            @click="handleComplete"
          >
            Завершить контракт
          </v-btn>

          <v-btn
            color="error"
            variant="tonal"
            prepend-icon="mdi-cancel"
            :loading="contractsStore.loading"
            @click="handleCancel"
          >
            Отменить
          </v-btn>

          <!-- Почему нельзя завершить -->
          <div
            v-if="isCustomer && !allMilestonesApproved"
            class="d-flex align-center text-caption w-100 mt-2"
            style="color: #fbbf24"
          >
            <v-icon size="16" class="mr-1">mdi-alert-outline</v-icon>
            <span v-if="!milestonesReady && milestonesStore.loading">
              Проверяем этапы контракта…
            </span>
            <span v-else-if="!milestonesReady">
              Не удалось загрузить этапы контракта — обновите страницу.
            </span>
            <span v-else-if="pendingMilestones > 0">
              Завершить контракт нельзя: не все этапы утверждены (осталось
              {{ pendingMilestones }} из
              {{ milestonesStore.milestones.length }}). Утверждает этапы заказчик.
            </span>
            <span v-else>Завершить контракт пока нельзя.</span>
          </div>
        </v-card-actions>
      </v-card>

      <!-- Этапы -->
      <h2 class="text-h5 mb-3">Этапы</h2>
      <MilestoneList
        :contract-id="contract.id"
        :contract-status="contract.status"   
        :is-freelancer="isFreelancer"
        :is-customer="isCustomer"
      />

      <!-- Чат -->
      <h2 class="text-h5 mb-3 mt-6">Чат</h2>
      <ChatBox :contract-id="contract.id" />

      <!-- Форма отзыва -->
      <template v-if="canLeaveReview">
        <h2 class="text-h5 mb-3 mt-6">Оставить отзыв</h2>
        <ReviewForm
          :loading="reviewsStore.loading"
          :error="reviewsStore.error"
          @submit="handleReviewSubmit"
        />
      </template>

      <!-- Список отзывов -->
      <template v-if="contract.status === 'completed'">
        <h2 class="text-h5 mb-3 mt-6">Отзывы</h2>
        <ReviewList />
      </template>
    </template>

    <!-- Результат операции -->
    <v-snackbar v-model="snackbar" color="success" :timeout="2500" location="bottom">
      {{ snackbarText }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useContractsStore } from '@/stores/contracts'
import { useAuthStore } from '@/stores/auth'
import { useReviewsStore } from '@/stores/reviews'
import { useMilestonesStore } from '@/stores/milestones'
import { useConfirm } from '@/composables/useConfirm'
import MilestoneList from '@/components/milestone/MilestoneList.vue'
import ChatBox from '@/components/chat/ChatBox.vue'
import ReviewForm from '@/components/review/ReviewForm.vue'
import ReviewList from '@/components/review/ReviewList.vue'

const route = useRoute()
const contractsStore = useContractsStore()
const authStore = useAuthStore()
const reviewsStore = useReviewsStore()
const milestonesStore = useMilestonesStore()
const { confirm } = useConfirm()

const snackbar = ref(false)
const snackbarText = ref('')

const contract = computed(() => contractsStore.currentContract)

const isCustomer = computed(
  () => contract.value?.customer_id === authStore.user?.id
)
const isFreelancer = computed(
  () => contract.value?.freelancer_id === authStore.user?.id
)

// Этапы этого контракта уже загружены (их грузит MilestoneList, стор общий)
const milestonesReady = computed(() =>
  milestonesStore.isLoaded(contract.value?.id)
)
const pendingMilestones = computed(
  () => milestonesStore.milestones.filter((m) => m.status !== 'approved').length
)
// Как и бэкенд (check_all_approved): контракт без этапов завершить можно
const allMilestonesApproved = computed(
  () => milestonesReady.value && pendingMilestones.value === 0
)

function showSuccess(text) {
  snackbarText.value = text
  snackbar.value = true
}

const canLeaveReview = computed(() => {
  if (!contract.value) return false
  if (contract.value.status !== 'completed') return false
  if (!isCustomer.value && !isFreelancer.value) return false

  const alreadyReviewed = reviewsStore.reviews.some(
    (r) => r.from_user_id === authStore.user?.id
  )
  return !alreadyReviewed
})

const statusMap = {
  active: { label: 'Активен', color: 'green' },
  completed: { label: 'Завершён', color: 'purple' },
  cancelled: { label: 'Отменён', color: 'red' },
  disputed: { label: 'Спор', color: 'orange' },
}

const statusLabel = computed(
  () => statusMap[contract.value?.status]?.label || ''
)
const statusColor = computed(
  () => statusMap[contract.value?.status]?.color || 'grey'
)

function formatBudget(value) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(value)
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
}

async function handleComplete() {
  const agreed = await confirm({
    title: 'Завершить контракт?',
    text: 'Все этапы утверждены. После завершения участники смогут оставить отзывы, чат закроется.',
    confirmText: 'Завершить',
    color: 'success',
  })
  if (!agreed) return

  const result = await contractsStore.completeContract(route.params.id)
  if (!result) return

  await loadContract()
  showSuccess('Контракт завершён')
}

async function handleCancel() {
  const agreed = await confirm({
    title: 'Отменить контракт?',
    text: 'Действие необратимо: контракт закроется, чат станет недоступен.',
    confirmText: 'Отменить контракт',
    color: 'error',
  })
  if (!agreed) return

  const result = await contractsStore.cancelContract(route.params.id)
  if (!result) return

  await loadContract()
  showSuccess('Контракт отменён')
}

async function handleReviewSubmit(data) {
  const result = await reviewsStore.createReview(contract.value.id, data)
  if (result) {
    await reviewsStore.fetchByContract(contract.value.id)
  }
}

async function loadContract() {
  await contractsStore.fetchContractById(route.params.id)

  if (contractsStore.currentContract?.status === 'completed') {
    await reviewsStore.fetchByContract(route.params.id)
  }
}

onMounted(loadContract)
watch(() => route.params.id, loadContract)
</script>