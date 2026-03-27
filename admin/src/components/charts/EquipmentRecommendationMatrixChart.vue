<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="total > 0"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="stats.loading"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.equipments_by_recommendations.title`) }}</div>
      <div class="text-subtitle1 text-grey-8 text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div>
    <p>{{ t(`stats.equipments_by_recommendations.texts.default`) }}</p>
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
  VisualMapComponent
} from 'echarts/components'
import { toMaxDecimals } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { equipmentLabels, type EquipmentPerRecommendation, type EquipmentRecommendationMatrix, recommendationLabels } from 'src/models'
// import { MODE_COLORS } from './commons'

const { t, locale } = useI18n()
const stats = useStats()
use([SVGRenderer, HeatmapChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, VisualMapComponent])

interface Props {
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const option = ref<EChartsOption>({})
const total = ref(0)

watch([() => stats.loading], () => {
  if (stats.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale], () => {
  if (!stats.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

const analysisText = computed(() => {
  if (!stats.equipmentsStats) return null

  const threshold = 0 // 5
  let smallestReco: keyof EquipmentRecommendationMatrix = recommendationLabels[0]
  let smallestEquipment: keyof EquipmentPerRecommendation = equipmentLabels[0]
  let smallestValue = stats.equipmentsStats.equipment_recommendation_matrix[smallestReco as keyof EquipmentRecommendationMatrix][smallestEquipment as keyof EquipmentPerRecommendation]
  
  for (const rec of recommendationLabels) {
    for (const eq of equipmentLabels) {
      const value = stats.equipmentsStats.equipment_recommendation_matrix[rec as keyof EquipmentRecommendationMatrix][eq as keyof EquipmentPerRecommendation]
      if (value < smallestValue && value > threshold) {
        smallestValue = value
        smallestReco = rec
        smallestEquipment = eq
      }
    }
  }

  const smallestRecoContent = stats.equipmentsStats.equipment_recommendation_matrix[smallestReco as keyof EquipmentRecommendationMatrix]
  const sumOfSmallestReco = Object.values(smallestRecoContent).reduce((sum, val) => sum + val, 0)
  const percentage = sumOfSmallestReco > 0 ? (smallestValue / sumOfSmallestReco) * 100 : 0

  return {
    percentage: toMaxDecimals(percentage, 2),
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
  const data: [number, number, number][] = [];

  recommendationLabels.forEach((recLabel, recIdx) => {
    const row = matrix[recLabel as keyof EquipmentRecommendationMatrix];
    equipmentLabels.forEach((eqLabel, eqIdx) => {
      const value = row[eqLabel as keyof EquipmentPerRecommendation];
      // ECharts Heatmap format: [xAxisIndex, yAxisIndex, value]
      if (value !== 0) data.push([recIdx, eqIdx, value]);
    });
  });

  return data;
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  if (!stats.equipmentsStats) {
    return
  }

  total.value = stats.equipmentsStats.total

  const data = transformMatrixToData(stats.equipmentsStats.equipment_recommendation_matrix)
  const max = data.reduce((max, item) => item[2] > max ? item[2] : max, 0)

  // total.value = recoEmissions[0]?.total || 0
  const newOption: EChartsOption = {
    grid: {
      left: '0',
      right: '20',
      top: '50',
      bottom: '30',
      containLabel: true,
    },
    animation: false,
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
    xAxis: {
      type: 'category',
      position: 'top',
      data: recommendationLabels.map(l => keyLabel(l)),
      splitArea: { show: true },
      axisLabel: {
        interval: 0,
        align: 'center',
        verticalAlign: 'bottom',
        margin: 10,
      }
    },
    yAxis: {
      type: 'category',
      data: equipmentLabels.map(l => keyLabel(l)),
      splitArea: { show: true },
      axisLabel: {
        interval: 0,
        rotate: 30,
        align: 'right',
        width: 100,
        overflow: 'break',
      }
    },
    // 5. ADD: VisualMap provides the color scale
    visualMap: {
      min: 0,
      max,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#cfc', '#0a0'] // Adjust colors to your theme
      }
    },
    tooltip: {
      trigger: "item",
      formatter: function (params: CallbackDataParams | CallbackDataParams[]) {
        const p = Array.isArray(params) ? params[0] : params
        if (!p) return ''

        const val = new Intl.NumberFormat().format(
          toMaxDecimals(p.value as number, 2) || 0
        );
        return `${p.name}<br/><b>${val} kgCO₂eq</b> (${p.percent}%)`;
      },
    },
    series: [
      {
        name: 'EmissionsByRecommendations',
        type: 'heatmap',
        label: {
          show: true,
        },
        data
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
