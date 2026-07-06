<template>
  <div class="bg-grey-3">
    <q-toolbar class="bg-white text-primary q-py-sm toolbar print-hide">
      <q-toolbar-title class="text-weight-bold">
        {{ t('form.recommendations') }}
      </q-toolbar-title>
      <q-space />
      <q-btn
        color="primary"
        icon="print"
        :label="t('print')"
        @click="printReport"
      />
    </q-toolbar>

    <div class="report-container">
      <report-page v-if="data">
        <img src="/LOGO-VIOLET.svg" alt="logo" class="q-mb-lg logo" />
        <h1 class="text-h2 q-mt-xl text-primary text-center">
          {{ t('form.recommendations_print.title') }}
        </h1>

        <RecommendationsPersoPanel
          :main-fm="data.perso.mainFm"
          :is-mode-sustainable="data.perso.isModeSustainable"
          :is-mode-options="data.perso.isModeOptions"
          :reco-dt="data.perso.recoDt"
          :center="data.perso.center"
          :mesure-dt1="data.perso.mesureDt1"
          :mesure-dt2="data.perso.mesureDt2"
          :global-actions="data.perso.globalActions"
          :benefits-expanded="true"
        />

        <RecommendationsProPanel
          class="q-mt-xl"
          :reco-pros="data.pro.recoPros"
          :pro-journey-locations="data.pro.proJourneyLocations"
          :mesure-pro="data.pro.mesurePro"
          :global-actions="data.pro.globalActions"
          :benefits-expanded="true"
        />

        <h3 class="text-h6 text-right q-mt-xl">
          {{ t('certificate.date', { date: new Date().toLocaleDateString() }) }}
        </h3>
      </report-page>
    </div>
  </div>
</template>

<script setup lang="ts">
import ReportPage from 'src/components/ReportPage.vue'
import RecommendationsPersoPanel from 'src/components/form/steps/RecommendationsPersoPanel.vue'
import RecommendationsProPanel from 'src/components/form/steps/RecommendationsProPanel.vue'
import type { RecommendationsPreviewData } from 'src/models'

const { t } = useI18n()
const route = useRoute()

const data = computed<RecommendationsPreviewData | null>(() => {
  const raw = route.query.data
  if (typeof raw !== 'string') return null

  try {
    return JSON.parse(decodeURIComponent(raw)) as RecommendationsPreviewData
  } catch {
    return null
  }
})

const printReport = () => {
  window.print()
}
</script>

<style scoped>
.report-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  color: black !important;
  counter-reset: page-counter;
}

.toolbar {
  position: sticky;
  top: 0;
  border-bottom: 1px solid var(--half-muted-color);
  z-index: 1000;
}

.logo {
  height: 15mm;
}

@media print {
  @page {
    size: A4 portrait;
    margin: 0;
  }

  .print-hide,
  .q-header,
  .q-footer,
  .q-drawer {
    display: none !important;
  }

  .bg-grey-3 {
    background: white !important;
  }

  :deep(.q-dialog),
  :deep(.q-dialog__inner),
  :deep(.q-card) {
    position: static !important;
    display: block !important;
    overflow: visible !important;
    height: auto !important;
    max-height: none !important;
    width: auto !important;
    max-width: none !important;
    transform: none !important;
    box-shadow: none !important;
  }

  .report-container {
    display: block !important;
    width: 100% !important;
    padding: 0 !important;
  }

  :deep(a) {
    color: var(--title-color) !important;
    text-decoration: underline !important;
  }
}
</style>