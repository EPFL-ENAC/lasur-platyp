<template>
  <q-card flat class="q-my-md">
    <q-card-section>
      <h5 class="text-h5 q-my-none">{{ t('stats.sections.mobility_analysis.title') }}</h5>
      <q-markdown
        class="q-mt-md compact text-caption"
        :src="t('stats.sections.mobility_analysis.description')"
      />
    </q-card-section>
    <q-separator />

    <q-card-section>
      <div class="grid-container">
        <div>
          <equipment-frequencies-chart :percent="percent" :height="height" />
        </div>
        <div>
          <frequencies-chart type="constraints" :percent="percent" :height="height" />
        </div>
        <div>
          <location-chart :title="t('stats.locationsHeatmap.title')" :height="height" />
        </div>
        <div>
          <travel-time-frequencies-chart
            type="travel_time"
            :xaxis="t('stats.travel_time.xaxis')"
            :range-step="5"
            :percent="percent"
            :height="height"
          />
        </div>
        <div>
          <modes-of-transport-share-chart :height="height" />
        </div>
        <div>
          <emissions-chart
            type="freq_mod"
            :xaxis="t('stats.emissions_freq_mod.xaxis')"
            :yaxis="t('stats.emissions_freq_mod.yaxis')"
            :height="height"
          />
        </div>
        <div>
          <journey-energy-chart type="current" :height="height" />
        </div>
        <div>
          <frequencies-stack-chart
            type="freq_mod_pro"
            :groups="['local', 'national', 'europe', 'inter']"
            :xaxis="t('stats.freq_mod_pro.xaxis')"
            :height="height"
          />
        </div>
        <div>
          <emissions-chart
            type="freq_mod_pro"
            :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
            :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
            :height="height"
          />
        </div>
      </div>
    </q-card-section>
  </q-card>

  <q-card flat class="q-my-md">
    <q-card-section>
      <h5 class="text-h5 q-my-none">{{ t('stats.sections.mobility_potentials.title') }}</h5>
      <q-markdown
        class="q-mt-md compact text-caption"
        :src="t('stats.sections.mobility_potentials.description')"
      />
    </q-card-section>
    <q-separator />

    <q-card-section>
      <div class="grid-container">
        <div>
          <share-chart type="reco_dt2" :height="height" />
        </div>
        <div>
          <links-chart type="mod_reco" :height="height" />
        </div>
        <div>
          <emissions-reductions-chart
            type="freq_mod"
            reduction-type="reductions_mod"
            :yaxis="t('stats.emissions_reductions_mod.yaxis')"
            :height="height"
          />
        </div>
        <div>
          <emissions-reductions-chart
            type="freq_mod_pro"
            reduction-type="reductions_mod_pro"
            :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
            :height="height"
          />
        </div>
        <div>
          <emissions-reductions-share-chart reduction-type="reductions_mod" :height="height" />
        </div>
        <div>
          <journey-energy-chart type="reco" :height="height" />
        </div>
        <div>
          <journey-energy-share-chart :height="height" />
        </div>
      </div>
    </q-card-section>
  </q-card>

  <q-card flat class="q-my-md">
    <q-card-section>
      <h5 class="text-h5 q-my-none">{{ t('stats.sections.behavioural_changes.title') }}</h5>
      <q-markdown
        class="q-mt-md compact text-caption"
        :src="t('stats.sections.behavioural_changes.description')"
      />
    </q-card-section>
    <q-separator />

    <q-card-section>
      <div class="grid-container">
        <div>
          <behavior-change-chart :height="height" type="levers" />
        </div>
        <div>
          <behavior-change-chart :height="height" type="motivation" />
        </div>
        <div>
          <equipment-recommendation-matrix-chart :height="height" />
        </div>
      </div>
    </q-card-section>
  </q-card>
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
  gap: 2rem;
}
</style>
