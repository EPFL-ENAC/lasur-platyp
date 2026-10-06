<template>
  <chart-panel
    :title="t('stats.emissions_reco_mod.title')"
    :description="t('stats.emissions_reco_mod.description')"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleRecoEmModalType">
              <q-item-section side>
                <q-icon :name="stats.recoEmModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.recoEmModalType === 'simple'
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
      v-if="stats.recoEmModalType === 'simple'"
      ref="simpleChartRef"
      chartTranslationName="reco_mod_simple"
      :emissions="stats.emissions?.['reco_mod_simple'] ?? null"
      :comparison-yaxis="t('stats.emissions_reco_mod_simple.comparison_yaxis')"
      share-label-key="stats.group_potential_emissions_share"
      :height="height"
      :loading="loading"
      :exportable="!inline"
      @update:chart-info-text="infoText = $event"
    />
    <emissions-chart
      v-if="stats.recoEmModalType === 'detailed'"
      ref="detailedChartRef"
      chartTranslationName="reco_mod_complex"
      :emissions="stats.emissions?.['reco_mod_complex'] ?? null"
      :comparison-yaxis="t('stats.emissions_reco_mod_complex.comparison_yaxis')"
      share-label-key="stats.group_potential_emissions_share"
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

interface Props {
  height: number
  loading?: boolean
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

// Only one of the two charts is rendered at a time, so it is the one emitting.
const infoText = ref('')

function onToggleRecoEmModalType() {
  stats.recoEmModalType = stats.recoEmModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.recoEmModalType === 'simple' ? simpleChartRef : detailedChartRef
  chartRef.value?.handleExport()
}
</script>
