<template>
  <q-card flat class="q-my-md">
    <q-expansion-item
      v-model="preferencesStore.statsSectionsExpandedState.mobilityAnalysis"
      :label="t('stats.sections.mobility_analysis.title')"
      header-class="text-h5"
      data-section-name="mobility_analysis"
      expand-icon-toggle
    >
      <q-markdown
        class="compact text-caption q-px-md q-pb-md q-mt-sm"
        :src="t('stats.sections.mobility_analysis.description')"
      />
      <q-separator />
      <q-card-section>
        <h6 class="text-h6 q-mt-none q-mb-md">{{ t('stats.sections.home_to_work') }}</h6>
        <div class="grid-container">
          <div>
            <location-chart
              :title="t('stats.locationsHeatmap.title')"
              :height="height"
              :home-locations-heatmap="stats.homeLocationsHeatmap"
              :workplace-locations="stats.workplaceLocations"
            />
          </div>
          <div>
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
          </div>
          <div>
            <travel-time-frequencies-chart
              :frequencies="getFreq('travel_time')"
              :xaxis="t('stats.travel_time.xaxis')"
              :range-step="5"
              :percent="percent"
              :height="height"
              :loading="stats.loading"
            />
          </div>
          <div>
            <equipment-frequencies-chart
              :frequencies="getFreq('equipments')"
              :percent="percent"
              :height="height"
              :loading="stats.loading"
            />
          </div>
          <div>
            <mobility-constraints-frequencies-chart
              :frequencies="getFreq('constraints')"
              :percent="percent"
              :height="height"
              :loading="stats.loading"
            />
          </div>
          <div>
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
          </div>
          <div>
            <journey-energy-chart
              type="current"
              :journey-energy-stats="stats.journeyEnergyStats"
              :height="height"
              :loading="stats.loading"
            />
          </div>
        </div>
      </q-card-section>
      <q-card-section>
        <h6 class="text-h6 q-mt-none q-mb-md">{{ t('stats.sections.professional_travel') }}</h6>
        <div class="grid-container">
          <div>
            <frequencies-stack-chart
              chartTranslationName="freq_mod_pro"
              :frequencies="getFreqArray('freq_mod_pro')"
              :groups="['local', 'national', 'europe', 'inter']"
              :xaxis="t('stats.freq_mod_pro.xaxis')"
              :height="height"
              :percent="percent"
              :loading="stats.loading"
            />
          </div>
          <div>
            <emissions-chart
              chartTranslationName="freq_mod_pro"
              :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
              :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
              :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-expansion-item>
  </q-card>

  <q-card flat class="q-my-md">
    <q-expansion-item
      v-model="preferencesStore.statsSectionsExpandedState.mobilityPotentials"
      :label="t('stats.sections.mobility_potentials.title')"
      header-class="text-h5"
      data-section-name="mobility_potentials"
      expand-icon-toggle
    >
      <q-markdown
        class="compact text-caption q-px-md q-pb-md q-mt-sm"
        :src="t('stats.sections.mobility_potentials.description')"
      />
      <mobility-potential-insights
        frequency-key="reco_inter"
        :reduction-key="redModalType === 'simple' ? 'reductions_mod_simple' : 'reductions_mod_complex'"
        :collaborators-count="collaboratorsCount || undefined"
      />
      <q-separator />

      <q-card-section>
        <h6 class="text-h6 q-mt-none q-mb-md">{{ t('stats.sections.home_to_work') }}</h6>
        <div class="grid-container">
          <div>
            <share-chart
              chartTranslationName="reco_inter"
              :frequencies="getFreq('reco_inter')"
              :height="height"
              :loading="stats.loading"
            />
          </div>
          <div>
            <links-chart
              type="mod_reco"
              :links="stats.links['mod_reco'] ?? null"
              :height="height"
              :loading="stats.loading"
            />
          </div>
          <div>
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
          </div>
          <div>
            <emissions-reductions-share-chart
              v-if="redModalType === 'simple'"
              chartTranslationName="reductions_share_simple"
              :reductions="stats.emissionsReductions?.['reductions_mod_simple'] ?? null"
              :height="height"
              :loading="stats.loading"
            />
            <emissions-reductions-share-chart
              v-if="redModalType === 'detailed'"
              chartTranslationName="reductions_share_complex"
              :reductions="stats.emissionsReductions?.['reductions_mod_complex'] ?? null"
              :height="height"
              :loading="stats.loading"
            />
          </div>
          <div>
            <journey-energy-chart
              type="reco"
              :height="height"
              :journey-energy-stats="stats.journeyEnergyStats"
              :loading="stats.loading"
            />
          </div>
          <div>
            <journey-energy-share-chart
              :journeyEnergyStats="stats.journeyEnergyStats"
              :height="height"
              :loading="stats.loading"
            />
          </div>
        </div>
      </q-card-section>

      <q-card-section>
        <h6 class="text-h6 q-mt-none q-mb-md">{{ t('stats.sections.professional_travel') }}</h6>
        <div class="grid-container">
          <div>
            <share-chart
              chartTranslationName="reco_pros"
              :height="height"
              :frequencies="getFreq('reco_pros')"
              :loading="stats.loading"
            />
          </div>
          <div>
            <emissions-reductions-chart
              chartTranslationName="reductions_mod_pro"
              :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
              :reductions="stats.emissionsReductions?.['reductions_mod_pro'] ?? null"
              :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
              :height="height"
              :loading="stats.loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-expansion-item>
  </q-card>

  <q-card flat class="q-my-md">
    <q-expansion-item
      v-model="preferencesStore.statsSectionsExpandedState.behaviouralChanges"
      :label="t('stats.sections.behavioural_changes.title')"
      header-class="text-h5"
      data-section-name="behavioural_changes"
      expand-icon-toggle
    >
      <q-markdown
        class="compact text-caption q-px-md q-pb-md q-mt-sm"
        :src="t('stats.sections.behavioural_changes.description')"
      />
      <q-separator />

      <q-card-section>
        <div class="grid-container">
          <div>
            <behavior-change-chart
              type="levers"
              :behavior-change-stats="stats.behaviorChange"
              :height="height"
              :loading="stats.loading"
              :percent="percent"
            />
          </div>
          <div>
            <behavior-change-chart
              type="motivation"
              :behavior-change-stats="stats.behaviorChange"
              :height="height"
              :loading="stats.loading"
              :percent="percent"
            />
          </div>
          <div>
            <equipment-recommendation-matrix-chart
              :equipmentsStats="stats.equipmentsStats"
              :height="height"
              :loading="stats.loading"
              has-options
            />
          </div>
        </div>
      </q-card-section>
    </q-expansion-item>
  </q-card>
</template>
<script setup lang="ts">
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

const freqModalType = ref('simple')
const emModalType = ref('simple')
const redModalType = ref('simple')

const getFreq = (key: string) => {
  return (stats.frequencies?.[key] ?? null) as Frequencies | null
}

const getFreqArray = (key: string) => {
  return (stats.frequencies?.[key] ?? null) as Frequencies[] | null
}
</script>

<style lang="css" scoped>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  gap: 2rem;
}
</style>
