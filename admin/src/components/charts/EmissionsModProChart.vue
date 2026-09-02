<template>
  <chart-panel
    :title="chartTitle"
    :description="descriptionText"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleModalType">
              <q-item-section side>
                <q-icon :name="stats.emProModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.emProModalType === 'simple'
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
      ref="chartRef"
      chartTranslationName="freq_mod_pro"
      :fold-mode-to-simple="modalType === 'simple'"
      :title="chartTitle"
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

watch(
  chartRef,
  (newVal) => {
    infoText.value = newVal?.chartInfoText || ''
  },
  { flush: 'post' },
)

const stats = useStats()

const { t } = useI18n()

const descriptionText = computed(() =>
  stats.comparisonMode ? '' : t('stats.emissions_freq_mod_pro.description'),
)

const modalType = computed(() => (stats.emProModalType === 'simple' ? 'simple' : 'detailed'))

const chartTitle = computed(
  () =>
    `${t('stats.emissions_freq_mod_pro.title')} (${t(
      `stats.freq_mod.modal_split.${modalType.value}`,
    ).toLowerCase()})`,
)

function onToggleModalType() {
  stats.emProModalType = stats.emProModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  chartRef.value?.handleExport()
}
</script>
