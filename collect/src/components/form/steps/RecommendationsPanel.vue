<template>
  <div>
    <div class="row justify-end q-mb-md">
      <q-btn color="primary" icon="print" :label="t('print')" @click="openPrintPreview" />
    </div>

    <div class="q-mb-lg">
      <div class="text-h5 text-bold q-mb-md">{{ t(`form.recommendations_preamble`) }}</div>
    </div>

    <RecommendationsPersoPanel
      :main-fm="mainFm"
      :is-mode-sustainable="isModeSustainable"
      :is-mode-options="isModeOptions"
      :reco-inter="recoInter"
      :bravo="bravo"
      :center="center"
      :mesure-dt1="mesureDt1"
      :mesure-dt2="mesureDt2"
      :global-actions="globalActionsPerso"
      :benefits-expanded="false"
    />
    <RecommendationsProPanel
      class="q-mt-xl"
      :reco-pros="recoPros"
      :pro-journey-locations="proJourneyLocations"
      :mesure-pro="mesurePro"
      :global-actions="globalActionsPro"
      :benefits-expanded="false"
    />
  </div>
</template>

<script setup lang="ts">
import RecommendationsPersoPanel from 'src/components/form/steps/RecommendationsPersoPanel.vue'
import RecommendationsProPanel from 'src/components/form/steps/RecommendationsProPanel.vue'
import type { RecommendationsPreviewData } from 'src/models'
import { resolveLocation } from 'src/utils/boundaries'

const { t } = useI18n()
const survey = useSurvey()
const router = useRouter()

const mainFm = computed(() => survey.getMainFreqMod())
const isModeSustainable = computed(() => survey.isModeSustainable(survey.getMainFreqMod(false)))
const isModeOptions = computed(() => survey.isModeInRecommendation(mainFm.value))

const recoInter = computed(() => survey.recommendation.reco?.reco_inter || [])
const bravo = computed(() => survey.recommendation.reco?.bravo || [])

const center = computed(() => {
  const loc = survey.record.data.origin
  if (!loc?.lon || !loc?.lat) return null
  return [loc.lon, loc.lat] as [number, number]
})

function normalizeArray(value?: string | string[]) {
  if (Array.isArray(value)) return value
  if (value === undefined || value === null) return []
  return [value]
}

const mesureDt1 = computed(() => normalizeArray(survey.recommendation.reco_actions?.mesure_dt1))

const mesureDt2 = computed(() => normalizeArray(survey.recommendation.reco_actions?.mesure_dt2))

const globalActionsPerso = computed(() => survey.recommendation.reco_actions?.mesures_globa || [])

const recoPros = computed(() => survey.recommendation.reco_pro?.reco_pros || [])

const proJourneyLocations = computed(() =>
  (survey.record.data.freq_mod_pro_journeys || []).map((j) =>
    resolveLocation(j.location, j.hex_id),
  ),
)

const mesurePro = computed(() => survey.recommendation.reco_actions?.mesure_pro || [])

const globalActionsPro = computed(() => survey.recommendation.reco_actions?.mesures_pro_globa || [])

const previewData = computed<RecommendationsPreviewData>(() => ({
  perso: {
    mainFm: mainFm.value,
    isModeSustainable: isModeSustainable.value,
    isModeOptions: isModeOptions.value,
    recoInter: recoInter.value,
    bravo: bravo.value,
    center: center.value,
    mesureDt1: mesureDt1.value,
    mesureDt2: mesureDt2.value,
    globalActions: globalActionsPerso.value,
  },
  pro: {
    recoPros: recoPros.value,
    proJourneyLocations: proJourneyLocations.value,
    mesurePro: mesurePro.value,
    globalActions: globalActionsPro.value,
  },
}))

function openPrintPreview() {
  const payload = JSON.stringify(previewData.value)

  const routeData = router.resolve({
    path: '/print-reco',
    query: {
      data: encodeURIComponent(payload),
    },
  })

  window.open(routeData.href, '_blank')
}
</script>
