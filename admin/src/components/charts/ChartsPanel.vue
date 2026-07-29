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
      <q-tab-panel name="analysis">
        <div class="text-h5 q-mb-md">{{ t('stats.sections.mobility_analysis.title') }}</div>
        <q-markdown
          class="compact q-mt-sm"
          :src="t('stats.sections.mobility_analysis.description')"
        />
        <details-panel class="q-mb-md">
          <q-markdown class="compact" :src="t('stats.sections.mobility_analysis.details')" />
        </details-panel>

        <div class="text-h6 q-my-md">{{ t('stats.sections.home_to_work') }}</div>
        <div class="grid-container">
          <chart-panel
            :title="t('stats.locations_heatmap.title')"
            description="stats.locations_heatmap.description"
            details="stats.locations_heatmap.details"
          >
            <location-chart
              :title="t('stats.locations_heatmap.title')"
              :height="height"
              :home-locations-heatmap="stats.homeLocationsHeatmap"
              :workplace-locations="stats.workplaceLocations"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.freq_mod.title')"
            description="stats.freq_mod.description"
            details="stats.freq_mod.details"
          >
            <div>
              <q-btn-toggle
                v-model="freqModalType"
                :options="[
                  { label: t('stats.freq_mod.modal_split.simple'), value: 'simple' },
                  { label: t('stats.freq_mod.modal_split.detailed'), value: 'detailed' },
                ]"
                outlined
                unelevated
                no-caps
                color="grey"
                toggle-color="primary"
              />
            </div>
            <simple-labels-share-chart
              v-if="freqModalType === 'simple'"
              :height="height"
              :frequencies="stats.frequencies?.['freq_mod_simple'] ?? null"
              :loading="stats.loading"
            />
            <complex-labels-share-chart
              v-if="freqModalType === 'detailed'"
              :height="height"
              :frequencies="stats.frequencies?.['freq_mod_complex'] ?? null"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.travel_time.title')"
            description="stats.travel_time.description"
            details="stats.travel_time.details"
          >
            <travel-time-frequencies-chart
              :frequencies="getFreq('travel_time')"
              :xaxis="t('stats.travel_time.xaxis')"
              :range-step="5"
              :percent="percent"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.equipments.title')"
            description="stats.equipments.description"
            details="stats.equipments.details"
          >
            <equipment-frequencies-chart
              :frequencies="getFreq('equipments')"
              :percent="percent"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.constraints.title')"
            description="stats.constraints.description"
            details="stats.constraints.details"
          >
            <mobility-constraints-frequencies-chart
              :frequencies="getFreq('constraints')"
              :percent="percent"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.emissions.title')"
            description="stats.emissions.description"
            details="stats.emissions.details"
          >
            <div>
              <q-btn-toggle
                v-model="emModalType"
                :options="[
                  { label: t('stats.freq_mod.modal_split.simple'), value: 'simple' },
                  { label: t('stats.freq_mod.modal_split.detailed'), value: 'detailed' },
                ]"
                outlined
                unelevated
                no-caps
                color="grey"
                toggle-color="primary"
              />
            </div>
            <emissions-chart
              v-if="emModalType === 'simple'"
              chartTranslationName="freq_mod_simple"
              :emissions="stats.emissions?.['freq_mod_simple'] ?? null"
              :xaxis="t('stats.emissions_freq_mod_simple.xaxis')"
              :yaxis="t('stats.emissions_freq_mod_simple.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
            <emissions-chart
              v-if="emModalType === 'detailed'"
              chartTranslationName="freq_mod_complex"
              :emissions="stats.emissions?.['freq_mod_complex'] ?? null"
              :xaxis="t('stats.emissions_freq_mod_complex.xaxis')"
              :yaxis="t('stats.emissions_freq_mod_complex.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.journey_energy.title')"
            description="stats.journey_energy.description"
            details="stats.journey_energy.details"
          >
            <journey-energy-chart
              type="current"
              :journey-energy-stats="stats.journeyEnergyStats"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
        </div>
        <div class="text-h6 q-my-md">{{ t('stats.sections.professional_travel') }}</div>
        <div class="grid-container">
          <chart-panel
            :title="t('stats.freq_mod_pro.title')"
            description="stats.freq_mod_pro.description"
            details="stats.freq_mod_pro.details"
          >
            <frequencies-stack-chart
              chartTranslationName="freq_mod_pro"
              :frequencies="getFreqArray('freq_mod_pro')"
              :groups="['local', 'national', 'europe', 'inter']"
              :xaxis="t('stats.freq_mod_pro.xaxis')"
              :height="height"
              :percent="percent"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.emissions_freq_mod_pro.title')"
            description="stats.emissions_freq_mod_pro.description"
            details="stats.emissions_freq_mod_pro.details"
          >
            <emissions-chart
              chartTranslationName="freq_mod_pro"
              :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
              :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
              :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
        </div>
      </q-tab-panel>
      <q-tab-panel name="potentials">
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
              redModalType === 'simple' ? 'reductions_mod_simple' : 'reductions_mod_complex'
            "
            :collaborators-count="collaboratorsCount || undefined"
            class="q-mb-md"
          />
        </details-panel>

        <div class="text-h6 q-my-md">{{ t('stats.sections.home_to_work') }}</div>
        <div class="grid-container">
          <chart-panel
            :title="t('stats.sections.home_to_work.title')"
            description="stats.sections.home_to_work.description"
            details="stats.sections.home_to_work.details"
          >
            <share-chart
              chartTranslationName="reco_inter"
              :frequencies="getFreq('reco_inter')"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.home_to_work.links.title')"
            description="stats.sections.home_to_work.links.description"
            details="stats.sections.home_to_work.links.details"
          >
            <links-chart
              type="mod_reco"
              :links="stats.links['mod_reco'] ?? null"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.home_to_work.reductions.title')"
            description="stats.sections.home_to_work.reductions.description"
            details="stats.sections.home_to_work.reductions.details"
          >
            <div>
              <q-btn-toggle
                v-model="redModalType"
                :options="[
                  { label: t('stats.freq_mod.modal_split.simple'), value: 'simple' },
                  { label: t('stats.freq_mod.modal_split.detailed'), value: 'detailed' },
                ]"
                outlined
                unelevated
                no-caps
                color="grey"
                toggle-color="primary"
              />
            </div>
            <emissions-reductions-chart
              v-if="redModalType === 'simple'"
              chartTranslationName="reductions_mod_simple"
              :emissions="stats.emissions?.['freq_mod_simple'] ?? null"
              :reductions="stats.emissionsReductions?.['reductions_mod_simple'] ?? null"
              :yaxis="t('stats.emissions_reductions_mod_simple.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
            <emissions-reductions-chart
              v-if="redModalType === 'detailed'"
              chartTranslationName="reductions_mod_complex"
              :emissions="stats.emissions?.['freq_mod_complex'] ?? null"
              :reductions="stats.emissionsReductions?.['reductions_mod_complex'] ?? null"
              :yaxis="t('stats.emissions_reductions_mod_complex.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.home_to_work.reductions_share.title')"
            description="stats.sections.home_to_work.reductions_share.description"
            details="stats.sections.home_to_work.reductions_share.details"
          >
            <div>
              <q-btn-toggle
                v-model="redShareModalType"
                :options="[
                  { label: t('stats.freq_mod.modal_split.simple'), value: 'simple' },
                  { label: t('stats.freq_mod.modal_split.detailed'), value: 'detailed' },
                ]"
                outlined
                unelevated
                no-caps
                color="grey"
                toggle-color="primary"
              />
            </div>
            <emissions-reductions-share-chart
              v-if="redShareModalType === 'simple'"
              chartTranslationName="reductions_share_simple"
              :reductions="stats.emissionsReductions?.['reductions_mod_simple'] ?? null"
              :height="height"
              :loading="stats.loading"
            />
            <emissions-reductions-share-chart
              v-if="redShareModalType === 'detailed'"
              chartTranslationName="reductions_share_complex"
              :reductions="stats.emissionsReductions?.['reductions_mod_complex'] ?? null"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.home_to_work.journey_energy.title')"
            description="stats.sections.home_to_work.journey_energy.description"
            details="stats.sections.home_to_work.journey_energy.details"
          >
            <journey-energy-chart
              type="reco"
              :height="height"
              :journey-energy-stats="stats.journeyEnergyStats"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.home_to_work.journey_energy_share.title')"
            description="stats.sections.home_to_work.journey_energy_share.description"
            details="stats.sections.home_to_work.journey_energy_share.details"
          >
            <journey-energy-share-chart
              :journeyEnergyStats="stats.journeyEnergyStats"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
        </div>

        <div class="text-h6 q-my-md">{{ t('stats.sections.professional_travel') }}</div>
        <div class="grid-container">
          <chart-panel
            :title="t('stats.sections.professional_travel.share.title')"
            description="stats.sections.professional_travel.share.description"
            details="stats.sections.professional_travel.share.details"
          >
            <share-chart
              chartTranslationName="reco_pros"
              :height="height"
              :frequencies="getFreq('reco_pros')"
              :loading="stats.loading"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.professional_travel.reductions.title')"
            description="stats.sections.professional_travel.reductions.description"
            details="stats.sections.professional_travel.reductions.details"
          >
            <emissions-reductions-chart
              chartTranslationName="reductions_mod_pro"
              :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
              :reductions="stats.emissionsReductions?.['reductions_mod_pro'] ?? null"
              :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
          </chart-panel>
        </div>
      </q-tab-panel>
      <q-tab-panel name="behavioural">
        <div class="text-h5" data-section-name="behavioural_changes" expand-icon-toggle>
          {{ t('stats.sections.behavioural_changes.title') }}
        </div>
        <q-markdown
          class="compact q-pb-md q-mt-sm"
          :src="t('stats.sections.behavioural_changes.description')"
        />
        <div class="grid-container">
          <chart-panel
            :title="t('stats.sections.behavioural_changes.levers.title')"
            description="stats.sections.behavioural_changes.levers.description"
            details="stats.sections.behavioural_changes.levers.details"
          >
            <behavior-change-chart
              type="levers"
              :behavior-change-stats="stats.behaviorChange"
              :height="height"
              :loading="stats.loading"
              :percent="percent"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.behavioural_changes.motivation.title')"
            description="stats.sections.behavioural_changes.motivation.description"
            details="stats.sections.behavioural_changes.motivation.details"
          >
            <behavior-change-chart
              type="motivation"
              :behavior-change-stats="stats.behaviorChange"
              :height="height"
              :loading="stats.loading"
              :percent="percent"
            />
          </chart-panel>
          <chart-panel
            :title="t('stats.sections.behavioural_changes.equipment.title')"
            description="stats.sections.behavioural_changes.equipment.description"
            details="stats.sections.behavioural_changes.equipment.details"
          >
            <equipment-recommendation-matrix-chart
              :equipmentsStats="stats.equipmentsStats"
              :height="height"
              :loading="stats.loading"
              has-options
            />
          </chart-panel>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>
<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import DetailsPanel from 'src/components/DetailsPanel.vue'
import EquipmentFrequenciesChart from 'src/components/charts/EquipmentFrequenciesChart.vue'
import MobilityConstraintsFrequenciesChart from './MobilityConstraintsFrequenciesChart.vue'
import FrequenciesStackChart from 'src/components/charts/FrequenciesStackChart.vue'
import TravelTimeFrequenciesChart from 'src/components/charts/TravelTimeFrequenciesChart.vue'
import LocationChart from 'src/components/charts/LocationChart.vue'
import EmissionsChart from 'src/components/charts/EmissionsChart.vue'
import EmissionsReductionsChart from 'src/components/charts/EmissionsReductionsChart.vue'
import EmissionsReductionsShareChart from 'src/components/charts/EmissionsReductionsShareChart.vue'
import LinksChart from 'src/components/charts/LinksChart.vue'
import ShareChart from 'src/components/charts/ShareChart.vue'
import SimpleLabelsShareChart from 'src/components/charts/SimpleLabelsShareChart.vue'
import ComplexLabelsShareChart from 'src/components/charts/ComplexLabelsShareChart.vue'
import JourneyEnergyChart from 'src/components/charts/JourneyEnergyChart.vue'
import JourneyEnergyShareChart from 'src/components/charts/JourneyEnergyShareChart.vue'
import BehaviorChangeChart from 'src/components/charts/BehaviorChangeChart.vue'
import EquipmentRecommendationMatrixChart from 'src/components/charts/EquipmentRecommendationMatrixChart.vue'
import MobilityPotentialInsights from '../MobilityPotentialInsights.vue'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  percent: boolean
  collaboratorsCount?: number | undefined
}

defineProps<Props>()

const { t } = useI18n()
const preferencesStore = usePreferencesStore()
const stats = useStats()

const tab = ref('analysis')

const freqModalType = ref('simple')
const emModalType = ref('simple')
const redModalType = ref('simple')
const redShareModalType = ref('simple')

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

defineExpose({
  freqModalType,
  emModalType,
  redModalType,
  redShareModalType,
})
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
