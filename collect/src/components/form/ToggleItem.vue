<template>
  <div>
    <div class="text-h4 text-bold q-mb-md">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="row justify-center q-mt-lg">
      <span
        class="text-h4 q-mt-md q-mr-lg cursor-pointer"
        :class="selected ? 'text-grey-6' : 'text-white'"
        @click="selected = false"
        >{{ leftLabel }}</span
      >
      <q-toggle v-model="selected" color="primary" size="80px" />
      <span
        class="text-h4 q-mt-md q-ml-lg cursor-pointer"
        :class="selected ? 'text-white' : 'text-grey-6'"
        @click="selected = true"
        >{{ rightLabel }}</span
      >
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean | undefined
  label?: string
  leftLabel?: string
  rightLabel?: string
  hint?: string
  required?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selected = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
})
</script>
