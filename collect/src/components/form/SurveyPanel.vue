<template>
  <div v-if="survey.record" v-touch-swipe.mouse.left.right="handleSwipe">
    <!--pre>{{ survey.step }} - {{ survey.stepName }}</pre-->
    <div v-if="survey.stepName === 'agreement'">
      <div>
        <SectionItem
          :label="t('form.agreement')"
          label-class="text-h4 text-bold"
          :hint="t('form.agreement_hint')"
          class="q-mb-lg"
        />
        <AgreementPanel />
      </div>
    </div>
    <div v-if="survey.stepName === 'age_class'">
      <AgePanel />
    </div>
    <div v-if="survey.stepName === 'employment'">
      <EmploymentPanel />
    </div>
    <div v-if="survey.stepName === 'workplace'">
      <div class="text-h4 text-bold">{{ t('form.workplace') }}</div>
      <WorkplacePanel />
    </div>
    <div v-if="survey.stepName === 'origin_places'">
      <OriginPlacePanel />
    </div>
    <div v-if="survey.stepName === 'travel_time'">
      <TravelTimePanel />
    </div>
    <div v-if="survey.stepName === 'constraints'">
      <ConstraintsPanel />
    </div>
    <div v-if="survey.stepName === 'equipments'">
      <EquipmentsPanel />
    </div>
    <div v-if="survey.stepName === 'intermodality'">
      <JourneysPanel />
    </div>
    <div v-if="survey.stepName === 'travel_pro'">
      <TravelProPanel />
    </div>
    <div v-if="survey.stepName === 'freq_mod_pro'">
      <ProJourneysPanel
        v-model="survey.record.data.freq_mod_pro_journeys"
        :modes="[
          'walking',
          'bike',
          'cargo',
          'pub',
          'moto',
          'car',
          'truck',
          'train',
          'boat',
          'plane',
        ]"
      />
    </div>
    <div v-if="survey.stepName === 'importance'">
      <div>
        <SectionItem
          :label="t('form.importance')"
          label-class="text-bold text-h4"
          :hint="t('form.importance_hint')"
          class="q-mb-lg"
        />
        <ImportancePanel />
      </div>
    </div>
    <div v-if="survey.stepName === 'needs'">
      <div>
        <SectionItem
          :label="t('form.needs')"
          label-class="text-bold text-h4"
          :hint="t('form.needs_hint')"
          class="q-mb-lg"
        />
        <NeedsPanel />
      </div>
    </div>
    <div v-if="survey.stepName === 'recommendations'">
      <div class="row justify-end q-mb-md">
        <q-btn color="primary" icon="print" :label="t('print')" @click="openPrintPreview" />
      </div>
      <div class="q-mb-lg">
        <div class="text-h5 text-bold q-mb-md">{{ t(`form.recommendations_header`) }}</div>
        <div>{{ t(`form.recommendations_preamble`) }}</div>
      </div>
      <RecommendationsPersoPanel
        :journeys="freqModJourneys"
        :reco-inter="recoInter"
        :bravo="bravo"
        :center="center"
        :mesure-dt1="mesureDt1"
        :mesure-dt2="mesureDt2"
        :global-actions="globalActionsPerso"
        :company-name="collector.info.company_name"
        :benefits-expanded="false"
      />
      <InfoPanel class="q-mt-lg" />
    </div>
    <div v-if="survey.stepName === 'recommendations_pro' && recoPros.length">
      <div class="q-mb-lg">
        <div class="text-h5 text-bold q-mb-sm">{{ t(`form.recommendations_pro_header`) }}</div>
        <div>{{ t(`form.recommendations_pro_preamble`) }}</div>
      </div>
      <RecommendationsProPanel
        :pro-journeys="freqModProJourneys"
        :reco-pros="recoPros"
        :pro-journey-locations="proJourneyLocations"
        :mesure-pro="mesurePro"
        :global-actions="globalActionsPro"
        :company-name="collector.info.company_name"
        :benefits-expanded="false"
      />
      <InfoPanel class="q-mt-lg" />
    </div>
    <div v-if="survey.stepName === 'change'">
      <ChangePanel :idx="survey.currentChangeIndex" @update:modelValue="onSave" />
    </div>
    <div v-if="survey.stepName === 'email'">
      <EmailPanel v-model="plainEmail" />
    </div>
    <div v-if="survey.stepName === 'comments'">
      <SectionItem
        :label="t('form.comments')"
        label-class="text-h4 text-bold q-mb-md"
        class="q-mb-lg"
      />
      <q-input
        v-model="survey.record.data.comments"
        type="textarea"
        class="q-mb-lg text-h6"
        bg-color="field"
        outlined
        rounded
      />
      <InfoPanel />
    </div>
    <div v-if="survey.stepName === 'final'">
      <FinalPanel />
    </div>
    <div class="row justify-center q-mt-xl">
      <q-btn
        rounded
        v-if="survey.isAfterStep('agreement') && survey.stepName !== 'final'"
        color="accent"
        icon="keyboard_arrow_left"
        size="lg"
        :title="t('previous')"
        @click="prevStep"
        class="q-mr-md"
      />
      <q-btn
        rounded
        v-if="survey.isBeforeStep('comments')"
        color="accent"
        icon="keyboard_arrow_right"
        size="lg"
        :title="t('next')"
        @click="nextStep"
        class="q-ml-md"
      />
      <q-btn
        rounded
        v-if="survey.stepName === 'comments'"
        color="accent"
        :label="t('finish')"
        icon-right="send"
        size="lg"
        @click="onSendComments"
        class="q-ml-md"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import SectionItem from '@/components/form/SectionItem.vue'
import AgreementPanel from '@/components/form/steps/AgreementPanel.vue'
import AgePanel from '@/components/form/steps/AgePanel.vue'
import EmploymentPanel from '@/components/form/steps/EmploymentPanel.vue'
import OriginPlacePanel from '@/components/form/steps/OriginPlacePanel.vue'
import WorkplacePanel from '@/components/form/steps/WorkplacePanel.vue'
import EquipmentsPanel from '@/components/form/steps/EquipmentsPanel.vue'
import ConstraintsPanel from '@/components/form/steps/ConstraintsPanel.vue'
import JourneysPanel from '@/components/form/steps/JourneysPanel.vue'
import ProJourneysPanel from '@/components/form/steps/ProJourneysPanel.vue'
import TravelTimePanel from '@/components/form/steps/TravelTimePanel.vue'
import TravelProPanel from '@/components/form/steps/TravelProPanel.vue'
import ImportancePanel from '@/components/form/steps/ImportancePanel.vue'
import NeedsPanel from '@/components/form/steps/NeedsPanel.vue'
import RecommendationsPersoPanel from '@/components/form/steps/RecommendationsPersoPanel.vue'
import RecommendationsProPanel from '@/components/form/steps/RecommendationsProPanel.vue'
import ChangePanel from '@/components/form/steps/ChangePanel.vue'
import EmailPanel from './steps/EmailPanel.vue'
import InfoPanel from '@/components/form/steps/InfoPanel.vue'
import FinalPanel from '@/components/form/steps/FinalPanel.vue'
import type { Journey, ProJourney, RecommendationsPreviewData } from '@/models'
import { notifyError } from '@/utils/notify'
import { resolveLocation } from '@/utils/boundaries'

const { t, locale } = useI18n()
const survey = useSurvey()
const collector = useCollector()
const router = useRouter()

const plainEmail = ref('')

const mainFm = computed(() => survey.getMainFreqMod())
const isModeSustainable = computed(() => survey.isModeSustainable(survey.getMainFreqMod(false)))
const isModeOptions = computed(() => survey.isModeInRecommendation(mainFm.value))
const freqModJourneys = computed<Journey[]>(() =>
  survey.record.data?.freq_mod_journeys || [],
)
const freqModProJourneys = computed<ProJourney[]>(() =>
  survey.record.data?.freq_mod_pro_journeys || [],
)

const recoInter = computed(() => survey.recommendation.reco?.reco_inter || [])
const recoPros = computed(() => survey.recommendation.reco_pro?.reco_pros || [])
const bravo = computed(() => survey.recommendation.reco?.bravo || [])
const center = computed(() => {
  const loc = survey.record.data.origin
  if (!loc?.lon || !loc?.lat) return null
  return [loc.lon, loc.lat] as [number, number]
})

const mesureDt1 = computed(() =>
  (function (v) {
    if (Array.isArray(v)) return v
    if (v === undefined || v === null) return []
    return [v]
  })(survey.recommendation.reco_actions?.mesure_dt1),
)
const mesureDt2 = computed(() =>
  (function (v) {
    if (Array.isArray(v)) return v
    if (v === undefined || v === null) return []
    return [v]
  })(survey.recommendation.reco_actions?.mesure_dt2),
)
const globalActionsPerso = computed(() => survey.recommendation.reco_actions?.mesures_globa || [])
const mesurePro = computed<string[][]>(() => {
  const ra = survey.recommendation.reco_actions
  const recos = recoPros.value
  if (!ra || !recos.length) return []

  const v2Fallback = (r: string): string[] => {
    const lookup: Record<string, string[] | undefined> = {
      elec: ra.mesures_pro_elec,
      elec_truck: ra.mesures_pro_elec,
      velo: ra.mesures_pro_velo,
      vae: ra.mesures_pro_velo,
      bike: ra.mesures_pro_velo,
      cargo: ra.mesures_pro_velo,
      tpu: ra.mesures_pro_tpu,
      pub: ra.mesures_pro_tpu,
      train: ra.mesures_pro_train,
    }
    return lookup[r] || []
  }

  // V1: use mesure_pro from API if available, normalize type issues
  const raw = ra.mesure_pro
  if (raw && raw.length > 0) {
    return recos.map((r, i) => {
      const entry = raw[i]
      if (Array.isArray(entry) && entry.length > 0) return entry
      if (typeof entry === 'string' && entry.length > 0) return [entry]
      return v2Fallback(r)
    })
  }

  // V2: derive from mesures_pro_* via mode mapping
  return recos.map((r) => v2Fallback(r))
})
const globalActionsPro = computed(() => survey.recommendation.reco_actions?.mesures_pro_globa || [])

const proJourneyLocations = computed(() =>
  (survey.record.data.freq_mod_pro_journeys || []).map((j) =>
    resolveLocation(j.location, j.hex_id),
  ),
)

const previewData = computed<RecommendationsPreviewData>(() => ({
  perso: {
    mainFm: mainFm.value,
    isModeSustainable: isModeSustainable.value,
    isModeOptions: isModeOptions.value,
    journeys: freqModJourneys.value,
    recoInter: recoInter.value,
    bravo: bravo.value,
    center: center.value,
    mesureDt1: mesureDt1.value,
    mesureDt2: mesureDt2.value,
    globalActions: globalActionsPerso.value,
    companyName: collector.info.company_name,
  },
  pro: {
    proJourneys: freqModProJourneys.value,
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
      locale: locale.value,
    },
  })
  window.open(routeData.href, '_blank')
}

onMounted(() => {
  if (survey.tokenOrSlug) {
    void collector.loadInfo(survey.tokenOrSlug)
  }
})

function nextStep() {
  if (survey.stepName === 'agreement') {
    if (!survey.record.data.terms_conditions) {
      notifyError(t('form.error.terms_conditions'))
      return
    }
    if (!survey.record.data.confidentiality) {
      notifyError(t('form.error.confidentiality'))
      return
    }
  }
  if (survey.stepName === 'employment') {
    if (
      survey.record.data.company_vehicle === undefined ||
      survey.record.data.company_vehicle === null
    ) {
      notifyError(t('form.error.company_vehicle'))
      return
    }
  }
  if (survey.stepName === 'workplace') {
    if (
      survey.record.data.workplace?.lat === undefined ||
      survey.record.data.workplace?.lat === 0
    ) {
      notifyError(t('form.error.workplace'))
      return
    }
  }
if (survey.stepName === 'origin_places') {
    if (survey.record.data.origin?.lat === undefined || survey.record.data.origin?.lat === 0) {
        notifyError(t('form.error.origin'))
        return
      }
    }
    if (survey.stepName === 'travel_time') {
      if (
        survey.record.data.travel_time === undefined ||
        survey.record.data.travel_time <= 0
      ) {
        notifyError(t('form.error.travel_time'))
        return
      }
    }
  if (survey.stepName === 'intermodality') {
    const journeys = survey.record.data.freq_mod_journeys || []
    if (journeys.length === 0) {
      notifyError(t('form.error.journey_mode'))
      return
    }
    for (const journey of journeys) {
      if (journey.modes === undefined || journey.modes.length === 0) {
        notifyError(t('form.error.journey_mode'))
        return
      }
    }
  }
  if (survey.stepName === 'freq_mod_pro') {
    const errors: string[] = []
    for (const journey of survey.record.data.freq_mod_pro_journeys || []) {
      if (journey.mode === undefined || journey.mode === '') {
        errors.push(t('form.error.pro_journey_mode'))
      }
      if (!journey.location && !journey.hex_id) {
        errors.push(t('form.error.pro_journey_hex_id'))
      }
      if (journey.days === undefined || journey.days <= 0) {
        errors.push(t('form.error.pro_journey_days'))
      }
    }
    if (errors.length) {
      errors.forEach((err) => notifyError(err))
      return
    }
  }
  if (survey.stepName === 'email') {
    if (plainEmail.value.trim() !== '') {
      // Basic email format validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(plainEmail.value.trim())) {
        notifyError(t('form.error.invalid_email'))
        return
      }
    }
  }
  if (survey.stepName === 'change') {
    // Both undefined and 0 mean no data
    const idx = survey.currentChangeIndex
    if (
      !survey.record.data.changes?.[idx]?.motivation &&
      !survey.isRecommendationAtIndexInUse(idx)
    ) {
      notifyError(t('form.error.change_motivation_required'))
      return
    }
    survey.syncChangeGroup(idx)
  }

  survey.incStep(collector.info.with_professional_questions ?? true)
  if (survey.tokenOrSlug) {
    void collector.loadInfo(survey.tokenOrSlug)
    if (survey.stepName === 'recommendations') {
      survey.recommendation = {}
      survey.recommendationLoaded = false
      survey.record.data.comments = ''
      collector
        .save(survey.tokenOrSlug, survey.record, plainEmail.value)
        .then(() => {
          void collector.loadInfo(survey.tokenOrSlug!)
          return collector.loadTypo(survey.record, locale.value)
        })
        .then((resp) => {
          survey.recommendation = resp
          survey.record.typo = resp
          survey.recommendationLoaded = true
        })
        .catch(notifyError)
    } else if (survey.isBeforeStep('recommendations')) {
      void collector.save(survey.tokenOrSlug, survey.record, plainEmail.value).catch(console.error)
    } else if (survey.stepName === 'change') {
      void collector.save(survey.tokenOrSlug, survey.record, plainEmail.value).catch(console.error)
    } else if (survey.previousStepName === 'email' || survey.previousStepName === 'recommendations_pro') {
      // step was just incremented, so we check previous step
      void collector.save(survey.tokenOrSlug, survey.record, plainEmail.value).catch(console.error)
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function prevStep() {
  if (survey.stepName === 'agreement') return
  survey.decStep(collector.info.with_professional_questions ?? true)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function handleSwipe(dir: any) {
  if (
    ['workplace', 'origin_places', 'intermodality', 'freq_mod_pro', 'recommendations', 'recommendations_pro'].includes(
      survey.stepName || '',
    )
  ) {
    // ignore because of map dragging conflict
    return
  }
  if (dir['direction'] === 'left') {
    nextStep()
  } else if (dir['direction'] === 'right') {
    prevStep()
  }
}

function onSave() {
  if (!survey.tokenOrSlug) return

  const idx = survey.currentChangeIndex
  const currentChange = survey.record.data.changes?.[idx]
  if (currentChange?.levers?.includes('other') === false) {
    currentChange.other_levers = undefined
  }
  survey.syncChangeGroup(idx)

  void collector.save(survey.tokenOrSlug, survey.record, plainEmail.value).catch(console.error)
}

function onSendComments() {
  if (survey.tokenOrSlug) {
    void collector
      .saveComments(survey.record)
      .catch(console.error)
      .finally(() => {
        nextStep()
      })
  }
}
</script>
