<template>
  <div>
    <div class="text-h4 q-mb-md">{{ label }}</div>
    <div v-if="hint" class="text-h6">{{ hint }}</div>
    <q-slider
      v-model="selected"
      marker-labels
      track-size="20px"
      thumb-size="45px"
      thumb-color="green-4"
      :min="min"
      :max="max"
      :step="step"
      @update:model-value="onUpdate"
    />
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: number | undefined
  label?: string
  hint?: string
  required?: boolean
  min?: number
  max?: number
  step?: number
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selected = ref<number>(0)

onMounted(() => {
  if (props.modelValue === undefined) {
    emit('update:modelValue', props.min === undefined ? 0 : props.min)
  } else {
    selected.value = props.modelValue
  }
})

function onUpdate() {
  emit('update:modelValue', selected.value === undefined ? 0 : selected.value)
}
</script>
