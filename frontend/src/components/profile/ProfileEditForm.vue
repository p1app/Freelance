<template>
  <v-card class="glass form-card">
    <v-card-title class="d-flex align-center pa-6 pb-2">
      <v-icon color="primary" size="28" class="mr-3">mdi-account-edit</v-icon>
      <span class="text-h5 font-weight-bold">Редактировать профиль</span>
    </v-card-title>

    <v-card-subtitle class="px-6 pb-4" style="color: #9CA3AF">
      Обновите информацию о себе
    </v-card-subtitle>

    <v-card-text class="pa-6">
      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <!-- Email только для чтения: не редактируется через этот эндпоинт -->
        <v-text-field
          :model-value="user.email"
          label="Email"
          prepend-inner-icon="mdi-email"
          variant="outlined"
          rounded="lg"
          readonly
          disabled
          hint="Email изменить нельзя"
          persistent-hint
          class="mb-4"
        />

        <v-text-field
          v-model="form.fullname"
          label="Полное имя"
          placeholder="Иван Иванов"
          prepend-inner-icon="mdi-card-account-details"
          :rules="[rules.required, rules.fullname]"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
        />

        <v-textarea
          v-model="form.bio"
          label="О себе"
          placeholder="Расскажите о своём опыте, специализации..."
          prepend-inner-icon="mdi-text"
          rows="4"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
          counter="500"
          maxlength="500"
          auto-grow
        />

        <v-combobox
          v-model="form.skills"
          label="Навыки"
          placeholder="Введите навык и нажмите Enter"
          prepend-inner-icon="mdi-tag-multiple"
          multiple
          chips
          closable-chips
          variant="outlined"
          rounded="lg"
          :disabled="loading"
          hint="Например: Python, Vue.js, Дизайн"
          persistent-hint
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
            prepend-icon="mdi-check"
            class="btn-glow flex-grow-1"
          >
            Сохранить
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
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true,
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

const form = reactive({
  fullname: '',
  bio: '',
  skills: [],
})

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  fullname: (v) => (v && v.length >= 2) || 'Минимум 2 символа',
}

watch(
  () => props.user,
  (val) => {
    if (val) {
      form.fullname = val.fullname || ''
      form.bio = val.bio || ''
      form.skills = val.skills || []
    }
  },
  { immediate: true }
)

async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  emit('submit', {
    fullname: form.fullname,
    bio: form.bio || null,
    skills: form.skills,
  })
}
</script>

<style scoped>
.form-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  animation: fadeIn 0.3s ease-out;
}

.gap-3 {
  gap: 12px;
}
</style>