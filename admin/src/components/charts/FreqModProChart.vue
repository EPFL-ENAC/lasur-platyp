<template>
  <chart-panel
    :title="t('stats.freq_mod_pro.title')"
    :description="t('stats.freq_mod_pro.description')"
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
    <frequencies-stack-chart
      ref="chartRef"
      chartTranslationName="freq_mod_pro"
      :frequencies="frequencies"
      :groups="['local', 'national', 'europe', 'inter']"
      :xaxis="t('stats.freq_mod_pro.xaxis')"
      :height="height"
      :percent="percent"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import FrequenciesStackChart from 'src/components/charts/FrequenciesStackChart.vue'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  percent: boolean
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

function onChartDownload() {
  chartRef.value?.handleExport()
}
</script>
