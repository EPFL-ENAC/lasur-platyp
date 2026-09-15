<template>
  <chart-panel
    :title="titleText"
    :description="descriptionText"
    :chart-info-text="infoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleRecoModalType">
              <q-item-section side>
                <q-icon :name="stats.recoModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.recoModalType === 'simple'
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
    <share-chart
      v-if="stats.recoModalType === 'simple'"
      ref="simpleChartRef"
      chartTranslationName="reco_simple"
      label-type="simple"
      reference-modal-split
      :frequencies="simpleFrequencies"
      :height="height"
      :loading="loading"
      :exportable="!inline"
      @update:chart-info-text="childText = $event"
    />
    <share-chart
      v-if="stats.recoModalType === 'detailed'"
      ref="detailedChartRef"
      chartTranslationName="reco_inter"
      reference-modal-split
      :frequencies="detailedFrequencies"
      :height="height"
      :loading="loading"
      :exportable="!inline"
      @update:chart-info-text="childText = $event"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import ShareChart from '@/components/charts/ShareChart.vue'
import type { Frequencies } from '@/models'

interface Props {
  height: number
  loading?: boolean
  simpleFrequencies: Frequencies | null
  detailedFrequencies: Frequencies | null
  inline?: boolean
}

defineProps<Props>()

type ShareChartExposed = {
  handleExport: () => Promise<void>
}

const simpleChartRef = ref<ShareChartExposed | null>(null)
const detailedChartRef = ref<ShareChartExposed | null>(null)
// Only one of the two charts is rendered at a time, so it is the one emitting.
const childText = ref('')

const stats = useStats()

const { t } = useI18n()

// The comparison charts carry the MRMT reference bar: cite its source, with
// the note the modal split charts already use.
const infoText = computed(() =>
  stats.comparisonMode ? `${childText.value}\n\n${t('stats.freq_mod.texts.ref')}` : childText.value,
)

const translationName = computed(() =>
  stats.recoModalType === 'simple' ? 'reco_simple' : 'reco_inter',
)

const titleText = computed(() => t(`stats.${translationName.value}.title`))

const descriptionText = computed(() =>
  stats.comparisonMode ? '' : t(`stats.${translationName.value}.description`),
)

function onToggleRecoModalType() {
  stats.recoModalType = stats.recoModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  const chartRef = stats.recoModalType === 'simple' ? simpleChartRef : detailedChartRef
  chartRef.value?.handleExport()
}
</script>
