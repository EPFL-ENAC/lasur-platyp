<template>
  <div>
    <div class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
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
                  @click="onOption(option)"
                >
                  <q-item-section>
                    <q-item-label class="text-h4" :class="optionLabelClass">{{
                      option.label
                    }}</q-item-label>
                    <q-item-label v-if="option.hint" class="text-h6">
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
import type { Option } from 'src/components/form/models'
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
