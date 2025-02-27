import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Record } from 'src/models'

export const useSurvey = defineStore(
  'survey',
  () => {
    const tokenOrSlug = ref<string | null>(null)
    const record = ref<Record>({} as Record)
    const step = ref(0)
    const timestamp = ref(Date.now())
    const recommendation = ref<{ [key: string]: string }>({})

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
      step.value += 1
      timestamp.value = Date.now()
    }

    function decStep() {
      step.value -= 1
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
