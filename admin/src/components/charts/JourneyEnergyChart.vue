<template>
  <chart-panel
    :title="t(`stats.energy_journey.title_${props.type}`)"
    :description="t(`stats.energy_journey.description_${props.type}`)"
    :chart-info-text="chartInfoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
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
      :show-table="!exportable"
      :no-data-title="t(`stats.energy_journey.title_${props.type}`)"
      :option="option"
      :exportable="!!exportable"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
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
import { GROUP_COLORS, MODE_COLORS } from './commons'
import type { JourneyEnergyData, JourneyEnergyStats } from 'src/models'
import { formatNumber } from 'src/utils/numbers'

const stats = useStats()
const isComparison = computed(() => !!stats.comparisonMode)

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
  inline?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

const { t, locale } = useI18n()

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

function onChartDownload() {
  shellRef.value?.handleExport()
}

const option = ref<EChartsOption>({})
const total = ref(0)
const addedEnergy = ref(0)
const newHealthyParticipants = ref(0)
const WHO_RECOMMENDATION = 150

const textLabelsCurrent = computed(() => {
  if (isComparison.value) return null
  if (props.type !== 'current' || total.value < 5 || !props.journeyEnergyStats) return null

  const averageEnergyExpenditurePerToken =
    props.journeyEnergyStats.current?.average_energy_per_unique_token || 0

  return {
    energy: formatNumber(averageEnergyExpenditurePerToken),
  }
})

const textLabelsReco = computed(() => {
  if (isComparison.value) return null
  if (props.type !== 'reco' || total.value < 5 || !props.journeyEnergyStats) return null

  return {
    added_energy: formatNumber(addedEnergy.value),
    yoga_min: formatNumber(addedEnergy.value / 4.7), // Approximate conversion to minutes of yoga
    count: formatNumber(newHealthyParticipants.value || 0),
    percent_current: formatNumber(
      (props.journeyEnergyStats.gains.current_above_who_count /
        props.journeyEnergyStats.current.total) *
        100,
    ),
    percent_potential: formatNumber(
      (props.journeyEnergyStats.gains.reco_above_who_count / props.journeyEnergyStats.reco.total) *
        100,
    ),
  }
})

const chartInfoText = computed(() => {
  const parts: string[] = [t(`stats.energy_journey.texts.default`)]
  if (textLabelsCurrent.value) {
    parts.push(t(`stats.energy_journey.texts.specific_current`, textLabelsCurrent.value))
  }
  if (textLabelsReco.value) {
    parts.push(t(`stats.energy_journey.texts.specific_reco`, textLabelsReco.value))
  }
  return parts.join('\n\n')
})

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    return chartInfoText.value
  },
})

watch([() => props.loading, () => props.height, locale], () => {
  initChartOptions()
})

onMounted(() => {
  initChartOptions()
})
function initChartOptions() {
  if (isComparison.value) {
    initComparisonChartOptions()
    return
  }

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

function initComparisonChartOptions() {
  option.value = {}
  total.value = 0

  const groups = stats.comparisonResults?.groups ?? []
  const groupStats = groups.map((group) => ({
    name: group.name,
    stats: group.journey_energy_stats,
  }))
  if (groupStats.every((group) => !group.stats)) return

  const avgKcal = groupStats.map((group) => {
    const journeyStats = group.stats?.[props.type]
    total.value += journeyStats?.data.length ?? 0
    return parseFloat((journeyStats?.average_energy_per_unique_token ?? 0).toFixed(2))
  })
  const aboveWhoCount = groupStats.map((group) => {
    const gains = group.stats?.gains
    return (
      (props.type === 'current' ? gains?.current_above_who_count : gains?.reco_above_who_count) ?? 0
    )
  })

  if (total.value === 0) return

  const series: SeriesOption[] = [
    {
      name: t('stats.energy_journey.yaxis'),
      type: 'bar',
      yAxisIndex: 0,
      color: GROUP_COLORS[0] ?? '#ccc',
      data: avgKcal,
      markLine: {
        symbol: ['none', 'none'],
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
        data: [{ yAxis: WHO_RECOMMENDATION }],
        z: 1000,
      },
    },
    {
      name: t('stats.energy_journey.who_above_count'),
      type: 'bar',
      yAxisIndex: 1,
      color: GROUP_COLORS[1] ?? '#ccc',
      data: aboveWhoCount,
    },
  ]

  option.value = {
    grid: {
      left: '10%',
      right: '10%',
      bottom: '20%',
      top: '60px',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t(`stats.energy_journey.title_${props.type}`),
      left: 'center',
      textStyle: { fontSize: 16 },
    },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      bottom: 0,
      data: [t('stats.energy_journey.yaxis'), t('stats.energy_journey.who_above_count')],
    },
    xAxis: {
      type: 'category',
      data: groupStats.map((group) => group.name),
      name: props.xaxis || '',
      nameLocation: 'middle',
      nameGap: 30,
    },
    yAxis: [
      {
        type: 'value',
        name: t('stats.energy_journey.yaxis'),
        nameLocation: 'middle',
        nameGap: 40,
      },
      {
        type: 'value',
        name: t('stats.nb_employees'),
        nameLocation: 'middle',
        nameGap: 40,
      },
    ],
    series,
  }
}
</script>
