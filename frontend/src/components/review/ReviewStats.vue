<template>
  <v-card v-if="stats" class="mb-4">
    <v-card-text>
      <v-row align="center">
        <!-- Средний балл -->
        <v-col cols="12" sm="4" class="text-center">
          <div class="text-h3 font-weight-bold">
            {{ stats.average_rating?.toFixed(1) || '0.0' }}
          </div>
          <RatingStars
            :value="Math.round(stats.average_rating || 0)"
            :size="20"
          />
          <div class="text-caption text-medium-emphasis mt-1">
            {{ stats.total_reviews }} отзывов
          </div>
        </v-col>

        <!-- Распределение -->
        <v-col cols="12" sm="8">
          <div
            v-for="star in [5, 4, 3, 2, 1]"
            :key="star"
            class="d-flex align-center mb-1"
          >
            <span class="text-body-2" style="width: 20px">{{ star }}</span>
            <v-icon size="16" color="amber" class="mx-1">mdi-star</v-icon>
            <v-progress-linear
              :model-value="getPercent(star)"
              color="amber"
              height="8"
              rounded
              class="flex-grow-1 mx-2"
            />
            <span class="text-caption" style="width: 40px">
              {{ getCount(star) }}
            </span>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import RatingStars from './RatingStars.vue'

const props = defineProps({
  stats: {
    type: Object,
    default: null,
  },
})

function getCount(star) {
  return props.stats?.rating_distribution?.[star] || 0
}

function getPercent(star) {
  const total = props.stats?.total_reviews || 0
  if (!total) return 0
  return (getCount(star) / total) * 100
}
</script>