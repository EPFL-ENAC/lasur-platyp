<template>
  <chart-panel
    :title="t('stats.emissions_freq_mod.title')"
    :description="descriptionText"
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
                <q-icon :name="stats.emModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.emModalType === 'simple'
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
      @update:chart-info-text="infoText = $event"
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
      @update:chart-info-text="infoText = $event"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import EmissionsChart from '@/components/charts/EmissionsChart.vue'
import type { Emissions } from '@/models'

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
}

const simpleChartRef = ref<EmissionsChartExposed | null>(null)
const detailedChartRef = ref<EmissionsChartExposed | null>(null)

const stats = useStats()

const { t } = useI18n()

const descriptionText = computed(() =>
  stats.comparisonMode ? '' : t('stats.emissions_freq_mod.description'),
)

// Only one of the two charts is rendered at a time, so it is the one emitting.
const infoText = ref('')

function onToggleEmModalType() {
  stats.emModalType = stats.emModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.emModalType === 'simple' ? simpleChartRef : detailedChartRef
  chartRef.value?.handleExport()
}
</script>
