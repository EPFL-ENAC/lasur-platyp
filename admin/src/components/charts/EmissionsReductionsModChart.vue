<template>
  <chart-panel
    :title="t('stats.emissions_reductions_mod.title')"
    :description="t('stats.emissions_reductions_mod.description')"
    :inline="inline"
  >
    <div v-if="!inline">
      <q-btn-toggle
        v-model="stats.redModalType"
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
    <emissions-reductions-chart
      v-if="stats.redModalType === 'simple'"
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
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EmissionsReductionsChart from 'src/components/charts/EmissionsReductionsChart.vue'

interface Props {
  height: number
  loading?: boolean
  inline?: boolean
}

defineProps<Props>()

const stats = useStats()

const { t } = useI18n()
</script>
