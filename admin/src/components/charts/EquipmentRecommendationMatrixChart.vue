<template>
  <div :style="`height: ${height}px; width: 100%; position: relative;`">
    <template v-if="total > 0">
      <e-charts
        ref="chart"
        autoresize
        :init-options="initOptions"
        :option="option"
        :update-options="updateOptions"
        :loading="stats.loading"
        :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
        :data-chart-id="chartId"
      />
      <div class="options">
        <q-toggle
          v-model="simpleMode"
          :label="t('stats.equipments_by_recommendations.simpleMode')"
          color="primary"
        />
      </div>
    </template>
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.equipments_by_recommendations.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div v-if="total > 0" class="q-mt-md chart-text" :data-chart-id="chartId">
    <p class="q-mb-xs">{{ t(`stats.equipments_by_recommendations.texts.default`) }}</p>
    <p v-if="analysisText">
      {{ t(`stats.equipments_by_recommendations.texts.specific`, analysisText) }}
    </p>
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
} from 'echarts/components'
import { formatNumber } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import {
  equipmentLabels,
  type EquipmentPerRecommendation,
  type EquipmentRecommendationMatrix,
  recommendationLabelsReversed,
  recommendationToEquipmentMap,
} from 'src/models'
import { useQuasar } from 'quasar'
import { getRandomId } from 'src/utils/random'
// import { MODE_COLORS } from './commons'

const { t, locale } = useI18n()
const $q = useQuasar()
const stats = useStats()
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
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chartId = getRandomId()
const option = ref<EChartsOption>({})
const total = ref(0)

const simpleMode = ref(false)

const recommendationLabelsFiltered = computed(() => {
  if (!simpleMode.value) {
    return recommendationLabelsReversed
  }

  const walking: 'marche' = 'marche' as const

  return [...recommendationLabelsReversed.filter((r) => !!recommendationToEquipmentMap[r]), walking] // we always want to show "marche" in simple mode, even if it's not in the mapping, because it's a common recommendation
})

watch([() => stats.loading], () => {
  if (stats.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale, simpleMode], () => {
  if (!stats.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

const analysisText = computed(() => {
  if (!stats.equipmentsStats) return null

  const threshold = 5
  let smallestReco: keyof EquipmentRecommendationMatrix | null = null
  let smallestValue = Infinity

  for (const rec of recommendationLabelsFiltered.value) {
    const eq = recommendationToEquipmentMap[rec as keyof EquipmentRecommendationMatrix]

    if (eq) {
      const value =
        stats.equipmentsStats.equipment_recommendation_matrix[
          rec as keyof EquipmentRecommendationMatrix
        ][eq as keyof EquipmentPerRecommendation]
      if (value < smallestValue && value > threshold) {
        smallestValue = value
        smallestReco = rec
      }
    }
  }

  if (!smallestReco) return null

  const smallestRecoContent =
    stats.equipmentsStats.equipment_recommendation_matrix[
      smallestReco as keyof EquipmentRecommendationMatrix
    ]
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
  return t(`stats.equipments_by_recommendations.labels.${shortKey(key)}`)
}

function transformMatrixToData(matrix: EquipmentRecommendationMatrix) {
  const data: [number, number, number][] = []

  recommendationLabelsFiltered.value.forEach((recLabel, recIdx) => {
    const row = matrix[recLabel as keyof EquipmentRecommendationMatrix]
    equipmentLabels.forEach((eqLabel, eqIdx) => {
      if (simpleMode.value && eqLabel !== recommendationToEquipmentMap[recLabel]) {
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
  recommendation: keyof EquipmentRecommendationMatrix
  equipment: keyof EquipmentPerRecommendation
} | null {
  const recommendation = recommendationLabelsFiltered.value[y]
  const equipment = equipmentLabels[x]
  if (!recommendation || !equipment) return null

  return { recommendation, equipment }
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  if (!stats.equipmentsStats) {
    return
  }

  total.value = stats.equipmentsStats.total

  const data = transformMatrixToData(stats.equipmentsStats.equipment_recommendation_matrix)

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
      text: t(`stats.equipments_by_recommendations.title`),
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
      data: recommendationLabelsFiltered.value.map((l) => {
        const reco =
          stats.equipmentsStats!.equipment_recommendation_matrix[
            l as keyof EquipmentRecommendationMatrix
          ]
        return `${keyLabel(l)} (${reco.total})`
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
        color: ['#cfc', '#0a0'], // Adjust colors to your theme
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: function (params: CallbackDataParams | CallbackDataParams[]) {
        const p = Array.isArray(params) ? params[0] : params
        if (!p || !p.value || !stats.equipmentsStats) return ''

        const v = p.value as [number, number, number]
        if (v[2] === 0) return ''
        const labels = matrixPositionToLabels(v[0], v[1])
        if (!labels) return ''

        const reco = keyLabel(labels.recommendation)
        const equipment = keyLabel(labels.equipment)
        const count =
          stats.equipmentsStats.equipment_recommendation_matrix[labels.recommendation][
            labels.equipment
          ]

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
            const count =
              stats.equipmentsStats!.equipment_recommendation_matrix[labels.recommendation][
                labels.equipment
              ]

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
}
</style>
