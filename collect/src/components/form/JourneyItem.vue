<template>
  <div>
    <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-sm">{{ hint }}</div>
    <StackItem
      :options="modeOptions"
      v-model="journey.modes"
      :option-label-class="q.screen.lt.sm ? 'text-h6' : 'text-h4'"
    />
    <SliderItem
      :label="t('form.journey.days_per_week')"
      v-model="journey.days"
      :min="1"
      :max="5"
      label-class="text-h5"
      class="q-pa-sm"
    />
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import StackItem from 'src/components/form/StackItem.vue'
import SliderItem from 'src/components/form/SliderItem.vue'
import type { Option } from 'src/components/form/models'
import type { Journey } from 'src/models'

interface Props {
  modelValue: Journey
  label?: string
  hint?: string
  required?: boolean
  max?: number
  col?: number
  labelClass?: string
  optionLabelClass?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])
const q = useQuasar()
const { t } = useI18n()

const journey = computed({
  get: () => props.modelValue,
  set: (val: Journey) => emit('update:modelValue', val),
})

const modeOptions = computed<Option[]>(() => [
  { value: 'walking', label: t('form.mode.walking'), icon: 'directions_walk' },
  {
    value: 'bike',
    label: t('form.mode.bike'),
    icon: 'directions_bike',
    children: [
      { value: 'bike', label: t('form.mode.bike'), icon: 'directions_bike' },
      { value: 'ebike', label: t('form.mode.ebike'), icon: 'electric_bike' },
    ],
  },
  { value: 'pub', label: t('form.mode.pub'), icon: 'directions_bus' },
  { value: 'moto', label: t('form.mode.moto'), icon: 'two_wheeler' },
  {
    value: 'car',
    label: t('form.mode.car'),
    icon: 'directions_car',
    children: [
      { value: 'car', label: t('form.mode.car'), icon: 'directions_car' },
      {
        value: 'carpool',
        label: t('form.mode.carpool'),
        icon: '/icons/directions_carpool.svg',
      },
    ],
  },
  { value: 'train', label: t('form.mode.train'), icon: 'train' },
])
</script>
