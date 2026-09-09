<template>
  <div>
    <div v-if="label" :class="labelClass">{{ label }}</div>
    <div v-if="hint" class="question-hint q-mb-md">{{ hint }}</div>

    <div class="row items-center">
      <q-btn
        v-if="props.step2"
        class="number-item__step"
        icon="keyboard_double_arrow_left"
        aria-label="Decrease value by larger step"
        :disable="atMin"
        @click="decrement2"
      />

      <q-btn
        class="number-item__step"
        :icon="props.step2 ? 'keyboard_arrow_left' : 'remove'"
        aria-label="Decrease value"
        :disable="atMin"
        @click="decrement"
      />

      <q-input
        v-model.number="draft"
        outlined
        dense
        class="number-input q-mx-md"
        :style="{ '--input-width': inputWidth }"
        :min="props.min"
        :max="props.max"
        type="number"
        :inputmode="noNegative ? 'numeric' : undefined"
        @keydown="onKeydown"
        @blur="onBlur"
      >
        <template #append>
          {{ props.unit }}
        </template>
      </q-input>

      <q-btn
        class="number-item__step"
        :icon="props.step2 ? 'keyboard_arrow_right' : 'add'"
        aria-label="Increase value"
        :disable="atMax"
        @click="increment"
      />

      <q-btn
        v-if="props.step2"
        class="number-item__step"
        icon="keyboard_double_arrow_right"
        aria-label="Increase value by larger step"
        :disable="atMax"
        @click="increment2"
      />
    </div>

    <div v-if="unitHint" class="q-mt-sm">
      <span class="text-caption">{{ props.unitHint }}</span>
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

// What the field shows. It follows the model, but while the traveller is
// typing it may hold something the model must never see: an empty field, or
// a value still below the minimum that the next digit will fix.
const draft = ref<number | string | undefined>(modelValue.value)

watch(modelValue, (val) => {
  if (val !== draft.value) draft.value = val
})

watch(draft, (val) => {
  if (typeof val !== 'number' || !Number.isFinite(val)) return
  const bounded = boundWhileTyping(val)
  if (bounded !== val) {
    draft.value = bounded
    return
  }
  if (bounded !== modelValue.value) modelValue.value = bounded
})

// A bound may move under the value -- the professional journey card lowers
// the maximum from 365 to 7 when the period switches from year to week -- so
// the value follows the bound rather than sitting outside it.
watch(
  () => [props.min, props.max],
  () => {
    if (modelValue.value === undefined) return
    const bounded = clamp(modelValue.value)
    if (bounded !== modelValue.value) modelValue.value = bounded
  },
)

const noNegative = computed(() => props.min !== undefined && props.min >= 0)
const atMin = computed(() => props.min !== undefined && (modelValue.value ?? props.min) <= props.min)
const atMax = computed(() => props.max !== undefined && (modelValue.value ?? props.max) >= props.max)

const inputWidth = computed(() => {
  const length = draft.value !== undefined ? draft.value.toString().length : 1
  return `${Math.max(length, 1)}ch`
})

function clamp(value: number): number {
  let result = value
  if (props.min !== undefined && result < props.min) result = props.min
  if (props.max !== undefined && result > props.max) result = props.max
  return result
}

// Typing more digits only makes a number bigger, so anything above the
// maximum is capped at once. A value below the minimum is left alone while
// typing -- "1" may be on its way to "15" -- unless it is negative on a field
// that does not allow negatives, which no further digit can repair.
function boundWhileTyping(value: number): number {
  if (props.max !== undefined && value > props.max) return props.max
  if (props.min !== undefined && props.min >= 0 && value < 0) return props.min
  return value
}

// Keys that would produce a sign or an exponent the field has no use for.
function onKeydown(event: KeyboardEvent) {
  if (['e', 'E', '+'].includes(event.key) || (noNegative.value && event.key === '-')) {
    event.preventDefault()
  }
}

// Leaving the field settles whatever is in it onto an allowed value: an empty
// or unfinished entry falls back to the current value, or the minimum.
function onBlur() {
  const current =
    typeof draft.value === 'number' && Number.isFinite(draft.value)
      ? draft.value
      : (modelValue.value ?? props.min ?? 0)
  const settled = clamp(current)
  draft.value = settled
  modelValue.value = settled
}

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

// 40px is comfortable with a pointer but tight under a thumb, so the stepper
// and the field it frames grow on a phone.
@media (max-width: 599px) {
  .number-item__step {
    width: 56px;
    min-width: 56px;
    height: 56px;
  }

  .number-item__step :deep(.q-icon) {
    font-size: 24px;
  }

  .number-input :deep(.q-field__control) {
    height: 56px;
    min-height: 56px;
  }
}
</style>
