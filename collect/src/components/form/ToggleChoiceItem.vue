<template>
  <div>
    <div class="text-h4 text-bold q-mb-md">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="q-mt-lg">
      <div :class="col ? 'row q-col-gutter-md' : ''">
        <template v-for="(group, idx) in optionGroups" :key="idx">
          <div :class="col ? `col-${12 / col}` : ''">
            <q-list>
              <template v-for="option in group" :key="option.value">
                <q-item
                  :active="isSelected(option)"
                  active-class="bg-teal-1 text-grey-8"
                  v-ripple
                  clickable
                  class="rounded-borders q-mb-md bg-primary text-green-3"
                >
                  <q-item-section
                    @click="onOptionValue(option, option.trueValue)"
                    class="rounded-borders"
                  >
                    <q-item-label
                      class="text-h4"
                      :class="`${optionLabelClass} ${isSelectedValue(option.trueValue) ? 'text-bold' : ''}`"
                    >
                      {{ option.trueLabel }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section @click="onOptionValue(option, option.falseValue)">
                    <q-item-label
                      class="text-h4"
                      :class="`${optionLabelClass} ${isSelectedValue(option.falseValue) ? 'text-bold rounded-borders' : ''}`"
                    >
                      {{ option.falseLabel }}
                    </q-item-label>
                    <q-item-label v-if="option.hint" caption>
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
import type { ToggleOption } from 'src/components/form/models'
interface Props {
  modelValue: string | string[] | undefined
  label?: string
  hint?: string
  options: ToggleOption[]
  required?: boolean
  max?: number
  col?: number
  optionLabelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selected = computed(() => {
  return (props.modelValue as string[]) || []
})

const optionGroups = computed(() => {
  const groups: ToggleOption[][] = []
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

function isSelected(option: ToggleOption) {
  return selected.value.includes(option.trueValue) || selected.value.includes(option.falseValue)
}

function isSelectedValue(optionValue: string) {
  return selected.value.includes(optionValue)
}

function onOptionValue(option: ToggleOption, optionValue: string) {
  let value = props.modelValue as string[]
  const index = value.indexOf(optionValue)
  if (index === -1) {
    value = value.filter((v) => v !== option.trueValue && v !== option.falseValue)
    if (props.max === undefined || value.length < props.max) {
      value.push(optionValue)
    }
  } else {
    value.splice(index, 1)
  }
  emit('update:modelValue', value)
}
</script>
