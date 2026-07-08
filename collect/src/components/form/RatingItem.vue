<template>
  <div>
    <QuestionText
      :label="label ?? ''"
      :containerClass="`text-bold q-mb-md ${labelClass || 'text-h4'}`"
    />
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <q-rating
      v-model="selected"
      size="3.5em"
      color="accent"
      icon="star_border"
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
