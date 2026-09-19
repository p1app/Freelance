<template>
  <div>
    <div class="d-flex align-center mb-4">
      <v-icon color="primary" size="28" class="mr-2">mdi-flag-checkered</v-icon>
      <h2 class="text-h5 font-weight-bold">Этапы</h2>
      <v-chip
        v-if="milestonesStore.milestones.length > 0"
        size="small"
        color="primary"
        variant="tonal"
        class="ml-2"
      >
        {{ milestonesStore.milestones.length }}
      </v-chip>

      <v-spacer />

      <v-btn
        v-if="isFreelancer && contractStatus === 'active' && !showForm"
        color="primary"
        prepend-icon="mdi-plus"
        variant="flat"
        class="btn-glow"
        @click="showForm = true"
      >
        Добавить этап
      </v-btn>
    </div>

    <!-- Форма -->
    <MilestoneForm
      v-if="showForm && contractStatus === 'active'"
      :milestone="editingMilestone"
      :loading="milestonesStore.loading"
      :error="milestonesStore.error"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />

    <!-- Ошибка -->
    <v-alert
      v-if="milestonesStore.error && !showForm"
      type="error"
      variant="tonal"
      class="mb-3"
      closable
      @click:close="milestonesStore.clearError()"
    >
      {{ milestonesStore.error }}
    </v-alert>

    <!-- Загрузка (или ещё не загружены этапы этого контракта) -->
    <v-skeleton-loader v-if="!isLoaded" type="card" />

    <!-- Пусто -->
    <v-empty-state
      v-else-if="milestonesStore.milestones.length === 0"
      icon="mdi-flag-outline"
      title="Этапов нет"
      :text="
        contractStatus !== 'active'
          ? 'Контракт завершён'
          : isFreelancer
          ? 'Добавьте первый этап'
          : 'Фрилансер ещё не добавил этапы'
      "
    />

    <!-- Timeline -->
    <div v-else class="milestones-timeline">
      <MilestoneItem
        v-for="milestone in milestonesStore.milestones"
        :key="milestone.id"
        :milestone="milestone"
        :contract-status="contractStatus"
        :is-freelancer="isFreelancer"
        :is-customer="isCustomer"
        :loading="milestonesStore.loading"
        @complete="handleComplete"
        @approve="handleApprove"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMilestonesStore } from '@/stores/milestones'
import { useConfirm } from '@/composables/useConfirm'
import MilestoneItem from './MilestoneItem.vue'
import MilestoneForm from './MilestoneForm.vue'

const props = defineProps({
  contractId: { type: Number, required: true },
  contractStatus: { type: String, default: 'active' },
  isFreelancer: { type: Boolean, default: false },
  isCustomer: { type: Boolean, default: false },
})

const milestonesStore = useMilestonesStore()
const { confirm } = useConfirm()

const showForm = ref(false)
const editingMilestone = ref(null)

// Список этапов именно этого контракта уже загружен
const isLoaded = computed(() => milestonesStore.isLoaded(props.contractId))

async function load({ force = false } = {}) {
  await milestonesStore.fetchByContract(props.contractId, { force })
}

async function handleSubmit(data) {
  if (editingMilestone.value) {
    await milestonesStore.updateMilestone(editingMilestone.value.id, data)
  } else {
    await milestonesStore.createMilestone(props.contractId, data)
  }
  showForm.value = false
  editingMilestone.value = null
  await load({ force: true })
}

function handleCancel() {
  showForm.value = false
  editingMilestone.value = null
}

function handleEdit(milestone) {
  editingMilestone.value = milestone
  showForm.value = true
}

async function handleDelete(milestoneId) {
  const agreed = await confirm({
    title: 'Удалить этап?',
    text: 'Этап исчезнет из контракта, восстановить его будет нельзя.',
    confirmText: 'Удалить',
    color: 'error',
  })
  if (!agreed) return

  await milestonesStore.deleteMilestone(milestoneId)
  await load({ force: true })
}

async function handleComplete(milestoneId) {
  await milestonesStore.completeMilestone(milestoneId)
  await load({ force: true })
}

async function handleApprove(milestoneId) {
  await milestonesStore.approveMilestone(milestoneId)
  await load({ force: true })
}

onMounted(() => load({ force: true }))
</script>