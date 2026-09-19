<template>
  <v-dialog
    :model-value="state.visible"
    max-width="440"
    persistent
    @update:model-value="(value) => !value && answer(false)"
  >
    <v-card class="glass confirm-card">
      <v-card-title class="d-flex align-center pa-5 pb-2">
        <v-icon :color="state.color" size="26" class="mr-3">mdi-help-circle-outline</v-icon>
        <span class="text-h6 font-weight-bold">{{ state.title }}</span>
      </v-card-title>

      <v-card-text v-if="state.text" class="pa-5 pt-2" style="color: #9ca3af">
        {{ state.text }}
      </v-card-text>

      <v-card-actions class="pa-5 pt-2">
        <v-spacer />
        <v-btn variant="outlined" @click="answer(false)">
          {{ state.cancelText }}
        </v-btn>
        <v-btn :color="state.color" variant="flat" class="btn-glow" @click="answer(true)">
          {{ state.confirmText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useConfirm } from '@/composables/useConfirm'

const { state, answer } = useConfirm()
</script>

<style scoped>
.confirm-card {
  border: 1px solid rgba(59, 130, 246, 0.15) !important;
}
</style>
