<template>
  <div>
    <v-skeleton-loader
      v-if="reviewsStore.loading && reviewsStore.reviews.length === 0"
      type="card"
    />

    <v-empty-state
      v-else-if="reviewsStore.reviews.length === 0"
      icon="mdi-comment-outline"
      title="Отзывов нет"
      text="Пока никто не оставил отзыв"
    />

    <ReviewItem
      v-for="review in reviewsStore.reviews"
      :key="review.id"
      :review="review"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
    />

    <v-pagination
      v-if="reviewsStore.pagination.pages > 1"
      :model-value="reviewsStore.pagination.page"
      :length="reviewsStore.pagination.pages"
      class="mt-4"
      @update:model-value="$emit('page-change', $event)"
    />
  </div>
</template>

<script setup>
import { useReviewsStore } from '@/stores/reviews'
import ReviewItem from './ReviewItem.vue'

defineEmits(['edit', 'delete', 'page-change'])

const reviewsStore = useReviewsStore()
</script>