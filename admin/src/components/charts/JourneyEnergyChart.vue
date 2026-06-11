<template>
  <e-charts-shell
    :height="height"
    :loading="props.loading"
    :has-data="total > 0"
    :show-info="total > 0"
    :no-data-title="t(`stats.energy_journey.title_${props.type}`)"
    :option="option"
    :exportable="!!exportable"
  >
    <p class="q-mb-xs">{{ t(`stats.energy_journey.texts.default`) }}</p>
    <q-markdown
      v-if="textLabelsCurrent"
      :src="t(`stats.energy_journey.texts.specific_current`, textLabelsCurrent)"
    />
    <q-markdown
      v-if="textLabelsReco"
      :src="t(`stats.energy_journey.texts.specific_reco`, textLabelsReco)"
    />
  </e-charts-shell>
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
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
import { MODE_COLORS } from './commons'
import type { JourneyEnergyData, JourneyEnergyStats } from 'src/models'
import { formatNumber } from 'src/utils/numbers'

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
  journeyEnergyStats?: JourneyEnergyStats | null
  xaxis?: string
  yaxis?: string
  height?: number
  loading?: boolean
  exportable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

const { t, locale } = useI18n()

const option = ref<EChartsOption>({})
const total = ref(0)
const addedEnergy = ref(0)
const newHealthyParticipants = ref(0)
const WHO_RECOMMENDATION = 150;

const textLabelsCurrent = computed(() => {
  if (props.type !== 'current' || total.value < 5 || !props.journeyEnergyStats) return null

  const averageEnergyExpenditurePerToken =
    props.journeyEnergyStats.current?.average_energy_per_unique_token || 0

  return {
    energy: formatNumber(averageEnergyExpenditurePerToken),
  }
})

const textLabelsReco = computed(() => {
  if (props.type !== 'reco' || total.value < 5 || !props.journeyEnergyStats) return null

  return {
    added_energy: formatNumber(addedEnergy.value),
    yoga_min: formatNumber(addedEnergy.value / 4.7), // Approximate conversion to minutes of yoga
    count: formatNumber(newHealthyParticipants.value || 0),
    percent_current: formatNumber(props.journeyEnergyStats.gains.current_above_who_count / props.journeyEnergyStats.current.data.length * 100),
    percent_potential: formatNumber(props.journeyEnergyStats.gains.reco_above_who_count / props.journeyEnergyStats.reco.data.length * 100),
  }
})

watch([() => props.loading, () => props.height, locale], () => {
  initChartOptions()
})

onMounted(() => {
  initChartOptions()
})
function initChartOptions() {
  option.value = {}

  total.value = 0

  if (!props.journeyEnergyStats) return

  const rawData = props.journeyEnergyStats[props.type]?.data || []
  total.value = rawData.length

  if (total.value === 0) return

  const averageEnergyExpenditurePerToken =
    props.journeyEnergyStats[props.type]?.average_energy_per_unique_token || 0
  addedEnergy.value =
    (props.journeyEnergyStats.reco.average_energy_per_unique_token ?? 0) -
    (props.journeyEnergyStats.current.average_energy_per_unique_token ?? 0)
  newHealthyParticipants.value =
    props.journeyEnergyStats.gains.reco_above_who_count -
    props.journeyEnergyStats.gains.current_above_who_count

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
      name: t(`transportation_modes.${mode}`),
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
      bottom: '25%',
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
        return `${formatNumber(value as number)} kcal`
      },
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      data: [
        ...modes.map((mode) => ({
          name: t(`transportation_modes.${mode}`),
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
      data: sortedTokens.map((_, i) => `${i + 1}`), // Truncate tokens for display
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
        data: sortedTokens.map(() => WHO_RECOMMENDATION), // Constant value for the line
        lineStyle: {
          width: 0, // Hide the line itself
        },
        markLine: {
          symbol: ['none', 'none'], // Remove arrows
          label: {
            show: true,
            position: 'insideEndTop',
            formatter: `${WHO_RECOMMENDATION} kcal`,
            distance: 10,
            fontWeight: 'bold',
          },
          lineStyle: {
            type: 'dashed',
            width: 2,
            opacity: 0.8,
          },
          data: [
            {
              yAxis: WHO_RECOMMENDATION,
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
            formatter: `${formatNumber(averageEnergyExpenditurePerToken)} kcal`,
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
