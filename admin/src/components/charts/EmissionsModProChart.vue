<template>
  <chart-panel
    :title="t('stats.emissions_freq_mod_pro.title')"
    :description="t('stats.emissions_freq_mod_pro.description')"
    :details="t('stats.emissions_freq_mod_pro.details')"
    :inline="inline"
  >
    <emissions-chart
      chartTranslationName="freq_mod_pro"
      :emissions="emissions"
      :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
      :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EmissionsChart from 'src/components/charts/EmissionsChart.vue'
import type { Emissions } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  emissions: Emissions[] | null
  inline?: boolean
}

defineProps<Props>()

const { t } = useI18n()
</script>
