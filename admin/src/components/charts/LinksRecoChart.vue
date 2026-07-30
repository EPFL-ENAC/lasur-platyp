<template>
  <chart-panel
    :title="t('stats.mod_reco.title')"
    :description="t('stats.mod_reco.description')"
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
    <links-chart
      ref="chartRef"
      type="mod_reco"
      :links="links"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import LinksChart from 'src/components/charts/LinksChart.vue'
import type { StatLinks } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  links: StatLinks | null
  inline?: boolean
}

defineProps<Props>()

type LinksChartExposed = {
  handleExport: () => Promise<void>
}

const chartRef = useTemplateRef<LinksChartExposed>('chartRef')

const { t } = useI18n()

function onChartDownload() {
  chartRef.value?.handleExport()
}
</script>
