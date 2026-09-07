<template>
  <div>
    <QuestionText v-if="label" :label="label" :class="`${labelClass}`" />
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="row items-center q-gutter-lg q-mt-lg">
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
