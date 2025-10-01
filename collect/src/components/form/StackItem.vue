<template>
  <div>
    <div class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-md">{{ hint }}</div>
    <div class="q-mt-lg">
      <q-list>
        <template v-for="(sel, idx) in selected" :key="idx">
          <q-item
            @dragenter="onDragEnter"
            @dragleave="onDragLeave"
            @dragover="onDragOver"
            @drop="onDropInsert($event, idx)"
            dropzone
            :id="`${itemPrefix}${idx}`"
            draggable="true"
            @dragstart="onDragStart"
            v-ripple
            class="rounded-borders q-mt-md q-mb-md bg-teal-1 text-grey-8"
            style="cursor: move"
          >
            <q-item-section v-if="q.screen.gt.xs" avatar>
              <q-icon name="drag_indicator" color="primary" size="lg" />
            </q-item-section>
            <q-item-section>
              <div class="row" :class="optionLabelClass">
                <span class="on-right"
                  >{{ `${withPosition ? idx + 1 + ' - ' : ''}` }}{{ getOption(sel)?.label }}</span
                >
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
      <div class="row justify-center q-mt-lg">
        <template v-for="option in options" :key="option.value">
          <q-btn
            v-if="!option.children || option.children.length === 0"
            :id="option.value"
            draggable="true"
            @dragstart="onDragStart"
            :icon="option.icon"
            :title="option.label"
            color="secondary"
            size="xl"
            class="on-right on-left q-mb-md"
            @click="onAdd(option)"
          />
          <q-btn
            v-else
            :id="option.value"
            :icon="option.icon"
            :title="option.label"
            color="secondary"
            size="xl"
            class="on-right on-left q-mb-md"
          >
            <q-menu auto-close>
              <q-list>
                <q-item
                  v-for="child in option.children"
                  :key="child.value"
                  clickable
                  v-ripple
                  @click="onAdd(child)"
                >
                  <q-item-section avatar>
                    <q-img
                      v-if="child.icon?.endsWith('.svg')"
                      :src="child.icon"
                      style="width: 38px; height: 38px"
                      class="icon-primary"
                    />
                    <q-icon v-else :name="child.icon" color="primary" size="lg" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ child.label }}</q-item-label>
                    <q-item-label v-if="child.hint" class="text-h6">{{ child.hint }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import type { Option } from 'src/components/form/models'
interface Props {
  modelValue: string | string[] | undefined
  label?: string | undefined
  hint?: string | undefined
  options: Option[]
  required?: boolean
  max?: number
  withPosition?: number
  labelClass?: string
  optionLabelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const q = useQuasar()

const itemPrefix = 'item-'

const selected = computed(() => {
  return (props.modelValue as string[]) || []
})

function getOption(value: string) {
  // find in options or in options children
  for (const opt of props.options) {
    if (opt.value === value) return opt
    if (opt.children) {
      const child = opt.children.find((child) => child.value === value)
      if (child) return child
    }
  }
  return undefined
}

function onAdd(option: Option | undefined) {
  if (!option) return
  const value = (props.modelValue as string[]) || []
  if (props.max === undefined || value.length < props.max) {
    value.push(option.value)
  }
  emit('update:modelValue', value)
}

function onInsert(option: Option | undefined, index: number) {
  if (!option) return
  const value = (props.modelValue as string[]) || []
  if (props.max === undefined || value.length < props.max) {
    value.splice(index, 0, option.value)
  }
  emit('update:modelValue', value)
}

function onRemove(index: number) {
  const value = (props.modelValue as string[]) || []
  value.splice(index, 1)
  emit('update:modelValue', value)
}

function onMove(position: number, index: number) {
  if (position === index) return
  const value = (props.modelValue as string[]) || []
  const movedValue = value[position]
  if (!movedValue) return
  if (position > index) {
    value.splice(index, 0, movedValue)
    value.splice(position + 1, 1)
  } else {
    value.splice(position, 1)
    value.splice(index - 1, 0, movedValue)
  }
  emit('update:modelValue', value)
}

function onDragStart(e: DragEvent) {
  if (!e.dataTransfer) return
  e.dataTransfer.setData('text', (e.target as HTMLElement).id)
  e.dataTransfer.dropEffect = 'move'
}

function onDragEnter(e: DragEvent) {
  e.preventDefault()
  if (!e.target) return
  // don't drop on other draggables
  const target = e.target as HTMLElement
  if (target.hasAttribute('dropzone')) {
    target.classList.add('drag-enter')
  } else {
    // get parent element with dropzone attribute
    let parent = target.parentElement
    while (parent && !parent.hasAttribute('dropzone')) {
      parent = parent.parentElement
    }
    if (parent) {
      parent.classList.add('drag-enter')
    }
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

function onDropInsert(e: DragEvent, index: number) {
  e.preventDefault()

  const target = e.target as HTMLElement
  if (!e.dataTransfer) return

  const draggedId = e.dataTransfer.getData('text')
  const draggedEl = document.getElementById(draggedId)

  // check if original parent node
  if (draggedEl && draggedEl.parentNode === target) {
    target.classList.remove('drag-enter')
    return
  }

  // make the exchange
  if (draggedId.startsWith(itemPrefix)) {
    // this is an item move
    const position = Number(draggedId.replace(itemPrefix, ''))
    onMove(position, index)
  } else {
    // this is an insert
    onInsert(getOption(draggedId), index)
  }
  target.classList.remove('drag-enter')
  // remove from dropzone parents
  let parent = target.parentElement
  while (parent && !parent.hasAttribute('dropzone')) {
    parent = parent.parentElement
  }
  if (parent) {
    parent.classList.remove('drag-enter')
  }
}
</script>

<style lang="scss">
.drop-zone {
  border: dashed 4px #ccc;
}
.drag-enter {
  // border: dashed 4px $secondary !important;
}
.icon-primary {
  filter: invert(26%) sepia(77%) saturate(3932%) hue-rotate(140deg) brightness(102%) contrast(99%);
}
</style>
