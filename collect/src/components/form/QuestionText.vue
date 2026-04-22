<template>
  <div :class="containerClass">
    <template v-for="(segment, index) in segments" :key="index">
      <span v-if="segment.startsWith('(') && segment.endsWith(')')" class="text-weight-regular">
        {{ segment }}
      </span>
      <template v-else>
        {{ segment }}
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label?: string
  containerClass?: string | string[] | object
}

const props = defineProps<Props>()

const segments = computed(() => {
  if (!props.label) return []
  // Splits the string while keeping the parentheses segments
  return props.label.split(/(\([^)]+\))/g)
})
</script>
