import type { CampaignStats, Emissions, Frequencies, H3Heatmap, Links, Stats } from 'src/models'
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
  const homeLocationsHeatmap = ref<H3Heatmap>({})
  const workplaceLocationsHeatmap = ref<H3Heatmap>({})

  async function loadStats(filter: Filter | undefined = undefined) {
    loading.value = true
    frequencies.value = {}
    emissions.value = {}
    links.value = {}
    homeLocationsHeatmap.value = {}
    workplaceLocationsHeatmap.value = {}
    return loadAllStats(filter).finally(() => {
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
          emissions.value['reco_mod'] = stats.reco_mode_emissions || []
          links.value['mod_reco'] = stats.mode_links || { total: 0, data: [] }
          stats.pro_frequencies?.forEach((freq) => {
            frequencies.value[freq.field] = freq
          })
          frequencies.value['freq_mod_pro'] = stats.pro_mode_frequencies || []
          emissions.value['freq_mod_pro'] = stats.pro_mode_emissions || []
          links.value['mod_reco_pro'] = stats.pro_mode_links || { total: 0, data: [] }
          homeLocationsHeatmap.value = stats.home_location_heatmap || {}
          workplaceLocationsHeatmap.value = stats.workplace_location_heatmap || {}
        })
        .catch((err) => {
          console.error(err)
        })
    })
  }

  async function getCampaignStats(campaignId: number) {
    loading.value = true
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get(`/stats/campaign/${campaignId}`, {
          ...config,
        })
        .then((res) => {
          return res.data as CampaignStats
        })
        .catch((err) => {
          console.error(err)
        })
        .finally(() => {
          loading.value = false
        })
    })
  }

  return {
    frequencies,
    emissions,
    links,
    homeLocationsHeatmap,
    workplaceLocationsHeatmap,
    loading,
    loadStats,
    getCampaignStats,
  }
})
