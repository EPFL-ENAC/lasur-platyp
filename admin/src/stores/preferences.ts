export interface StatsSectionsCollapsedState {
  mobilityAnalysis: boolean
  mobilityPotentials: boolean
  behaviouralChanges: boolean
}

function getLocalStorageBoolean(key: string, defaultValue: boolean): boolean {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(key) === 'true'
  }
  return defaultValue
}

function getLocalStorageJSON<T>(key: string, defaultValue: T): T {
  if (typeof window !== 'undefined') {
    const storedValue = localStorage.getItem(key)
    if (storedValue) {
      return JSON.parse(storedValue) as T
    }
  }
  return defaultValue
}

function setLocalStorage(key: string, value: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, value)
  }
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

  return {
    doNotShowNotice,
    statsSectionsCollapsedState
  }
})
