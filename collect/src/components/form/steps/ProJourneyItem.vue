<template>
  <!-- One rhythm for the whole card: the sections are laid out with a single
  gap rather than each carrying its own margin, so a section that is not shown
  -- the company vehicle question, until a vehicle mode is picked -- leaves no
  gap of its own behind. -->
  <div class="journey-item">
    <div v-if="label || hint">
      <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'question-label'">
        {{ label }}
      </div>
      <div v-if="hint" class="question-hint">{{ hint }}</div>
    </div>
    <PlaceItem :map-id="mapId" label-class="text-h6" v-model="location" :zoom="8" />
    <div class="mode-picker">
      <q-btn
        v-for="option in modeOptions"
        :key="option.value"
        flat
        :title="option.label"
        :aria-label="option.label"
        :aria-pressed="journey.mode === option.value"
        class="picker-option mode-picker__option"
        :class="{ 'picker-option--selected': journey.mode === option.value }"
        @click="onSelect(option)"
      >
        <q-img
          v-if="option.icon?.endsWith('.svg')"
          :src="option.icon"
          class="picker-option__svg"
          no-spinner
          no-transition
        />
        <q-icon v-else :name="option.icon" />
      </q-btn>
    </div>
    <ToggleItem
      v-if="canBeCompanyVehicle"
      :label="t('form.journey_pro.is_company_vehicle.label')"
      label-class="question-label text-bold"
      :true-label="t('form.journey_pro.is_company_vehicle.option.company_vehicle')"
      :false-label="t('form.journey_pro.is_company_vehicle.option.private_vehicle')"
      v-model="journey.is_company_vehicle"
      color="accent"
    />
    <ToggleItem
      v-if="journey.mode"
      :label="t('form.journey_pro.has_to_carry_heavy_equipment')"
      label-class="question-label text-bold"
      :true-label="t('form.yes')"
      :false-label="t('form.no')"
      v-model="hasHeavyEquipment"
      color="accent"
    />
    <div class="journey-frequency">
      <div class="text-bold q-mb-md question-label">
        {{ t('form.journey_pro.frequency.label') }}
      </div>
      <div class="journey-frequency__controls">
        <NumberItem
          class="journey-frequency__count"
          v-model="journey.days"
          :min="1"
          :max="daysPerMax"
          :step="1"
          :unit="t('form.journey_pro.frequency.days')"
        />
        <div class="journey-frequency__per text-hint">
          {{ t('form.journey_pro.frequency.per') }}
        </div>
        <div
          class="journey-frequency__periods"
          role="group"
          :aria-label="t('form.journey_pro.frequency.label')"
        >
          <q-btn
            v-for="option in daysPerOptions"
            :key="option.value"
            flat
            no-caps
            :label="option.label"
            :aria-pressed="journey.days_per === option.value"
            class="picker-option journey-frequency__period"
            :class="{ 'picker-option--selected': journey.days_per === option.value }"
            @click="onSelectDaysPer(option.value)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

// The three periods are laid out as a segmented control rather than cycled
// through by a single button: all the options stay visible, and the current one
// is readable without clicking.
const daysPerOptions = computed<{ value: ProJourney['days_per']; label: string }[]>(() => [
  { value: 'week', label: t('form.journey_pro.frequency.week') },
  { value: 'month', label: t('form.journey_pro.frequency.month') },
  { value: 'year', label: t('form.journey_pro.frequency.year') },
])

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

function onSelectDaysPer(value: ProJourney['days_per']) {
  journey.value.days_per = value
  // A count entered against a longer period can overflow a shorter one.
  if (journey.value.days > daysPerMax.value) {
    journey.value.days = daysPerMax.value
  }
}
</script>

<style scoped lang="scss">
.journey-item {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

// Both pickers in this card -- the mode and the period -- wear the header
// control skin: hairline border, radius-default corner and the small
// skeuomorphic shadow. `flat` keeps them clear of the global button skin, so
// everything they need is declared here.
.q-btn.picker-option {
  height: 48px;
  min-height: 48px;
  padding: 10px 14px !important;
  border: 1px solid var(--secondary-border-color);
  border-radius: 8px;
  background-color: var(--card-bg) !important;
  color: $brand-purple-800;
  box-shadow:
    0 1px 2px 0 rgba(10, 13, 18, 0.05),
    inset 0 -2px 0 0 rgba(10, 13, 18, 0.05);
}

.body--dark .q-btn.picker-option {
  color: $brand-purple-50;
}

.q-btn.picker-option :deep(.q-icon) {
  font-size: 20px;
  color: var(--half-muted-color);
}

// The picked option takes the brand surface, the way a selected option does
// everywhere else in the form.
.q-btn.picker-option--selected,
.body--dark .q-btn.picker-option--selected {
  border-color: $primary;
  background-color: $brand-yellow-400 !important;
  color: $brand-yellow-800;
}

.q-btn.picker-option--selected :deep(.q-icon) {
  color: $brand-yellow-800;
}

.picker-option__svg {
  width: 20px;
  height: 20px;
}

// The source file is a dark grey glyph, which needs flipping only where it sits
// on a dark surface -- so not on the yellow of the selected mode.
.body--dark .picker-option:not(.picker-option--selected) .picker-option__svg {
  filter: invert(100%);
}

// A square cell for the icon-only mode options, wrapping left to right so a
// long list reads as one block instead of a centred row that re-centres on
// every wrap.
.mode-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

// Squarer and larger than the header controls they borrow their skin from:
// these are the choice being made on this card, not a utility in a toolbar.
.q-btn.mode-picker__option {
  width: 64px;
  min-width: 64px;
  height: 64px;
  min-height: 64px;
  padding: 10px !important;
}

.q-btn.mode-picker__option :deep(.q-icon) {
  font-size: 28px;
}

.mode-picker__option .picker-option__svg {
  width: 28px;
  height: 28px;
}

// Count and period read as one sentence -- "12 days per year" -- so they sit on
// a single line when there is room for it.
.journey-frequency__controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.journey-frequency__periods {
  display: flex;
  gap: 8px;
}

// The period sits beside the count, so it takes the height of the number field
// rather than the 48px of the mode cells.
.q-btn.journey-frequency__period {
  height: 40px;
  min-height: 40px;
}

// Below `sm` the sentence breaks into stacked lines and the periods spread over
// the full width, which keeps each of them a comfortable tap target.
@media (max-width: 599px) {
  .journey-frequency__controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .journey-frequency__count :deep(.row) {
    justify-content: center;
  }

  .journey-frequency__per {
    text-align: center;
  }

  .journey-frequency__periods .q-btn.journey-frequency__period {
    flex: 1 1 0;
    height: 56px;
    min-height: 56px;
    padding-left: 0 !important;
    padding-right: 0 !important;
  }
}
</style>
