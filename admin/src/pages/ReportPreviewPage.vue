<template>
  <div class="bg-grey-3">
    <q-toolbar class="bg-white text-primary q-py-sm toolbar print-hide">
      <q-toolbar-title class="text-weight-bold">
        {{ t('generated_report.title') }}
      </q-toolbar-title>
      <q-space />
      <q-btn color="primary" icon="print" :label="t('print')" @click="printReport" />
    </q-toolbar>

    <div v-if="stats" class="report-container">
      <report-page is-title>
        <img src="/admin/LOGO-ALTER-VIOLET.svg" alt="logo" />
        <h1 class="text-h2">{{ t('mobility_statistics') }}</h1>
        <div class="text-h6">{{ orgs.join(', ') }}</div>
        <div class="text-h6">{{ campaigns.join(', ') }}</div>
        <div class="text-h6">{{ reportDate }}</div>
      </report-page>

      <report-page :org-names="orgs">
        <h1 class="text-h4 q-mt-none">
          {{ t('stats.sections.mobility_analysis.title') }}
        </h1>
        <q-markdown
          class="compact text-body2 q-mb-lg"
          :src="t('stats.sections.mobility_analysis.description')"
        />
      </report-page>

      <report-page :org-names="orgs">
        <h2 class="text-h6 q-mb-md">
          {{ t('stats.sections.home_to_work') }}
        </h2>
        <location-chart
          :title="t('stats.locationsHeatmap.title')"
          :height="height"
          :home-locations-heatmap="stats.homeLocationsHeatmap"
          :workplace-locations="stats.workplaceLocations"
          :exportable="false"
          no-controls
        />
      </report-page>

      <report-page :org-names="orgs">
        <modes-of-transport-share-chart
          :height="height"
          :frequencies="stats.frequencies?.['freq_mod'] ?? null"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <travel-time-frequencies-chart
          :frequencies="getFreq('travel_time')"
          :xaxis="t('stats.travel_time.xaxis')"
          :range-step="5"
          :percent="percent"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <equipment-frequencies-chart
          :frequencies="getFreq('equipments')"
          :percent="percent"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <frequencies-chart
          chart-translation-name="constraints"
          :frequencies="getFreq('constraints')"
          :percent="percent"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-chart
          chart-translation-name="freq_mod"
          :emissions="stats.emissions?.['freq_mod'] ?? null"
          :xaxis="t('stats.emissions_freq_mod.xaxis')"
          :yaxis="t('stats.emissions_freq_mod.yaxis')"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <journey-energy-chart
          type="current"
          :journey-energy-stats="stats.journeyEnergyStats"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <h2 class="text-h6 q-mt-xl q-mb-md">
          {{ t('stats.sections.professional_travel') }}
        </h2>
        <frequencies-stack-chart
          chart-translation-name="freq_mod_pro"
          :frequencies="getFreqArray('freq_mod_pro')"
          :groups="['local', 'national', 'europe', 'inter']"
          :xaxis="t('stats.freq_mod_pro.xaxis')"
          :height="height"
          :percent="percent"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-chart
          chart-translation-name="freq_mod_pro"
          :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
          :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
          :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <h1 class="text-h4 q-mt-none">
          {{ t('stats.sections.mobility_potentials.title') }}
        </h1>
        <q-markdown
          class="compact text-body2 q-mb-lg"
          :src="t('stats.sections.mobility_potentials.description')"
        />
      </report-page>

      <report-page :org-names="orgs">
        <h2 class="text-h6 q-mb-md">
          {{ t('stats.sections.home_to_work') }}
        </h2>
        <share-chart
          chart-translation-name="reco_dt2"
          :frequencies="getFreq('reco_dt2')"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <links-chart
          type="mod_reco"
          :links="stats.links['mod_reco'] ?? null"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-reductions-chart
          chart-translation-name="reductions_mod"
          :emissions="stats.emissions?.['freq_mod'] ?? null"
          :reductions="stats.emissionsReductions?.['reductions_mod'] ?? null"
          :yaxis="t('stats.emissions_reductions_mod.yaxis')"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-reductions-share-chart
          :reductions="stats.emissionsReductions?.['reductions_mod'] ?? null"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <journey-energy-chart
          type="reco"
          :journey-energy-stats="stats.journeyEnergyStats"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <journey-energy-share-chart
          :journey-energy-stats="stats.journeyEnergyStats"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <h2 class="text-h6 q-mt-none q-mb-md">
          {{ t('stats.sections.professional_travel') }}
        </h2>
        <emissions-reductions-chart
          chart-translation-name="reductions_mod_pro"
          :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
          :reductions="stats.emissionsReductions?.['reductions_mod_pro'] ?? null"
          :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
          :height="height"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <h1 class="text-h4 q-mt-xl">
          {{ t('stats.sections.behavioural_changes.title') }}
        </h1>
        <q-markdown
          class="compact text-body2 q-mb-lg"
          :src="t('stats.sections.behavioural_changes.description')"
        />
        <behavior-change-chart
          :height="height"
          type="levers"
          :behavior-change-stats="stats.behaviorChange"
          :percent="percent"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <behavior-change-chart
          :height="height"
          type="motivation"
          :behavior-change-stats="stats.behaviorChange"
          :percent="percent"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <equipment-recommendation-matrix-chart
          :height="height"
          :equipments-stats="stats.equipmentsStats"
          :exportable="false"
        />
      </report-page>

      <report-page :org-names="orgs">
        <h1 class="text-h4">
          {{ t('generated_report.final_page_title') }}
        </h1>

        <h2 class="text-h6">
          {{ t('generated_report.final_page_subtitle') }}
        </h2>

        <q-markdown :src="t('generated_report.final_page_body')" />

        <div class="text-center q-mt-lg">
          <img src="/admin/V1-ROUE_DEM_MOBILITE-MOBILYSE.svg" alt="graph" />
        </div>
      </report-page>
    </div>
  </div>
</template>

<script setup lang="ts">
import ReportPage from 'src/components/ReportPage.vue'
import EquipmentFrequenciesChart from 'src/components/charts/EquipmentFrequenciesChart.vue'
import FrequenciesChart from 'src/components/charts/FrequenciesChart.vue'
import FrequenciesStackChart from 'src/components/charts/FrequenciesStackChart.vue'
import TravelTimeFrequenciesChart from 'src/components/charts/TravelTimeFrequenciesChart.vue'
import LocationChart from 'src/components/charts/LocationChart.vue'
import EmissionsChart from 'src/components/charts/EmissionsChart.vue'
import EmissionsReductionsChart from 'src/components/charts/EmissionsReductionsChart.vue'
import EmissionsReductionsShareChart from 'src/components/charts/EmissionsReductionsShareChart.vue'
import LinksChart from 'src/components/charts/LinksChart.vue'
import ShareChart from 'src/components/charts/ShareChart.vue'
import ModesOfTransportShareChart from 'src/components/charts/ModesOfTransportShareChart.vue'
import JourneyEnergyChart from 'src/components/charts/JourneyEnergyChart.vue'
import JourneyEnergyShareChart from 'src/components/charts/JourneyEnergyShareChart.vue'
import BehaviorChangeChart from 'src/components/charts/BehaviorChangeChart.vue'
import EquipmentRecommendationMatrixChart from 'src/components/charts/EquipmentRecommendationMatrixChart.vue'
import {
  type StatsState,
  flushStateFromLocalStorage,
  getStateFromLocalStorage,
} from 'src/stores/stats'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  percent: boolean
}

withDefaults(defineProps<Props>(), {
  height: 400,
  percent: true,
})

const { t, locale } = useI18n()
const route = useRoute()
const stats = ref<StatsState | null>(null)
const orgs = ref<string[]>([])
const campaigns = ref<string[]>([])

onMounted(() => {
  stats.value = getStateFromLocalStorage(route.query.statsStateId as string)
  orgs.value = (route.query.orgs as string)?.split(';').map(decodeURIComponent) || []
  campaigns.value = (route.query.campaigns as string)?.split(';').map(decodeURIComponent) || []

  window.addEventListener('beforeunload', cleanUpLocalStorage)
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', cleanUpLocalStorage)
  cleanUpLocalStorage()
})

function cleanUpLocalStorage() {
  flushStateFromLocalStorage(route.query.statsStateId as string)
}

const reportDate = computed(() => {
  const df = new Intl.DateTimeFormat(locale.value, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
  return df.format(new Date())
})

const printReport = () => {
  window.print()
}

const getFreq = (key: string) => {
  return (stats.value!.frequencies?.[key] ?? null) as Frequencies | null
}

const getFreqArray = (key: string) => {
  return (stats.value!.frequencies?.[key] ?? null) as Frequencies[] | null
}
</script>

<style scoped>
.report-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  color: black !important;

  counter-reset: page-counter;
}

.toolbar {
  position: sticky;
  top: 0;
  border-bottom: 1px solid var(--half-muted-color);
  z-index: 1000;
}

@media print {
  @page {
    size: A4 portrait;
    margin: 0;
  }

  .print-hide,
  .q-header,
  .q-footer,
  .q-drawer {
    display: none !important;
  }

  .bg-grey-3 {
    background: white !important;
  }

  :deep(.q-dialog),
  :deep(.q-dialog__inner),
  :deep(.q-card) {
    position: static !important;
    display: block !important;
    overflow: visible !important;
    height: auto !important;
    max-height: none !important;
    width: auto !important;
    max-width: none !important;
    transform: none !important;
    box-shadow: none !important;
  }

  .report-container {
    display: block !important;
    width: 100% !important;
    padding: 0 !important;
  }

  :deep(a) {
    color: var(--title-color) !important;
    text-decoration: underline !important;
  }
}
</style>
