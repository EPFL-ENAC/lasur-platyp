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
      'employment',
      'workplace',
      'origin_places',
      'travel_time',
      'constraints',
      'equipments',
      'intermodality',
      'travel_pro',
      'freq_mod_pro',
      'importance',
      'needs',
      'age_class',
      'recommendations',
      'recommendations_pro',
      'change',
      'email',
      'comments',
      'final',
    ]

    const tokenOrSlug = ref<string | null>(null)
    const record = ref<Record>({} as Record)
    const started = ref(false)
    const step = ref(0)
    const changeStepIndex = ref(0)
    const timestamp = ref(Date.now())
    const recommendation = ref<Recommendation>({})
    const recommendationLoaded = ref(false)

    const stepName = computed(() => stepNames[step.value - 1])
    const previousStepName = computed(() => stepNames[step.value - 2])

    function init(cr: Record) {
      record.value = cr
      recommendation.value = {}
      recommendationLoaded.value = false
      started.value = false
      step.value = 1
      changeStepIndex.value = 0
      timestamp.value = Date.now()
    }

    function finish() {
      record.value = {} as Record
      recommendation.value = {}
      recommendationLoaded.value = false
      tokenOrSlug.value = null
    }

    function reset() {
      record.value = {} as Record
      recommendation.value = {}
      recommendationLoaded.value = false
      started.value = false
      step.value = 0
      changeStepIndex.value = 0
      timestamp.value = Date.now()
      tokenOrSlug.value = null
    }

    /**
     * Raw reco_inter indices of the first occurrence of each unique recommended mode,
     * in order of appearance. The same mode can appear several times in reco_inter;
     * this drives the 'change' step so it is only shown once per unique mode.
     */
    function uniqueChangeIndices() {
      const recoInter = recommendation.value.reco?.reco_inter
      if (!recoInter || !recoInter.length) return [0]
      const seen = new Set<string>()
      const indices: number[] = []
      recoInter.forEach((mode, i) => {
        if (!seen.has(mode)) {
          seen.add(mode)
          indices.push(i)
        }
      })
      return indices
    }

    /**
     * Number of 'change' sub-steps, one per unique recommended mode (reco_inter).
     * At least one, so the step is still shown when there is no recommendation.
     */
    function changeStepsCount() {
      return uniqueChangeIndices().length
    }

    /**
     * Raw reco_inter/changes index of the recommendation currently shown in the
     * 'change' step, mapping the deduplicated changeStepIndex back to the first
     * occurrence of that mode.
     */
    const currentChangeIndex = computed(() => uniqueChangeIndices()[changeStepIndex.value] ?? 0)

    /**
     * All raw reco_inter indices sharing the same mode as the given index.
     */
    function changeGroupIndices(index: number) {
      const recoInter = recommendation.value.reco?.reco_inter
      if (!recoInter || !recoInter.length) return [index]
      const mode = recoInter[index]
      return recoInter.reduce<number[]>((acc, m, i) => {
        if (m === mode) acc.push(i)
        return acc
      }, [])
    }

    /**
     * Copy the answer at `index` to every other reco_inter occurrence sharing the
     * same mode, so a recommendation repeated several times is answered once in the
     * UI but still recorded for each occurrence.
     */
    function syncChangeGroup(index: number) {
      const changes = record.value.data.changes
      const source = changes?.[index]
      if (!changes || !source) return
      changeGroupIndices(index).forEach((i) => {
        if (i !== index) changes[i] = { ...source }
      })
    }

    function isBeforeStep(name: string) {
      return step.value < stepNames.indexOf(name) + 1
    }

    function isAfterStep(name: string) {
      return step.value > stepNames.indexOf(name) + 1
    }

    function incStep(withProfessionalQuestions = true) {
      if (stepName.value === 'change' && changeStepIndex.value < changeStepsCount() - 1) {
        changeStepIndex.value += 1
        timestamp.value = Date.now()
        return
      }
      step.value += 1
      if (stepName.value === 'change') {
        changeStepIndex.value = 0
      }
      let skipped = skipIncSteps(withProfessionalQuestions)
      while (skipped) {
        skipped = skipIncSteps(withProfessionalQuestions)
      }
      timestamp.value = Date.now()
    }

    function decStep(withProfessionalQuestions = true) {
      if (stepName.value === 'change' && changeStepIndex.value > 0) {
        changeStepIndex.value -= 1
        timestamp.value = Date.now()
        return
      }
      step.value -= 1
      if (stepName.value === 'change') {
        changeStepIndex.value = changeStepsCount() - 1
      }
      let skipped = skipDecSteps(withProfessionalQuestions)
      while (skipped) {
        skipped = skipDecSteps(withProfessionalQuestions)
      }
      timestamp.value = Date.now()
    }

    function skipIncSteps(withProfessionalQuestions = true) {
      if (stepName.value === 'freq_mod_pro' && !record.value.data.travel_pro) {
        record.value.data = {
          ...record.value.data,
          freq_mod_pro_journeys: [],
        }
        step.value += 1
        return true
      }
      if (!withProfessionalQuestions && stepName.value === 'travel_pro') {
        step.value += 1
        return true
      }
      if (recommendationLoaded.value && stepName.value === 'recommendations_pro' && !recommendation.value.reco_pro?.reco_pros?.length) {
        step.value += 1
        return true
      }

      return false
    }

    function skipDecSteps(withProfessionalQuestions = true) {
      if (stepName.value === 'freq_mod_pro' && !record.value.data.travel_pro) {
        step.value -= 1
        return true
      }
      if (!withProfessionalQuestions && stepName.value === 'travel_pro') {
        step.value -= 1
        return true
      }
      if (recommendationLoaded.value && stepName.value === 'recommendations_pro' && !recommendation.value.reco_pro?.reco_pros?.length) {
        step.value -= 1
        return true
      }

      return false
    }

    function getFreqMod(mode: string) {
      if (record.value.data?.freq_mod_journeys && record.value.data?.freq_mod_journeys.length) {
        let freq = 0
        record.value.data.freq_mod_journeys.forEach((j) => {
          // unique values of modes
          const modes = Array.from(new Set(j.modes))
          if (modes.includes(mode)) {
            if (mode === 'walking') {
              // only count walking if it's the only mode
              if (modes.length === 1) {
                freq += j.days
              }
            } else {
              freq += j.days
            }
          }
        })
        return freq
      }
      return 0
    }

    function isIntermodality() {
      if (record.value.data.freq_mod_journeys && record.value.data.freq_mod_journeys.length) {
        return (
          record.value.data.freq_mod_journeys
            // remove walking from modes
            .map((j) => ({ ...j, modes: j.modes.filter((m) => m !== 'walking') }))
            .some((j) => j.modes.length > 1)
        )
      }
      return false
    }

    /**
     * Get the main frequency mode (the one with the highest frequency).
     * If there is a tie, return the first one found.
     * If there is a combined mode, return 'inter'.
     * If no mode is found, return ''.
     */
    function getMainFreqMod(withCombined = true) {
      if (withCombined && isIntermodality()) return 'inter'
      const fm = getFreqMods()
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

    function getFreqMods(): { [key: string]: number } {
      return {
        walking: getFreqMod('walking'),
        bike: getFreqMod('bike'),
        ebike: getFreqMod('ebike'),
        pub: getFreqMod('pub'),
        moto: getFreqMod('moto'),
        car: getFreqMod('car'),
        carpool: getFreqMod('carpool'),
        train: getFreqMod('train'),
      }
    }

    function isModeSustainable(mode: string) {
      return !['car', 'moto'].includes(mode)
    }

    function isRecommendationAtIndexInUse(index: number) {
      if (
        recommendation.value.reco &&
        recommendation.value.reco.reco_inter &&
        recommendation.value.reco.reco_inter.length > index
      ) {
        const freqMods = getFreqMods()
        const mode = recommendation.value.reco.reco_inter[index]
        if (!mode) return false

        const translatedMode = RecoToMode[mode] || mode
        return freqMods[translatedMode] !== undefined && freqMods[translatedMode] > 0
      }
      return false
    }

    /**
     * Check if a mode is one of the recommendations (reco_inter).
     */
    function isModeInRecommendation(mode: string) {
      if (
        recommendation.value.reco &&
        recommendation.value.reco.reco_inter &&
        recommendation.value.reco.reco_inter.length
      ) {
        return recommendation.value.reco.reco_inter.some(
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
      changeStepIndex,
      stepName,
      previousStepName,
      timestamp,
      recommendation,
      recommendationLoaded,
      init,
      finish,
      reset,
      isBeforeStep,
      isAfterStep,
      incStep,
      decStep,
      changeStepsCount,
      currentChangeIndex,
      changeGroupIndices,
      syncChangeGroup,
      getFreqMod,
      getMainFreqMod,
      isModeSustainable,
      isModeInRecommendation,
      isRecommendationAtIndexInUse,
    }
  },
  { persist: true },
)
