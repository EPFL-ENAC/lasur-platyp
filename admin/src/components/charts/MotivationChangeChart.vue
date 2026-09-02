<template>
  <chart-panel
    :title="chartTitle"
    :description="t('stats.behavior_change_motivation.texts.info')"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleModalType">
              <q-item-section side>
                <q-icon :name="stats.motivationModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.motivationModalType === 'simple'
                    ? t('stats.freq_mod.modal_split.detailed')
                    : t('stats.freq_mod.modal_split.simple')
                }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="onTogglePercent">
              <q-item-section side>
                <q-icon :name="stats.motivationPercent ? 'check_box' : 'check_box_outline_blank'" />
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
      type="motivation"
      :behavior-change-stats="behaviorChangeStats"
      :height="height"
      :loading="loading"
      :percent="stats.motivationPercent"
      :modal-type="modalType"
      :exportable="!inline"
      :description="chartDescription"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import BehaviorChangeChart from '@/components/charts/BehaviorChangeChart.vue'
import { formatNumber } from '@/utils/numbers'
import type { BehaviorChangeStats } from '@/models'

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

const modalType = computed(() => (stats.motivationModalType === 'simple' ? 'simple' : 'detailed'))

const chartTitle = computed(
  () =>
    `${t('stats.behavior_change_motivation.title')} (${t(
      `stats.freq_mod.modal_split.${modalType.value}`,
    ).toLowerCase()})`,
)

function onToggleModalType() {
  stats.motivationModalType = stats.motivationModalType === 'simple' ? 'detailed' : 'simple'
}

function onTogglePercent() {
  stats.motivationPercent = !stats.motivationPercent
}

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
