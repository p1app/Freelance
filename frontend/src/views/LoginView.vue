<template>
  <div class="auth-page">
    <!-- Декоративные круги на фоне -->
    <div class="bg-circle bg-circle-1" />
    <div class="bg-circle bg-circle-2" />
    <div class="bg-circle bg-circle-3" />

    <v-container class="fill-height position-relative" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="10" md="6" lg="5" xl="4">
          <!-- Логотип -->
          <div class="text-center mb-6 fade-in">
            <v-icon color="primary" size="56" class="mb-2">mdi-briefcase</v-icon>
            <h1 class="text-h4 font-weight-bold gradient-text">
              Freelance LITE
            </h1>
            <p class="text-body-2 mt-2" style="color: #9CA3AF">
              Платформа для фриланс-проектов
            </p>
          </div>

          <!-- Карточка -->
          <v-card class="glass pa-2 auth-card">
            <v-card-text class="pa-6">
              <h2 class="text-h5 font-weight-bold mb-1">Добро пожаловать</h2>
              <p class="text-body-2 mb-6" style="color: #9CA3AF">
                Войдите в свой аккаунт
              </p>

              <v-form ref="formRef" @submit.prevent="handleLogin">
                <v-text-field
                  v-model="username"
                  label="Username"
                  prepend-inner-icon="mdi-account"
                  :rules="[rules.required, rules.username]"
                  :disabled="authStore.loading"
                  variant="outlined"
                  rounded="lg"
                />

                <v-text-field
                  v-model="password"
                  label="Пароль"
                  prepend-inner-icon="mdi-lock"
                  :type="showPassword ? 'text' : 'password'"
                  :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  :rules="[rules.required, rules.minLength]"
                  :disabled="authStore.loading"
                  variant="outlined"
                  rounded="lg"
                  @click:append-inner="showPassword = !showPassword"
                />

                <v-alert
                  v-if="authStore.error"
                  type="error"
                  variant="tonal"
                  density="compact"
                  class="mt-3"
                  closable
                  @click:close="authStore.clearError()"
                >
                  {{ authStore.error }}
                </v-alert>

                <v-btn
                  type="submit"
                  color="primary"
                  size="large"
                  block
                  class="mt-6 btn-glow"
                  :loading="authStore.loading"
                  :disabled="authStore.loading"
                >
                  Войти
                </v-btn>
              </v-form>

              <v-divider class="my-6" />

              <div class="text-center">
                <span class="text-body-2" style="color: #9CA3AF">
                  Нет аккаунта?
                </span>
                <v-btn
                  variant="text"
                  color="primary"
                  size="small"
                  :to="{ name: 'Register' }"
                >
                  Зарегистрироваться
                </v-btn>
              </div>
            </v-card-text>
          </v-card>

          <!-- Футер -->
          <div class="text-center mt-6 fade-in">
            <p class="text-caption" style="color: #6B7280">
              © 2025 Freelance LITE. Все права защищены.
            </p>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref(null)
const username = ref('')
const password = ref('')
const showPassword = ref(false)

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  username: (v) => (v && v.length >= 3) || 'Минимум 3 символа',
  minLength: (v) => (v && v.length >= 6) || 'Минимум 6 символов',
}

async function handleLogin() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  const success = await authStore.login(username.value, password.value)

  if (success) {
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: radial-gradient(ellipse at top, #0F172A 0%, #0A0E1A 70%);
  position: relative;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  pointer-events: none;
}

.bg-circle-1 {
  width: 400px;
  height: 400px;
  background: #3B82F6;
  top: -100px;
  left: -100px;
  animation: float 8s ease-in-out infinite;
}

.bg-circle-2 {
  width: 300px;
  height: 300px;
  background: #8B5CF6;
  bottom: -100px;
  right: -100px;
  animation: float 10s ease-in-out infinite reverse;
}

.bg-circle-3 {
  width: 200px;
  height: 200px;
  background: #1E40AF;
  top: 50%;
  right: 10%;
  animation: float 12s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(30px, -30px) scale(1.1);
  }
}

.auth-card {
  animation: fadeIn 0.5s ease-out;
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
}
</style>