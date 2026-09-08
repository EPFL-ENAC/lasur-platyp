<template>
  <chart-panel :title="chartTitle" :description="descriptionText" :inline="inline">
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleModalType">
              <q-item-section side>
                <q-icon :name="stats.freqProModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.freqProModalType === 'simple'
                    ? t('stats.freq_mod.modal_split.detailed')
                    : t('stats.freq_mod.modal_split.simple')
                }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="onTogglePercent">
              <q-item-section side>
                <q-icon :name="stats.freqModProPercent ? 'check_box' : 'check_box_outline_blank'" />
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
    <frequencies-stack-chart
      ref="chartRef"
      chartTranslationName="freq_mod_pro"
      :fold-mode-to-simple="modalType === 'simple'"
      :title="chartTitle"
      :frequencies="frequencies"
      :groups="['local', 'national', 'europe', 'inter']"
      :xaxis="t('stats.freq_mod_pro.xaxis')"
      :height="height"
      :percent="stats.freqModProPercent"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import FrequenciesStackChart from '@/components/charts/FrequenciesStackChart.vue'
import { getProModalityLabels } from '@/utils/modalities'
import type { Frequencies } from '@/models'

interface Props {
  height: number
  loading?: boolean
  frequencies: Frequencies[] | null
  inline?: boolean
}

defineProps<Props>()

type FrequenciesStackChartExposed = {
  handleExport: () => Promise<void>
}

const chartRef = useTemplateRef<FrequenciesStackChartExposed>('chartRef')

const { t } = useI18n()

const stats = useStats()

const modalType = computed(() => (stats.freqProModalType === 'simple' ? 'simple' : 'detailed'))

const chartTitle = computed(
  () =>
    `${t('stats.freq_mod_pro.title')} (${t(
      `stats.freq_mod.modal_split.${modalType.value}`,
    ).toLowerCase()})`,
)

// Share of the local professional trips made with active modes (walking, cycling)
// by the last comparison group: the example the comparison description builds on.
const localActiveModesExample = computed(() => {
  const groups = stats.comparisonResults?.groups ?? []
  const lastGroup = groups[groups.length - 1]
  if (!lastGroup) {
    return null
  }
  let active = 0
  let total = 0
  ;(lastGroup.pro_mode_frequencies ?? []).forEach((item) => {
    const key = item.field.replace('freq_mod_pro_', '')
    if (!key.startsWith('local_')) {
      return
    }
    const value = item.data.map((d) => d.sum ?? 0).reduce((a, b) => a + b, 0)
    total += value
    if (getProModalityLabels(key.slice('local_'.length))?.simple === 'MA') {
      active += value
    }
  })
  if (total === 0) {
    return null
  }
  return { lastGroup: lastGroup.name, percent: Math.round((active / total) * 100) }
})

const descriptionText = computed(() => {
  if (!stats.comparisonMode) {
    return t('stats.freq_mod_pro.description')
  }
  const example = localActiveModesExample.value
  return [
    t('stats.freq_mod_pro.description'),
    example ? t('stats.freq_mod_pro.texts.comparison', example) : '',
  ]
    .filter(Boolean)
    .join(' ')
})

function onToggleModalType() {
  stats.freqProModalType = stats.freqProModalType === 'simple' ? 'detailed' : 'simple'
}

function onTogglePercent() {
  stats.freqModProPercent = !stats.freqModProPercent
}

function onChartDownload() {
  chartRef.value?.handleExport()
}
</script>
