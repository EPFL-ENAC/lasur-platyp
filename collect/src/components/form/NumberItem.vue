<template>
  <div>
    <div :class="labelClass">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>

    <div class="row justify-center">
      <q-btn
        v-if="props.step2"
        flat
        dense
        rounded
        color="accent"
        size="lg"
        icon="keyboard_double_arrow_left"
        :disable="modelValue === props.min"
        @click="decrement2"
      />

      <q-btn
        flat
        dense
        rounded
        color="accent"
        size="lg"
        :icon="props.step2 ? 'keyboard_arrow_left' : 'remove'"
        :disable="modelValue === props.min"
        @click="decrement"
      />

      <q-input
        v-model.number="modelValue"
        class="number-input text-h4 q-ml-lg q-mr-lg"
        :style="{ '--input-width': inputWidth }"
        :min="props.min"
        :max="props.max"
        type="number"
      >
        <template #append>
          {{ props.unit }}
        </template>
      </q-input>

      <q-btn
        flat
        dense
        rounded
        color="accent"
        size="lg"
        :icon="props.step2 ? 'keyboard_arrow_right' : 'add'"
        :disable="modelValue === props.max"
        @click="increment"
      />

      <q-btn
        v-if="props.step2"
        flat
        dense
        rounded
        color="accent"
        size="lg"
        icon="keyboard_double_arrow_right"
        :disable="modelValue === props.max"
        @click="increment2"
      />
    </div>

    <div v-if="unitHint" class="row justify-center q-mt-md">
      <span class="text-h5 q-ml-lg q-mr-lg">{{ props.unitHint }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
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

const modelValue = defineModel<number | undefined>()

const inputWidth = computed(() => {
  const length = modelValue.value !== undefined ? modelValue.value.toString().length : 1
  return `${Math.max(length, 1)}ch`
})

function decrement() {
  const value = modelValue.value === undefined ? (props.min ?? 0) : modelValue.value

  const newValue = value - (props.step ?? 1)
  modelValue.value = props.min !== undefined && newValue < props.min ? props.min : newValue
}

function increment() {
  const value = modelValue.value === undefined ? 0 : modelValue.value
  const newValue = value + (props.step ?? 1)
  modelValue.value = props.max !== undefined && newValue > props.max ? props.max : newValue
}

function decrement2() {
  const value = modelValue.value === undefined ? (props.min ?? 0) : modelValue.value

  const newValue = value - (props.step2 ?? 5)
  modelValue.value = props.min !== undefined && newValue < props.min ? props.min : newValue
}

function increment2() {
  const value = modelValue.value === undefined ? 0 : modelValue.value
  const newValue = value + (props.step2 ?? 5)
  modelValue.value = props.max !== undefined && newValue > props.max ? props.max : newValue
}

const labelClass = computed(() => props.labelClass || 'text-h4')
</script>

<style scoped>
.number-input :deep(.q-field__control-container) {
  width: var(--input-width, 5rem);
}

.number-input :deep(input[type='number']::-webkit-outer-spin-button),
.number-input :deep(input[type='number']::-webkit-inner-spin-button) {
  -webkit-appearance: none;
  margin: 0;
}

.number-input :deep(input[type='number']) {
  -moz-appearance: textfield;
}
</style>
