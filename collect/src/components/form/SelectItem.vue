<template>
  <div>
    <div class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="q-mt-lg">
      <div
        v-if="selectedOption && options.length === 1"
        class="q-mb-md bg-primary text-white rounded-borders q-px-md q-py-sm"
      >
        <div :class="optionLabelClass">{{ selectedOption.label }}</div>
        <div class="text-subtitle1">{{ selectedOption.hint }}</div>
      </div>
      <q-select
        v-else
        v-model="selectModel"
        :options="options"
        map-options
        emit-value
        filled
        hide-dropdown-icon
        bg-color="primary"
        @update:model-value="emit('update:modelValue', $event)"
      >
        <template v-slot:selected>
          <template v-for="option in options" :key="option.value">
            <div v-if="isSelected(option)" class="text-white">
              <div :class="optionLabelClass">{{ option.label }}</div>
              <div v-if="option.hint" class="text-subtitle1">{{ option.hint }}</div>
            </div>
          </template>
        </template>
        <template v-slot:option="scope">
          <q-item
            v-bind="scope.itemProps"
            :class="scope.selected ? 'text-primary' : 'bg-primary text-grey-4'"
          >
            <q-item-section v-if="scope.opt.icon" avatar>
              <q-icon :name="scope.opt.icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label :class="optionLabelClass">{{ scope.opt.label }}</q-item-label>
              <q-item-label class="text-subtitle1">{{ scope.opt.hint }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Option } from 'src/components/form/models'
interface Props {
  modelValue: string | undefined
  label?: string
  hint?: string
  options: Option[]
  required?: boolean
  labelClass?: string
  optionLabelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selectModel = ref<string | undefined>(props.modelValue)

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === selectModel.value)
})

function isSelected(option: Option) {
  return selectModel.value === option.value
}
</script>
