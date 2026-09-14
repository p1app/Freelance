<template>
  <v-card class="glass form-card mb-3">
    <v-card-title class="d-flex align-center pa-5 pb-2">
      <v-icon color="primary" size="24" class="mr-2">
        {{ isEdit ? 'mdi-pencil' : 'mdi-flag-plus' }}
      </v-icon>
      <span class="text-h6 font-weight-bold">
        {{ isEdit ? 'Редактировать этап' : 'Новый этап' }}
      </span>
    </v-card-title>

    <v-card-text class="pa-5">
      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <v-text-field
          v-model="form.title"
          label="Название этапа"
          placeholder="Например: Верстка главной страницы"
          prepend-inner-icon="mdi-format-title"
          :rules="[rules.required, rules.titleLength]"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
        />

        <v-textarea
          v-model="form.description"
          label="Описание"
          placeholder="Что нужно сделать на этом этапе..."
          prepend-inner-icon="mdi-text"
          rows="3"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
          auto-grow
        />

        <v-text-field
          v-model="form.due_date"
          label="Дедлайн этапа"
          prepend-inner-icon="mdi-calendar"
          type="date"
          :rules="[rules.required, rules.futureDate]"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
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

        <div class="d-flex gap-2 mt-4">
          <v-btn
            type="submit"
            color="primary"
            :loading="loading"
            prepend-icon="mdi-check"
            class="btn-glow"
          >
            {{ isEdit ? 'Сохранить' : 'Создать' }}
          </v-btn>
          <v-btn
            variant="outlined"
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
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  milestone: {
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
  title: '',
  description: '',
  due_date: '',
})

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  titleLength: (v) => (v && v.length >= 5) || 'Минимум 5 символов',
  futureDate: (v) => {
    if (!v) return 'Укажите дату'
    return new Date(v) > new Date() || 'Дата должна быть в будущем'
  },
}

watch(
  () => props.milestone,
  (val) => {
    if (val) {
      isEdit.value = true
      form.title = val.title
      form.description = val.description || ''
      form.due_date = val.due_date?.split('T')[0] || ''
    } else {
      isEdit.value = false
      form.title = ''
      form.description = ''
      form.due_date = ''
    }
  },
  { immediate: true }
)

async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  emit('submit', {
    title: form.title,
    description: form.description || null,
    due_date: new Date(form.due_date).toISOString(),
  })
}
</script>

<style scoped>
.form-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  animation: fadeIn 0.3s ease-out;
}

.gap-2 {
  gap: 8px;
}
</style>