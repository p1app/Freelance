<template>
  <v-container>
    <v-skeleton-loader v-if="!authStore.user" type="article" />

    <template v-else>
      <!-- Редактирование профиля -->
      <template v-if="isEditingProfile">
        <ProfileEditForm
          :user="authStore.user"
          :loading="userStore.loading"
          :error="userStore.error"
          @submit="handleUpdateProfile"
          @cancel="isEditingProfile = false"
        />
      </template>

      <!-- Просмотр -->
      <template v-else>
        <v-row>
          <!-- Левая колонка -->
          <v-col cols="12" md="4">
            <!-- Карточка профиля -->
            <v-card class="glass profile-card fade-in">
              <v-card-text class="text-center pa-6">
                <!-- Аватар с градиентной обводкой -->
                <div class="avatar-wrapper mb-4">
                  <v-avatar :image="avatarUrl" size="120" class="profile-avatar" />
                  <div class="avatar-ring" />
                </div>

                <h2 class="text-h5 font-weight-bold">
                  {{ authStore.user.fullname || authStore.user.username }}
                </h2>
                <p class="text-body-2 mt-1" style="color: #9CA3AF">
                  @{{ authStore.user.username }}
                </p>

                <v-chip
                  :color="roleColor"
                  variant="flat"
                  size="small"
                  class="mt-3"
                  :prepend-icon="roleIcon"
                >
                  {{ roleLabel }}
                </v-chip>

                <v-divider class="my-5" style="border-color: rgba(59, 130, 246, 0.15)" />

                <v-btn
                  color="primary"
                  variant="flat"
                  block
                  prepend-icon="mdi-pencil"
                  class="btn-glow mb-2"
                  @click="isEditingProfile = true"
                >
                  Редактировать
                </v-btn>

                <v-btn
                  color="error"
                  variant="outlined"
                  block
                  prepend-icon="mdi-delete"
                  @click="showDeleteDialog = true"
                >
                  Удалить профиль
                </v-btn>
              </v-card-text>
            </v-card>

            <!-- Статистика -->
            <v-card class="glass mt-4 fade-in">
              <v-card-title class="pa-5 pb-3">
                <v-icon color="primary" class="mr-2">mdi-chart-box</v-icon>
                <span class="font-weight-bold">Статистика</span>
              </v-card-title>

              <v-card-text class="pa-5">
                <v-row dense>
                  <v-col cols="6">
                    <div class="stat-card stat-blue">
                      <v-icon size="24" class="mb-1">mdi-folder-multiple</v-icon>
                      <div class="text-h4 font-weight-bold">
                        {{ stats?.projects_count || 0 }}
                      </div>
                      <div class="text-caption">Проектов</div>
                    </div>
                  </v-col>

                  <v-col cols="6">
                    <div class="stat-card stat-green">
                      <v-icon size="24" class="mb-1">mdi-check-circle</v-icon>
                      <div class="text-h4 font-weight-bold">
                        {{ stats?.completed_count || 0 }}
                      </div>
                      <div class="text-caption">Завершено</div>
                    </div>
                  </v-col>

                  <v-col cols="6">
                    <div class="stat-card stat-purple">
                      <v-icon size="24" class="mb-1">mdi-comment-multiple</v-icon>
                      <div class="text-h4 font-weight-bold">
                        {{ stats?.reviews_count || 0 }}
                      </div>
                      <div class="text-caption">Отзывов</div>
                    </div>
                  </v-col>

                  <v-col cols="6">
                    <div class="stat-card stat-amber">
                      <v-icon size="24" class="mb-1">mdi-star</v-icon>
                      <div class="text-h4 font-weight-bold">
                        {{ stats?.average_rating?.toFixed(1) || '0.0' }}
                      </div>
                      <div class="text-caption">Рейтинг</div>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Правая колонка -->
          <v-col cols="12" md="8">
            <!-- О себе -->
            <v-card class="glass mb-4 fade-in">
              <v-card-title class="pa-5 pb-3 d-flex align-center">
                <v-icon color="primary" class="mr-2">mdi-account-details</v-icon>
                <span class="font-weight-bold">О себе</span>
              </v-card-title>
              <v-card-text class="pa-5 pt-0">
                <p v-if="authStore.user.bio" class="text-body-1">
                  {{ authStore.user.bio }}
                </p>
                <p v-else style="color: #6B7280">
                  Информация не заполнена. Нажмите "Редактировать", чтобы добавить.
                </p>
              </v-card-text>
            </v-card>

            <!-- Навыки -->
            <v-card class="glass mb-4 fade-in">
              <v-card-title class="pa-5 pb-3 d-flex align-center">
                <v-icon color="primary" class="mr-2">mdi-tag-multiple</v-icon>
                <span class="font-weight-bold">Навыки</span>
                <v-chip
                  v-if="authStore.user.skills?.length"
                  size="small"
                  class="ml-2"
                  variant="tonal"
                  color="primary"
                >
                  {{ authStore.user.skills.length }}
                </v-chip>
              </v-card-title>
              <v-card-text class="pa-5 pt-0">
                <template v-if="authStore.user.skills?.length">
                  <v-chip
                    v-for="skill in authStore.user.skills"
                    :key="skill"
                    class="mr-2 mb-2 skill-chip"
                    variant="tonal"
                    color="primary"
                    size="default"
                  >
                    {{ skill }}
                  </v-chip>
                </template>
                <p v-else style="color: #6B7280">
                  Навыки не указаны
                </p>
              </v-card-text>
            </v-card>

            <!-- Отзывы -->
            <v-card class="glass fade-in">
              <v-card-title class="pa-5 pb-3 d-flex align-center">
                <v-icon color="primary" class="mr-2">mdi-star-circle</v-icon>
                <span class="font-weight-bold">Отзывы обо мне</span>
              </v-card-title>
              <v-card-text class="pa-5 pt-0">
                <ReviewStats :stats="reviewsStats" />
                <ReviewList @page-change="handleReviewPageChange" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </template>

    <!-- Диалог удаления профиля -->
    <v-dialog v-model="showDeleteDialog" max-width="480">
      <v-card class="glass">
        <v-card-title class="d-flex align-center pa-5">
          <v-icon color="error" size="28" class="mr-3">mdi-alert</v-icon>
          <span class="text-h6 font-weight-bold">Удалить профиль?</span>
        </v-card-title>

        <v-card-text class="pa-5">
          Это действие <strong>деактивирует</strong> ваш аккаунт. Вы больше не сможете войти.
          Все ваши проекты и контракты останутся в системе.
        </v-card-text>

        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn
            variant="outlined"
            :disabled="deleting"
            @click="showDeleteDialog = false"
          >
            Отмена
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="deleting"
            prepend-icon="mdi-delete"
            @click="handleDeleteAccount"
          >
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { useReviewsStore } from '@/stores/reviews'
import ProfileEditForm from '@/components/profile/ProfileEditForm.vue'
import ReviewList from '@/components/review/ReviewList.vue'
import ReviewStats from '@/components/review/ReviewStats.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const reviewsStore = useReviewsStore()

const isEditingProfile = ref(false)
const showDeleteDialog = ref(false)
const deleting = ref(false)

const stats = computed(() => userStore.stats)
const reviewsStats = computed(() => userStore.reviewsStats)

const avatarUrl = computed(() => {
  const name = authStore.user?.fullname || authStore.user?.username || 'User'
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3B82F6&color=fff&size=240`
})

const roleLabel = computed(() => {
  const roles = {
    admin: 'Администратор',
    client: 'Заказчик',
    freelancer: 'Фрилансер',
  }
  return roles[authStore.user?.role] || 'Пользователь'
})

const roleIcon = computed(() => {
  const icons = {
    admin: 'mdi-shield-account',
    client: 'mdi-account-tie',
    freelancer: 'mdi-briefcase-account',
  }
  return icons[authStore.user?.role] || 'mdi-account'
})

const roleColor = computed(() => {
  const colors = {
    admin: 'red',
    client: 'blue',
    freelancer: 'green',
  }
  return colors[authStore.user?.role] || 'grey'
})

async function loadData() {
  await authStore.fetchProfile()
  await userStore.fetchStats()
  if (authStore.user?.id) {
    await userStore.fetchUserReviewsStats(authStore.user.id)
    await reviewsStore.fetchByUser(authStore.user.id)
  }
}

async function handleUpdateProfile(data) {
  const result = await userStore.updateProfile(data)
  if (result) {
    await authStore.fetchProfile()
    isEditingProfile.value = false
  }
}

function handleReviewPageChange(page) {
  reviewsStore.setPage(page)
  reviewsStore.fetchByUser(authStore.user.id)
}

async function handleDeleteAccount() {
  deleting.value = true
  const success = await authStore.deleteAccount()
  deleting.value = false

  if (success) {
    showDeleteDialog.value = false
    router.push('/login')
  }
}

onMounted(loadData)
</script>

<style scoped>
.profile-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
}

/* Аватар с градиентной обводкой */
.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.profile-avatar {
  border: 3px solid #0A0E1A;
  position: relative;
  z-index: 2;
}

.avatar-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6, #3B82F6);
  z-index: 1;
  animation: rotate 3s linear infinite;
  filter: blur(8px);
  opacity: 0.7;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Карточки статистики */
.stat-card {
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  transition: all 0.2s ease;
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-blue {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05));
  color: #60A5FA;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.stat-green {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.stat-purple {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.05));
  color: #A78BFA;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.stat-amber {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
  color: #FBBF24;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

/* Чипы навыков */
.skill-chip {
  transition: all 0.2s ease;
}

.skill-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>