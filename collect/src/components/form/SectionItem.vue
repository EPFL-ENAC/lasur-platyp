<template>
  <div>
    <QuestionText :label="label ?? ''" :containerClass="`text-bold q-mb-md ${labelClass}`" />
    <div v-if="hint" class="question-hint">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
import QuestionText from './QuestionText.vue'

interface Props {
  label?: string
  hint?: string
  labelClass?: string
}
defineProps<Props>()
</script>
