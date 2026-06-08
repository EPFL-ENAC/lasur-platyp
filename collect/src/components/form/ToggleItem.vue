<template>
  <div>
    <QuestionText v-if="label" :label="label" :class="`${labelClass}`" />
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="row justify-center q-mt-lg">
      <span
        class="text-h4 q-mr-lg cursor-pointer"
        :class="selected ? 'text-muted' : 'text-foreground'"
        @click="selected = false"
        >{{ leftLabel }}</span
      >
      <q-toggle
        v-model="selected"
        :color="props.color ?? 'primary'"
        :toggle-indeterminate="required !== true"
        dense
        size="80px"
      />
      <span
        class="text-h4 q-ml-lg cursor-pointer"
        :class="selected ? 'text-foreground' : 'text-muted'"
        @click="selected = true"
        >{{ rightLabel }}</span
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import QuestionText from './QuestionText.vue'

interface Props {
  modelValue: boolean | undefined
  label?: string
  labelClass?: string
  leftLabel?: string
  rightLabel?: string
  hint?: string
  required?: boolean
  color?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selected = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
})

const labelClass = computed(() => props.labelClass || 'text-h4')
</script>
