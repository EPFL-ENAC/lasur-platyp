<template>
  <div>
    <div class="text-h4 q-mb-md">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="row justify-center q-mt-lg">
      <span
        class="text-h4 q-mt-md q-mr-lg cursor-pointer"
        :class="selected ? 'text-grey-6' : 'text-white'"
        @click="selected = false"
        >{{ leftLabel }}</span
      >
      <q-toggle v-model="selected" color="primary" size="80px" @update:model-value="onUpdate" />
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

const selected = ref<boolean>(false)

onMounted(() => {
  if (props.modelValue === undefined) {
    emit('update:modelValue', false)
  } else {
    selected.value = props.modelValue
  }
})

function onUpdate(value: boolean) {
  emit('update:modelValue', value === undefined ? false : value)
}
</script>
