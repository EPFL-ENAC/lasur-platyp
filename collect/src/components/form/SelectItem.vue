<template>
  <div>
    <div class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="q-mt-lg">
      <div
        v-if="selectedOption && options.length === 1 && selectModel === options[0]?.value"
        class="q-mb-md bg-primary text-white rounded-borders q-px-md q-py-sm"
      >
        <div :class="optionLabelClass">{{ selectedOption.label }}</div>
        <div class="text-subtitle1">{{ selectedOption.hint }}</div>
      </div>
      <q-select
        v-else
        v-model="selectModel"
        :options="selectOptions"
        :use-input="options.length > 10"
        input-debounce="0"
        map-options
        emit-value
        filled
        hide-dropdown-icon
        bg-color="primary"
        input-class="text-h6 text-white"
        :placeholder="!selectModel ? t('form.search_or_select_option') : ''"
        @filter="filterFn"
        @blur="onBlur"
        @update:model-value="onUpdated"
      >
        <template v-slot:selected>
          <template v-for="option in options" :key="option.value">
            <div v-if="isSelected(option) && !filtering" class="text-white">
              <div :class="optionLabelClass">{{ option.label }}</div>
              <div v-if="option.hint" class="text-subtitle1">{{ option.hint }}</div>
            </div>
          </template>
        </template>
        <template v-slot:option="scope">
          <q-item
            v-bind="scope.itemProps"
            :class="scope.selected ? 'text-primary' : 'bg-primary text-grey-3'"
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
        <template v-slot:no-option>
          <q-item>
            <q-item-section class="text-grey">{{ t('no_results') }}</q-item-section>
          </q-item>
        </template>
      </q-select>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Option } from 'src/components/form/models'

const { t } = useI18n()

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
const selectOptions = ref<Option[]>(props.options)
const filter = ref<string>('')
const filtering = computed(() => !!filter.value)

watch([() => props.options, () => props.modelValue], () => {
  selectOptions.value = props.options
  selectModel.value = props.modelValue
})

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === selectModel.value)
})

function isSelected(option: Option) {
  return selectModel.value === option.value
}

function filterFn(val: string, update: (callback: () => void) => void) {
  filter.value = val
  if (!val || val.length === 0) {
    update(() => {
      selectOptions.value = props.options
    })
    return
  }
  update(() => {
    const needle = val.toLowerCase()
    selectOptions.value = props.options.filter(
      (option) =>
        option.label.toLowerCase().indexOf(needle) > -1 ||
        (option.hint && option.hint.toLowerCase().indexOf(needle) > -1),
    )
  })
}

function onUpdated(value: string | undefined) {
  emit('update:modelValue', value)
  filter.value = ''
}

function onBlur() {
  filter.value = ''
}
</script>
