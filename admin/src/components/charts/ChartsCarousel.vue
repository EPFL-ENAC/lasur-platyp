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
      <frequencies-chart type="equipments" :percent="percent" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="constraints" class="column no-wrap flex-center item">
      <frequencies-chart type="constraints" :percent="percent" :height="height" />
    </q-carousel-slide>
    <q-carousel-slide name="travel_time" class="column no-wrap flex-center item">
      <frequencies-chart
        type="travel_time"
        :xaxis="t('stats.travel_time.xaxis')"
        :range-step="5"
        :percent="percent"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="freq_mod" class="column no-wrap flex-center item">
      <share-chart type="freq_mod" :height="height" />
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
    <q-carousel-slide name="emissions_reco_mod" class="column no-wrap flex-center item">
      <reco-emissions-chart
        type="freq_mod"
        reco="reco_mod"
        :yaxis="t('stats.emissions_reco_mod.yaxis')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="freq_mod_pro" class="column no-wrap flex-center item">
      <frequencies-stack-chart
        type="freq_mod_pro"
        :groups="['local', 'region', 'inter']"
        :xaxis="t('stats.freq_mod_pro.xaxis')"
        :height="height"
      />
    </q-carousel-slide>
    <q-carousel-slide name="emissions_freq_mod" class="column no-wrap flex-center item">
      <emissions-chart
        type="freq_mod"
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
  </q-carousel>
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
const slide = ref('equipments')
</script>
