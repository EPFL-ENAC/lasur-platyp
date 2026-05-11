<template>
  <div class="bg-grey-3">
    <q-toolbar class="bg-white text-primary q-py-sm toolbar print-hide">
      <q-toolbar-title class="text-weight-bold">
        {{ t('certificate.title') }}
      </q-toolbar-title>
      <q-space />
      <q-btn color="primary" icon="print" :label="t('print')" @click="printReport" />
    </q-toolbar>

    <div class="report-container">
      <report-page v-if="certificate">
        <img src="/LOGO-VIOLET.svg" alt="logo" class="q-mb-lg logo" />
        <h1 class="text-h2 q-mt-xl text-primary text-center">
          {{ t('certificate.title') }}
        </h1>
        <div class="bg-white q-pa-md text-center">
          <q-markdown
            class="compact text-body2 q-mb-lg text-secondary"
            :src="text"
          />
          <h3 class="text-h5 text-secondary q-mb-none">{{ t('certificate.participation_id', { id: certificate.response_id_in_campaign }) }}</h3>
        </div>
        <h3 class="text-h6 text-right">{{ t('certificate.date', { date: new Date().toLocaleDateString() }) }}</h3>
      </report-page>
    </div>
  </div>
</template>

<script setup lang="ts">
import ReportPage from 'src/components/ReportPage.vue'
import type { RecordCertificate } from 'src/models'

const { t, locale } = useI18n()
const collector = useCollector()
const route = useRoute()

const token = computed(() => {
  return route.params.token as string
})

const certificate = ref<RecordCertificate | null>(null)

const text = computed(() => {
  if (!certificate.value) {
    return ''
  }
  const rewardsMessage = certificate.value.rewards_message?.[locale.value] || ''
  return rewardsMessage
})

watch(token, async (newToken) => {
  if (!newToken) {
    return
  }
  certificate.value = await collector.loadRecordCertificate(newToken)
}, { immediate: true })


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

.box {
  background-color: white;
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
