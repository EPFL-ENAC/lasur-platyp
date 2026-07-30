<template>
  <chart-panel
    :title="t('stats.freq_mod_pro.title')"
    :description="t('stats.freq_mod_pro.description')"
    :inline="inline"
  >
    <frequencies-stack-chart
      chartTranslationName="freq_mod_pro"
      :frequencies="frequencies"
      :groups="['local', 'national', 'europe', 'inter']"
      :xaxis="t('stats.freq_mod_pro.xaxis')"
      :height="height"
      :percent="percent"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import FrequenciesStackChart from 'src/components/charts/FrequenciesStackChart.vue'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  percent: boolean
  loading?: boolean
  frequencies: Frequencies[] | null
  inline?: boolean
}

defineProps<Props>()

const { t } = useI18n()
</script>
