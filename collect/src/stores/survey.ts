import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Record, Recommendation } from 'src/models'

const RecoToMode: { [key: string]: string | undefined } = {
  marche: 'walking',
  velo: 'bike',
  vae: 'ebike',
  covoit: 'carpool',
  tpu: 'pub',
}

export const useSurvey = defineStore(
  'survey',
  () => {
    const stepNames = [
      'agreement',
      'age_class',
      'employment',
      'places',
      'travel_time',
      'constraints',
      'equipments',
      'intermodality',
      'travel_pro',
      'freq_mod_pro',
      'importance',
      'needs',
      'recommendations',
      'change',
      'comments',
      'final',
    ]

    const tokenOrSlug = ref<string | null>(null)
    const record = ref<Record>({} as Record)
    const started = ref(false)
    const step = ref(0)
    const timestamp = ref(Date.now())
    const recommendation = ref<Recommendation>({})

    const stepName = computed(() => stepNames[step.value - 1])

    function init(cr: Record) {
      record.value = cr
      recommendation.value = {} as Recommendation
      started.value = false
      step.value = 1
      timestamp.value = Date.now()
    }

    function finish() {
      record.value = {} as Record
      recommendation.value = {} as Recommendation
      tokenOrSlug.value = null
    }

    function reset() {
      record.value = {} as Record
      recommendation.value = {} as Recommendation
      started.value = false
      step.value = 0
      timestamp.value = Date.now()
      tokenOrSlug.value = null
    }

    function isBeforeStep(name: string) {
      return step.value < stepNames.indexOf(name) + 1
    }

    function isAfterStep(name: string) {
      return step.value > stepNames.indexOf(name) + 1
    }

    function incStep() {
      step.value += 1
      let skipped = skipIncSteps()
      while (skipped) {
        skipped = skipIncSteps()
      }
      timestamp.value = Date.now()
    }

    function decStep() {
      step.value -= 1
      let skipped = skipDecSteps()
      while (skipped) {
        skipped = skipDecSteps()
      }
      timestamp.value = Date.now()
    }

    function skipIncSteps() {
      if (stepName.value === 'freq_mod_pro' && !record.value.data.travel_pro) {
        record.value.data = {
          ...record.value.data,
          freq_mod_pro_journeys: [],
        }
        step.value += 1
        return true
      }

      return false
    }

    function skipDecSteps() {
      if (stepName.value === 'freq_mod_pro' && !record.value.data.travel_pro) {
        step.value -= 1
        return true
      }
      return false
    }

    function getFreqMod(mode: string) {
      if (record.value.data.freq_mod_journeys && record.value.data.freq_mod_journeys.length) {
        let freq = 0
        record.value.data.freq_mod_journeys.forEach((j) => {
          if (j.modes.includes(mode)) {
            freq += j.days
          }
        })
        return freq
      }
      return 0
    }

    function getFreqModCombined() {
      if (record.value.data.freq_mod_journeys && record.value.data.freq_mod_journeys.length) {
        return record.value.data.freq_mod_journeys.some((j) => j.modes.length > 1)
      }
      return false
    }

    /**
     * Get the main frequency mode (the one with the highest frequency).
     * If there is a tie, return the first one found.
     * If there is a combined mode, return 'combined'.
     * If no mode is found, return ''.
     */
    function getMainFreqMod() {
      if (getFreqModCombined()) return 'combined'
      const fm: { [key: string]: number } = {
        walking: getFreqMod('walking'),
        bike: getFreqMod('bike'),
        ebike: getFreqMod('ebike'),
        pub: getFreqMod('pub'),
        moto: getFreqMod('moto'),
        car: getFreqMod('car'),
        carpool: getFreqMod('carpool'),
        train: getFreqMod('train'),
      }
      let max = -1
      let main = ''
      Object.keys(fm).forEach((key) => {
        if (fm[key] !== undefined && fm[key] > max) {
          max = fm[key]
          main = key
        }
      })
      return main
    }

    /**
     * Check if a mode is in the recommendation (reco_dt2).
     */
    function isModeInRecommendation(mode: string) {
      if (recommendation.value.reco && recommendation.value.reco.reco_dt2) {
        return recommendation.value.reco.reco_dt2.some(
          (reco) => (RecoToMode[reco] || reco) === mode,
        )
      }
      return false
    }

    return {
      stepNames,
      tokenOrSlug,
      record,
      started,
      step,
      stepName,
      timestamp,
      recommendation,
      init,
      finish,
      reset,
      isBeforeStep,
      isAfterStep,
      incStep,
      decStep,
      getFreqMod,
      getFreqModCombined,
      getMainFreqMod,
      isModeInRecommendation,
    }
  },
  { persist: true },
)
