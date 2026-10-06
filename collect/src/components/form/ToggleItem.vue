<template>
  <div>
    <QuestionText v-if="label" :label="label" :class="`${labelClass}`" />
    <div v-if="hint" class="question-hint q-mb-md">{{ hint }}</div>
    <!-- Nothing above to clear when the step title carries the question. -->
    <div
      class="toggle-item__options row items-center"
      :class="{ 'toggle-item__options--spaced': label || hint }"
    >
      <q-radio
        v-model="selected"
        :val="true"
        :label="trueLabel"
        :color="props.color ?? 'primary'"
        size="sm"
        class="text-subtitle1"
      />
      <q-radio
        v-model="selected"
        :val="false"
        :label="falseLabel"
        :color="props.color ?? 'primary'"
        size="sm"
        class="text-subtitle1"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import QuestionText from './QuestionText.vue'

interface Props {
  modelValue: boolean | undefined
  label?: string
  labelClass?: string
  trueLabel?: string
  falseLabel?: string
  hint?: string
  color?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selected = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
})

const labelClass = computed(() => props.labelClass || 'question-label')
</script>

<style scoped lang="scss">
.toggle-item__options {
  display: flex;
  gap: 24px;
}

// At `sm` Quasar rings the 17px circle with a ~9px touch target. Pulling that
// off the first one lines the control up with the label above it, and keeps the
// gap below the label the one set here rather than the ring plus a margin.
.toggle-item__options :deep(.q-radio:first-child) {
  margin-left: -9px;
}

.toggle-item__options--spaced {
  margin-top: 8px;
}
</style>
