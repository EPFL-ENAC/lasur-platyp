<template>
  <div>
    <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6 q-mb-sm">{{ hint }}</div>
    <div class="q-mt-md">
      <PlaceItem
        :map-id="mapId"
        label-class="text-h6"
        v-model="location"
        :zoom="8"
        class="q-mb-xl"
      />
    </div>
    <div class="row justify-center q-mt-lg" style="max-width: 500px; margin: auto">
      <template v-for="option in modeOptions" :key="option.value">
        <q-btn
          :title="option.label"
          :color="journey.mode === option.value ? 'accent' : 'secondary'"
          size="xl"
          class="on-right on-left q-mb-md"
          @click="onSelect(option)"
        >
          <q-img
            v-if="option.icon?.endsWith('.svg')"
            :src="option.icon"
            style="width: 45px; height: 45px"
            no-spinner
            no-transition
            class="icon-white"
          />
          <q-icon v-else :name="option.icon" color="white" size="lg" />
        </q-btn>
      </template>
    </div>
    <div v-if="canBeCompanyVehicle">
      <ToggleItem
        :label="t('form.journey_pro.is_company_vehicle.label')"
        label-class="text-h5"
        :left-label="t('form.journey_pro.is_company_vehicle.option.private_vehicle')"
        :right-label="t('form.journey_pro.is_company_vehicle.option.company_vehicle')"
        v-model="journey.is_company_vehicle"
        required
        class="q-mt-xl q-mb-xl"
        color="accent"
      />
    </div>
    <div v-if="journey.mode">
      <ToggleItem
        :label="t('form.journey_pro.has_to_carry_heavy_equipment')"
        label-class="text-h5"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="hasHeavyEquipment"
        required
        class="q-mb-lg"
        color="accent"
      />
    </div>
    <div class="row justify-center q-mt-lg">
      <NumberItem
        v-model="journey.days"
        :min="1"
        :max="daysPerMax"
        :step="1"
        :step2="10"
        label-class="text-subtitle1 text-center"
        class="q-pa-md"
      />
      <q-btn
        :label="daysPerLabel"
        :icon="daysPerIcon"
        @click="onToggleDaysPer"
        :color="$q.dark.isActive ? 'primary' : 'secondary'"
        flat
        no-caps
        size="lg"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import PlaceItem from '@/components/form/PlaceItem.vue'
import NumberItem from '@/components/form/NumberItem.vue'
import ToggleItem from '@/components/form/ToggleItem.vue'
import type { Option } from '@/components/form/models'
import type { ProJourney, PlaceLocation } from '@/models'
import { H3Utils } from '@/utils/h3'

interface Props {
  modelValue: ProJourney
  mapId: string
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
const $q = useQuasar()

const journey = computed({
  get: () => props.modelValue,
  set: (val: ProJourney) => emit('update:modelValue', val),
})

const location = computed({
  get: () => journey.value.location,
  set: (val: PlaceLocation | undefined) => {
    journey.value.location = val
    journey.value.hex_id = val ? H3Utils.fromPlaceLocation(val) : undefined
  },
})

const modeOptions = computed<Option[]>(() =>
  [
    { value: 'walking', label: t('form.mode.walking'), icon: 'directions_walk' },
    { value: 'bike', label: t('form.mode.bike'), icon: 'pedal_bike' },
    { value: 'cargo', label: t('form.mode.cargo'), icon: '/icons/cargo_bike.svg' },
    { value: 'pub', label: t('form.mode.pub'), icon: 'directions_bus' },
    { value: 'moto', label: t('form.mode.moto'), icon: 'two_wheeler' },
    { value: 'car', label: t('form.mode.car'), icon: 'directions_car' },
    { value: 'truck', label: t('form.mode.truck'), icon: 'local_shipping' },
    { value: 'train', label: t('form.mode.train'), icon: 'directions_railway' },
    { value: 'boat', label: t('form.mode.boat'), icon: 'directions_boat' },
    { value: 'plane', label: t('form.mode.plane'), icon: 'flight' },
  ].filter((opt) => props.modes.includes(opt.value)),
)

const daysPerLabel = computed(() => {
  switch (journey.value.days_per) {
    case 'week':
      return t('form.journey_pro.days_per_week')
    case 'month':
      return t('form.journey_pro.days_per_month')
    case 'year':
      return t('form.journey_pro.days_per_year')
    default:
      return ''
  }
})

const daysPerIcon = computed(() => {
  switch (journey.value.days_per) {
    case 'week':
      return 'calendar_view_week'
    case 'month':
      return 'calendar_view_month'
    case 'year':
      return 'calendar_month'
    default:
      return ''
  }
})

const daysPerMax = computed(() => {
  switch (journey.value.days_per) {
    case 'week':
      return 7
    case 'month':
      return 31
    case 'year':
      return 365
    default:
      return 365
  }
})

const canBeCompanyVehicle = computed(() =>
  ['bike', 'cargo', 'car', 'truck', 'moto'].includes(journey.value.mode),
)

const hasHeavyEquipment = computed({
  get: () => journey.value.constraints?.includes('heavy') ?? false,
  set: (val: boolean) => {
    const current = new Set(journey.value.constraints || [])
    if (val) {
      current.add('heavy')
    } else {
      current.delete('heavy')
    }
    journey.value.constraints = Array.from(current)
  },
})

function onSelect(option: Option | undefined) {
  if (!option) return
  journey.value.mode = option.value
  if (!canBeCompanyVehicle.value) {
    journey.value.is_company_vehicle = undefined
  }
}

function onToggleDaysPer() {
  journey.value.days_per =
    journey.value.days_per === 'week'
      ? 'month'
      : journey.value.days_per === 'month'
        ? 'year'
        : 'week'
  if (journey.value.days > daysPerMax.value) {
    journey.value.days = daysPerMax.value
  }
}
</script>

<style lang="scss">
.icon-white {
  filter: invert(100%);
}
</style>
