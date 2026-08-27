<template>
  <chart-panel
    :title="t('stats.emissions_freq_mod_pro.title')"
    :description="descriptionText"
    :chart-info-text="infoText"
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
    <emissions-chart
      ref="chartRef"
      chartTranslationName="freq_mod_pro"
      :emissions="emissions"
      :xaxis="t('stats.emissions_freq_mod_pro.xaxis')"
      :yaxis="t('stats.emissions_freq_mod_pro.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
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
  emissions: Emissions[] | null
  inline?: boolean
}

defineProps<Props>()

type EmissionsChartExposed = {
  handleExport: () => Promise<void>
  chartInfoText: string
}

const chartRef = ref<EmissionsChartExposed | null>(null)
const infoText = ref('')

watch(chartRef, (newVal) => {
  infoText.value = newVal?.chartInfoText || ''
}, { flush: 'post' })

const stats = useStats()

const { t } = useI18n()

const descriptionText = computed(() =>
  stats.comparisonMode ? '' : t('stats.emissions_freq_mod_pro.description'),
)

function onChartDownload() {
  chartRef.value?.handleExport()
}
</script>
