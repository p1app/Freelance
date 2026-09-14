<template>
  <div class="d-flex align-center">
    <v-icon
      v-for="i in 5"
      :key="i"
      :color="i <= value ? color : 'grey-lighten-1'"
      :size="size"
      class="mr-1"
    >
      {{ i <= value ? 'mdi-star' : 'mdi-star-outline' }}
    </v-icon>
    <span v-if="showValue" class="ml-2 text-body-2">
      {{ value }} / 5
    </span>
  </div>
</template>

<script setup>
defineProps({
  value: {
    type: Number,
    default: 0,
  },
  size: {
    type: [Number, String],
    default: 20,
  },
  color: {
    type: String,
    default: 'amber',
  },
  showValue: {
    type: Boolean,
    default: false,
  },
})
</script>