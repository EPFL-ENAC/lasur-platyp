<template>
  <div class="grid-container">
    <div class="item">
      <frequencies-chart type="equipments" :percent="percent" :height="height" />
    </div>
    <div class="item">
      <frequencies-chart type="constraints" :percent="percent" :height="height" />
    </div>
    <div class="item">
      <frequencies-chart
        type="travel_time"
        :xaxis="t('stats.travel_time.xaxis')"
        :range-step="5"
        :percent="percent"
        :height="height"
      />
    </div>
    <div class="item">
      <share-chart type="freq_mod" :height="height" />
    </div>
    <div class="item">
      <emissions-chart
        type="freq_mod"
        :xaxis="t('stats.emissions_freq_mod.xaxis')"
        :yaxis="t('stats.emissions_freq_mod.yaxis')"
        :height="height"
      />
    </div>
    <div class="item">
      <share-chart type="reco_dt2" :height="height" />
    </div>
    <div class="item">
      <links-chart type="mod_reco" :height="height" />
    </div>
    <div class="item">
      <reco-emissions-chart
        type="freq_mod"
        reco="reco_mod"
        :yaxis="t('stats.emissions_reco_mod.yaxis')"
        :height="height"
      />
    </div>
    <div class="item">
      <frequencies-stack-chart
        type="freq_mod_pro"
        :groups="['local', 'national', 'europe', 'inter']"
        :xaxis="t('stats.freq_mod_pro.xaxis')"
        :height="height"
      />
    </div>
    <div class="item">
      <emissions-chart
        type="freq_mod_pro"
        :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
        :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
        :height="height"
      />
    </div>
    <div class="item">
      <share-chart type="reco_pros" :height="height" />
    </div>
    <div class="item">
      <links-chart type="mod_reco_pro" :height="height" />
    </div>
  </div>
</template>
<script setup lang="ts">
import FrequenciesChart from 'src/components/charts/FrequenciesChart.vue'
import FrequenciesStackChart from 'src/components/charts/FrequenciesStackChart.vue'
import EmissionsChart from 'src/components/charts/EmissionsChart.vue'
import RecoEmissionsChart from 'src/components/charts/RecoEmissionsChart.vue'
import LinksChart from 'src/components/charts/LinksChart.vue'
import ShareChart from 'src/components/charts/ShareChart.vue'

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
