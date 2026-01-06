<template>
  <div>
    <div class="text-bold q-mb-md text-h4">
      {{ t('form.intermodality') }}
    </div>
    <div class="text-h6 q-mb-md">{{ t('form.intermodality_hint') }}</div>
    <template v-for="(journey, idx) in survey.record.data.freq_mod_journeys" :key="idx">
      <q-card class="bg-primary q-mb-md">
        <q-card-section>
          <q-toolbar>
            <div class="on-left text-h6 q-pt-xs">{{ t('form.journey.hint') }}</div>
            <q-space />
            <q-btn
              round
              :title="t('form.journey.remove')"
              icon="close"
              color="accent"
              @click="onRemoveJourney(idx)"
            />
          </q-toolbar>
          <JourneyItem
            v-if="survey.record.data.freq_mod_journeys[idx]"
            v-model="survey.record.data.freq_mod_journeys[idx]"
            :option-label-class="q.screen.lt.sm ? 'text-h5' : 'text-h5'"
          />
        </q-card-section>
      </q-card>
    </template>
    <q-btn icon="add" :label="t('form.journey.add')" color="accent" @click="onAddJourney" />
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import JourneyItem from 'src/components/form/steps/JourneyItem.vue'

const { t } = useI18n()
const survey = useSurvey()
const q = useQuasar()

function onAddJourney() {
  if (!survey.record.data.freq_mod_journeys) {
    survey.record.data.freq_mod_journeys = []
  }
  survey.record.data.freq_mod_journeys.push({
    days: 1,
    modes: [],
  })
}

function onRemoveJourney(idx: number) {
  if (survey.record.data.freq_mod_journeys) {
    survey.record.data.freq_mod_journeys.splice(idx, 1)
  }
}
</script>
