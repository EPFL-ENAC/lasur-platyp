<template>
  <chart-panel
    :title="t('stats.behavior_change_levers.title')"
    :description="t('stats.behavior_change_levers.texts.info')"
    :details="chartDescription"
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
import { lowerCaseFirst } from 'src/utils/string'
import type { BehaviorChangeStats } from 'src/models'

interface Props {
  height: number
  percent: boolean
  loading?: boolean
  behaviorChangeStats: BehaviorChangeStats | null
  inline?: boolean
}

const props = defineProps<Props>()

const { t } = useI18n()

const total = computed(() => props.behaviorChangeStats?.levers?.total_responses ?? 0)

const descriptionValues = computed(() => {
  const levers = props.behaviorChangeStats?.levers
  if (!levers) {
    return {}
  }

  const mostNeededLever = levers.by_mode_levers
    .flatMap((item) => item.levers.map((lever) => ({ ...lever, mode: item.mode })))
    .sort((a, b) => b.count - a.count)[0]
  if (!mostNeededLever) {
    return {}
  }

  return {
    lever: keyLabel(mostNeededLever.category),
  }
})

const chartDescription = computed(() => {
  if (total.value < 5) {
    return t('stats.behavior_change_levers.texts.default')
  }

  return `${t('stats.behavior_change_levers.texts.default')}\n\n${t(
    'stats.behavior_change_levers.texts.specific',
    descriptionValues.value,
  )}`
})

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  if (Number.isInteger(Number(key))) {
    return key
  }
  return t(`stats.behavior_change_levers.labels.${shortKey(key)}`)
}

function shortKey(key: string) {
  return lowerCaseFirst(key.replace('freq_mod_pro_', '').replace('freq_mod_', ''))
}
</script>
