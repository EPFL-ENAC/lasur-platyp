<template>
  <div>
    <div class="text-h4 text-bold q-mb-md" :class="labelClass">{{ label }}</div>
    <div v-if="hint" class="text-h6">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label?: string
  hint?: string
  labelClass?: string
}
defineProps<Props>()
</script>
