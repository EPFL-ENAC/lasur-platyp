<template>
  <chart-panel
    :title="t('stats.sections.home_to_work.links.title')"
    :description="t('stats.sections.home_to_work.links.description')"
    :details="t('stats.sections.home_to_work.links.details')"
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
