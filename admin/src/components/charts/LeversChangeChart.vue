<template>
  <chart-panel
    :title="t('stats.behavior_change_levers.title')"
    :description="t('stats.behavior_change_levers.texts.info')"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onTogglePercent">
              <q-item-section side>
                <q-icon :name="stats.leversPercent ? 'check_box' : 'check_box_outline_blank'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('stats.percent_employees') }}</q-item-label>
              </q-item-section>
            </q-item>
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
      type="levers"
      :behavior-change-stats="behaviorChangeStats"
      :height="height"
      :loading="loading"
      :percent="stats.leversPercent"
      :exportable="!inline"
      :description="chartDescription"
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
  loading?: boolean
  behaviorChangeStats: BehaviorChangeStats | null
  inline?: boolean
}

const props = defineProps<Props>()

type BehaviorChangeChartExposed = {
  handleExport: () => Promise<void>
  chartInfoText: string
}

const chartRef = ref<BehaviorChangeChartExposed | null>(null)
const infoText = ref('')

watch([chartRef, () => props.behaviorChangeStats], ([newRef]) => {
  if (newRef) {
    infoText.value = newRef.chartInfoText || ''
  }
})

const { t } = useI18n()

const stats = useStats()

function onTogglePercent() {
  stats.leversPercent = !stats.leversPercent
}

function onChartDownload() {
  chartRef.value?.handleExport()
}

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
