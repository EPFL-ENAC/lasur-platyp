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
    <q-carousel-slide name="equipments" class="column no-wrap flex-center item">
      <equipment-frequencies-chart :percent="percent" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="constraints" class="column no-wrap flex-center item">
      <frequencies-chart type="constraints" :percent="percent" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="locations" class="column no-wrap flex-center item">
      <location-chart
        :title="t('stats.locationsHeatmap.title')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="travel_time" class="column no-wrap flex-center item">
      <travel-time-frequencies-chart
        type="travel_time"
        :xaxis="t('stats.travel_time.xaxis')"
        :range-step="5"
        :percent="percent"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="freq_mod" class="column no-wrap flex-center item">
      <modes-of-transport-share-chart :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_freq_mod" class="column no-wrap flex-center item">
      <emissions-chart
        type="freq_mod"
        :xaxis="t('stats.emissions_freq_mod.xaxis')"
        :yaxis="t('stats.emissions_freq_mod.yaxis')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="reco_dt2" class="column no-wrap flex-center item">
      <share-chart type="reco_dt2" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="mod_reco" class="column no-wrap flex-center item">
      <links-chart type="mod_reco" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_reductions_mod" class="column no-wrap flex-center item">
      <emissions-reductions-chart
        type="freq_mod"
        reduction-type="reductions_mod"
        :yaxis="t('stats.emissions_reductions_mod.yaxis')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_reductions_share" class="column no-wrap flex-center item">
      <emissions-reductions-share-chart reduction-type="reductions_mod" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="journey_energy_current" class="column no-wrap flex-center item">
      <journey-energy-chart type="current" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="journey_energy_reco" class="column no-wrap flex-center item">
      <journey-energy-chart type="reco" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="journey_energy_share" class="column no-wrap flex-center item">
      <journey-energy-share-chart :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="freq_mod_pro" class="column no-wrap flex-center item">
      <frequencies-stack-chart
        type="freq_mod_pro"
        :groups="['local', 'national', 'europe', 'inter']"
        :xaxis="t('stats.freq_mod_pro.xaxis')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_freq_mod_pro" class="column no-wrap flex-center item">
      <emissions-chart
        type="freq_mod_pro"
        :xaxis="t('stats.emissions_freq_mod.xaxis')"
        :yaxis="t('stats.emissions_freq_mod.yaxis')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="reco_pros" class="column no-wrap flex-center item">
      <share-chart type="reco_pros" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="mod_reco_pro" class="column no-wrap flex-center item">
      <links-chart type="mod_reco_pro" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_reductions" class="column no-wrap flex-center item">
      <emissions-reductions-chart
        type="freq_mod_pro"
        reduction-type="reductions_mod_pro"
        :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="behaviors_levers" class="column no-wrap flex-center item">
      <behavior-change-chart :height="height" type="levers" />
    </q-carousel-slide>
    <q-carousel-slide name="behaviors_motivation" class="column no-wrap flex-center item">
      <behavior-change-chart :height="height" type="motivation" />
    </q-carousel-slide>
    <q-carousel-slide name="equipment_recommendation_matrix" class="column no-wrap flex-center item">
      <equipment-recommendation-matrix-chart :height="height" />
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
import ModesOfTransportShareChart from 'src/components/charts/ModesOfTransportShareChart.vue'
import JourneyEnergyChart from 'src/components/charts/JourneyEnergyChart.vue'
import JourneyEnergyShareChart from 'src/components/charts/JourneyEnergyShareChart.vue'
import BehaviorChangeChart from 'src/components/charts/BehaviorChangeChart.vue'
import EquipmentRecommendationMatrixChart from 'src/components/charts/EquipmentRecommendationMatrixChart.vue'

interface Props {
  height: number
  percent: boolean
}

defineProps<Props>()

const { t } = useI18n()
const slide = ref('equipments')
</script>
