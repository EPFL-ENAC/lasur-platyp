<template>
  <chart-panel
    :title="t('stats.mod_reco.title')"
    :description="t('stats.mod_reco.description')"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleLinksModalType">
              <q-item-section side>
                <q-icon :name="stats.linksModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.linksModalType === 'simple'
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
    <links-chart
      v-if="stats.linksModalType === 'simple'"
      ref="simpleChartRef"
      type="mod_reco"
      label-type="simple"
      :links="simpleLinks"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
    <links-chart
      v-if="stats.linksModalType === 'detailed'"
      ref="detailedChartRef"
      type="mod_reco"
      label-type="complex"
      :links="detailedLinks"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import LinksChart from '@/components/charts/LinksChart.vue'
import type { StatLinks } from '@/models'

interface Props {
  height: number
  loading?: boolean
  simpleLinks: StatLinks | null
  detailedLinks: StatLinks | null
  inline?: boolean
}

defineProps<Props>()

type LinksChartExposed = {
  handleExport: () => Promise<void>
  chartInfoText: string
}

const simpleChartRef = ref<LinksChartExposed | null>(null)
const detailedChartRef = ref<LinksChartExposed | null>(null)
const infoText = ref('')

const stats = useStats()

watch(
  [() => stats.linksModalType, simpleChartRef, detailedChartRef],
  () => {
    const active = stats.linksModalType === 'simple' ? simpleChartRef : detailedChartRef
    infoText.value = active.value?.chartInfoText || ''
  },
  { flush: 'post' },
)

const { t } = useI18n()

function onToggleLinksModalType() {
  stats.linksModalType = stats.linksModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.linksModalType === 'simple' ? simpleChartRef : detailedChartRef
  chartRef.value?.handleExport()
}
</script>
