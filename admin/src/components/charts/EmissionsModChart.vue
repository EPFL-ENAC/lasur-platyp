<template>
  <chart-panel
    :title="t('stats.emissions_freq_mod.title')"
    :description="t('stats.emissions_freq_mod.description')"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleEmModalType">
              <q-item-section side>
                <q-icon :name="stats.emModalType === 'simple' ? 'lens' : 'pie_chart'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.emModalType === 'simple'
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
    <emissions-chart
      v-if="stats.emModalType === 'simple'"
      ref="simpleChartRef"
      chartTranslationName="freq_mod_simple"
      :emissions="simpleEmissions"
      :xaxis="t('stats.emissions_freq_mod_simple.xaxis')"
      :yaxis="t('stats.emissions_freq_mod_simple.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
    <emissions-chart
      v-if="stats.emModalType === 'detailed'"
      ref="detailedChartRef"
      chartTranslationName="freq_mod_complex"
      :emissions="detailedEmissions"
      :xaxis="t('stats.emissions_freq_mod_complex.xaxis')"
      :yaxis="t('stats.emissions_freq_mod_complex.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EmissionsChart from 'src/components/charts/EmissionsChart.vue'
import type { Emissions } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  simpleEmissions: Emissions[] | null
  detailedEmissions: Emissions[] | null
  inline?: boolean
}

defineProps<Props>()

type EmissionsChartExposed = {
  handleExport: () => Promise<void>
  chartInfoText: string
}

const simpleChartRef = ref<EmissionsChartExposed | null>(null)
const detailedChartRef = ref<EmissionsChartExposed | null>(null)

const stats = useStats()

const { t } = useI18n()

const infoText = ref('')

watch([() => stats.emModalType, simpleChartRef, detailedChartRef], () => {
  const active = stats.emModalType === 'simple' ? simpleChartRef : detailedChartRef
  if (active.value) {
    infoText.value = active.value.chartInfoText || ''
  }
})

function onToggleEmModalType() {
  stats.emModalType = stats.emModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.emModalType === 'simple' ? simpleChartRef : detailedChartRef
  chartRef.value?.handleExport()
}
</script>
