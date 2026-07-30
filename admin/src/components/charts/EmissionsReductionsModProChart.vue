<template>
  <chart-panel
    :title="t('stats.emissions_reductions_mod_pro.title')"
    :description="t('stats.emissions_reductions_mod_pro.description')"
    :inline="inline"
  >
    <emissions-reductions-chart
      chartTranslationName="reductions_mod_pro"
      :emissions="emissions"
      :reductions="reductions"
      :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EmissionsReductionsChart from 'src/components/charts/EmissionsReductionsChart.vue'
import type { Emissions, EmissionReduction } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  emissions: Emissions[] | null
  reductions: EmissionReduction[] | null
  inline?: boolean
}

defineProps<Props>()

const { t } = useI18n()
</script>
