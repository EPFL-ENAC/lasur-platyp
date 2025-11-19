import type { Emissions, Frequencies, Links, Stats } from 'src/models'
import type { Filter } from 'src/components/models'
import { api } from 'src/boot/api'

const authStore = useAuthStore()

export const useStats = defineStore('stats', () => {
  const frequencies = ref<{ [key: string]: Frequencies | Frequencies[] }>(
    {} as { [key: string]: Frequencies },
  )
  const emissions = ref<{ [key: string]: Emissions[] }>({} as { [key: string]: Emissions[] })
  const links = ref<{ [key: string]: Links }>({} as { [key: string]: Links })
  const loading = ref(false)

  async function loadStats(filter: Filter | undefined = undefined) {
    loading.value = true
    frequencies.value = {}
    emissions.value = {}
    links.value = {}
    return Promise.all([
      loadAllStats(filter),
      loadFrequencies('freq_mod_pro', filter),
      loadLinks('mod_reco', filter),
    ]).finally(() => {
      loading.value = false
    })
  }

  async function loadAllStats(filter: Filter | undefined) {
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get('/stats/all', {
          ...config,
          params: { filter: filter ? JSON.stringify(filter) : undefined },
        })
        .then((res) => {
          const stats = res.data as Stats
          stats.frequencies?.forEach((freq) => {
            frequencies.value[freq.field] = freq
          })
          frequencies.value['freq_mod'] = stats.mode_frequencies || []
          emissions.value['freq_mod'] = stats.mode_emissions || []
        })
        .catch((err) => {
          console.error(err)
        })
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

  async function loadLinks(type: string, filter: Filter | undefined) {
    links.value[type] = { total: 0, data: [] }
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get(`/stats/${type}`, {
          ...config,
          params: { filter: filter ? JSON.stringify(filter) : undefined },
        })
        .then((res) => {
          links.value[type] = res.data
        })
        .catch(() => {
          links.value[type] = { total: 0, data: [] }
        })
    })
  }

  return {
    frequencies,
    emissions,
    links,
    loading,
    loadStats,
  }
})
