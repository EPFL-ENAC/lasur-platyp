<template>
  <chart-panel
    :title="t('stats.sections.behavioural_changes.levers.title')"
    :description="t('stats.sections.behavioural_changes.levers.description')"
    :details="t('stats.sections.behavioural_changes.levers.details')"
    :inline="inline"
  >
    <behavior-change-chart
      type="levers"
      :behavior-change-stats="behaviorChangeStats"
      :height="height"
      :loading="loading"
      :percent="percent"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import BehaviorChangeChart from 'src/components/charts/BehaviorChangeChart.vue'
import type { BehaviorChangeStats } from 'src/models'

interface Props {
  height: number
  percent: boolean
  loading?: boolean
  behaviorChangeStats: BehaviorChangeStats | null
  inline?: boolean
}

defineProps<Props>()

const { t } = useI18n()
</script>
