<template>
  <div class="chart-panel">
    <div class="text-h6 chart-panel__title">{{ title }}</div>
    <div v-if="combinedDescription" class="chart-panel__description">
      <div class="q-chart-description">
        <q-markdown compact :src="panelDescription" />
      </div>
    </div>
    <div v-if="!noDetails" class="chart-panel__details">
      <a
        href="#"
        v-if="!inline"
        class="modus chart-panel__link"
        @click.prevent="showDialog = true"
        >{{ t('more_details') }}</a
      >
    </div>
    <q-card flat class="chart-panel__card">
      <q-card-section>
        <slot></slot>
      </q-card-section>
    </q-card>

    <q-dialog
      v-model="showDialog"
      :maximized="true"
      transition-show="slide-up"
      transition-hide="slide-down"
    >
      <q-card flat class="chart-panel-dialog">
        <q-btn
          round
          unelevated
          color="primary"
          icon="close"
          :aria-label="t('close')"
          class="chart-panel-dialog__close"
          v-close-popup
        />
        <q-card-section class="chart-panel-dialog__body">
          <div class="chart-panel-dialog-content">
            <div class="text-h6 q-mb-md">{{ title }}</div>
            <q-markdown
              v-if="combinedDescription"
              class="compact chart-panel-dialog__description q-mt-sm q-mb-lg"
              :src="combinedDescription"
            />
            <slot></slot>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { chartPanelDialogOpenKey } from './commons'

const { t } = useI18n()

interface Props {
  title: string
  description?: string
  chartInfoText?: string
  inline?: boolean
  noDetails?: boolean
}

const props = defineProps<Props>()

const showDialog = ref(false)

const combinedDescription = computed(() => {
  const parts: string[] = []
  if (props.description) {
    parts.push(props.description)
  }
  if (props.chartInfoText) {
    parts.push(props.chartInfoText)
  }
  return parts.join('\n\n').trim() || ''
})

const panelDescription = computed(() =>
  combinedDescription.value
    .split('\n')
    .map((line) => (line.trim() === '' ? '' : line))
    .join('<br>'),
)

provide(chartPanelDialogOpenKey, showDialog)
</script>

<style scoped>
.chart-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Title and description sit tight; any leftover height a row needs to keep
   its cards level goes between the description and the link. */
.chart-panel__title {
  flex: none;
  margin-bottom: 8px;
}

.chart-panel__description {
  flex: 1 0 auto;
  margin-bottom: 4px;
}

.chart-panel__details {
  margin-bottom: 16px;
}

.q-chart-description :deep(p:last-child) {
  margin-bottom: 0;
}

.chart-panel__link {
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
}

/* Full-screen details: generous top / bottom margins, content centred, and a
   close cross pinned to the top right corner. */
.chart-panel-dialog {
  position: relative;
}

.chart-panel-dialog__body {
  padding: 96px 48px;
}

.chart-panel-dialog__description :deep(p) {
  font-size: 16px;
  line-height: 26px;
}

/* Top-right corner: the chart's own "..." menu (a round neutral button) sits
   beside the yellow round close button. */
.chart-panel-dialog__close {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 101;
  width: 44px;
  height: 44px;
}

/* Only the chart sits in a bordered container (the data table below stays
   outside it), so the "..." menu keeps anchoring to the dialog corner. */
.chart-panel-dialog :deep(.chart-shell__frame) {
  padding: 24px;
  border: 1px solid var(--secondary-border-color);
  border-radius: 12px; /* radius-lg */
  background-color: white;
}

.body--dark .chart-panel-dialog :deep(.chart-shell__frame) {
  background-color: var(--nav-bg);
}

.chart-panel-dialog :deep(.chart-toolbar) {
  top: 24px;
  right: 80px;
  min-height: 0;
  padding: 0;
}

.chart-panel-dialog :deep(.chart-toolbar .q-btn) {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: 1px solid var(--secondary-border-color);
  background-color: white;
  color: var(--foreground-color);
}

.body--dark .chart-panel-dialog :deep(.chart-toolbar .q-btn) {
  background-color: var(--nav-bg);
}

.chart-panel-dialog-content {
  width: 100%;
  max-width: 1024px;
  margin: 0 auto;
}

@media (max-width: 767px) {
  .chart-panel-dialog__body {
    padding: 72px 16px 48px;
  }

  .chart-panel-dialog__close {
    top: 12px;
    right: 12px;
  }

  .chart-panel-dialog :deep(.chart-toolbar) {
    top: 12px;
    right: 68px;
  }
}

.q-chart-description {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5rem;
  min-height: calc(3 * 1.5rem);
}
</style>
