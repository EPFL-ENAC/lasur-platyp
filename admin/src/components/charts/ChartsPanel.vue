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
          class="compact q-pb-md q-mt-sm"
          :src="t('stats.sections.mobility_analysis.description')"
        />
        <q-separator />
        <div class="text-h6 q-my-md">{{ t('stats.sections.home_to_work') }}</div>
        <div class="grid-container">
          <q-card flat>
            <q-card-section>
              <location-chart
                :title="t('stats.locationsHeatmap.title')"
                :height="height"
                :home-locations-heatmap="stats.homeLocationsHeatmap"
                :workplace-locations="stats.workplaceLocations"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
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
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <travel-time-frequencies-chart
                :frequencies="getFreq('travel_time')"
                :xaxis="t('stats.travel_time.xaxis')"
                :range-step="5"
                :percent="percent"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <equipment-frequencies-chart
                :frequencies="getFreq('equipments')"
                :percent="percent"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <mobility-constraints-frequencies-chart
                :frequencies="getFreq('constraints')"
                :percent="percent"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
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
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <journey-energy-chart
                type="current"
                :journey-energy-stats="stats.journeyEnergyStats"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
        </div>
        <div class="text-h6 q-my-md">{{ t('stats.sections.professional_travel') }}</div>
        <div class="grid-container">
          <q-card flat>
            <q-card-section>
              <frequencies-stack-chart
                chartTranslationName="freq_mod_pro"
                :frequencies="getFreqArray('freq_mod_pro')"
                :groups="['local', 'national', 'europe', 'inter']"
                :xaxis="t('stats.freq_mod_pro.xaxis')"
                :height="height"
                :percent="percent"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <emissions-chart
                chartTranslationName="freq_mod_pro"
                :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
                :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
                :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
        </div>
      </q-tab-panel>
      <q-tab-panel name="potentials">
        <div class="text-h5">
          {{ t('stats.sections.mobility_potentials.title') }}
        </div>
        <q-markdown
          class="compact q-pb-md q-mt-sm"
          :src="t('stats.sections.mobility_potentials.description')"
        />
        <mobility-potential-insights
          frequency-key="reco_inter"
          :reduction-key="
            redModalType === 'simple' ? 'reductions_mod_simple' : 'reductions_mod_complex'
          "
          :collaborators-count="collaboratorsCount || undefined"
          class="q-mb-md"
        />
        <q-separator />

        <div class="text-h6 q-my-md">{{ t('stats.sections.home_to_work') }}</div>
        <div class="grid-container">
          <q-card flat>
            <q-card-section>
              <share-chart
                chartTranslationName="reco_inter"
                :frequencies="getFreq('reco_inter')"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <links-chart
                type="mod_reco"
                :links="stats.links['mod_reco'] ?? null"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
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
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
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
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <journey-energy-chart
                type="reco"
                :height="height"
                :journey-energy-stats="stats.journeyEnergyStats"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <journey-energy-share-chart
                :journeyEnergyStats="stats.journeyEnergyStats"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
        </div>

        <div class="text-h6 q-my-md">{{ t('stats.sections.professional_travel') }}</div>
        <div class="grid-container">
          <q-card flat>
            <q-card-section>
              <share-chart
                chartTranslationName="reco_pros"
                :height="height"
                :frequencies="getFreq('reco_pros')"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <emissions-reductions-chart
                chartTranslationName="reductions_mod_pro"
                :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
                :reductions="stats.emissionsReductions?.['reductions_mod_pro'] ?? null"
                :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
                :height="height"
                :loading="stats.loading"
              />
            </q-card-section>
          </q-card>
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
          <q-card flat>
            <q-card-section>
              <behavior-change-chart
                type="levers"
                :behavior-change-stats="stats.behaviorChange"
                :height="height"
                :loading="stats.loading"
                :percent="percent"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <behavior-change-chart
                type="motivation"
                :behavior-change-stats="stats.behaviorChange"
                :height="height"
                :loading="stats.loading"
                :percent="percent"
              />
            </q-card-section>
          </q-card>
          <q-card flat>
            <q-card-section>
              <equipment-recommendation-matrix-chart
                :equipmentsStats="stats.equipmentsStats"
                :height="height"
                :loading="stats.loading"
                has-options
              />
            </q-card-section>
          </q-card>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </div>
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
</style>
