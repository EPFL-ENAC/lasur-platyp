<template>
  <q-carousel
    v-model="slide"
    :height="`${height + 100}px`"
    transition-prev="scale"
    transition-next="scale"
    control-color="primary"
    navigation
    padding
    arrows
    infinite
  >
    <q-carousel-slide name="locations" class="column no-wrap flex-center item">
      <location-chart
        :title="t('stats.locationsHeatmap.title')"
        :height="height"
        :home-locations-heatmap="stats.homeLocationsHeatmap"
        :workplace-locations="stats.workplaceLocations"
      />
    </q-carousel-slide>
    <q-carousel-slide name="freq_mod" class="column no-wrap flex-center item">
      <simple-labels-share-chart
        :height="height"
        :frequencies="stats.frequencies?.['freq_mod_simple'] ?? null"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="freq_mod" class="column no-wrap flex-center item">
      <complex-labels-share-chart
        :height="height"
        :frequencies="stats.frequencies?.['freq_mod_complex'] ?? null"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="travel_time" class="column no-wrap flex-center item">
      <travel-time-frequencies-chart
        :frequencies="getFreq('travel_time')"
        :xaxis="t('stats.travel_time.xaxis')"
        :range-step="5"
        :percent="percent"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="equipments" class="column no-wrap flex-center item">
      <equipment-frequencies-chart
        :frequencies="getFreq('equipments')"
        :percent="percent"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="constraints" class="column no-wrap flex-center item">
      <frequencies-chart
        chartTranslationName="constraints"
        :frequencies="getFreq('constraints')"
        :percent="percent"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_freq_mod" class="column no-wrap flex-center item">
      <emissions-chart
        chartTranslationName="freq_mod"
        :emissions="stats.emissions?.['freq_mod'] ?? null"
        :xaxis="t('stats.emissions_freq_mod.xaxis')"
        :yaxis="t('stats.emissions_freq_mod.yaxis')"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="journey_energy_current" class="column no-wrap flex-center item">
      <journey-energy-chart
        type="current"
        :height="height"
        :journey-energy-stats="stats.journeyEnergyStats"
      />
    </q-carousel-slide>
    <q-carousel-slide name="freq_mod_pro" class="column no-wrap flex-center item">
      <frequencies-stack-chart
        chartTranslationName="freq_mod_pro"
        :frequencies="getFreqArray('freq_mod_pro')"
        :groups="['local', 'national', 'europe', 'inter']"
        :xaxis="t('stats.freq_mod_pro.xaxis')"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_freq_mod_pro" class="column no-wrap flex-center item">
      <emissions-chart
        chartTranslationName="freq_mod_pro"
        :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
        :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
        :height="height"
        :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="reco_inter" class="column no-wrap flex-center item">
      <share-chart
        chartTranslationName="reco_inter"
        :frequencies="stats.frequencies?.['reco_inter'] ?? null"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="mod_reco" class="column no-wrap flex-center item">
      <links-chart
        type="mod_reco"
        :links="stats.links['mod_reco'] ?? null"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_reductions_mod" class="column no-wrap flex-center item">
      <emissions-reductions-chart
        chartTranslationName="reductions_mod"
        :emissions="stats.emissions?.['freq_mod'] ?? null"
        :reductions="stats.emissionsReductions?.['reductions_mod'] ?? null"
        :yaxis="t('stats.emissions_reductions_mod.yaxis')"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_reductions_share" class="column no-wrap flex-center item">
      <emissions-reductions-share-chart
        :reductions="stats.emissionsReductions?.['reductions_mod'] ?? null"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="journey_energy_reco" class="column no-wrap flex-center item">
      <journey-energy-chart
        type="reco"
        :height="height"
        :journey-energy-stats="stats.journeyEnergyStats"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="journey_energy_share" class="column no-wrap flex-center item">
      <journey-energy-share-chart
        :journey-energy-stats="stats.journeyEnergyStats"
        :height="height"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="reco_pros" class="column no-wrap flex-center item">
      <share-chart
        chartTranslationName="reco_pros"
        :height="height"
        :frequencies="stats.frequencies?.['reco_pros'] ?? null"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="mod_reco_pro" class="column no-wrap flex-center item">
      <links-chart
        type="mod_reco_pro"
        :height="height"
        :links="stats.links['mod_reco_pro'] ?? null"
        :loading="stats.loading"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_reductions" class="column no-wrap flex-center item">
      <emissions-reductions-chart
        chartTranslationName="reductions_mod_pro"
        :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
        :height="height"
        :emissions="stats.emissions?.['freq_mod_pro'] ?? null"
        :reductions="stats.emissionsReductions?.['reductions_mod_pro'] ?? null"
      />
    </q-carousel-slide>
    <q-carousel-slide name="behaviors_levers" class="column no-wrap flex-center item">
      <behavior-change-chart
        :height="height"
        type="levers"
        :behavior-change-stats="stats.behaviorChange"
        :loading="stats.loading"
        :percent="percent"
      />
    </q-carousel-slide>
    <q-carousel-slide name="behaviors_motivation" class="column no-wrap flex-center item">
      <behavior-change-chart
        :height="height"
        type="motivation"
        :behavior-change-stats="stats.behaviorChange"
        :loading="stats.loading"
        :percent="percent"
      />
    </q-carousel-slide>
    <q-carousel-slide
      name="equipment_recommendation_matrix"
      class="column no-wrap flex-center item"
    >
      <equipment-recommendation-matrix-chart
        :height="height"
        :loading="stats.loading"
        :equipmentsStats="stats.equipmentsStats"
        has-options
      />
    </q-carousel-slide>
  </q-carousel>
</template>

<script setup lang="ts">
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
import SimpleLabelsShareChart from 'src/components/charts/SimpleLabelsShareChart.vue'
import ComplexLabelsShareChart from 'src/components/charts/ComplexLabelsShareChart.vue'
import JourneyEnergyChart from 'src/components/charts/JourneyEnergyChart.vue'
import JourneyEnergyShareChart from 'src/components/charts/JourneyEnergyShareChart.vue'
import BehaviorChangeChart from 'src/components/charts/BehaviorChangeChart.vue'
import EquipmentRecommendationMatrixChart from 'src/components/charts/EquipmentRecommendationMatrixChart.vue'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  percent: boolean
}

defineProps<Props>()

const { t } = useI18n()
const stats = useStats()
const slide = ref('equipments')

const getFreq = (key: string) => {
  return (stats.frequencies?.[key] ?? null) as Frequencies | null
}

const getFreqArray = (key: string) => {
  return (stats.frequencies?.[key] ?? null) as Frequencies[] | null
}
</script>
