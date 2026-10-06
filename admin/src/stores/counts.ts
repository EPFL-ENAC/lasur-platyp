import { defineStore } from 'pinia'
import { api } from '@/boot/api'

/**
 * Totals shown as badges in the navigation drawer. Each one is the same
 * total the corresponding table page reports, fetched with a one-row query.
 */
export const useCountsStore = defineStore('counts', () => {
  const authStore = useAuthStore()
  const services = useServices()

  const companies = ref<number>()
  const records = ref<number>()
  const users = ref<number>()

  async function fetchTotal(entityName: 'company' | 'record'): Promise<number | undefined> {
    const result = await services.make(entityName).find({ $skip: 0, $limit: 1 })
    return typeof result?.total === 'number' ? result.total : undefined
  }

  async function fetchUsersTotal(): Promise<number | undefined> {
    await authStore.updateToken()
    const res = await api.get('/user/', {
      headers: { Authorization: `Bearer ${authStore.accessToken}` },
    })
    return typeof res.data?.total === 'number' ? res.data.total : undefined
  }

  async function refresh() {
    if (!authStore.isAuthenticated) return
    const jobs: Promise<void>[] = [
      fetchTotal('company').then((n) => {
        companies.value = n
      }),
    ]
    // Records and users are listed for super admins only, same rule as their pages
    if (authStore.isAdmin) {
      jobs.push(
        fetchTotal('record').then((n) => {
          records.value = n
        }),
        fetchUsersTotal().then((n) => {
          users.value = n
        }),
      )
    } else {
      records.value = undefined
      users.value = undefined
    }
    await Promise.allSettled(jobs)
  }

  return { companies, records, users, refresh }
})
