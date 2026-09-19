<template>
  <v-card class="mb-3">
    <v-card-item>
      <template #prepend>
        <v-avatar color="primary" size="40">
          <span class="text-white font-weight-bold">
            {{ initials }}
          </span>
        </v-avatar>
      </template>

      <v-card-title class="text-body-1">
        <router-link
          :to="{ name: 'UserPublic', params: { id: review.from_user_id } }"
          class="text-decoration-none text-primary"
        >
          {{ review.from_user_name }}
        </router-link>
      </v-card-title>

      <v-card-subtitle>
        {{ formatDate(review.created_at) }}
      </v-card-subtitle>

      <template #append>
        <RatingStars :value="review.rating" :size="18" />
      </template>
    </v-card-item>

    <v-card-text v-if="review.comment">
      <p class="text-body-2">{{ review.comment }}</p>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import RatingStars from './RatingStars.vue'

const props = defineProps({
  review: {
    type: Object,
    required: true,
  },
})

const initials = computed(() => {
  const name = props.review.from_user_name || 'U'
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

function formatDate(value) {
  return new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
}
</script>