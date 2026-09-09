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
      <q-card flat>
        <q-card-section>
          <div class="chart-panel-dialog-content">
            <div class="text-h6 q-mb-md">{{ title }}</div>
            <q-markdown
              v-if="combinedDescription"
              class="compact q-mt-sm q-mb-md"
              :src="combinedDescription"
            />
            <slot></slot>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn no-caps :label="t('close')" color="primary" v-close-popup />
        </q-card-actions>
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

.chart-panel-dialog-content {
  width: 100%;
  max-width: 1024px;
  margin: 0 auto;
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
