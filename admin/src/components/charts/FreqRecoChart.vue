<template>
  <chart-panel
    :title="t('stats.sections.home_to_work.title')"
    :description="t('stats.sections.home_to_work.description')"
    :details="t('stats.sections.home_to_work.details')"
    :inline="inline"
  >
    <share-chart
      chartTranslationName="reco_inter"
      :frequencies="frequencies"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import ShareChart from 'src/components/charts/ShareChart.vue'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  frequencies: Frequencies | null
  inline?: boolean
}

defineProps<Props>()

const { t } = useI18n()
</script>
