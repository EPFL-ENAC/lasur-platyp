<template>
  <div>
    <div class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
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

onMounted(() => {
  if (props.modelValue === undefined) {
    emit('update:modelValue', 0)
  } else {
    selected.value = props.modelValue
  }
})

function onUpdate() {
  if (selected.value === undefined || selected.value === 0) selected.value = 1
  emit('update:modelValue', selected.value)
}
</script>
