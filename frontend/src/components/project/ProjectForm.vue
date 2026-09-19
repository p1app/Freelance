<template>
  <v-card class="glass form-card">
    <v-card-title class="d-flex align-center pa-6 pb-2">
      <v-icon color="primary" size="28" class="mr-3">
        {{ isEdit ? 'mdi-pencil' : 'mdi-plus-circle' }}
      </v-icon>
      <span class="text-h5 font-weight-bold">
        {{ isEdit ? 'Редактировать проект' : 'Новый проект' }}
      </span>
    </v-card-title>

    <v-card-subtitle class="px-6 pb-4" style="color: #9CA3AF">
      {{ isEdit ? 'Измените данные проекта' : 'Заполните информацию о проекте' }}
    </v-card-subtitle>

    <v-card-text class="pa-6">
      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <!-- Название -->
        <v-text-field
          v-model="form.title"
          label="Название проекта"
          placeholder="Например: Разработка интернет-магазина"
          prepend-inner-icon="mdi-format-title"
          :rules="[rules.required, rules.titleLength]"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
          counter="255"
        />

        <!-- Описание -->
        <v-textarea
          v-model="form.description"
          label="Описание"
          placeholder="Опишите задачу, требования, ожидания..."
          prepend-inner-icon="mdi-text"
          :rules="[rules.required, rules.descriptionLength]"
          rows="5"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
          counter="5000"
          maxlength="5000"
          auto-grow
        />

        <v-row dense>
          <!-- Бюджет -->
          <v-col cols="12" sm="6">
            <v-text-field
              v-model.number="form.budget"
              label="Бюджет"
              placeholder="50000"
              prepend-inner-icon="mdi-cash"
              suffix="₽"
              type="number"
              :rules="[rules.required, rules.positive]"
              variant="outlined"
              rounded="lg"
              :disabled="loading"
            />
          </v-col>

          <!-- Дедлайн -->
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.deadline"
              label="Дедлайн"
              prepend-inner-icon="mdi-calendar"
              type="date"
              :rules="[rules.required, rules.futureDate]"
              variant="outlined"
              rounded="lg"
              :disabled="loading"
            />
          </v-col>
        </v-row>

        <!-- Категория -->
        <div class="mb-3">
          <div class="text-body-2 mb-2" style="color: #9CA3AF">
            Категория проекта
          </div>
          <v-row dense>
            <v-col
              v-for="cat in categories"
              :key="cat.value"
              cols="6"
              sm="4"
              md="2"
            >
              <v-card
                :class="{ 'category-active': form.category === cat.value }"
                class="category-card text-center pa-3"
                @click="form.category = cat.value"
              >
                <v-icon
                  size="28"
                  :color="form.category === cat.value ? 'primary' : 'grey'"
                >
                  {{ cat.icon }}
                </v-icon>
                <div class="text-caption mt-1 font-weight-medium">
                  {{ cat.title }}
                </div>
              </v-card>
            </v-col>
          </v-row>
          <v-alert
            v-if="categoryError"
            type="error"
            variant="tonal"
            density="compact"
            class="mt-2"
          >
            Выберите категорию
          </v-alert>
        </div>

        <!-- Ошибка -->
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          density="compact"
          class="mt-3"
          closable
        >
          {{ error }}
        </v-alert>

        <!-- Кнопки -->
        <div class="d-flex gap-3 mt-6">
          <v-btn
            type="submit"
            color="primary"
            size="large"
            :loading="loading"
            prepend-icon="mdi-check"
            class="btn-glow flex-grow-1"
          >
            {{ isEdit ? 'Сохранить' : 'Создать проект' }}
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
  project: {
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
const categoryError = ref(false)

const form = reactive({
  title: '',
  description: '',
  budget: null,
  deadline: '',
  category: null,
})

const categories = [
  { value: 'development', title: 'Разработка', icon: 'mdi-code-tags' },
  { value: 'design', title: 'Дизайн', icon: 'mdi-palette' },
  { value: 'marketing', title: 'Маркетинг', icon: 'mdi-bullhorn' },
  { value: 'writing', title: 'Тексты', icon: 'mdi-pencil' },
  { value: 'other', title: 'Другое', icon: 'mdi-dots-horizontal' },
]

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  titleLength: (v) => (v && v.length >= 5) || 'Минимум 5 символов',
  descriptionLength: (v) => (v && v.length >= 20) || 'Минимум 20 символов',
  positive: (v) => (v && v > 0) || 'Значение должно быть больше 0',
  futureDate: (v) => {
    if (!v) return 'Укажите дату'
    return new Date(v) > new Date() || 'Дата должна быть в будущем'
  },
}

watch(
  () => props.project,
  (val) => {
    if (val) {
      isEdit.value = true
      form.title = val.title
      form.description = val.description
      form.budget = val.budget
      form.deadline = val.deadline?.split('T')[0] || ''
      form.category = val.category
    } else {
      isEdit.value = false
      form.title = ''
      form.description = ''
      form.budget = null
      form.deadline = ''
      form.category = null
    }
  },
  { immediate: true }
)

async function handleSubmit() {
  const { valid } = await formRef.value.validate()

  categoryError.value = !form.category

  if (!valid || categoryError.value) return

  emit('submit', {
    title: form.title,
    description: form.description,
    budget: form.budget,
    deadline: new Date(form.deadline).toISOString(),
    category: form.category,
  })
}
</script>

<style scoped>
.form-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  animation: fadeIn 0.3s ease-out;
}

.category-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid rgba(59, 130, 246, 0.1) !important;
  border-radius: 12px;
  height: 100%;
}

.category-card:hover {
  border-color: rgba(59, 130, 246, 0.4) !important;
  transform: translateY(-2px);
}

.category-active {
  border-color: #3B82F6 !important;
  background: rgba(59, 130, 246, 0.1) !important;
}

.gap-3 {
  gap: 12px;
}
</style>