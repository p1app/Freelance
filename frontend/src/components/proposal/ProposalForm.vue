<template>
  <v-card class="glass form-card">
    <v-card-title class="d-flex align-center pa-6 pb-2">
      <v-icon color="primary" size="28" class="mr-3">mdi-send</v-icon>
      <span class="text-h5 font-weight-bold">Оставить отклик</span>
    </v-card-title>

    <v-card-subtitle class="px-6 pb-4" style="color: #9CA3AF">
      Расскажите заказчику, почему вы подходите для этой задачи
    </v-card-subtitle>

    <v-card-text class="pa-6">
      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <v-textarea
          v-model="form.cover_letter"
          label="Сопроводительное письмо"
          placeholder="Опишите ваш опыт, подход к работе, почему вы подходите..."
          prepend-inner-icon="mdi-text"
          :rules="[rules.required, rules.minLength]"
          rows="5"
          variant="outlined"
          rounded="lg"
          :disabled="loading"
          counter="2000"
          maxlength="2000"
          auto-grow
        />

        <v-row dense>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model.number="form.bid_amount"
              label="Ваша цена"
              placeholder="50000"
              prepend-inner-icon="mdi-currency-usd"
              suffix="₽"
              type="number"
              :rules="[rules.required, rules.positive]"
              variant="outlined"
              rounded="lg"
              :disabled="loading"
            />
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model.number="form.estimated_days"
              label="Срок выполнения"
              placeholder="7"
              prepend-inner-icon="mdi-clock-outline"
              suffix="дней"
              type="number"
              :rules="[rules.required, rules.positive]"
              variant="outlined"
              rounded="lg"
              :disabled="loading"
            />
          </v-col>
        </v-row>

        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          density="compact"
          class="mt-3"
        >
          {{ error }}
        </v-alert>

        <v-btn
          type="submit"
          color="primary"
          size="large"
          block
          class="mt-6 btn-glow"
          :loading="loading"
          prepend-icon="mdi-send"
        >
          Отправить отклик
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, reactive } from 'vue'

defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['submit'])

const formRef = ref(null)

const form = reactive({
  cover_letter: '',
  bid_amount: null,
  estimated_days: null,
})

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  minLength: (v) => (v && v.length >= 10) || 'Минимум 10 символов',
  positive: (v) => (v && v > 0) || 'Значение должно быть больше 0',
}

async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  emit('submit', { ...form })
}
</script>

<style scoped>
.form-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
  animation: fadeIn 0.3s ease-out;
}
</style>