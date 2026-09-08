<template>
  <div class="content-stack step-content">
    <div class="question-hint">{{ t('form.intermodality_hint') }}</div>

    <ContentCard v-for="(journey, idx) in journeys" :key="idx">
      <JourneyItem
        :model-value="journey"
        :index="idx + 1"
        :count="journeys.length"
        @remove="onRemoveJourney(idx)"
      />
    </ContentCard>

    <!-- A second journey covers the other days of the week; it only makes
         sense once the current ones are set up. -->
    <q-btn
      flat
      no-caps
      icon="add"
      :label="t('form.journey.add')"
      :disable="!canAddJourney"
      class="picker-option picker-option--dashed picker-option--block"
      @click="onAddJourney"
    />
  </div>
</template>

<script setup lang="ts">
import ContentCard from '@/components/form/ContentCard.vue'
import JourneyItem from '@/components/form/steps/JourneyItem.vue'
import type { Journey } from '@/models'

const { t } = useI18n()
const survey = useSurvey()

function makeJourney(): Journey {
  return { modes: [], days: 1 }
}

// The step always shows at least one card to fill in.
if (!survey.record.data.freq_mod_journeys?.length) {
  survey.record.data.freq_mod_journeys = [makeJourney()]
}

const journeys = computed(() => survey.record.data.freq_mod_journeys)

const canAddJourney = computed(() => journeys.value.every((j) => j.modes && j.modes.length > 0))

function onAddJourney() {
  if (!canAddJourney.value) return
  journeys.value.push(makeJourney())
}

function onRemoveJourney(idx: number) {
  journeys.value.splice(idx, 1)
  if (journeys.value.length === 0) {
    journeys.value.push(makeJourney())
  }
}
</script>
