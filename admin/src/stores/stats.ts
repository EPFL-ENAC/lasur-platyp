import {
  type BehaviorChangeStats,
  makeDefaultBehaviorChangeStats,
  makeDefaultJourneyEnergyStats,
  type CampaignStats,
  type Emissions,
  type Frequencies,
  type H3Heatmap,
  type JourneyEnergyStats,
  type StatLinks,
  type Stats,
  type EquipmentsStats,
  type EmissionReduction,
} from 'src/models'
import type { Filter } from 'src/components/models'
import { api } from 'src/boot/api'
import { getLocalStorageJSON, setLocalStorage } from 'src/utils/localStorage'
import { getRandomId } from 'src/utils/random'

const authStore = useAuthStore()

export interface StatsState {
  frequencies: { [key: string]: Frequencies | Frequencies[] }
  emissions: { [key: string]: Emissions[] }
  emissionsReductions: { [key: string]: EmissionReduction[] }
  links: { [key: string]: StatLinks }
  homeLocationsHeatmap: H3Heatmap
  workplaceLocations: { lat: number; lon: number }[]
  journeyEnergyStats: JourneyEnergyStats
  behaviorChange: BehaviorChangeStats
  equipmentsStats: EquipmentsStats | null
}

export const useStats = defineStore('stats', () => {
  const frequencies = ref<{ [key: string]: Frequencies | Frequencies[] }>(
    {} as { [key: string]: Frequencies },
  )
  const emissions = ref<{ [key: string]: Emissions[] }>({} as { [key: string]: Emissions[] })
  const emissionsReductions = ref<{ [key: string]: EmissionReduction[] }>(
    {} as { [key: string]: EmissionReduction[] },
  )
  const links = ref<{ [key: string]: StatLinks }>({} as { [key: string]: StatLinks })
  const homeLocationsHeatmap = ref<H3Heatmap>({})
  const workplaceLocations = ref<{ lat: number; lon: number }[]>([])
  const journeyEnergyStats = ref<JourneyEnergyStats>({} as JourneyEnergyStats)
  const behaviorChange = ref<BehaviorChangeStats>({} as BehaviorChangeStats)
  const equipmentsStats = ref<EquipmentsStats | null>(null)

  const loading = ref(false)

  async function loadStats(filter: Filter | undefined = undefined) {
    loading.value = true
    frequencies.value = {}
    emissions.value = {}
    emissionsReductions.value = {}
    links.value = {}
    homeLocationsHeatmap.value = {}
    workplaceLocations.value = []
    journeyEnergyStats.value = makeDefaultJourneyEnergyStats()
    behaviorChange.value = makeDefaultBehaviorChangeStats()
    equipmentsStats.value = null

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
          emissionsReductions.value['reductions_mod'] = stats.mode_emission_reductions || []
          links.value['mod_reco'] = stats.mode_links || {
            total: 0,
            data: [],
            most_recommended_target: null,
          }
          stats.pro_frequencies?.forEach((freq) => {
            frequencies.value[freq.field] = freq
          })
          frequencies.value['freq_mod_pro'] = stats.pro_mode_frequencies || []
          emissions.value['freq_mod_pro'] = stats.pro_mode_emissions || []
          emissions.value['reco_mod_pro'] = stats.pro_reco_mode_emissions || []
          emissionsReductions.value['reductions_mod_pro'] = stats.pro_mode_emission_reductions || []
          links.value['mod_reco_pro'] = stats.pro_mode_links || {
            total: 0,
            data: [],
            most_recommended_target: null,
          }
          homeLocationsHeatmap.value = stats.home_location_heatmap || {}
          workplaceLocations.value = stats.workplace_locations || []
          journeyEnergyStats.value = stats.journey_energy_stats || makeDefaultJourneyEnergyStats()
          behaviorChange.value = stats.behavior_change || makeDefaultBehaviorChangeStats()
          equipmentsStats.value = stats.equipments_stats || null
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

  function dumpToLocalStorage() {
    const id = getRandomId()
    setLocalStorage(makeStatsStateId(id), JSON.stringify(toJSONState()))
    return id
  }

  function toJSONState(): StatsState {
    return {
      frequencies: frequencies.value,
      emissions: emissions.value,
      emissionsReductions: emissionsReductions.value,
      links: links.value,
      homeLocationsHeatmap: homeLocationsHeatmap.value,
      workplaceLocations: workplaceLocations.value,
      journeyEnergyStats: journeyEnergyStats.value,
      behaviorChange: behaviorChange.value,
      equipmentsStats: equipmentsStats.value,
    }
  }

  return {
    frequencies,
    behaviorChange,
    emissions,
    emissionsReductions,
    links,
    homeLocationsHeatmap,
    workplaceLocations,
    journeyEnergyStats,
    equipmentsStats,
    loading,
    loadStats,
    getCampaignStats,
    toJSONState,
    dumpToLocalStorage,
  }
})

function makeStatsStateId(uuid: string): string {
  return `stats_${uuid}`
}

export function getStateFromLocalStorage(id: string): StatsState | null {
  return getLocalStorageJSON<StatsState | null>(makeStatsStateId(id), null)
}

export function flushStateFromLocalStorage(id: string): void {
  localStorage.removeItem(makeStatsStateId(id))
}
