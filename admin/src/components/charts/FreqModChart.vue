<template>
  <chart-panel
    :title="t('stats.freq_mod.title')"
    :description="t('stats.freq_mod.description')"
    :details="t('stats.freq_mod.texts.default')"
    :inline="inline"
  >
    <div v-if="!inline">
      <q-btn-toggle
        v-model="stats.freqModalType"
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
    <simple-labels-share-chart
      v-if="stats.freqModalType === 'simple'"
      :height="height"
      :frequencies="simpleFrequencies"
      :loading="loading"
      :exportable="!inline"
    />
    <complex-labels-share-chart
      v-if="stats.freqModalType === 'detailed'"
      :height="height"
      :frequencies="detailedFrequencies"
      :loading="loading"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import SimpleLabelsShareChart from 'src/components/charts/SimpleLabelsShareChart.vue'
import ComplexLabelsShareChart from 'src/components/charts/ComplexLabelsShareChart.vue'
import type { Frequencies } from 'src/models'

interface Props {
  height: number
  loading?: boolean
  simpleFrequencies: Frequencies | Frequencies[] | null
  detailedFrequencies: Frequencies | Frequencies[] | null
  inline?: boolean
}

defineProps<Props>()

const stats = useStats()

const { t } = useI18n()
</script>
