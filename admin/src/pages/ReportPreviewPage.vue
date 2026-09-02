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
          :height="height"
          :home-locations-heatmap="stats.homeLocationsHeatmap"
          :workplace-locations="stats.workplaceLocations"
          no-controls
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <freq-mod-chart
          :height="height"
          :simple-frequencies="stats.frequencies?.['freq_mod_simple'] ?? null"
          :detailed-frequencies="stats.frequencies?.['freq_mod_complex'] ?? null"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <travel-time-frequencies-chart
          :frequencies="getFreq('travel_time')"
          :xaxis="t('stats.travel_time.xaxis')"
          :range-step="5"
          :height="height"
          :exportable="false"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <equipment-frequencies-chart
          :frequencies="getFreq('equipments')"
          :height="height"
          :exportable="false"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <mobility-constraints-frequencies-chart
          :frequencies="getFreq('constraints')"
          :height="height"
          :exportable="false"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-mod-chart
          :height="height"
          :simple-emissions="stats.emissions?.['freq_mod_simple'] ?? null"
          :detailed-emissions="stats.emissions?.['freq_mod_complex'] ?? null"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <journey-energy-chart
          type="current"
          :journey-energy-stats="stats.journeyEnergyStats"
          :height="height"
          :exportable="false"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <h2 class="text-h6 q-mt-xl q-mb-md">
          {{ t('stats.sections.professional_travel') }}
        </h2>
        <freq-mod-pro-chart :frequencies="getFreqArray('freq_mod_pro')" :height="height" inline />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-mod-pro-chart
          :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
          :height="height"
          inline
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
        <freq-reco-chart
          :simple-frequencies="getFreq('reco_simple')"
          :detailed-frequencies="getFreq('reco_inter')"
          :height="height"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <links-reco-chart
          :simple-links="stats.links['mod_reco_simple'] ?? null"
          :detailed-links="stats.links['mod_reco_complex'] ?? null"
          :height="height"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-reductions-mod-chart :height="height" inline />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-reductions-mod-share-chart :height="height" inline />
      </report-page>

      <report-page :org-names="orgs">
        <journey-energy-chart
          type="reco"
          :journey-energy-stats="stats.journeyEnergyStats"
          :height="height"
          :exportable="false"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <journey-energy-share-chart
          :journey-energy-stats="stats.journeyEnergyStats"
          :height="height"
          :exportable="false"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <h2 class="text-h6 q-mt-none q-mb-md">
          {{ t('stats.sections.professional_travel') }}
        </h2>
        <freq-reco-pro-chart :frequencies="getFreq('reco_pros')" :height="height" inline />
      </report-page>

      <report-page :org-names="orgs">
        <emissions-reductions-mod-pro-chart
          :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
          :reductions="stats.emissionsReductions?.['reductions_mod_pro'] ?? null"
          :height="height"
          inline
        />
      </report-page>

      <report-page v-if="stats.comparisonMode === 'longitudinal'" :org-names="orgs">
        <modal-evolution-sankey :height="height" :exportable="false" inline />
      </report-page>

      <report-page :org-names="orgs">
        <h1 class="text-h4 q-mt-xl">
          {{ t('stats.sections.behavioural_changes.title') }}
        </h1>
        <q-markdown
          class="compact text-body2 q-mb-lg"
          :src="t('stats.sections.behavioural_changes.description')"
        />
        <levers-change-chart
          :height="height"
          :behavior-change-stats="stats.behaviorChange"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <motivation-change-chart
          :height="height"
          :behavior-change-stats="stats.behaviorChange"
          inline
        />
      </report-page>

      <report-page :org-names="orgs">
        <equipment-recommendation-matrix-chart
          :height="height"
          :equipments-stats="stats.equipmentsStats"
          :exportable="false"
          inline
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
import ReportPage from '@/components/ReportPage.vue'
import EquipmentFrequenciesChart from '@/components/charts/EquipmentFrequenciesChart.vue'
import MobilityConstraintsFrequenciesChart from '@/components/charts/MobilityConstraintsFrequenciesChart.vue'
import TravelTimeFrequenciesChart from '@/components/charts/TravelTimeFrequenciesChart.vue'
import LocationChart from '@/components/charts/LocationChart.vue'
import FreqModChart from '@/components/charts/FreqModChart.vue'
import FreqModProChart from '@/components/charts/FreqModProChart.vue'
import FreqRecoChart from '@/components/charts/FreqRecoChart.vue'
import FreqRecoProChart from '@/components/charts/FreqRecoProChart.vue'
import EmissionsModChart from '@/components/charts/EmissionsModChart.vue'
import EmissionsModProChart from '@/components/charts/EmissionsModProChart.vue'
import EmissionsReductionsModChart from '@/components/charts/EmissionsReductionsModChart.vue'
import EmissionsReductionsModProChart from '@/components/charts/EmissionsReductionsModProChart.vue'
import EmissionsReductionsModShareChart from '@/components/charts/EmissionsReductionsModShareChart.vue'
import LinksRecoChart from '@/components/charts/LinksRecoChart.vue'
import JourneyEnergyChart from '@/components/charts/JourneyEnergyChart.vue'
import JourneyEnergyShareChart from '@/components/charts/JourneyEnergyShareChart.vue'
import LeversChangeChart from '@/components/charts/LeversChangeChart.vue'
import MotivationChangeChart from '@/components/charts/MotivationChangeChart.vue'
import EquipmentRecommendationMatrixChart from '@/components/charts/EquipmentRecommendationMatrixChart.vue'
import ModalEvolutionSankey from '@/components/charts/ModalEvolutionSankey.vue'
import { type StatsState, flushStateFromIndexedDB, getStateFromIndexedDB } from '@/stores/stats'
import type { Frequencies } from '@/models'

interface Props {
  height: number
}

withDefaults(defineProps<Props>(), {
  height: 400,
})

const { t, locale } = useI18n()
const route = useRoute()
const statsStore = useStats()
const stats = ref<StatsState | null>(null)
const orgs = ref<string[]>([])
const campaigns = ref<string[]>([])

onMounted(async () => {
  stats.value = await getStateFromIndexedDB(route.query.statsStateId as string)
  orgs.value = (route.query.orgs as string)?.split(';').map(decodeURIComponent) || []
  campaigns.value = (route.query.campaigns as string)?.split(';').map(decodeURIComponent) || []
  statsStore.freqModalType = (route.query.freqModalType as string) || 'simple'
  statsStore.emModalType = (route.query.emModalType as string) || 'simple'
  statsStore.redModalType = (route.query.redModalType as string) || 'simple'
  statsStore.redShareModalType = (route.query.redShareModalType as string) || 'simple'
  statsStore.linksModalType = (route.query.linksModalType as string) || 'simple'
  statsStore.recoModalType = (route.query.recoModalType as string) || 'simple'
  statsStore.leversModalType = (route.query.leversModalType as string) || 'simple'
  statsStore.motivationModalType = (route.query.motivationModalType as string) || 'simple'
  statsStore.equipmentsModalType = (route.query.equipmentsModalType as string) || 'simple'
  statsStore.recoProModalType = (route.query.recoProModalType as string) || 'simple'
  statsStore.freqProModalType = (route.query.freqProModalType as string) || 'simple'
  statsStore.emProModalType = (route.query.emProModalType as string) || 'simple'
  statsStore.redProModalType = (route.query.redProModalType as string) || 'simple'

  statsStore.travelTimePercent = route.query.travelTimePercent !== 'false'
  statsStore.equipmentsPercent = route.query.equipmentsPercent !== 'false'
  statsStore.constraintsPercent = route.query.constraintsPercent !== 'false'
  statsStore.freqModProPercent = route.query.freqModProPercent !== 'false'
  statsStore.leversPercent = route.query.leversPercent !== 'false'
  statsStore.motivationPercent = route.query.motivationPercent !== 'false'

  // EmissionsReductionsModChart/EmissionsReductionsModShareChart, and every chart's
  // comparison-mode rendering, read these directly from the store
  if (stats.value) {
    statsStore.emissions = stats.value.emissions
    statsStore.emissionsReductions = stats.value.emissionsReductions
    statsStore.comparisonResults = stats.value.comparisonResults
    statsStore.comparisonMode = stats.value.comparisonMode
    statsStore.privacyWarnings = stats.value.privacyWarnings
  }

  window.addEventListener('beforeunload', cleanUpLocalStorage)
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', cleanUpLocalStorage)
  cleanUpLocalStorage()
})

function cleanUpLocalStorage() {
  void flushStateFromIndexedDB(route.query.statsStateId as string)
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
