<template>
  <v-container>
    <v-skeleton-loader v-if="userStore.loading" type="article" />

    <v-empty-state
      v-else-if="!profile"
      icon="mdi-account-off-outline"
      title="Пользователь не найден"
    >
      <template #actions>
        <v-btn color="primary" to="/">На главную</v-btn>
      </template>
    </v-empty-state>

    <template v-else>
      <v-btn
        variant="text"
        prepend-icon="mdi-arrow-left"
        class="mb-4"
        @click="$router.back()"
      >
        Назад
      </v-btn>

      <v-row>
        <!-- Левая колонка -->
        <v-col cols="12" md="4">
          <v-card class="glass profile-card fade-in">
            <v-card-text class="text-center pa-6">
              <!-- Аватар с градиентной обводкой -->
              <div class="avatar-wrapper mb-4">
                <v-avatar :image="avatarUrl" size="120" class="profile-avatar" />
                <div class="avatar-ring" />
              </div>

              <h2 class="text-h5 font-weight-bold">
                {{ profile.fullname || profile.username }}
              </h2>
              <p class="text-body-2 mt-1" style="color: #9CA3AF">
                @{{ profile.username }}
              </p>

              <v-divider class="my-5" style="border-color: rgba(59, 130, 246, 0.15)" />

              <v-row dense>
                <v-col cols="6">
                  <div class="stat-card stat-green">
                    <v-icon size="20" class="mb-1">mdi-check-circle</v-icon>
                    <div class="text-h5 font-weight-bold">
                      {{ profile.completed_projects || 0 }}
                    </div>
                    <div class="text-caption">Завершено</div>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="stat-card stat-amber">
                    <v-icon size="20" class="mb-1">mdi-star</v-icon>
                    <div class="text-h5 font-weight-bold">
                      {{ profile.rating?.toFixed(1) || '0.0' }}
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
          <v-card class="glass mb-4 fade-in">
            <v-card-title class="pa-5 pb-3 d-flex align-center">
              <v-icon color="primary" class="mr-2">mdi-account-details</v-icon>
              <span class="font-weight-bold">О себе</span>
            </v-card-title>
            <v-card-text class="pa-5 pt-0">
              <p v-if="profile.bio" class="text-body-1">{{ profile.bio }}</p>
              <p v-else style="color: #6B7280">Информация не заполнена</p>
            </v-card-text>
          </v-card>

          <v-card class="glass mb-4 fade-in">
            <v-card-title class="pa-5 pb-3 d-flex align-center">
              <v-icon color="primary" class="mr-2">mdi-tag-multiple</v-icon>
              <span class="font-weight-bold">Навыки</span>
            </v-card-title>
            <v-card-text class="pa-5 pt-0">
              <template v-if="profile.skills?.length">
                <v-chip
                  v-for="skill in profile.skills"
                  :key="skill"
                  class="mr-2 mb-2 skill-chip"
                  variant="tonal"
                  color="primary"
                >
                  {{ skill }}
                </v-chip>
              </template>
              <p v-else style="color: #6B7280">Навыки не указаны</p>
            </v-card-text>
          </v-card>

          <v-card class="glass fade-in">
            <v-card-title class="pa-5 pb-3 d-flex align-center">
              <v-icon color="primary" class="mr-2">mdi-star-circle</v-icon>
              <span class="font-weight-bold">Отзывы</span>
            </v-card-title>
            <v-card-text class="pa-5 pt-0">
              <ReviewStats :stats="reviewsStats" />
              <ReviewList @page-change="handleReviewPageChange" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useReviewsStore } from '@/stores/reviews'
import ReviewList from '@/components/review/ReviewList.vue'
import ReviewStats from '@/components/review/ReviewStats.vue'

const route = useRoute()
const userStore = useUserStore()
const reviewsStore = useReviewsStore()

const profile = computed(() => userStore.publicProfile)
const reviewsStats = computed(() => userStore.reviewsStats)

const avatarUrl = computed(() => {
  const name = profile.value?.fullname || profile.value?.username || 'User'
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3B82F6&color=fff&size=240`
})

async function loadProfile() {
  const id = route.params.id
  await userStore.fetchPublicProfile(id)
  await userStore.fetchUserReviewsStats(id)
  await reviewsStore.fetchByUser(id)
}

function handleReviewPageChange(page) {
  reviewsStore.setPage(page)
  reviewsStore.fetchByUser(route.params.id)
}

onMounted(loadProfile)
watch(() => route.params.id, loadProfile)
</script>

<style scoped>
.profile-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
}

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
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.stat-card {
  padding: 12px;
  border-radius: 12px;
  text-align: center;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-green {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.stat-amber {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
  color: #FBBF24;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.skill-chip {
  transition: all 0.2s ease;
}

.skill-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>