<template>
  <chart-panel
    :title="chartTitle"
    :description="descriptionText"
    :chart-info-text="chartInfoText"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item v-if="!isComparison" clickable v-close-popup @click="onToggleModalType">
              <q-item-section side>
                <q-icon :name="modalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  modalType === 'simple'
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
    <e-charts-shell
      ref="shellRef"
      :height="height"
      :loading="props.loading"
      :has-data="total > 0"
      :show-table="!exportable"
      :no-data-title="chartTitle"
      :option="option"
      :exportable="!!exportable"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
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
import {
  GROUP_COLORS,
  MODE_COLORS,
  SIMPLE_LABELS_COLORS,
  COMPLEX_LABELS_COLORS,
  modeSortOrder,
  simpleLabelSortOrder,
  complexLabelSortOrder,
} from './commons'
import type { EnergyByLabel, JourneyEnergyStats } from '@/models'
import { formatNumber } from '@/utils/numbers'

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

const modalType = ref<'simple' | 'detailed'>('simple')

function onToggleModalType() {
  modalType.value = modalType.value === 'simple' ? 'detailed' : 'simple'
  initChartOptions()
}

// Which label vocabulary/colors to use for the current (type, modalType) combination:
// - simple labels (MA/TP/...) are shared between current and reco.
// - detailed current labels come from typo.reco.complex_labels (can be '+'-joined combos).
// - detailed reco labels come from typo.reco.reco_inter (a single real mode, never joined).
const labelNamespace = computed(() => {
  if (modalType.value === 'simple') return 'simple_labels'
  return props.type === 'current' ? 'complex_labels' : 'transportation_modes'
})
const labelColors = computed(() => {
  if (modalType.value === 'simple') return SIMPLE_LABELS_COLORS
  return props.type === 'current' ? COMPLEX_LABELS_COLORS : MODE_COLORS
})
function labelSortOrder(label: string): number {
  if (modalType.value === 'simple') return simpleLabelSortOrder(label)
  return props.type === 'current' ? complexLabelSortOrder(label) : modeSortOrder(label)
}
function labelText(label: string): string {
  return t(`${labelNamespace.value}.${label}`)
}

// Comparison mode doesn't use the simple/detailed breakdown at all (the toggle
// is hidden there too), so the title stays plain in that case.
const chartTitle = computed(() => {
  const base = t(`stats.energy_journey.title_${props.type}`)
  if (isComparison.value) return base
  return `${base} (${t(`stats.freq_mod.modal_split.${modalType.value}`).toLowerCase()})`
})

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

const descriptionText = computed(() =>
  isComparison.value && props.type === 'current'
    ? ''
    : t(`stats.energy_journey.description_${props.type}`),
)

const comparisonEnergyItems = computed(() => {
  if (!isComparison.value || props.type !== 'current') return null

  const groups = stats.comparisonResults?.groups ?? []
  if (groups.length < 2) return null

  const lastGroup = groups[groups.length - 1]!
  const prevGroup = groups[groups.length - 2]!
  const lastStats = lastGroup.journey_energy_stats?.current
  const prevStats = prevGroup.journey_energy_stats?.current
  if (!lastStats || !prevStats || lastStats.total === 0 || prevStats.total === 0) return null

  const lastCount = lastGroup.journey_energy_stats?.gains.current_above_who_count ?? 0
  const prevCount = prevGroup.journey_energy_stats?.gains.current_above_who_count ?? 0

  return {
    lastGroup: lastGroup.name,
    prevGroup: prevGroup.name,
    lastCount,
    lastPercent: (lastCount / lastStats.total) * 100,
    prevCount,
    prevPercent: (prevCount / prevStats.total) * 100,
  }
})

const comparisonEnergyItemsLabels = computed(() => {
  const ci = comparisonEnergyItems.value
  if (!ci) return null

  return {
    lastGroup: ci.lastGroup,
    prevGroup: ci.prevGroup,
    lastCount: formatNumber(ci.lastCount),
    lastPercent: formatNumber(Math.round(ci.lastPercent)),
    prevCount: formatNumber(ci.prevCount),
    prevPercent: formatNumber(Math.round(ci.prevPercent)),
  }
})

const chartInfoText = computed(() => {
  if (comparisonEnergyItemsLabels.value) {
    return t(`stats.energy_journey.texts.comparison`, comparisonEnergyItemsLabels.value)
  }

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

  const rawData: EnergyByLabel[] =
    props.journeyEnergyStats[props.type]?.breakdown[modalType.value] || []
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

  // Data already summed per (token, label) backend-side: no leg-level aggregation left to do here.
  const tokenMap: Record<string, Record<string, number>> = {}
  const labelsSet = new Set<string>()

  rawData.forEach((item) => {
    if (!tokenMap[item.token]) {
      tokenMap[item.token] = {}
    }
    tokenMap[item.token]![item.label] = (tokenMap[item.token]![item.label] || 0) + item.energy_kcal
    labelsSet.add(item.label)
  })

  // 2. Sort tokens by total energy (descending)
  const sortedTokens = Object.keys(tokenMap).sort((a, b) => {
    const totalA = Object.values(tokenMap[a]!).reduce((s, v) => s + v, 0)
    const totalB = Object.values(tokenMap[b]!).reduce((s, v) => s + v, 0)
    return totalB - totalA
  })

  const labels = Array.from(labelsSet).sort((a, b) => labelSortOrder(a) - labelSortOrder(b))

  // 3. Create Series (one series per label for stacking)
  const series: SeriesOption[] = labels.map((label) => {
    return {
      name: labelText(label),
      type: 'bar',
      stack: 'total', // This enables the stacking
      emphasis: { focus: 'series' },
      itemStyle: {
        color: labelColors.value[label] || labelColors.value['default'] || '#000000',
      },
      data: sortedTokens.map((token) => {
        const value = tokenMap[token]![label] || 0
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
      text: chartTitle.value,
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
        ...labels.map((label) => ({
          name: labelText(label),
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
    total.value += journeyStats?.total ?? 0
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
      text: chartTitle.value,
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
