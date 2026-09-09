<template>
  <div class="journey-item">
    <div class="journey-item__header">
      <div class="journey-item__heading">
        <span class="journey-item__title">{{ title }}</span>
        <span class="journey-item__summary text-hint">{{ summary }}</span>
      </div>
      <q-btn
        v-if="count > 1"
        no-caps
        :label="t('form.journey.remove')"
        class="journey-item__remove"
        @click="emit('remove')"
      />
    </div>

    <div>
      <div class="question-label text-bold q-mb-sm">{{ t('form.journey.modes_label') }}</div>


      <div v-if="modes.length > 0 || showAddMode" class="journey-chain q-mb-sm">
        <template v-for="(mode, idx) in modes" :key="idx">
          <q-btn
            flat
            no-caps
            :label="modeLabel(mode)"
            icon-right="close"
            :title="t('form.journey.remove_mode', { mode: modeLabel(mode) })"
            :aria-label="t('form.journey.remove_mode', { mode: modeLabel(mode) })"
            class="picker-option picker-option--outlined journey-chain__step"
            @click="onRemoveMode(idx)"
          />
          <q-icon
            v-if="idx < modes.length - 1"
            name="arrow_forward"
            color="primary"
            class="journey-chain__arrow"
          />
        </template>
        <q-btn
          v-if="showAddMode"
          flat
          no-caps
          icon="add"
          :label="t('form.journey.add_mode')"
          class="picker-option picker-option--dashed"
          @click="pickerOpen = true"
        />
      </div>

      <div class="question-hint">{{ modesHint }}</div>

      <div v-if="pickerOpen" class="journey-modes q-mt-sm">
        <!-- A mode that comes in an electric version is one option with a
        switch, not two options: the switch swaps the value the option adds,
        so the label and icon always show exactly what a tap will add. The
        switch is a sibling of the button, not a child, so flipping it never
        counts as picking the mode. -->
        <div
          v-for="option in modeOptions"
          :key="option.base"
          class="journey-modes__cell"
          :class="{ 'journey-modes__cell--switchable': option.variant }"
        >
          <q-btn
            flat
            no-caps
            align="left"
            :title="option.hint ?? option.label"
            :aria-label="option.label"
            class="picker-option journey-modes__option"
            :class="{ 'picker-option--outlined': option.electric }"
            @click="onSelectMode(option.value)"
          >
            <span
              v-if="option.isSvg"
              class="picker-option__svg"
              :style="{ '--picker-option-icon': `url('${option.icon}')` }"
            />
            <q-icon v-else :name="option.icon" />
            <span class="journey-modes__label">{{ option.label }}</span>
          </q-btn>
          <q-toggle
            v-if="option.variant"
            :model-value="option.electric"
            icon="bolt"
            size="sm"
            color="primary"
            :title="t('form.journey.electric', { mode: option.baseLabel })"
            :aria-label="t('form.journey.electric', { mode: option.baseLabel })"
            class="journey-modes__electric"
            @update:model-value="setElectric(option.base, $event)"
          />
        </div>
      </div>
    </div>

    <q-separator />

    <div>
      <div class="question-label text-bold q-mb-sm">{{ t('form.journey.frequency_label') }}</div>
      <div class="journey-frequency">
        <NumberItem
          :model-value="journey.days"
          :min="MIN_DAYS"
          :max="MAX_DAYS"
          :unit="t('form.journey.days')"
          @update:model-value="(val) => (journey = { ...journey, days: val })"
        />
        <span class="text-hint">{{ t('form.journey.per_week') }}</span>
      </div>
      <div class="question-hint q-mt-xs">{{ t('form.journey.frequency_hint') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import NumberItem from '@/components/form/NumberItem.vue'
import type { Journey } from '@/models'
import { getModeIcon } from '@/utils/modeicons'


// The modes offered by the picker, and for each one that exists in an electric
// version, the value stored when its switch is on. Only pairs the backend
// typology and the stats know as distinct values belong here.
const BASE_MODES = ['walking', 'bike', 'pub', 'train', 'car', 'carpool', 'moto', 'other']
const ELECTRIC_VARIANTS: Record<string, string> = { bike: 'ebike' }
const MAX_MODES = 5
const MIN_DAYS = 1
const MAX_DAYS = 5

interface Props {
  modelValue: Journey
  index: number
  count: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [journey: Journey]
  remove: []
}>()

const { t } = useI18n()

const journey = computed({
  get: () => props.modelValue,
  set: (val: Journey) => emit('update:modelValue', val),
})

const modes = computed(() => journey.value.modes ?? [])

// A journey with nothing in it opens straight onto the picker; afterwards the
// picker only appears on request, so the card stays compact once set up.
const pickerOpen = ref(modes.value.length === 0)

watch(
  () => modes.value.length,
  (length) => {
    if (length === 0) pickerOpen.value = true
  },
)

const canAddMode = computed(() => modes.value.length < MAX_MODES)
const showAddMode = computed(() => canAddMode.value && !pickerOpen.value)

// Which switchable modes currently have their electric version on. Starts
// from whatever the journey already holds, so reopening the picker on an
// e-bike journey shows the switch where the traveller left it.
const electric = reactive<Record<string, boolean>>(
  Object.fromEntries(
    Object.entries(ELECTRIC_VARIANTS).map(([base, variant]) => [base, modes.value.includes(variant)]),
  ),
)

watch(
  () => props.modelValue,
  (val) => {
    for (const [base, variant] of Object.entries(ELECTRIC_VARIANTS)) {
      electric[base] = (val.modes ?? []).includes(variant)
    }
    pickerOpen.value = (val.modes?.length ?? 0) === 0
  },
  { deep: false },
)

function setElectric(base: string, on: boolean) {
  electric[base] = on
}

const modeOptions = computed(() =>
  BASE_MODES.map((base) => {
    const variant = ELECTRIC_VARIANTS[base]
    const isElectric = variant !== undefined && electric[base] === true
    const value = isElectric && variant ? variant : base
    const modeIcon = getModeIcon(value)
    return {
      base,
      value,
      variant,
      electric: isElectric,
      baseLabel: modeLabel(base),
      label: modeLabel(value),
      hint: value === 'other' ? t('form.mode.other_hint') : undefined,
      icon: modeIcon?.icon ?? 'commute',
      isSvg: modeIcon?.isSvg ?? false,
    }
  }),
)

const title = computed(() =>
  props.count > 1 ? t('form.journey.title_idx', { index: props.index }) : t('form.journey.title'),
)

const summary = computed(() =>
  modes.value.length > 0
    ? modes.value.map(modeLabel).join(' → ')
    : t('form.journey.not_set_up'),
)

const modesHint = computed(() =>
  modes.value.length > 0
    ? t('form.journey.modes_hint', { max: MAX_MODES })
    : t('form.journey.modes_hint_empty'),
)

function modeLabel(mode: string): string {
  return t(`form.mode.${mode}`)
}

function onSelectMode(value: string) {
  if (!canAddMode.value) return
  if (!journey.value.modes) journey.value.modes = []
  journey.value.modes.push(value)
  pickerOpen.value = false
}

function onRemoveMode(idx: number) {
  journey.value.modes.splice(idx, 1)
}
</script>

<style scoped lang="scss">
.journey-item {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.journey-item__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

// Title and summary sit on one baseline and wrap as a unit when the summary
// gets long -- "Walking → Train → Bicycle" -- rather than pushing the delete
// button off the row.
.journey-item__heading {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 10px;
  min-width: 0;
}

.journey-item__title {
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.5rem;
}

.journey-item__remove {
  flex-shrink: 0;
}

.journey-chain {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.journey-chain .q-btn.picker-option {
  height: 40px;
  min-height: 40px;
  padding: 6px 12px !important;
}

.journey-chain__arrow {
  font-size: 18px;
}


.journey-modes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
}

.journey-modes__cell {
  position: relative;
  display: flex;
}

.q-btn.journey-modes__option {
  flex: 1;
  height: auto;
  min-height: 44px;
  padding: 6px 12px !important;
  text-align: left;
}

// Room for the switch, which sits over the right edge of the option.
.journey-modes__cell--switchable .q-btn.journey-modes__option {
  padding-right: 64px !important;
}

.journey-modes__electric {
  position: absolute;
  top: 50%;
  right: 6px;
  transform: translateY(-50%);
}

.q-btn.journey-modes__option :deep(.q-btn__content) {
  flex-wrap: nowrap;
  justify-content: flex-start;
  gap: 10px;
}

.journey-modes__label {
  white-space: normal;
  line-height: 1.25rem;
}

// Count and unit read as one sentence -- "4 days per week".
.journey-frequency {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

// Under a thumb the chips and the add slot take the same 56px as every other
// control on a phone; the header stacks so the delete button keeps its width.
@media (max-width: 599px) {
  .journey-item__header {
    flex-direction: column;
    align-items: stretch;
  }

  .journey-chain .q-btn.picker-option,
  .q-btn.journey-modes__option {
    height: 56px;
    min-height: 56px;
  }

  .journey-modes {
    grid-template-columns: 1fr;
  }
}
</style>
