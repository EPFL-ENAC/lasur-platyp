<template>
  <chart-panel
    :title="t('stats.emissions_freq_mod.title')"
    :description="t('stats.emissions_freq_mod.description')"
    :inline="inline"
  >
    <div v-if="!inline">
      <q-btn-toggle
        v-model="stats.emModalType"
        :options="[
          { label: t('stats.freq_mod.modal_split.simple'), value: 'simple' },
          { label: t('stats.freq_mod.modal_split.detailed'), value: 'detailed' },
        ]"
        outlined
        unelevated
        no-caps
        color="grey"
        toggle-color="primary"
      />
    </div>
    <emissions-chart
      v-if="stats.emModalType === 'simple'"
      chartTranslationName="freq_mod_simple"
      :emissions="simpleEmissions"
      :xaxis="t('stats.emissions_freq_mod_simple.xaxis')"
      :yaxis="t('stats.emissions_freq_mod_simple.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
    <emissions-chart
      v-if="stats.emModalType === 'detailed'"
      chartTranslationName="freq_mod_complex"
      :emissions="detailedEmissions"
      :xaxis="t('stats.emissions_freq_mod_complex.xaxis')"
      :yaxis="t('stats.emissions_freq_mod_complex.yaxis')"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EmissionsChart from 'src/components/charts/EmissionsChart.vue'
import type { Emissions } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  simpleEmissions: Emissions[] | null
  detailedEmissions: Emissions[] | null
  inline?: boolean
}

defineProps<Props>()

const stats = useStats()

const { t } = useI18n()
</script>
