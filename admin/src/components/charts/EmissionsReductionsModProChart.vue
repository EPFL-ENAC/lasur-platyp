<template>
  <chart-panel
    :title="chartTitle"
    :description="t('stats.emissions_reductions_mod_pro.description')"
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
                <q-icon :name="stats.redProModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.redProModalType === 'simple'
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
    <emissions-reductions-chart
      ref="chartRef"
      chartTranslationName="reductions_mod_pro"
      :fold-reco-to-simple="modalType === 'simple'"
      :title="chartTitle"
      :emissions="emissions"
      :reductions="reductions"
      :yaxis="t('stats.emissions_reductions_mod_pro.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import EmissionsReductionsChart from '@/components/charts/EmissionsReductionsChart.vue'
import type { Emissions, EmissionReduction } from '@/models'

interface Props {
  height: number
  loading?: boolean
  emissions: Emissions[] | null
  reductions: EmissionReduction[] | null
  inline?: boolean
}

defineProps<Props>()

type EmissionsReductionsChartExposed = {
  handleExport: () => Promise<void>
  chartInfoText: string
}

const chartRef = ref<EmissionsReductionsChartExposed | null>(null)
const infoText = ref('')

watch(
  chartRef,
  (newVal) => {
    infoText.value = newVal?.chartInfoText || ''
  },
  { flush: 'post' },
)

const { t } = useI18n()

const stats = useStats()

const modalType = computed(() => (stats.redProModalType === 'simple' ? 'simple' : 'detailed'))

const chartTitle = computed(
  () =>
    `${t('stats.emissions_reductions_mod_pro.title')} (${t(
      `stats.freq_mod.modal_split.${modalType.value}`,
    ).toLowerCase()})`,
)

function onToggleModalType() {
  stats.redProModalType = stats.redProModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  chartRef.value?.handleExport()
}
</script>
