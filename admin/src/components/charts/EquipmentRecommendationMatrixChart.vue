<template>
  <chart-panel
    :title="chartTitle"
    :description="t('stats.equipments_by_recommendations.texts.default')"
    :chart-info-text="chartInfoText"
    :inline="inline"
  >
    <div>
      <q-toolbar v-if="!inline" class="chart-toolbar">
        <q-space />
        <q-btn flat icon="more_vert">
          <q-menu>
            <q-list style="min-width: 200px">
              <q-item clickable v-close-popup @click="onToggleModalType">
                <q-item-section side>
                  <q-icon :name="stats.equipmentsModalType === 'simple' ? 'pie_chart' : 'lens'" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{
                    stats.equipmentsModalType === 'simple'
                      ? t('stats.freq_mod.modal_split.detailed')
                      : t('stats.freq_mod.modal_split.simple')
                  }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="withOptions" clickable v-close-popup @click="onToggleSimpleMode">
                <q-item-section side>
                  <q-icon :name="simpleMode ? 'check_box' : 'check_box_outline_blank'" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{
                    t('stats.equipments_by_recommendations.simpleMode')
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
      <e-charts-shell
        ref="shellRef"
        :height="height"
        :loading="props.loading"
        :has-data="total > 0"
        :show-table="inline"
        :no-data-title="chartTitle"
        :option="option"
        :exportable="!inline"
      >
      </e-charts-shell>
    </div>
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
} from 'echarts/components'
import { formatNumber } from '@/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import {
  equipmentLabels,
  type EquipmentPerRecommendation,
  type EquipmentsStats,
  recommendationLabelsReversed,
  recommendationToEquipmentMap,
} from '@/models'
import {
  aggregateEquipmentMatrixBySimpleLabel,
  aggregateRecommendationEquipmentsBySimpleLabel,
  simpleLabelSortOrder,
} from './commons'
import { isSimpleLabel } from '@/utils/modalities'

const { t, locale } = useI18n()
use([
  SVGRenderer,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
])

interface Props {
  equipmentsStats: EquipmentsStats | null
  height?: number
  loading?: boolean
  hasOptions?: boolean
  inline?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const stats = useStats()

const modalType = computed(() => (stats.equipmentsModalType === 'simple' ? 'simple' : 'detailed'))

const chartTitle = computed(
  () =>
    `${t('stats.equipments_by_recommendations.title')} (${t(
      `stats.freq_mod.modal_split.${modalType.value}`,
    ).toLowerCase()})`,
)

function onToggleModalType() {
  stats.equipmentsModalType = stats.equipmentsModalType === 'simple' ? 'detailed' : 'simple'
}

function onChartDownload() {
  shellRef.value?.handleExport()
}

const option = ref<EChartsOption>({})
const total = ref(0)

const simpleMode = ref(false)

function onToggleSimpleMode() {
  simpleMode.value = !simpleMode.value
}

const withOptions = computed(() => {
  return props.hasOptions && total.value > 0
})

const chartInfoText = computed(() => {
  const parts: string[] = []
  if (analysisText.value) {
    parts.push(t('stats.equipments_by_recommendations.texts.specific', analysisText.value))
  }
  if (withOptions.value) {
    parts.push(t('stats.equipments_by_recommendations.texts.hover_hint'))
  }
  return parts.join('\n\n')
})

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    return chartInfoText.value
  },
})

// The recommendation axis: one row per recommendation, or per simple typology
// label when they are folded. Least to most sustainable, bottom to top, as
// ECharts renders the first category at the bottom.
//
// We disable filtering of the rows without matching equipments for now, kept as
// a comment for reference in case we want to re-enable it in the future.
// return [
//   ...recommendationLabelsReversed.filter((r) => !!recommendationToEquipmentMap[r]),
//   'marche', // always shown, even out of the mapping: it is a common recommendation
// ]
const recommendationRows = computed<string[]>(() => {
  if (modalType.value !== 'simple') {
    return [...recommendationLabelsReversed]
  }
  return Object.keys(recommendationMatrix.value).sort(
    (a, b) => simpleLabelSortOrder(b) - simpleLabelSortOrder(a),
  )
})

const recommendationMatrix = computed<Record<string, EquipmentPerRecommendation>>(() => {
  const matrix = props.equipmentsStats?.equipment_recommendation_matrix
  if (!matrix) {
    return {}
  }
  return modalType.value === 'simple'
    ? aggregateEquipmentMatrixBySimpleLabel(matrix)
    : { ...matrix }
})

const rowEquipments = computed<Record<string, (typeof equipmentLabels)[number][] | null>>(() =>
  modalType.value === 'simple'
    ? aggregateRecommendationEquipmentsBySimpleLabel()
    : recommendationToEquipmentMap,
)

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale, simpleMode, modalType], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

const analysisText = computed(() => {
  if (!props.equipmentsStats) return null

  const threshold = 5
  let smallestReco: string | null = null
  let smallestValue = Infinity

  for (const rec of recommendationRows.value) {
    const eqs = rowEquipments.value[rec]
    const row = recommendationMatrix.value[rec]

    if (eqs && row) {
      const value = eqs.reduce((sum, eq) => sum + row[eq as keyof EquipmentPerRecommendation], 0)
      if (value < smallestValue && value > threshold) {
        smallestValue = value
        smallestReco = rec
      }
    }
  }

  if (!smallestReco) return null

  const smallestRecoContent = recommendationMatrix.value[smallestReco]
  if (!smallestRecoContent) return null
  const percentage =
    smallestRecoContent.total > 0 ? (smallestValue / smallestRecoContent.total) * 100 : 0

  return {
    percentage: formatNumber(percentage),
    mode: keyLabel(smallestReco),
  }
})

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  // simple typology labels live in their own namespace
  if (isSimpleLabel(key)) {
    return t(`simple_labels.${key}`)
  }
  return t(`stats.equipments_by_recommendations.labels.${shortKey(key)}`)
}

function transformMatrixToData() {
  const data: [number, number, number][] = []

  recommendationRows.value.forEach((recLabel, recIdx) => {
    const row = recommendationMatrix.value[recLabel]
    if (!row) {
      return
    }
    equipmentLabels.forEach((eqLabel, eqIdx) => {
      if (simpleMode.value && !rowEquipments.value[recLabel]?.includes(eqLabel)) {
        return
      }

      const count = row[eqLabel as keyof EquipmentPerRecommendation]
      // ECharts Heatmap format: [xAxisIndex, yAxisIndex, value]
      if (count !== 0) {
        const percent = (count / row.total) * 100
        data.push([eqIdx, recIdx, percent])
      }
    })
  })

  return data
}

function matrixPositionToLabels(
  x: number,
  y: number,
): {
  recommendation: string
  equipment: keyof EquipmentPerRecommendation
} | null {
  const recommendation = recommendationRows.value[y]
  const equipment = equipmentLabels[x]
  if (!recommendation || !equipment) return null

  return { recommendation, equipment }
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  if (!props.equipmentsStats) {
    return
  }

  total.value = props.equipmentsStats.total

  const data = transformMatrixToData()

  // total.value = recoEmissions[0]?.total || 0
  const newOption: EChartsOption = {
    grid: {
      left: '0',
      right: '20',
      top: '50',
      bottom: '30',
      containLabel: true,
    },
    height: props.height - 100,
    title: {
      text: chartTitle.value,
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    // 4. ADD: xAxis and yAxis are REQUIRED for heatmap
    yAxis: {
      type: 'category',
      data: recommendationRows.value.map((l) => {
        const reco = recommendationMatrix.value[l]
        return `${keyLabel(l)} (${reco?.total ?? 0})`
      }),
      splitArea: { show: true },
      axisLabel: {
        interval: 0,
        align: 'right',
        margin: 10,
      },
    },
    xAxis: {
      type: 'category',
      position: 'top',
      data: equipmentLabels.map((l) => keyLabel(l)),
      splitArea: { show: true },
      axisLabel: {
        interval: 0,
        align: 'center',
        width: 80,
        overflow: 'break',
      },
    },
    // 5. ADD: VisualMap provides the color scale
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#FFCC33', '#FFFFE0', '#74C365'],
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: function (params: CallbackDataParams | CallbackDataParams[]) {
        const p = Array.isArray(params) ? params[0] : params
        if (!p || !p.value || !props.equipmentsStats) return ''

        const v = p.value as [number, number, number]
        if (v[2] === 0) return ''
        const labels = matrixPositionToLabels(v[0], v[1])
        if (!labels) return ''

        const reco = keyLabel(labels.recommendation)
        const equipment = keyLabel(labels.equipment)
        const count = recommendationMatrix.value[labels.recommendation]?.[labels.equipment] ?? 0

        return t(`stats.equipments_by_recommendations.tooltip`, {
          reco,
          equipment,
          count: formatNumber(count),
          percentage: formatNumber(v[2] || 0),
        })
      },
    },
    series: [
      {
        name: 'EmissionsByRecommendations',
        type: 'heatmap',
        label: {
          show: true,
          formatter: function (params) {
            if (!params.value || (params.value as [number, number, number])[2] === 0) {
              return ''
            }
            const labels = matrixPositionToLabels(
              (params.value as [number, number, number])[0],
              (params.value as [number, number, number])[1],
            )
            if (!labels) return ''
            const count = recommendationMatrix.value[labels.recommendation]?.[labels.equipment] ?? 0

            return `${formatNumber(count)} (${formatNumber((params.value as [number, number, number])[2] || 0)}%)`
          },
        },
        data,
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>

<style scoped>
.options {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.options > * {
  pointer-events: all;
}
</style>
