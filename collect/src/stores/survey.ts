import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Record, Recommendation } from 'src/models'

export const useSurvey = defineStore(
  'survey',
  () => {
    const tokenOrSlug = ref<string | null>(null)
    const record = ref<Record>({} as Record)
    const step = ref(0)
    const timestamp = ref(Date.now())
    const recommendation = ref<Recommendation>({})

    function init(cr: Record) {
      record.value = cr
      step.value = 1
      timestamp.value = Date.now()
    }

    function reset() {
      record.value = {} as Record
      step.value = 0
      timestamp.value = Date.now()
      tokenOrSlug.value = null
    }

    function incStep() {
      if (step.value === 8 && record.value.data.freq_trav_pro_local < 4) {
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
        step.value += 2
      } else if (step.value === 10 && record.value.data.freq_trav_pro_region < 2) {
        record.value.data = {
          ...record.value.data,
          freq_mod_pro_region_pub: 0,
          freq_mod_pro_region_moto: 0,
          freq_mod_pro_region_car: 0,
          freq_mod_pro_region_train: 0,
          freq_mod_pro_region_plane: 0,
          freq_mod_pro_region_combined: false,
        }
        step.value += 2
      } else if (step.value === 12 && record.value.data.freq_trav_pro_inter < 1) {
        record.value.data = {
          ...record.value.data,
          freq_mod_pro_inter_car: 0,
          freq_mod_pro_inter_train: 0,
          freq_mod_pro_inter_plane: 0,
          freq_mod_pro_inter_combined: false,
        }
        step.value += 2
      } else {
        step.value += 1
      }

      timestamp.value = Date.now()
    }

    function decStep() {
      if (step.value === 10 && record.value.data.freq_trav_pro_local < 4) {
        step.value -= 2
      } else if (step.value === 12 && record.value.data.freq_trav_pro_region < 2) {
        step.value -= 2
      } else if (step.value === 14 && record.value.data.freq_trav_pro_inter < 1) {
        step.value -= 2
      } else {
        step.value -= 1
      }
      timestamp.value = Date.now()
    }

    return {
      tokenOrSlug,
      record,
      step,
      timestamp,
      recommendation,
      init,
      reset,
      incStep,
      decStep,
    }
  },
  { persist: true },
)
