<template>
  <chart-panel
    :title="t('stats.freq_mod.title')"
    :description="t('stats.freq_mod.description')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleFreqModalType">
              <q-item-section side>
                <q-icon :name="stats.freqModalType === 'simple' ? 'lens' : 'pie_chart'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.freqModalType === 'simple'
                    ? t('stats.freq_mod.modal_split.simple')
                    : t('stats.freq_mod.modal_split.detailed')
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
    <q-markdown compact :src="t('stats.freq_mod.texts.default')" />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import SimpleLabelsShareChart from 'src/components/charts/SimpleLabelsShareChart.vue'
import ComplexLabelsShareChart from 'src/components/charts/ComplexLabelsShareChart.vue'
import type { Frequencies } from 'src/models'

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
}

const simpleChartRef = useTemplateRef<ShareChartExposed>('simpleChartRef')
const complexChartRef = useTemplateRef<ShareChartExposed>('complexChartRef')

const stats = useStats()

const { t } = useI18n()

function onToggleFreqModalType() {
  stats.freqModalType = stats.freqModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.freqModalType === 'simple' ? simpleChartRef : complexChartRef
  chartRef.value?.handleExport()
}
</script>
