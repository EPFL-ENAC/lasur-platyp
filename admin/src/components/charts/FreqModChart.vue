<template>
  <chart-panel
    :title="t('stats.freq_mod.title')"
    :description="descriptionText"
    :chart-info-text="chartInfoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleFreqModalType">
              <q-item-section side>
                <q-icon :name="stats.freqModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.freqModalType === 'simple'
                    ? t('stats.freq_mod.modal_split.detailed')
                    : t('stats.freq_mod.modal_split.simple')
                }}</q-item-label>
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
    <simple-labels-share-chart
      v-if="stats.freqModalType === 'simple'"
      ref="simpleChartRef"
      :height="height"
      :frequencies="simpleFrequencies"
      :loading="loading"
      :exportable="!inline"
    />
    <complex-labels-share-chart
      v-if="stats.freqModalType === 'detailed'"
      ref="complexChartRef"
      :height="height"
      :frequencies="detailedFrequencies"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import SimpleLabelsShareChart from '@/components/charts/SimpleLabelsShareChart.vue'
import ComplexLabelsShareChart from '@/components/charts/ComplexLabelsShareChart.vue'
import type { Frequencies } from '@/models'

interface Props {
  height: number
  loading?: boolean
  simpleFrequencies: Frequencies | Frequencies[] | null
  detailedFrequencies: Frequencies | Frequencies[] | null
  inline?: boolean
}

defineProps<Props>()

type ShareChartExposed = {
  handleExport: () => Promise<void>
  chartInfoText: string
}

const simpleChartRef = useTemplateRef<ShareChartExposed>('simpleChartRef')
const complexChartRef = useTemplateRef<ShareChartExposed>('complexChartRef')

const stats = useStats()

const { t } = useI18n()

const descriptionText = computed(() =>
  stats.comparisonMode ? '' : t('stats.freq_mod.description'),
)

function onToggleFreqModalType() {
  stats.freqModalType = stats.freqModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.freqModalType === 'simple' ? simpleChartRef : complexChartRef
  chartRef.value?.handleExport()
}

const chartInfoText = computed(() => {
  let childText = ''
  if (stats.freqModalType === 'simple' && simpleChartRef.value) {
    childText = simpleChartRef.value.chartInfoText
  } else if (stats.freqModalType === 'detailed' && complexChartRef.value) {
    childText = complexChartRef.value.chartInfoText
  }
  if (stats.comparisonMode) {
    return childText
  }
  const text = t('stats.freq_mod.texts.default')
  if (childText) {
    return `${text}\n\n${childText}`
  }
  return text
})
</script>
