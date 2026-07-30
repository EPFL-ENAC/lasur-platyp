<template>
  <chart-panel
    :title="t('stats.behavior_change_motivation.title')"
    :description="t('stats.behavior_change_motivation.texts.info')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onChartDownload">
              <q-item-section side>
                <q-icon name="download" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('download') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </q-toolbar>
    <behavior-change-chart
      ref="chartRef"
      type="motivation"
      :behavior-change-stats="behaviorChangeStats"
      :height="height"
      :loading="loading"
      :percent="percent"
      :exportable="!inline"
      :description="chartDescription"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import BehaviorChangeChart from 'src/components/charts/BehaviorChangeChart.vue'
import { formatNumber } from 'src/utils/numbers'
import type { BehaviorChangeStats } from 'src/models'

interface Props {
  height: number
  percent: boolean
  loading?: boolean
  behaviorChangeStats: BehaviorChangeStats | null
  inline?: boolean
}

const props = defineProps<Props>()

type BehaviorChangeChartExposed = {
  handleExport: () => Promise<void>
}

const chartRef = useTemplateRef<BehaviorChangeChartExposed>('chartRef')

const { t } = useI18n()

function onChartDownload() {
  chartRef.value?.handleExport()
}

const total = computed(() => props.behaviorChangeStats?.motivation?.total_responses ?? 0)

const descriptionValues = computed(() => {
  const motivation = props.behaviorChangeStats?.motivation
  if (!motivation) {
    return {}
  }

  const motivatedByMode = motivation.by_mode_motivation.map((item) => {
    return item.motivations.filter((m) => m.level >= 4).reduce((sum, m) => sum + m.percentage, 0)
  })
  return {
    percentage: formatNumber(
      motivatedByMode.reduce((sum, p) => sum + p, 0) / motivatedByMode.length,
    ),
  }
})

const chartDescription = computed(() => {
  if (total.value < 5) {
    return t('stats.behavior_change_motivation.texts.default')
  }

  return t('stats.behavior_change_motivation.texts.specific', descriptionValues.value)
})
</script>
