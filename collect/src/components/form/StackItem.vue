<template>
  <div>
    <div class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="q-mt-lg">
      <q-list>
        <template v-for="(sel, idx) in selected" :key="idx">
          <q-item
            :id="`#${idx}`"
            draggable="true"
            @dragstart="onDragStart"
            v-ripple
            class="rounded-borders q-mt-md q-mb-md bg-teal-1 text-grey-8"
          >
            <q-item-section>
              <div class="row" :class="optionLabelClass">
                <q-icon name="drag_indicator" color="primary" size="lg" />
                <span class="text-h4 on-right">{{ idx + 1 }} - {{ getOption(sel)?.label }}</span>
              </div>
              <q-item-label v-if="getOption(sel)?.hint" class="text-h6">
                {{ getOption(sel)?.hint }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-btn flat round icon="close" color="primary" @click="onRemove(idx)" />
            </q-item-section>
          </q-item>
        </template>
      </q-list>
      <div
        @dragenter="onDragEnter"
        @dragleave="onDragLeave"
        @dragover="onDragOver"
        @drop="onDrop"
        class="q-pa-md text-h5"
        style="border: dashed 4px"
      >
        <span class="text-grey-6">{{ t('select_or_drag_item') }}</span>
      </div>
      <div class="row justify-center q-mt-lg" v-if="!col">
        <template v-for="option in options" :key="option.value">
          <q-btn
            :id="option.value"
            draggable="true"
            @dragstart="onDragStart"
            round
            :icon="option.icon"
            :title="option.label"
            color="primary"
            size="xl"
            class="on-right on-left"
            @click="onAdd(option)"
          />
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
  max?: number
  col?: number
  labelClass?: string
  optionLabelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const selected = computed(() => {
  return (props.modelValue as string[]) || []
})

function getOption(value: string) {
  return props.options.find((opt) => opt.value === value)
}

function onAdd(option: Option | undefined) {
  if (!option) return
  const value = (props.modelValue as string[]) || []
  if (props.max === undefined || value.length < props.max) {
    value.push(option.value)
  }
  emit('update:modelValue', value)
}

function onRemove(index: number) {
  const value = (props.modelValue as string[]) || []
  value.splice(index, 1)
  emit('update:modelValue', value)
}

function onDragStart(e: DragEvent) {
  if (!e.dataTransfer) return
  e.dataTransfer.setData('text', (e.target as HTMLElement).id)
  e.dataTransfer.dropEffect = 'move'
}

function onDragEnter(e: DragEvent) {
  if (!e.target) return
  // don't drop on other draggables
  const target = e.target as HTMLElement
  if (target.draggable !== true) {
    target.classList.add('drag-enter')
  }
}

function onDragLeave(e: DragEvent) {
  if (!e.target) return
  const target = e.target as HTMLElement
  target.classList.remove('drag-enter')
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
}

function onDrop(e: DragEvent) {
  e.preventDefault()

  // don't drop on other draggables
  const target = e.target as HTMLElement
  if (target.draggable === true) return
  if (!e.dataTransfer) return

  const draggedId = e.dataTransfer.getData('text')
  const draggedEl = document.getElementById(draggedId)

  // check if original parent node
  if (draggedEl && draggedEl.parentNode === target) {
    target.classList.remove('drag-enter')
    return
  }

  // make the exchange
  onAdd(getOption(draggedId))
  target.classList.remove('drag-enter')
}
</script>

<style lang="css">
.drag-enter {
  border: dashed 4px #1976d2 !important;
}
</style>
