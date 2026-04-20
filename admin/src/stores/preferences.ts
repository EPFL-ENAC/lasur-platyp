import {
  getLocalStorageBoolean,
  getLocalStorageJSON,
  setLocalStorage,
} from 'src/utils/localStorage'

export interface StatsSectionsExpandedState {
  mobilityAnalysis: boolean
  mobilityPotentials: boolean
  behaviouralChanges: boolean
}

const defaultStatsSectionsExpandedState: StatsSectionsExpandedState = {
  mobilityAnalysis: false,
  mobilityPotentials: false,
  behaviouralChanges: false,
}

export const usePreferencesStore = defineStore('preferences', () => {
  const doNotShowDataProtectionNoticeKey = 'doNotShowDataProtectionNotice'
const statsSectionsExpandedStateKey = 'statsSectionsExpandedState'

  const doNotShowNotice = ref(getLocalStorageBoolean(doNotShowDataProtectionNoticeKey, false))
  const statsSectionsExpandedState = ref(
    getLocalStorageJSON<StatsSectionsExpandedState>(
      statsSectionsExpandedStateKey,
      defaultStatsSectionsExpandedState,
    ),
  )

  watch(doNotShowNotice, (newValue) => {
    setLocalStorage(doNotShowDataProtectionNoticeKey, newValue.toString())
  })

  watch(
    statsSectionsExpandedState,
    (newValue) => {
      setLocalStorage(statsSectionsExpandedStateKey, JSON.stringify(newValue))
    },
    { deep: true },
  )

  const hasAlreadyShownDataProtectionNoticeThisTime = ref(false)

  return {
    hasAlreadyShownDataProtectionNoticeThisTime,
    doNotShowNotice,
    statsSectionsExpandedState,
  }
})
