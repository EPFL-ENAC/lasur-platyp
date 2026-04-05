<template>
  <div class="grid-container">
    <q-card flat>
      <q-card-section>
        <equipment-frequencies-chart :percent="percent" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <frequencies-chart type="constraints" :percent="percent" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <location-chart :title="t('stats.locationsHeatmap.title')" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <travel-time-frequencies-chart
          type="travel_time"
          :xaxis="t('stats.travel_time.xaxis')"
          :range-step="5"
          :percent="percent"
          :height="height"
        />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <modes-of-transport-share-chart :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <emissions-chart
          type="freq_mod"
          :xaxis="t('stats.emissions_freq_mod.xaxis')"
          :yaxis="t('stats.emissions_freq_mod.yaxis')"
          :height="height"
        />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <share-chart type="reco_dt2" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <links-chart type="mod_reco" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <emissions-reductions-chart
          type="freq_mod"
          reduction-type="reductions_mod"
          :yaxis="t('stats.emissions_reductions_mod.yaxis')"
          :height="height"
        />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <emissions-reductions-share-chart reduction-type="reductions_mod" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <journey-energy-chart type="current" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <journey-energy-chart type="reco" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <journey-energy-share-chart :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <frequencies-stack-chart
          type="freq_mod_pro"
          :groups="['local', 'national', 'europe', 'inter']"
          :xaxis="t('stats.freq_mod_pro.xaxis')"
          :height="height"
        />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <emissions-chart
          type="freq_mod_pro"
          :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
          :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
          :height="height"
        />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <share-chart type="reco_pros" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <links-chart type="mod_reco_pro" :height="height" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <emissions-reductions-chart
          type="freq_mod_pro"
          reduction-type="reductions_mod_pro"
          :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
          :height="height"
        />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <behavior-change-chart :height="height" type="levers" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <behavior-change-chart :height="height" type="motivation" />
      </q-card-section>
    </q-card>
    <q-card flat>
      <q-card-section>
        <equipment-recommendation-matrix-chart :height="height" />
      </q-card-section>
    </q-card>
  </div>
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
</script>

<style lang="css">
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  gap: 16px;
}
.item {
  background: #fafafa;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 4px;
}
</style>
