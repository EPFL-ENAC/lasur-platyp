<template>
  <chart-panel
    :title="t('stats.sections.professional_travel.share.title')"
    :description="t('stats.sections.professional_travel.share.description')"
    :details="t('stats.sections.professional_travel.share.details')"
    :inline="inline"
  >
    <share-chart
      chartTranslationName="reco_pros"
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
