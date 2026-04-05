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
      theme="platyp"
    />
    <div v-else>
      <div class="text-h6 text-center">
        {{ t(`stats.energy_journey.title_${props.type}`) }}
      </div>
      <div class="text-subtitle1 text-grey-8 text-center">
        {{ t('stats.no_data') }}
      </div>
    </div>
  </div>

  <div>
    <p>{{ t(`stats.energy_journey.texts.default`) }}</p>
    <q-markdown v-if="textLabels" :src="t(`stats.energy_journey.texts.specific`, textLabels)" />
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption, SeriesOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  MarkLineComponent,
} from 'echarts/components'
import { initOptions, updateOptions, MODE_COLORS } from './commons'
import type { JourneyEnergyData } from 'src/models'
import { toMaxDecimals } from 'src/utils/numbers'

// Register ECharts modules
use([
  SVGRenderer,
  BarChart,
  TitleComponent,
  LineChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  MarkLineComponent,
])

interface Props {
  type: 'current' | 'reco'
  xaxis?: string
  yaxis?: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const { t, locale } = useI18n()
const stats = useStats()

const option = ref<EChartsOption>({})
const total = ref(0)
const addedEnergy = ref(0)
const newHealthyParticipants = ref(0)

const textLabels = computed(() => {
  if (total.value < 5) return null

  return {
    added_energy: new Intl.NumberFormat().format(toMaxDecimals(addedEnergy.value, 2) || 0),
    count: new Intl.NumberFormat().format(newHealthyParticipants.value || 0),
  }
})

watch([() => stats.loading, () => props.height, locale], () => {
  initChartOptions()
})

onMounted(() => {
  initChartOptions()
})
function initChartOptions() {
  option.value = {}

  const rawData = stats.journeyEnergyStats[props.type]?.data || []
  total.value = rawData.length

  if (total.value === 0) return

  const averageEnergyExpenditurePerToken =
    stats.journeyEnergyStats[props.type]?.average_energy_per_unique_token || 0
  addedEnergy.value =
    (stats.journeyEnergyStats.reco.average_energy_per_unique_token ?? 0) -
    (stats.journeyEnergyStats.current.average_energy_per_unique_token ?? 0)
  newHealthyParticipants.value =
    stats.journeyEnergyStats.gains.reco_above_who_count -
    stats.journeyEnergyStats.gains.current_above_who_count

  const tokenMap: Record<string, Record<string, number>> = {}
  const modesSet = new Set<string>()

  rawData.forEach((item: JourneyEnergyData) => {
    if (!tokenMap[item.token]) {
      tokenMap[item.token] = {}
    }
    tokenMap[item.token]![item.mode] = (tokenMap[item.token]![item.mode] || 0) + item.energy_kcal
    modesSet.add(item.mode)
  })

  // 2. Sort tokens by total energy (descending)
  const sortedTokens = Object.keys(tokenMap).sort((a, b) => {
    const totalA = Object.values(tokenMap[a]!).reduce((s, v) => s + v, 0)
    const totalB = Object.values(tokenMap[b]!).reduce((s, v) => s + v, 0)
    return totalB - totalA
  })

  const modes = Array.from(modesSet)

  // 3. Create Series (one series per mode for stacking)
  const series: SeriesOption[] = modes.map((mode) => {
    return {
      name: t(`stats.energy_journey.labels.${mode}`),
      type: 'bar',
      stack: 'total', // This enables the stacking
      emphasis: { focus: 'series' },
      itemStyle: {
        color: MODE_COLORS[mode] || MODE_COLORS['default'] || '#000000',
      },
      data: sortedTokens.map((token) => {
        const value = tokenMap[token]![mode] || 0
        return parseFloat(value.toFixed(2))
      }),
    }
  })

  // 4. Set Chart Options
  option.value = {
    grid: {
      left: '5%',
      right: '5%',
      bottom: '20%',
      top: '60px',
      containLabel: true,
    },
    title: {
      text: t(`stats.energy_journey.title_${props.type}`),
      left: 'center',
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter(value) {
        return `${toMaxDecimals(value as number, 2)} kcal`
      },
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      data: [
        ...modes.map((mode) => ({
          name: t(`stats.energy_journey.labels.${mode}`),
          icon: 'circle',
        })),
        {
          name: t(`stats.energy_journey.whoMin`),
          icon: 'rect',
          itemStyle: { color: 'black' },
        },
        {
          name: t(`stats.energy_journey.participantsAverage`),
          icon: 'rect',
          itemStyle: { color: '#d32f2f' },
        },
      ],
    },
    xAxis: {
      type: 'category',
      data: sortedTokens.map((_, i) => `#${i + 1}`), // Truncate tokens for display
      name: props.xaxis || t(`stats.energy_journey.xaxis`),
      nameLocation: 'middle',
      nameGap: 30,
    },
    yAxis: {
      type: 'value',
      name: t(`stats.energy_journey.yaxis`),
      nameLocation: 'middle',
      nameGap: 40,
    },
    series: [
      ...series,
      {
        type: 'line',
        name: t(`stats.energy_journey.whoMin`),
        color: 'black',
        symbol: 'none',
        silent: true, // Doesn't intercept mouse events
        data: sortedTokens.map(() => 150), // Constant value for the line
        lineStyle: {
          width: 0, // Hide the line itself
        },
        markLine: {
          symbol: ['none', 'none'], // Remove arrows
          label: {
            show: true,
            position: 'insideEndTop',
            formatter: '150 kcal',
            distance: 10,
            fontWeight: 'bold',
            color: 'black',
          },
          lineStyle: {
            color: 'black',
            type: 'dashed',
            width: 2,
            opacity: 0.8,
          },
          data: [
            {
              yAxis: 150,
            },
          ],
          z: 1000,
        },
      },
      {
        type: 'line',
        name: t(`stats.energy_journey.participantsAverage`),
        symbol: 'none',
        silent: true,
        data: sortedTokens.map(() => averageEnergyExpenditurePerToken),
        itemStyle: {
          color: '#d32f2f',
        },
        lineStyle: {
          opacity: 0,
        },
        markLine: {
          symbol: ['none', 'none'], // Remove arrows
          label: {
            show: true,
            position: 'insideEndTop',
            formatter: `${toMaxDecimals(averageEnergyExpenditurePerToken, 2)} kcal`,
            distance: 10,
            fontWeight: 'bold',
            color: '#d32f2f',
          },
          lineStyle: {
            color: '#d32f2f', // Red line
            type: 'dashed',
            width: 2,
            opacity: 0.8,
          },
          data: [
            {
              yAxis: averageEnergyExpenditurePerToken,
            },
          ],
          z: 1001,
        },
      },
    ],
  }
}
</script>
