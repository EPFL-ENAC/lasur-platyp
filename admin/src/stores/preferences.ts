import { getLocalStorageBoolean, getLocalStorageJSON, setLocalStorage } from "src/utils/localStorage"

export interface StatsSectionsCollapsedState {
  mobilityAnalysis: boolean
  mobilityPotentials: boolean
  behaviouralChanges: boolean
}

const defaultStatsSectionsCollapsedState: StatsSectionsCollapsedState = {
  mobilityAnalysis: false,
  mobilityPotentials: false,
  behaviouralChanges: false
}

export const usePreferencesStore = defineStore('preferences', () => {
  const doNotShowDataProtectionNoticeKey = 'doNotShowDataProtectionNotice'
  const statsSectionsCollapsedStateKey = 'statsSectionsCollapsedState'

  const doNotShowNotice = ref(getLocalStorageBoolean(doNotShowDataProtectionNoticeKey, false))
  const statsSectionsCollapsedState = ref(getLocalStorageJSON<StatsSectionsCollapsedState>(statsSectionsCollapsedStateKey, defaultStatsSectionsCollapsedState))

  watch(doNotShowNotice, (newValue) => {
    setLocalStorage(doNotShowDataProtectionNoticeKey, newValue.toString())
  })

  watch(statsSectionsCollapsedState, (newValue) => {
    setLocalStorage(statsSectionsCollapsedStateKey, JSON.stringify(newValue))
  }, { deep: true })

  const hasAlreadyShownDataProtectionNoticeThisTime = ref(false)

  return {
    hasAlreadyShownDataProtectionNoticeThisTime,
    doNotShowNotice,
    statsSectionsCollapsedState
  }
})
