<template>
  <chart-panel
    :title="t('stats.reco_inter.title')"
    :description="t('stats.reco_inter.description')"
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
    <share-chart
      ref="chartRef"
      chartTranslationName="reco_inter"
      :frequencies="frequencies"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import ShareChart from 'src/components/charts/ShareChart.vue'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  frequencies: Frequencies | null
  inline?: boolean
}

defineProps<Props>()

type ShareChartExposed = {
  handleExport: () => Promise<void>
}

const chartRef = useTemplateRef<ShareChartExposed>('chartRef')

const { t } = useI18n()

function onChartDownload() {
  chartRef.value?.handleExport()
}
</script>
