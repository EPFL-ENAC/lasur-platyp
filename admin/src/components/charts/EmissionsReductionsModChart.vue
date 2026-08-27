<template>
  <chart-panel
    :title="t('stats.emissions_reductions_mod.title')"
    :description="t('stats.emissions_reductions_mod.description')"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleRedModalType">
              <q-item-section side>
                <q-icon :name="stats.redModalType === 'simple' ? 'lens' : 'pie_chart'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.redModalType === 'simple'
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
    <emissions-reductions-chart
      v-if="stats.redModalType === 'simple'"
      ref="simpleChartRef"
      chartTranslationName="reductions_mod_simple"
      :emissions="stats.emissions?.['freq_mod_simple'] ?? null"
      :reductions="stats.emissionsReductions?.['reductions_mod_simple'] ?? null"
      :yaxis="t('stats.emissions_reductions_mod_simple.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
    <emissions-reductions-chart
      v-if="stats.redModalType === 'detailed'"
      ref="detailedChartRef"
      chartTranslationName="reductions_mod_complex"
      :emissions="stats.emissions?.['freq_mod_complex'] ?? null"
      :reductions="stats.emissionsReductions?.['reductions_mod_complex'] ?? null"
      :yaxis="t('stats.emissions_reductions_mod_complex.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import EmissionsReductionsChart from '@/components/charts/EmissionsReductionsChart.vue'

interface Props {
  height: number
  loading?: boolean
  inline?: boolean
}

defineProps<Props>()

type EmissionsReductionsChartExposed = {
  handleExport: () => Promise<void>
  chartInfoText: string
}

const simpleChartRef = ref<EmissionsReductionsChartExposed | null>(null)
const detailedChartRef = ref<EmissionsReductionsChartExposed | null>(null)

const stats = useStats()

const { t } = useI18n()

const infoText = ref('')

watch([() => stats.redModalType, simpleChartRef, detailedChartRef], () => {
  const active = stats.redModalType === 'simple' ? simpleChartRef : detailedChartRef
  if (active.value) {
    infoText.value = active.value.chartInfoText || ''
  }
})

function onToggleRedModalType() {
  stats.redModalType = stats.redModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.redModalType === 'simple' ? simpleChartRef : detailedChartRef
  chartRef.value?.handleExport()
}
</script>
