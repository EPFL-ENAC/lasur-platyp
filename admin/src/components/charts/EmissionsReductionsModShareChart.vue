<template>
  <chart-panel
    :title="t('stats.emissions_reductions_share.title')"
    :description="t('stats.emissions_reductions_share.description')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleRedShareModalType">
              <q-item-section side>
                <q-icon :name="stats.redShareModalType === 'simple' ? 'lens' : 'pie_chart'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.redShareModalType === 'simple'
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
    <emissions-reductions-share-chart
      v-if="stats.redShareModalType === 'simple'"
      ref="simpleChartRef"
      chartTranslationName="reductions_share_simple"
      :reductions="stats.emissionsReductions?.['reductions_mod_simple'] ?? null"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
    <emissions-reductions-share-chart
      v-if="stats.redShareModalType === 'detailed'"
      ref="detailedChartRef"
      chartTranslationName="reductions_share_complex"
      :reductions="stats.emissionsReductions?.['reductions_mod_complex'] ?? null"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EmissionsReductionsShareChart from 'src/components/charts/EmissionsReductionsShareChart.vue'

interface Props {
  height: number
  loading?: boolean
  inline?: boolean
}

defineProps<Props>()

type EmissionsReductionsShareChartExposed = {
  handleExport: () => Promise<void>
}

const simpleChartRef = useTemplateRef<EmissionsReductionsShareChartExposed>('simpleChartRef')
const detailedChartRef = useTemplateRef<EmissionsReductionsShareChartExposed>('detailedChartRef')

const stats = useStats()

const { t } = useI18n()

function onToggleRedShareModalType() {
  stats.redShareModalType = stats.redShareModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.redShareModalType === 'simple' ? simpleChartRef : detailedChartRef
  chartRef.value?.handleExport()
}
</script>
