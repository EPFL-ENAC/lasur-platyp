import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CaseReport } from 'src/models'

export const useSurvey = defineStore(
  'survey',
  () => {
    const tokenOrSlug = ref<string | null>(null)
    const caseReport = ref<CaseReport>({} as CaseReport)
    const step = ref(0)
    const timestamp = ref(Date.now())

    function init(cr: CaseReport) {
      caseReport.value = cr
      step.value = 1
      timestamp.value = Date.now()
    }

    function reset() {
      caseReport.value = {} as CaseReport
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
      caseReport,
      step,
      timestamp,
      init,
      reset,
      incStep,
      decStep,
    }
  },
  { persist: true },
)
