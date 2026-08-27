<template>
  <div>
    <div class="text-bold q-mb-md text-h4">
      {{ t('form.intermodality') }}
    </div>
    <div class="text-h6 q-mb-md">{{ t('form.intermodality_hint') }}</div>

    <template v-for="(journey, idx) in savedJourneysList" :key="idx">
      <q-card flat bordered class="q-mb-md">
        <q-card-section>
          <div class="row items-center justify-between">
            <div class="row items-center q-gutter-sm">
              <template v-for="(mode, mIdx) in journey.modes" :key="mIdx">
                <div class="row items-center journey-chip">
                  <span class="text-h6">{{ getOptionLabel(mode) }}</span>
                </div>
                <q-icon v-if="mIdx < journey.modes.length - 1" name="arrow_forward" color="primary" size="sm" />
              </template>
            </div>
            <q-btn
              round
              dense
              :title="t('form.journey.remove')"
              icon="close"
              color="accent"
              @click="onRemoveJourney(idx)"
            />
          </div>
          <div class="row justify-start q-mt-sm text-h6">
            {{ journey.days }} {{ t('form.journey.days_per_week').toLowerCase() }}
          </div>
        </q-card-section>
      </q-card>
    </template>

    <JourneyStepWizard
      v-if="showWizard"
      @save="onSaveJourney"
      @done="onWizardDone"
    />

    <q-btn
      v-if="!showWizard"
      icon="add"
      unelevated
      rounded
      no-caps
      :label="t('form.journey.add')"
      color="primary"
      size="lg"
      class="full-width q-mt-md"
      :style="{ maxWidth: '300px' }"
      @click="onStartWizard"
    />
  </div>
</template>

<script setup lang="ts">
import JourneyStepWizard from '@/components/form/steps/JourneyStepWizard.vue'
import type { Option } from '@/components/form/models'
import type { Journey } from '@/models'

const { t } = useI18n()
const survey = useSurvey()

const showWizard = ref(true)

const savedJourneysList = computed(() => {
  const journeys = survey.record.data.freq_mod_journeys || []
  return journeys.filter((j: Journey) => j.modes && j.modes.length > 0)
})

const modeOptions = computed<Option[]>(() => [
  { value: 'walking', label: t('form.mode.walking'), icon: 'directions_walk' },
  {
    value: 'bike',
    label: t('form.mode.bike'),
    icon: 'directions_bike',
    children: [
      { value: 'bike', label: t('form.mode.bike'), icon: 'pedal_bike' },
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
  { value: 'train', label: t('form.mode.train'), icon: 'directions_railway' },
  {
    value: 'other',
    label: t('form.mode.other'),
    icon: '/icons/scooter.svg',
    hint: t('form.mode.other_hint'),
  },
])

function getOptionLabel(value: string) {
  for (const opt of modeOptions.value) {
    if (opt.value === value) return opt.label
    if (opt.children) {
      const child = opt.children.find((c) => c.value === value)
      if (child) return child.label
    }
  }
  return value
}

function onSaveJourney(journey: Journey) {
  if (!survey.record.data.freq_mod_journeys) {
    survey.record.data.freq_mod_journeys = []
  }
  survey.record.data.freq_mod_journeys = survey.record.data.freq_mod_journeys.filter(
    (j: Journey) => j.modes && j.modes.length > 0,
  )
  survey.record.data.freq_mod_journeys.push(journey)
}

function onRemoveJourney(idx: number) {
  if (survey.record.data.freq_mod_journeys) {
    survey.record.data.freq_mod_journeys.splice(idx, 1)
  }
}

function onWizardDone() {
  showWizard.value = false
}

function onStartWizard() {
  showWizard.value = true
}
</script>

<style scoped lang="scss">
.journey-chip {
  padding: 4px 8px;
  border: 1px solid var(--q-primary);
  border-radius: 4px;
  background: rgba(var(--q-primary-rgb), 0.05);
}
</style>