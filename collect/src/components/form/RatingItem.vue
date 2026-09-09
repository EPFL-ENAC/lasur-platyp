<template>
  <div class="rating-item">
    <QuestionText
      :label="label ?? ''"
      :containerClass="`text-bold q-mb-md ${labelClass || 'question-label'}`"
    />
    <div v-if="hint" class="question-hint q-mb-md">{{ hint }}</div>
    <q-rating
      v-model="selected"
      size="2em"
      no-dimming
      icon="star_border"
      icon-selected="star"
      :max="max || 5"
      @update:model-value="onUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import QuestionText from './QuestionText.vue'

interface Props {
  modelValue: number | undefined
  label?: string
  hint?: string
  required?: boolean
  max?: number
  labelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selected = ref<number>(0)

watch(
  () => props.modelValue,
  (value) => {
    if (value === undefined) {
      selected.value = 0
      emit('update:modelValue', 0)
    } else {
      selected.value = value
    }
  },
  { immediate: true },
)

function onUpdate() {
  if (selected.value === undefined || selected.value === 0) selected.value = 1
  emit('update:modelValue', selected.value)
}
</script>

<style scoped lang="scss">
// Laid out in a grid, cells stretch to the tallest label in their row. Pushing
// the stars to the bottom keeps them on one line however the labels wrap.
.rating-item {
  display: flex;
  flex-direction: column;
}

.rating-item :deep(.q-rating) {
  margin-top: auto;
  align-self: flex-start;
}

// Unpicked stars are outlines in the border colour, picked ones fill with the
// brand yellow. Quasar's default is to dim the accent colour instead, so
// `no-dimming` on the component hands the colours over to these rules.
.rating-item :deep(.q-rating__icon) {
  color: var(--secondary-border-color);
  text-shadow: none;
}

.rating-item :deep(.q-rating__icon--active) {
  color: $primary;
}
</style>
