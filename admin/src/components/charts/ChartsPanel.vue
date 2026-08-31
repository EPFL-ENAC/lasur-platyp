<template>
  <div>
    <q-tabs
      v-model="tab"
      dense
      no-caps
      class="text-grey"
      active-color="secondary"
      active-bg-color="grey-4"
      indicator-color="primary"
      align="left"
      @update:model-value="onTabChanged"
    >
      <q-tab name="analysis" :label="t('stats.sections.mobility_analysis.title')" />
      <q-tab name="potentials" :label="t('stats.sections.mobility_potentials.title')" />
      <q-tab name="behavioural" :label="t('stats.sections.behavioural_changes.title')" />
    </q-tabs>
    <q-tab-panels v-model="tab">
      <q-tab-panel name="analysis" class="q-px-none">
        <div class="text-h5 q-mb-md">{{ t('stats.sections.mobility_analysis.title') }}</div>
        <q-markdown
          class="compact q-mt-sm"
          :src="t('stats.sections.mobility_analysis.description')"
        />
        <details-panel class="q-mb-md">
          <q-markdown class="compact" :src="t('stats.sections.mobility_analysis.details')" />
        </details-panel>

        <div class="text-h6 q-my-md">
          {{ t('stats.sections.mobility_analysis.title') }} -
          {{ t('stats.sections.home_to_work') }}
        </div>
        <div class="grid-container">
          <location-chart
            :height="height"
            :home-locations-heatmap="stats.homeLocationsHeatmap"
            :workplace-locations="stats.workplaceLocations"
          />
          <freq-mod-chart
            :height="height"
            :simple-frequencies="stats.frequencies?.['freq_mod_simple'] ?? null"
            :detailed-frequencies="stats.frequencies?.['freq_mod_complex'] ?? null"
            :loading="stats.loading"
          />
          <travel-time-frequencies-chart
            :frequencies="getFreq('travel_time')"
            :xaxis="t('stats.travel_time.xaxis')"
            :range-step="5"
            :height="height"
            :loading="stats.loading"
          />
          <equipment-frequencies-chart
            :frequencies="getFreq('equipments')"
            :height="height"
            :loading="stats.loading"
          />
          <mobility-constraints-frequencies-chart
            :frequencies="getFreq('constraints')"
            :height="height"
            :loading="stats.loading"
          />
          <emissions-mod-chart
            :height="height"
            :simple-emissions="stats.emissions?.['freq_mod_simple'] ?? null"
            :detailed-emissions="stats.emissions?.['freq_mod_complex'] ?? null"
            :loading="stats.loading"
          />
          <journey-energy-chart
            type="current"
            :journey-energy-stats="stats.journeyEnergyStats"
            :height="height"
            :loading="stats.loading"
          />
        </div>
        <div class="text-h6 q-my-md">
          {{ t('stats.sections.mobility_analysis.title') }} -
          {{ t('stats.sections.professional_travel') }}
        </div>
        <div class="grid-container">
          <freq-mod-pro-chart
            :frequencies="getFreqArray('freq_mod_pro')"
            :height="height"
            :loading="stats.loading"
          />
          <emissions-mod-pro-chart
            :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
            :height="height"
            :loading="stats.loading"
          />
        </div>
      </q-tab-panel>
      <q-tab-panel name="potentials" class="q-px-none">
        <div class="text-h5" data-section-name="mobility_potentials" expand-icon-toggle>
          {{ t('stats.sections.mobility_potentials.title') }}
        </div>
        <q-markdown
          class="compact q-mt-sm"
          :src="t('stats.sections.mobility_potentials.description')"
        />
        <details-panel class="q-mb-md">
          <mobility-potential-insights
            frequency-key="reco_inter"
            :reduction-key="
              stats.redModalType === 'simple' ? 'reductions_mod_simple' : 'reductions_mod_complex'
            "
            :collaborators-count="collaboratorsCount || undefined"
            class="q-mb-md"
          />
        </details-panel>

        <div class="text-h6 q-my-md">
          {{ t('stats.sections.mobility_potentials.title') }} -
          {{ t('stats.sections.home_to_work') }}
        </div>
        <div class="grid-container">
          <freq-reco-chart
            :simple-frequencies="getFreq('reco_simple')"
            :detailed-frequencies="getFreq('reco_inter')"
            :height="height"
            :loading="stats.loading"
          />
          <links-reco-chart
            :simple-links="stats.links['mod_reco_simple'] ?? null"
            :detailed-links="stats.links['mod_reco_complex'] ?? null"
            :height="height"
            :loading="stats.loading"
          />
          <emissions-reductions-mod-chart :height="height" :loading="stats.loading" />
          <emissions-reductions-mod-share-chart :height="height" :loading="stats.loading" />
          <journey-energy-chart
            type="reco"
            :height="height"
            :journey-energy-stats="stats.journeyEnergyStats"
            :loading="stats.loading"
          />
          <journey-energy-share-chart
            :journeyEnergyStats="stats.journeyEnergyStats"
            :height="height"
            :loading="stats.loading"
          />
        </div>

        <div class="text-h6 q-my-md">
          {{ t('stats.sections.mobility_potentials.title') }} -
          {{ t('stats.sections.professional_travel') }}
        </div>
        <div class="grid-container">
          <freq-reco-pro-chart
            :frequencies="getFreq('reco_pros')"
            :height="height"
            :loading="stats.loading"
          />
          <emissions-reductions-mod-pro-chart
            :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
            :reductions="stats.emissionsReductions?.['reductions_mod_pro'] ?? null"
            :height="height"
            :loading="stats.loading"
          />
        </div>

        <modal-evolution-sankey
          v-if="stats.comparisonMode === 'longitudinal'"
          :height="height"
          :loading="stats.loading"
          class="q-mt-md"
        />
      </q-tab-panel>
      <q-tab-panel name="behavioural" class="q-px-none">
        <div class="text-h5" data-section-name="behavioural_changes" expand-icon-toggle>
          {{ t('stats.sections.behavioural_changes.title') }}
        </div>
        <q-markdown
          class="compact q-pb-md q-mt-sm"
          :src="t('stats.sections.behavioural_changes.description')"
        />
        <div class="grid-container">
          <levers-change-chart
            :behavior-change-stats="stats.behaviorChange"
            :height="height"
            :loading="stats.loading"
          />
          <motivation-change-chart
            :behavior-change-stats="stats.behaviorChange"
            :height="height"
            :loading="stats.loading"
          />
          <equipment-recommendation-matrix-chart
            class="grid-item-full-row"
            :equipmentsStats="stats.equipmentsStats"
            :height="height"
            :loading="stats.loading"
            has-options
          />
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>
<script setup lang="ts">
import DetailsPanel from '@/components/DetailsPanel.vue'
import EquipmentFrequenciesChart from '@/components/charts/EquipmentFrequenciesChart.vue'
import MobilityConstraintsFrequenciesChart from './MobilityConstraintsFrequenciesChart.vue'
import TravelTimeFrequenciesChart from '@/components/charts/TravelTimeFrequenciesChart.vue'
import LocationChart from '@/components/charts/LocationChart.vue'
import EmissionsModChart from '@/components/charts/EmissionsModChart.vue'
import EmissionsModProChart from '@/components/charts/EmissionsModProChart.vue'
import EmissionsReductionsModChart from '@/components/charts/EmissionsReductionsModChart.vue'
import EmissionsReductionsModProChart from '@/components/charts/EmissionsReductionsModProChart.vue'
import EmissionsReductionsModShareChart from '@/components/charts/EmissionsReductionsModShareChart.vue'
import LinksRecoChart from '@/components/charts/LinksRecoChart.vue'
import FreqModChart from '@/components/charts/FreqModChart.vue'
import FreqRecoChart from '@/components/charts/FreqRecoChart.vue'
import FreqRecoProChart from '@/components/charts/FreqRecoProChart.vue'
import FreqModProChart from '@/components/charts/FreqModProChart.vue'
import JourneyEnergyChart from '@/components/charts/JourneyEnergyChart.vue'
import JourneyEnergyShareChart from '@/components/charts/JourneyEnergyShareChart.vue'
import LeversChangeChart from '@/components/charts/LeversChangeChart.vue'
import MotivationChangeChart from '@/components/charts/MotivationChangeChart.vue'
import EquipmentRecommendationMatrixChart from '@/components/charts/EquipmentRecommendationMatrixChart.vue'
import ModalEvolutionSankey from '@/components/charts/ModalEvolutionSankey.vue'
import MobilityPotentialInsights from '../MobilityPotentialInsights.vue'
import type { Frequencies } from '@/models'

interface Props {
  height: number
  collaboratorsCount?: number | undefined
}

defineProps<Props>()

const { t } = useI18n()
const preferencesStore = usePreferencesStore()
const stats = useStats()

const tab = ref('analysis')

onMounted(() => {
  if (preferencesStore.statsSectionsExpandedState.mobilityAnalysis) {
    tab.value = 'analysis'
  } else if (preferencesStore.statsSectionsExpandedState.mobilityPotentials) {
    tab.value = 'potentials'
  } else if (preferencesStore.statsSectionsExpandedState.behaviouralChanges) {
    tab.value = 'behavioural'
  }
})

const getFreq = (key: string) => {
  return (stats.frequencies?.[key] ?? null) as Frequencies | null
}

const getFreqArray = (key: string) => {
  return (stats.frequencies?.[key] ?? null) as Frequencies[] | null
}

const onTabChanged = (newTab: string) => {
  preferencesStore.statsSectionsExpandedState.mobilityAnalysis = newTab === 'analysis'
  preferencesStore.statsSectionsExpandedState.mobilityPotentials = newTab === 'potentials'
  preferencesStore.statsSectionsExpandedState.behaviouralChanges = newTab === 'behavioural'
}
</script>

<style lang="css" scoped>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  gap: 2rem;
}

.grid-item-full-row {
  grid-column: 1 / -1;
}
</style>
