<template>
  <div>
    <div class="text-h4 text-bold q-mb-md" :class="labelClass">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="row justify-center q-mt-xl">
      <q-btn
        flat
        v-if="props.step2"
        rounded
        @click="decrement2"
        :disable="props.modelValue === props.min"
        color="accent"
        icon="keyboard_double_arrow_left"
        class="q-mr-md"
      />
      <q-btn
        flat
        rounded
        @click="decrement"
        :disable="props.modelValue === props.min"
        color="accent"
        :icon="step2 ? 'keyboard_arrow_left' : 'remove'"
      />
      <span class="text-h4 q-ml-lg q-mr-lg">{{ props.modelValue }} {{ props.unit }}</span>
      <q-btn
        flat
        rounded
        @click="increment"
        :disable="props.modelValue === props.max"
        color="accent"
        :icon="step2 ? 'keyboard_arrow_right' : 'add'"
      />
      <q-btn
        flat
        v-if="props.step2"
        rounded
        @click="increment2"
        :disable="props.modelValue === props.max"
        color="accent"
        icon="keyboard_double_arrow_right"
        class="q-ml-md"
      />
    </div>
    <div class="row justify-center q-mt-md">
      <span class="text-h5 q-ml-lg q-mr-lg">{{ props.unitHint }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: number | undefined
  label?: string
  hint?: string
  unit?: string
  unitHint?: string
  required?: boolean
  min?: number
  max?: number
  step?: number
  step2?: number
  labelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

function decrement() {
  const value =
    props.modelValue === undefined ? (props.min === undefined ? 0 : props.min) : props.modelValue
  const newValue = value - (props.step ? props.step : 1)
  emit('update:modelValue', props.min !== undefined && newValue < props.min ? props.min : newValue)
}

function increment() {
  const value = props.modelValue === undefined ? 0 : props.modelValue
  const newValue = value + (props.step ? props.step : 1)
  emit('update:modelValue', props.max !== undefined && newValue > props.max ? props.max : newValue)
}

function decrement2() {
  const value =
    props.modelValue === undefined ? (props.min === undefined ? 0 : props.min) : props.modelValue
  const newValue = value - (props.step2 ? props.step2 : 5)
  emit('update:modelValue', props.min !== undefined && newValue < props.min ? props.min : newValue)
}

function increment2() {
  const value = props.modelValue === undefined ? 0 : props.modelValue
  const newValue = value + (props.step2 ? props.step2 : 5)
  emit('update:modelValue', props.max !== undefined && newValue > props.max ? props.max : newValue)
}
</script>
