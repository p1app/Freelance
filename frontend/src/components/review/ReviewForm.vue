<template>
  <v-card class="glass form-card">
    <v-card-title class="d-flex align-center pa-6 pb-2">
      <v-icon color="primary" size="28" class="mr-3">
        {{ isEdit ? 'mdi-pencil' : 'mdi-star-plus' }}
      </v-icon>
      <span class="text-h5 font-weight-bold">
        {{ isEdit ? 'Редактировать отзыв' : 'Оставить отзыв' }}
      </span>
    </v-card-title>

    <v-card-subtitle class="px-6 pb-4" style="color: #9CA3AF">
      Поделитесь впечатлениями о работе
    </v-card-subtitle>

    <v-card-text class="pa-6">
      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <!-- Звёзды -->
        <div class="mb-4 text-center">
          <div class="text-body-2 mb-3" style="color: #9CA3AF">
            Ваша оценка
          </div>
          <div class="d-flex justify-center">
            <v-icon
              v-for="i in 5"
              :key="i"
              :color="i <= form.rating ? 'amber' : 'grey-lighten-1'"
              size="48"
              class="mx-1 star-icon"
              @click="form.rating = i"
            >
              {{ i <= form.rating ? 'mdi-star' : 'mdi-star-outline' }}
            </v-icon>
          </div>
          <div class="text-h6 font-weight-bold mt-2">
            {{ ratingText }}
          </div>
        </div>

        <v-textarea
          v-model="form.comment"
          label="Комментарий"
          placeholder="Расскажите о сотрудничестве..."
          prepend-inner-icon="mdi-text"
          rows="4"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
          counter="250"
          maxlength="250"
          auto-grow
        />

        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          density="compact"
          class="mt-3"
        >
          {{ error }}
        </v-alert>

        <div class="d-flex gap-3 mt-6">
          <v-btn
            type="submit"
            color="primary"
            size="large"
            :loading="loading"
            prepend-icon="mdi-send"
            class="btn-glow flex-grow-1"
          >
            {{ isEdit ? 'Сохранить' : 'Отправить' }}
          </v-btn>
          <v-btn
            variant="outlined"
            size="large"
            :disabled="loading"
            prepend-icon="mdi-close"
            @click="$emit('cancel')"
          >
            Отмена
          </v-btn>
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'

const props = defineProps({
  review: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref(null)
const isEdit = ref(false)

const form = reactive({
  rating: 5,
  comment: '',
})

const ratingText = computed(() => {
  const texts = {
    1: 'Ужасно',
    2: 'Плохо',
    3: 'Нормально',
    4: 'Хорошо',
    5: 'Отлично',
  }
  return texts[form.rating] || ''
})

watch(
  () => props.review,
  (val) => {
    if (val) {
      isEdit.value = true
      form.rating = val.rating
      form.comment = val.comment || ''
    } else {
      isEdit.value = false
      form.rating = 5
      form.comment = ''
    }
  },
  { immediate: true }
)

async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  emit('submit', {
    rating: form.rating,
    comment: form.comment || null,
  })
}
</script>

<style scoped>
.form-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  animation: fadeIn 0.3s ease-out;
}

.star-icon {
  cursor: pointer;
  transition: all 0.2s ease;
}

.star-icon:hover {
  transform: scale(1.2) rotate(-5deg);
}

.gap-3 {
  gap: 12px;
}
</style>