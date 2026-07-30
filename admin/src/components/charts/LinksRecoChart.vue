<template>
  <chart-panel
    :title="t('stats.mod_reco.title')"
    :description="t('stats.mod_reco.description')"
    :inline="inline"
  >
    <links-chart
      type="mod_reco"
      :links="links"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import LinksChart from 'src/components/charts/LinksChart.vue'
import type { StatLinks } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  links: StatLinks | null
  inline?: boolean
}

defineProps<Props>()

const { t } = useI18n()
</script>
