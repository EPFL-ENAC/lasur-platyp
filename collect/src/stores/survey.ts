import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Record, Recommendation } from 'src/models'

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
      'freq_mod',
      'trav_pro',
      'freq_mod_pro_local',
      'freq_mod_pro_region',
      'freq_mod_pro_europe',
      'freq_mod_pro_inter',
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
      if (
        stepName.value === 'freq_mod_pro_local' &&
        !record.value.data.trav_pro?.includes('local')
      ) {
        record.value.data = {
          ...record.value.data,
          freq_mod_pro_local_walking: 0,
          freq_mod_pro_local_bike: 0,
          freq_mod_pro_local_pub: 0,
          freq_mod_pro_local_moto: 0,
          freq_mod_pro_local_car: 0,
          freq_mod_pro_local_train: 0,
          freq_mod_pro_local_combined: false,
        }
        step.value += 1
        return true
      }

      if (
        stepName.value === 'freq_mod_pro_region' &&
        !record.value.data.trav_pro?.includes('region')
      ) {
        record.value.data = {
          ...record.value.data,
          freq_mod_pro_region_pub: 0,
          freq_mod_pro_region_moto: 0,
          freq_mod_pro_region_car: 0,
          freq_mod_pro_region_train: 0,
          freq_mod_pro_region_plane: 0,
          freq_mod_pro_region_combined: false,
        }
        step.value += 1
        return true
      }

      if (
        stepName.value === 'freq_mod_pro_inter' &&
        !record.value.data.trav_pro?.includes('inter')
      ) {
        record.value.data = {
          ...record.value.data,
          freq_mod_pro_inter_car: 0,
          freq_mod_pro_inter_train: 0,
          freq_mod_pro_inter_plane: 0,
          freq_mod_pro_inter_combined: false,
        }
        step.value += 1
        return true
      }

      return false
    }

    function skipDecSteps() {
      if (
        stepName.value === 'freq_mod_pro_local' &&
        !record.value.data.trav_pro?.includes('local')
      ) {
        step.value -= 1
        return true
      }
      if (
        stepName.value === 'freq_mod_pro_region' &&
        !record.value.data.trav_pro?.includes('region')
      ) {
        step.value -= 1
        return true
      }
      if (
        stepName.value === 'freq_mod_pro_inter' &&
        !record.value.data.trav_pro?.includes('inter')
      ) {
        step.value -= 1
        return true
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
    }
  },
  { persist: true },
)
