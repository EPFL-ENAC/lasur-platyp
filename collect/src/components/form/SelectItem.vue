<template>
  <div>
    <div class="text-bold q-mb-md" :class="labelClass || 'question-label'">{{ label }}</div>
    <div v-if="hint" class="question-hint q-mb-md">{{ hint }}</div>
    <div>
      <div
        v-if="selectedOption && options.length === 1 && selectModel === options[0]?.value"
        class="select-item__single"
      >
        <div :class="optionLabelClass">{{ selectedOption.label }}</div>
        <div v-if="selectedOption.hint" class="question-hint">{{ selectedOption.hint }}</div>
      </div>
      <q-select
        v-else
        v-model="selectModel"
        :options="selectOptions"
        :use-input="options.length > 10"
        input-debounce="0"
        map-options
        emit-value
        hide-dropdown-icon
        outlined
        color="field"
        bg-color="field"
        input-class="question-label"
        :placeholder="!selectModel ? t('form.search_or_select_option') : ''"
        @filter="filterFn"
        @blur="onBlur"
        @update:model-value="onUpdated"
      >
        <template v-slot:selected>
          <template v-for="option in options" :key="option.value">
            <div v-if="isSelected(option) && !filtering">
              <div :class="optionLabelClass">{{ option.label }}</div>
              <div v-if="option.hint" class="question-hint">{{ option.hint }}</div>
            </div>
          </template>
        </template>
        <template v-slot:option="scope">
          <q-item v-bind="scope.itemProps">
            <q-item-section v-if="scope.opt.icon" avatar>
              <q-icon :name="scope.opt.icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label :class="optionLabelClass">{{ scope.opt.label }}</q-item-label>
              <q-item-label class="question-hint">{{ scope.opt.hint }}</q-item-label>
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
import type { Option } from '@/components/form/models'

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

<style scoped lang="scss">
// With a single option there is nothing to choose, so it reads as a filled
// field rather than a highlighted selection: same border, radius and surface as
// the select it replaces.
.select-item__single {
  padding: 12px 16px;
  border: 1px solid var(--secondary-border-color);
  border-radius: $button-border-radius;
  background: var(--card-bg);
}
</style>
