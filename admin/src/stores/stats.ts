import {
  type BehaviorChangeStats,
  makeDefaultBehaviorChangeStats,
  makeDefaultJourneyEnergyStats,
  type CampaignGroup,
  type CampaignStats,
  type ComparisonMode,
  type ComparisonResult,
  type Emissions,
  type Frequencies,
  type H3Heatmap,
  type JourneyEnergyStats,
  type StatLinks,
  type Stats,
  type EquipmentsStats,
  type EmissionReduction,
} from '@/models'
import type { Filter } from '@/components/models'
import { api } from '@/boot/api'
import { getIndexedDB, removeIndexedDB, setIndexedDB } from '@/utils/indexedDb'
import { getRandomId } from '@/utils/random'

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
  comparisonResults: ComparisonResult | null
  privacyWarnings: string[]
  comparisonMode: ComparisonMode | null
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

  const comparisonResults = ref<ComparisonResult | null>(null)
  const privacyWarnings = ref<string[]>([])
  const comparisonMode = ref<ComparisonMode | null>(null)

  const freqModalType = ref('simple')
  const emModalType = ref('simple')
  const redModalType = ref('simple')
  const redShareModalType = ref('simple')

  const travelTimePercent = ref(true)
  const equipmentsPercent = ref(true)
  const constraintsPercent = ref(true)
  const freqModProPercent = ref(true)
  const leversPercent = ref(true)
  const motivationPercent = ref(true)

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
    resetComparison()

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
          frequencies.value['freq_mod_complex'] = stats.mode_frequencies_complex_labels || []
          frequencies.value['freq_mod_simple'] = stats.mode_frequencies_simple_labels || []
          emissions.value['freq_mod_simple'] = stats.mode_emissions_simple_labels || []
          emissions.value['freq_mod_complex'] = stats.mode_emissions_complex_labels || []
          emissions.value['reco_mod_simple'] = stats.reco_mode_emissions_simple_labels || []
          emissions.value['reco_mod_complex'] = stats.reco_mode_emissions_complex_labels || []
          emissionsReductions.value['reductions_mod_simple'] =
            stats.mode_emission_reductions_simple_labels || []
          emissionsReductions.value['reductions_mod_complex'] =
            stats.mode_emission_reductions_complex_labels || []
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

  async function loadComparison(
    groups: CampaignGroup[],
    mode: ComparisonMode,
    geoFilter: Filter | undefined = undefined,
  ) {
    loading.value = true
    comparisonResults.value = null
    privacyWarnings.value = []
    return authStore
      .updateToken()
      .then(() => {
        const config = {
          headers: {
            Authorization: `Bearer ${authStore.accessToken}`,
          },
        }
        return api
          .post('/stats/compare', { groups, mode, filter: geoFilter }, config)
          .then((res) => {
            const result = res.data as ComparisonResult
            comparisonResults.value = result
            privacyWarnings.value = result.warnings || []
            comparisonMode.value = mode
          })
          .catch((err) => {
            console.error(err)
          })
      })
      .finally(() => {
        loading.value = false
      })
  }

  function resetComparison() {
    comparisonResults.value = null
    privacyWarnings.value = []
    comparisonMode.value = null
  }

  async function dumpToIndexedDB() {
    const id = getRandomId()
    await setIndexedDB(makeStatsStateId(id), toJSONState())
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
      comparisonResults: comparisonResults.value,
      privacyWarnings: privacyWarnings.value,
      comparisonMode: comparisonMode.value,
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
    comparisonResults,
    privacyWarnings,
    comparisonMode,
    freqModalType,
    emModalType,
    redModalType,
    redShareModalType,
    travelTimePercent,
    equipmentsPercent,
    constraintsPercent,
    freqModProPercent,
    leversPercent,
    motivationPercent,
    loading,
    loadStats,
    getCampaignStats,
    loadComparison,
    resetComparison,
    toJSONState,
    dumpToIndexedDB,
  }
})

function makeStatsStateId(uuid: string): string {
  return `stats_${uuid}`
}

export async function getStateFromIndexedDB(id: string): Promise<StatsState | null> {
  return getIndexedDB<StatsState>(makeStatsStateId(id))
}

export async function flushStateFromIndexedDB(id: string): Promise<void> {
  return removeIndexedDB(makeStatsStateId(id))
}
