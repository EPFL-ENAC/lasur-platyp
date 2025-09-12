<template>
  <div>
    <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-sm">{{ hint }}</div>
    <div class="row justify-center q-mt-lg">
      <template v-for="option in modeOptions" :key="option.value">
        <q-btn
          :icon="option.icon"
          :title="option.label"
          :color="journey.mode === option.value ? 'accent' : 'secondary'"
          size="xl"
          class="on-right on-left q-mb-md"
          @click="onSelect(option)"
        />
      </template>
    </div>
    <NumberItem
      :label="t('form.journey_pro.days_per_month')"
      v-model="journey.days"
      :min="1"
      :max="30"
      :step="1"
      :step2="5"
      label-class="text-subtitle1 text-center"
      class="bg-primary rounded-borders q-pa-md"
    />
  </div>
</template>

<script setup lang="ts">
import NumberItem from 'src/components/form/NumberItem.vue'
import type { Option } from 'src/components/form/models'
import type { ProJourney } from 'src/models'

interface Props {
  modelValue: ProJourney
  label?: string
  hint?: string
  modes: string[]
  required?: boolean
  labelClass?: string
  optionLabelClass?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()

const journey = computed({
  get: () => props.modelValue,
  set: (val: ProJourney) => emit('update:modelValue', val),
})

const modeOptions = computed<Option[]>(() =>
  [
    { value: 'walking', label: t('form.mode.walking'), icon: 'directions_walk' },
    { value: 'bike', label: t('form.mode.bike'), icon: 'directions_bike' },
    { value: 'pub', label: t('form.mode.pub'), icon: 'directions_bus' },
    { value: 'moto', label: t('form.mode.moto'), icon: 'two_wheeler' },
    { value: 'car', label: t('form.mode.car'), icon: 'directions_car' },
    { value: 'train', label: t('form.mode.train'), icon: 'train' },
    { value: 'plane', label: t('form.mode.plane'), icon: 'flight' },
  ].filter((opt) => props.modes.includes(opt.value)),
)

function onSelect(option: Option | undefined) {
  if (!option) return
  journey.value.mode = option.value
}
</script>
