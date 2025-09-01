import type { Frequencies } from 'src/models'
import type { Filter } from 'src/components/models'
import { api } from 'src/boot/api'

const authStore = useAuthStore()

export const useStats = defineStore('stats', () => {
  const frequencies = ref<{ [key: string]: Frequencies | Frequencies[] }>(
    {} as { [key: string]: Frequencies },
  )
  const loading = ref(false)

  async function loadStats(filter: Filter | undefined = undefined) {
    loading.value = true
    return Promise.all([
      loadFrequencies('equipments', filter),
      loadFrequencies('constraints', filter),
      loadFrequencies('travel_time', filter),
      loadFrequencies('freq_mod', filter),
      loadFrequencies('freq_mod_pro', filter),
    ]).finally(() => {
      loading.value = false
    })
  }

  async function loadFrequencies(field: string, filter: Filter | undefined) {
    frequencies.value[field] = { field, total: 0, data: [] }
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get(`/stats/${field}`, {
          ...config,
          params: { filter: filter ? JSON.stringify(filter) : undefined },
        })
        .then((res) => {
          frequencies.value[field] = res.data
        })
        .catch(() => {
          frequencies.value[field] = { field, total: 0, data: [] }
        })
    })
  }

  return {
    frequencies,
    loading,
    loadStats,
  }
})
