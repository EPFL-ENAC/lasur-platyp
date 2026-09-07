<template>
  <div>
    <div :class="labelClass">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>

    <div class="row items-center">
      <q-btn
        v-if="props.step2"
        class="number-item__step"
        icon="keyboard_double_arrow_left"
        :disable="modelValue === props.min"
        @click="decrement2"
      />

      <q-btn
        class="number-item__step"
        :icon="props.step2 ? 'keyboard_arrow_left' : 'remove'"
        :disable="modelValue === props.min"
        @click="decrement"
      />

      <q-input
        v-model.number="modelValue"
        outlined
        dense
        class="number-input q-mx-md"
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
        class="number-item__step"
        :icon="props.step2 ? 'keyboard_arrow_right' : 'add'"
        :disable="modelValue === props.max"
        @click="increment"
      />

      <q-btn
        v-if="props.step2"
        class="number-item__step"
        icon="keyboard_double_arrow_right"
        :disable="modelValue === props.max"
        @click="increment2"
      />
    </div>

    <div v-if="unitHint" class="q-mt-md">
      <span class="text-h5">{{ props.unitHint }}</span>
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

const labelClass = computed(() => props.labelClass || 'question-label')
</script>

<style scoped lang="scss">
.number-item__step {
  width: 40px;
  min-width: 40px;
  height: 40px;
  padding: 0 !important;
}

.number-input {
  font-size: 1rem;
}

.number-input :deep(.q-field__append) {
  font-size: 1rem;
}

.number-input :deep(.q-field__control) {
  height: 40px;
  min-height: 40px;
  border-radius: $button-border-radius;

  &::before {
    border: 1px solid var(--secondary-border-color);
  }
}

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
