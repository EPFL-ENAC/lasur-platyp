<template>
  <div>
    <QuestionText
      v-if="label"
      :label="label"
      :containerClass="`text-bold q-mb-md ${labelClass || 'question-label'}`"
    />
    <div v-if="hint" class="question-hint q-mb-md">{{ hint }}</div>
    <div v-if="multiple" class="question-hint">{{ t('form.multiple_options') }}</div>
    <div class="step-content">
      <div :class="col ? 'row q-col-gutter-md' : ''">
        <template v-for="(group, idx) in optionGroups" :key="idx">
          <div :class="col ? `col-${12 / col}` : ''">
            <q-list>
              <template v-for="option in group" :key="option.value">
                <q-item
                  :active="isSelected(option)"
                  active-class="choice-option--selected"
                  v-ripple
                  clickable
                  class="choice-option q-mb-md"
                  @click="onOption(option)"
                >
                  <q-item-section avatar>
                    <q-checkbox
                      v-if="multiple"
                      :model-value="isSelected(option)"
                      size="md"
                      color="primary"
                      tabindex="-1"
                      class="choice-option__control"
                    />
                    <q-radio
                      v-else
                      :model-value="isSelected(option)"
                      :val="true"
                      size="md"
                      color="primary"
                      tabindex="-1"
                      class="choice-option__control"
                    />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="question-label" :class="optionLabelClass">{{
                      option.label
                    }}</q-item-label>
                    <q-item-label v-if="option.hint" class="text-caption">
                      {{ option.hint }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-list>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Option } from '@/components/form/models'
import QuestionText from './QuestionText.vue'

interface Props {
  modelValue: string | string[] | undefined
  label?: string
  hint?: string
  options: Option[]
  required?: boolean
  multiple?: boolean
  max?: number
  col?: number
  labelClass?: string
  optionLabelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const selected = computed(() => {
  if (props.multiple) {
    return (props.modelValue as string[]) || []
  } else {
    return [props.modelValue as string]
  }
})

const optionGroups = computed(() => {
  const groups: Option[][] = []
  const split = props.col ? Math.round(props.options.length / props.col) : 1
  if (props.col) {
    for (let i = 0; i < props.options.length; i += split) {
      groups.push(props.options.slice(i, i + split))
    }
  } else {
    groups.push(props.options)
  }
  return groups
})

function isSelected(option: Option) {
  return selected.value.includes(option.value)
}

function onOption(option: Option) {
  if (props.multiple) {
    const value = (props.modelValue as string[]) || []
    const index = value.indexOf(option.value)
    if (option.exclusive) {
      if (index === -1) {
        // select exclusive option: clear all others
        emit('update:modelValue', [option.value])
      } else {
        // unselect exclusive option
        value.splice(index, 1)
        emit('update:modelValue', value)
      }
      return
    } else {
      // unselect all exclusive options
      props.options
        .filter((opt) => opt.exclusive)
        .forEach((opt) => {
          const i = value.indexOf(opt.value)
          if (i !== -1) value.splice(i, 1)
        })
    }
    // toggle option
    if (index === -1) {
      if (props.max === undefined || value.length < props.max) {
        value.push(option.value)
      }
    } else {
      value.splice(index, 1)
    }
    emit('update:modelValue', value)
  } else {
    emit('update:modelValue', option.value)
  }
}
</script>

<style scoped lang="scss">
// Options wear the same skin as the agreement cards: a bordered surface that
// turns yellow once picked, with a real checkbox or radio rather than an icon.
.choice-option {
  padding: 16px 24px;
  border-radius: $button-border-radius;
  border: 1px solid var(--secondary-border-color);
  background: var(--card-bg);
  transition: border-color 0.2s ease;
}

// Quasar tints any active item with the primary colour; only the border should
// change on selection, so the label keeps the same colour as every other row.
.choice-option--selected {
  border-color: $primary;
  color: inherit;
}

// The row itself handles the click, so the control is display only and must not
// swallow the event and toggle the option a second time.
.choice-option__control {
  pointer-events: none;
}
</style>
