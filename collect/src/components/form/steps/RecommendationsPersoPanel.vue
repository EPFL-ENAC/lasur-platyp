<template>
  <div>
    <div class="q-mb-lg">
      <div class="text-h5 text-bold q-mb-md">{{ t(`main_mode.${mainFm}`) }}</div>
    </div>
    <q-card class="bg-primary">
      <q-card-section>
        <div class="text-h5">
          <SectionItem
            v-if="isModeSustainable && !isModeOptions"
            :label="t(`main_mode.sustainable`)"
          />
          <SectionItem
            v-else-if="isModeSustainable && isModeOptions"
            :label="t(`main_mode.sustainable_options`)"
          />
          <SectionItem v-else :label="t(`main_mode.not_sustainable`)" />
        </div>
        <template v-for="(reco, idx) in recoDt" :key="idx">
          <div class="rounded-borders q-mb-md bg-secondary text-white">
            <div class="q-pa-md">
              <q-item-label class="text-body1 text-green-6 text-bold">{{
                t(
                  isModeSustainable && isModeOptions
                    ? 'form.journey.label_option_idx'
                    : 'form.journey.label_idx',
                  { index: idx + 1 },
                )
              }}</q-item-label>
              <q-item-label class="text-h5">{{ t(`reco.${reco}`) }}</q-item-label>
              <BenefitsPanel :reco="reco" class="q-mt-sm" />
              <IsochronesMap
                v-if="showIsochrones(reco)"
                :center="center"
                :reco="reco"
                :height="'400px'"
                :zoom="zoomIsochrones(reco)"
                class="q-mt-sm"
              />
              <q-item-label
                v-if="getActions(idx).length"
                class="text-body1 text-green-2 text-bold q-mt-md"
                >{{
                  t('form.actions', {
                    count: getActions(idx).length,
                    actions: getActions(idx).join('; '),
                  })
                }}</q-item-label
              >
            </div>
          </div>
        </template>
      </q-card-section>
      <q-card-section v-if="globalActions.length" class="q-pt-none">
        <div class="text-body1 text-bold text-green-2">
          {{
            t('form.actions_global', {
              count: globalActions.length,
              actions: globalActions.join('; '),
            })
          }}
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import SectionItem from 'src/components/form/SectionItem.vue'
import BenefitsPanel from 'src/components/form/steps/BenefitsPanel.vue'
import IsochronesMap from 'src/components/form/IsochronesMap.vue'

const { t } = useI18n()
const survey = useSurvey()

// main frequency mode
const mainFm = computed(() => survey.getMainFreqMod())
const isModeSustainable = computed(() => survey.isModeSustainable(survey.getMainFreqMod(false)))
const isModeOptions = computed(() => survey.isModeInRecommendation(mainFm.value))
const recoDt = computed(() =>
  survey.recommendation.reco ? survey.recommendation.reco.reco_dt2 : [],
)
const center = computed(() => {
  const loc = survey.record.data.origin
  return [loc.lon, loc.lat] as [number, number]
})
const mesure_dt1 = computed(() =>
  Array.isArray(survey.recommendation.reco_actions?.mesure_dt1)
    ? survey.recommendation.reco_actions?.mesure_dt1
    : survey.recommendation.reco_actions?.mesure_dt1 === undefined
      ? []
      : [survey.recommendation.reco_actions?.mesure_dt1],
)
const mesure_dt2 = computed(() =>
  Array.isArray(survey.recommendation.reco_actions?.mesure_dt2)
    ? survey.recommendation.reco_actions?.mesure_dt2
    : survey.recommendation.reco_actions?.mesure_dt2 === undefined
      ? []
      : [survey.recommendation.reco_actions?.mesure_dt2],
)
// const hasActions = computed(() => mesure_dt1.value.length > 0 || mesure_dt2.value.length > 0)

const globalActions = computed(() => {
  return survey.recommendation.reco_actions?.mesures_globa?.map(translateAction) || []
})

function showIsochrones(reco: string) {
  return ['marche', 'velo', 'vae', 'cargo', 'train', 'tpu'].includes(reco)
}

function zoomIsochrones(reco: string) {
  return reco === 'marche' ? 11 : 9
}

function getActions(idx: number) {
  if (idx === 0) {
    return mesure_dt1.value.map(translateAction) || []
  } else if (idx === 1) {
    return mesure_dt2.value.map(translateAction) || []
  }
  return []
}

function translateAction(action: string) {
  const label = t(`actions.${action}`)
  if (label === `actions.${action}`) {
    return action
  }
  return label
}
</script>
