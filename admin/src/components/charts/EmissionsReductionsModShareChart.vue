<template>
  <chart-panel
    :title="t('stats.sections.home_to_work.reductions_share.title')"
    :description="t('stats.sections.home_to_work.reductions_share.description')"
    :details="t('stats.sections.home_to_work.reductions_share.details')"
    :inline="inline"
  >
    <div v-if="!inline">
      <q-btn-toggle
        v-model="stats.redShareModalType"
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
    <emissions-reductions-share-chart
      v-if="stats.redShareModalType === 'simple'"
      chartTranslationName="reductions_share_simple"
      :reductions="stats.emissionsReductions?.['reductions_mod_simple'] ?? null"
      :height="height"
      :loading="loading"
      :exportable="!inline"
    />
    <emissions-reductions-share-chart
      v-if="stats.redShareModalType === 'detailed'"
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

const stats = useStats()

const { t } = useI18n()
</script>
