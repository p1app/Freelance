<template>
  <div class="auth-page">
    <div class="bg-circle bg-circle-1" />
    <div class="bg-circle bg-circle-2" />
    <div class="bg-circle bg-circle-3" />

    <v-container class="fill-height position-relative" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="10" md="7" lg="6" xl="5">
          <div class="text-center mb-6 fade-in">
            <v-icon color="primary" size="56" class="mb-2">mdi-account-plus</v-icon>
            <h1 class="text-h4 font-weight-bold gradient-text">
              Создать аккаунт
            </h1>
            <p class="text-body-2 mt-2" style="color: #9CA3AF">
              Присоединяйтесь к Freelance LITE
            </p>
          </div>

          <v-card class="glass pa-2 auth-card">
            <v-card-text class="pa-6">
              <v-form ref="formRef" @submit.prevent="handleRegister">
                <v-row dense>
                  <v-col cols="12" sm="6">
                    <v-text-field
                      v-model="form.username"
                      label="Username"
                      prepend-inner-icon="mdi-account"
                      :rules="[rules.required, rules.username]"
                      :disabled="authStore.loading"
                      variant="outlined"
                      rounded="lg"
                    />
                  </v-col>

                  <v-col cols="12" sm="6">
                    <v-text-field
                      v-model="form.fullname"
                      label="Полное имя"
                      prepend-inner-icon="mdi-card-account-details"
                      :rules="[rules.required, rules.fullname]"
                      :disabled="authStore.loading"
                      variant="outlined"
                      rounded="lg"
                    />
                  </v-col>
                </v-row>

                <v-text-field
                  v-model="form.email"
                  label="Email"
                  prepend-inner-icon="mdi-email"
                  type="email"
                  :rules="[rules.required, rules.email]"
                  :disabled="authStore.loading"
                  variant="outlined"
                  rounded="lg"
                />

                <v-text-field
                  v-model="form.password"
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

                <!-- Выбор роли -->
                <div class="mb-2 mt-2">
                  <div class="text-body-2 mb-2" style="color: #9CA3AF">
                    Я регистрируюсь как:
                  </div>
                  <v-row dense>
                    <v-col cols="6">
                      <v-card
                        :class="{ 'role-active': form.role === 'client' }"
                        class="role-card text-center pa-3"
                        @click="form.role = 'client'"
                      >
                        <v-icon
                          size="32"
                          :color="form.role === 'client' ? 'primary' : 'grey'"
                        >
                          mdi-account-tie
                        </v-icon>
                        <div class="mt-1 font-weight-bold">Заказчик</div>
                        <div class="text-caption" style="color: #9CA3AF">
                          Ищу исполнителей
                        </div>
                      </v-card>
                    </v-col>
                    <v-col cols="6">
                      <v-card
                        :class="{ 'role-active': form.role === 'freelancer' }"
                        class="role-card text-center pa-3"
                        @click="form.role = 'freelancer'"
                      >
                        <v-icon
                          size="32"
                          :color="form.role === 'freelancer' ? 'primary' : 'grey'"
                        >
                          mdi-briefcase-account
                        </v-icon>
                        <div class="mt-1 font-weight-bold">Фрилансер</div>
                        <div class="text-caption" style="color: #9CA3AF">
                          Ищу проекты
                        </div>
                      </v-card>
                    </v-col>
                  </v-row>
                </div>

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
                  Зарегистрироваться
                </v-btn>
              </v-form>

              <v-divider class="my-6" />

              <div class="text-center">
                <span class="text-body-2" style="color: #9CA3AF">
                  Уже есть аккаунт?
                </span>
                <v-btn
                  variant="text"
                  color="primary"
                  size="small"
                  :to="{ name: 'Login' }"
                >
                  Войти
                </v-btn>
              </div>
            </v-card-text>
          </v-card>

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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const showPassword = ref(false)

const form = reactive({
  username: '',
  email: '',
  fullname: '',
  password: '',
  role: 'client',
})

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  username: (v) => (v && v.length >= 3) || 'Минимум 3 символа',
  fullname: (v) => (v && v.length >= 2) || 'Минимум 2 символа',
  minLength: (v) => (v && v.length >= 6) || 'Минимум 6 символов',
  email: (v) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(v) || 'Некорректный email'
  },
}

async function handleRegister() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  const success = await authStore.register({
    username: form.username,
    email: form.email,
    fullname: form.fullname,
    password: form.password,
    role: form.role,
  })

  if (success) {
    router.push('/')
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

.role-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid rgba(59, 130, 246, 0.1) !important;
  border-radius: 12px;
}

.role-card:hover {
  border-color: rgba(59, 130, 246, 0.4) !important;
  transform: translateY(-2px);
}

.role-active {
  border-color: #3B82F6 !important;
  background: rgba(59, 130, 246, 0.1) !important;
}
</style>