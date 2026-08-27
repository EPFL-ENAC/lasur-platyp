export function getLocalStorageBoolean(key: string, defaultValue: boolean): boolean {
  if (typeof window !== 'undefined') {
    const item = localStorage.getItem(key)
    if (item !== null && item !== undefined) {
      return item === 'true'
    }
  }
  return defaultValue
}

export function getLocalStorageJSON<T>(key: string, defaultValue: T): T {
  if (typeof window !== 'undefined') {
    const storedValue = localStorage.getItem(key)
    if (storedValue) {
      return JSON.parse(storedValue) as T
    }
  }
  return defaultValue
}

export function setLocalStorage(key: string, value: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, value)
  }
}

const alreadyVisitedKey = 'alreadyVisited' as const

export function isFirstVisit(): boolean {
  return !getLocalStorageBoolean(alreadyVisitedKey, false) // inversion is on purpose to default to true on first visit
}

export function markVisited(): void {
  setLocalStorage(alreadyVisitedKey, 'true')
}
