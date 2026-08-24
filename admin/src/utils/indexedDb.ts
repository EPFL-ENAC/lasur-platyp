const DB_NAME = 'platyp-admin'
const DB_VERSION = 1
const STORE_NAME = 'kv'

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    request.onupgradeneeded = () => {
      request.result.createObjectStore(STORE_NAME)
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

export async function setIndexedDB(key: string, value: unknown): Promise<void> {
  const db = await openDb()
  // Vue wraps reactive state in Proxies, which the structured clone algorithm
  // used by IndexedDB can fail to clone. Round-tripping through JSON strips
  // reactivity and yields a plain, cloneable value.
  const plainValue = JSON.parse(JSON.stringify(value)) as unknown
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).put(plainValue, key)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  }).finally(() => db.close())
}

export async function getIndexedDB<T>(key: string): Promise<T | null> {
  const db = await openDb()
  return new Promise<T | null>((resolve, reject) => {
    const request = db.transaction(STORE_NAME, 'readonly').objectStore(STORE_NAME).get(key)
    request.onsuccess = () => resolve((request.result ?? null) as T | null)
    request.onerror = () => reject(request.error)
  }).finally(() => db.close())
}

export async function removeIndexedDB(key: string): Promise<void> {
  const db = await openDb()
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).delete(key)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  }).finally(() => db.close())
}
