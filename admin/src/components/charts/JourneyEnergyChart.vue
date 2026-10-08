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
            <q-item v-if="boxplotActive" clickable v-close-popup @click="onToggleJitter">
              <q-item-section side>
                <q-icon :name="showJitter ? 'visibility_off' : 'visibility'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  showJitter
                    ? t('stats.energy_journey.hide_jitter')
                    : t('stats.energy_journey.show_jitter')
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
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { use } from 'echarts/core'
import { BarChart, BoxplotChart, LineChart, ScatterChart } from 'echarts/charts'
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
  comparisonTotal,
} from './commons'
import type { EnergyByLabel, JourneyEnergyStats } from '@/models'
import { formatKcal, formatNumber, formatPercent } from '@/utils/numbers'
import { boxGroups, sortBoxGroups, boxRecoKcal, type BoxKeyField } from './energyBoxes'

const stats = useStats()
const isComparison = computed(() => !!stats.comparisonMode)

// Register ECharts modules
use([
  SVGRenderer,
  BarChart,
  BoxplotChart,
  ScatterChart,
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
// Individual answers (jitter) over the boxplot: on by default, toggleable from
// the chart menu when the boxplot is rendered.
const showJitter = ref(true)

// The boxplot replaces the bar chart past the answer threshold, single-campaign
// view only, when the box payload exists. Shared by the dispatch below and the
// menu item's visibility.
const boxplotActive = computed(
  () =>
    !isComparison.value &&
    (props.journeyEnergyStats?.current?.total ?? 0) > BOX_ANSWER_THRESHOLD &&
    boxSamples.value.length > 0,
)

function onToggleModalType() {
  modalType.value = modalType.value === 'simple' ? 'detailed' : 'simple'
  initChartOptions()
}

function onToggleJitter() {
  showJitter.value = !showJitter.value
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

// Boxplot (journey-level distributions): the grouping key follows the chart --
// the current chart groups by the journey's current label, the reco chart by
// its recommended one -- at the modal split the toggle selects. 'Autres' and
// 'Total' get their own labels from the behavior-change namespace.
const boxKeyField = computed(() => {
  if (props.type === 'current') {
    return modalType.value === 'simple' ? ('current_simple' as const) : ('current_complex' as const)
  }
  return modalType.value === 'simple' ? ('reco_simple' as const) : ('reco_mode' as const)
})

// Boxplot replaces the bar chart when the journey data has more than
// BOX_ANSWER_THRESHOLD answers (journeyEnergyStats.current.total).
const boxSamples = computed(() => props.journeyEnergyStats?.boxes?.samples ?? [])

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

// Boxplot replaces the bar chart above this many answers
const BOX_ANSWER_THRESHOLD = 100

const textLabelsCurrent = computed(() => {
  if (isComparison.value) return null
  if (props.type !== 'current' || total.value < 5 || !props.journeyEnergyStats) return null

  const averageEnergyExpenditurePerToken =
    props.journeyEnergyStats.current?.average_energy_per_unique_token || 0

  return {
    energy: formatKcal(averageEnergyExpenditurePerToken),
  }
})

const textLabelsReco = computed(() => {
  if (isComparison.value) return null
  if (props.type !== 'reco' || total.value < 5 || !props.journeyEnergyStats) return null

  return {
    added_energy: formatKcal(addedEnergy.value),
    yoga_min: formatNumber(addedEnergy.value / 4.7), // Approximate conversion to minutes of yoga
    count: formatNumber(newHealthyParticipants.value || 0),
    percent_current: formatPercent(
      (props.journeyEnergyStats.gains.current_above_who_count /
        props.journeyEnergyStats.current.total) *
        100,
    ),
    percent_potential: formatPercent(
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
    lastPercent: formatPercent(ci.lastPercent),
    prevCount: formatNumber(ci.prevCount),
    prevPercent: formatPercent(ci.prevPercent),
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
  if (textLabelsReco.value && addedEnergy.value > 0) {
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

  // Boxplot replaces the bar chart past the answer threshold (single-campaign
  // view; comparison mode keeps its own bars). The store's initial stats are
  // an empty object (no `current`) until /stats/all resolves: guard the read.
  if (boxplotActive.value) {
    initBoxplotOptions()
    return
  }

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
        return Math.round(value)
      }),
    }
  })

  // 4. Set Chart Options
  option.value = {
    grid: {
      left: '5%',
      right: '5%',
      bottom: '25%',
      top: '80px',
      containLabel: true,
    },
    title: {
      text: chartTitle.value,
      subtext: t(`stats.total_participants`, {
        count: props.journeyEnergyStats?.[props.type].total ?? 0,
      }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter(value) {
        return `${formatKcal(value as number)}\u00A0kcal`
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
          itemStyle: { color: '#c96f6b' },
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
            formatter: `${WHO_RECOMMENDATION}\u00A0kcal`,
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
          color: '#c96f6b',
        },
        lineStyle: {
          opacity: 0,
        },
        markLine: {
          symbol: ['none', 'none'], // Remove arrows
          label: {
            show: true,
            position: 'insideEndTop',
            formatter: `${formatKcal(averageEnergyExpenditurePerToken)}\u00A0kcal`,
            distance: 10,
            fontWeight: 'bold',
            color: '#c96f6b',
          },
          lineStyle: {
            color: '#c96f6b', // Red line
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

/**
 * Boxplot view (journey-level distributions, replaces the bar chart when the
 * journey data has more than BOX_ANSWER_THRESHOLD answers). One box pair per
 * group: 'Total' always first, then a box per mode reaching the split
 * threshold (10 samples), then 'Autres' pooling the modes below it. The reco
 * chart shows two boxes per group -- the journey's current daily kcal and its
 * potential daily kcal under the recommended mode (current when the journey
 * has no per-journey recommendation); the current chart shows one box per
 * group (current kcal). Real samples are jittered over each box.
 */
function initBoxplotOptions() {
  const journeyStats = props.journeyEnergyStats
  if (!journeyStats?.current) return
  option.value = {}
  total.value = journeyStats.current.total ?? 0

  const keyField = boxKeyField.value
  const keyOrderFn = boxKeyOrder(keyField)
  const samples = boxSamples.value
  const grouped = sortBoxGroups(boxGroups(samples, keyField, keyOrderFn), keyOrderFn)
  if (grouped.length === 0) {
    return
  }

  const isPaired = props.type === 'reco'
  // One category per BOX slot: two per group in paired mode (current box left,
  // reco box right), one per group otherwise. The two boxplot series are
  // null-padded so each box renders in its own slot (a series maps box i to
  // category i, so overlapping slots would draw the pairs on top of each
  // other).
  const slots: string[] = []
  grouped.forEach((group) => {
    if (isPaired) {
      slots.push(boxGroupLabel(group.key), boxGroupLabel(group.key))
    } else {
      slots.push(boxGroupLabel(group.key))
    }
  })

  const boxCurrentValues: (number[] | null)[] = []
  const boxRecoValues: (number[] | null)[] = []
  const jitterCurrent: [number, number][] = []
  const jitterReco: [number, number][] = []

  grouped.forEach((group, groupIndex) => {
    const groupSamples = group.samples
    const currentIdx = isPaired ? groupIndex * 2 : groupIndex
    const recoIdx = isPaired ? groupIndex * 2 + 1 : -1
    // A single sample has no spread: the jitter point carries it.
    boxCurrentValues[currentIdx] =
      groupSamples.length >= 2 ? groupSamples.map((s) => Math.round(s.current_kcal)) : null
    if (isPaired) {
      boxRecoValues[recoIdx] =
        groupSamples.length >= 2 ? groupSamples.map((s) => Math.round(boxRecoKcal(s))) : null
    }
    const jitterHalf = isPaired ? 0.2 : 0.25
    groupSamples.forEach((sample, i) => {
      // Deterministic scatter (i % 5), not random: the chart is stable across
      // re-renders, exports, and the printable report.
      jitterCurrent.push([currentIdx - jitterHalf + (i % 5) * (jitterHalf / 2), sample.current_kcal])
      if (isPaired) {
        jitterReco.push([recoIdx + jitterHalf - (i % 5) * (jitterHalf / 2), boxRecoKcal(sample)])
      }
    })
  })

  // ECharts boxplot takes [min, Q1, median, Q3, max] per box, and CRASHES on
  // null data entries (getInitialData reads item.value unconditionally) -- so
  // both box colors live in ONE series as per-item itemStyle, empty slots
  // carry an invisible zero box, and the pair colors appear in the legend via
  // empty dummy series (a series maps box i to category i, so two series with
  // null slots is not an option).
  const computeFiveNumbers = (values: number[]): number[] => {
    const sorted = [...values].sort((a, b) => a - b)
    const q = (p: number) => {
      const pos = (sorted.length - 1) * p
      const base = Math.floor(pos)
      const rest = pos - base
      return (
        sorted[base]! +
        (sorted[base + 1] !== undefined ? rest * (sorted[base + 1]! - sorted[base]!) : 0)
      )
    }
    return [sorted[0]!, q(0.25), q(0.5), q(0.75), sorted[sorted.length - 1]!]
  }

  const styleCurrent = boxItemStyle('current')
  const styleReco = boxItemStyle('reco')
  const boxplotData = slots.map((_, slotIdx) => {
    if (Array.isArray(boxCurrentValues[slotIdx])) {
      return { value: computeFiveNumbers(boxCurrentValues[slotIdx]!), itemStyle: styleCurrent }
    }
    if (Array.isArray(boxRecoValues[slotIdx])) {
      return { value: computeFiveNumbers(boxRecoValues[slotIdx]!), itemStyle: styleReco }
    }
    // No box in this slot (single-sample group): invisible placeholder, the
    // jitter points carry the values.
    return { value: [0, 0, 0, 0, 0], itemStyle: { opacity: 0 } }
  })

  const series: SeriesOption[] = [
    {
      name: 'boxplot',
      type: 'boxplot',
      data: boxplotData,
      // Tooltip rows are built per box color by the formatter below; the
      // series' own name never shows.
      silent: false,
    },
    // Legend dummies: empty data renders nothing, the icon carries the color.
    {
      name: t('stats.energy_journey.box_current'),
      type: 'line',
      data: [],
      itemStyle: { color: styleCurrent.borderColor },
      silent: true,
    },
    ...(isPaired
      ? [
          {
            name: t('stats.energy_journey.box_reco'),
            type: 'line',
            data: [],
            itemStyle: { color: styleReco.borderColor },
            silent: true,
          } as SeriesOption,
        ]
      : []),
    ...(showJitter.value
      ? [
          {
            name: t('stats.energy_journey.box_jitter'),
            type: 'scatter',
            data: isPaired ? [...jitterCurrent, ...jitterReco] : jitterCurrent,
            symbolSize: 5,
            itemStyle: { color: 'rgba(0,0,0,0.25)' },
            z: 20,
          } as SeriesOption,
        ]
      : []),
    {
      type: 'line',
      name: t('stats.energy_journey.whoMin'),
      color: 'black',
      symbol: 'none',
      silent: true, // Doesn't intercept mouse events
      data: [],
      markLine: {
        symbol: ['none', 'none'], // Remove arrows
        label: {
          show: true,
          position: 'insideEndTop',
          formatter: `${WHO_RECOMMENDATION}\u00A0kcal`,
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
  ]

  option.value = {
    grid: {
      left: '5%',
      right: '5%',
      bottom: '20%',
      top: '80px',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: chartTitle.value,
      subtext: t('stats.total_participants', { count: journeyStats.current.total }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (paramsList: CallbackDataParams | CallbackDataParams[]) => {
        const list = Array.isArray(paramsList) ? paramsList : [paramsList]
        let res = `${list[0]?.name}<br/>`
        list.forEach((item) => {
          if (item.seriesType === 'scatter') return
          const value = item.value
          if (Array.isArray(value) && value.length >= 5) {
            const [lo, q1, med, q3, hi] = value as number[]
            // An invisible placeholder box (all zeros, single-sample slot)
            // contributes no row.
            if (lo === 0 && q1 === 0 && med === 0 && q3 === 0 && hi === 0) return
            const style = (item as unknown as { data?: { itemStyle?: { borderColor?: string } } })
              .data?.itemStyle
            const isReco = style?.borderColor === styleReco.borderColor
            const name = isReco
              ? t('stats.energy_journey.box_reco')
              : t('stats.energy_journey.box_current')
            res +=
              `${item.marker} ${name}: ` +
              `${formatKcal(lo)} / ${formatKcal(med)} / ${formatKcal(hi)}<br/>` +
              `&nbsp;&nbsp;Q1 ${formatKcal(q1)} · Q3 ${formatKcal(q3)}<br/>`
          } else if (typeof value === 'number') {
            res += `${item.marker} ${item.seriesName}: ${formatKcal(value)}\u00A0kcal<br/>`
          }
        })
        return res
      },
    },
    legend: {
      bottom: 0,
      data: [
        { name: t('stats.energy_journey.box_current'), icon: 'roundRect' },
        ...(isPaired ? [{ name: t('stats.energy_journey.box_reco'), icon: 'roundRect' }] : []),
        ...(showJitter.value ? [{ name: t('stats.energy_journey.box_jitter'), icon: 'circle' }] : []),
        { name: t('stats.energy_journey.whoMin'), icon: 'rect', itemStyle: { color: 'black' } },
      ],
    },
    xAxis: {
      type: 'category',
      data: slots,
      name: props.xaxis || '',
      nameLocation: 'middle',
      nameGap: 30,
      axisLabel: {
        interval: 0,
        width: 120,
        overflow: 'break',
      },
    },
    yAxis: {
      type: 'value',
      name: t('stats.energy_journey.yaxis'),
      nameLocation: 'middle',
      nameGap: 40,
    },
    series,
  }
}

function boxGroupLabel(key: string): string {
  if (key === 'total') return t(`stats.behavior_change_levers.labels.total`)
  if (key === 'autres') return t(`stats.behavior_change_levers.labels.autres`)
  return labelText(key)
}

function boxItemStyle(kind: 'current' | 'reco') {
  if (kind === 'current') {
    return { color: '#eef3f8', borderColor: '#6a88b0', borderWidth: 1.5 }
  }
  return { color: '#f3f8ee', borderColor: '#8fb87d', borderWidth: 1.5 }
}

function boxKeyOrder(keyField: BoxKeyField): (key: string) => number {
  if (keyField === 'current_simple' || keyField === 'reco_simple') {
    return simpleLabelSortOrder
  }
  if (keyField === 'current_complex') {
    return complexLabelSortOrder
  }
  return modeSortOrder
}

function initComparisonChartOptions() {
  option.value = {}
  total.value = 0

  const groups = stats.comparisonResults?.groups ?? []
  const groupStats = groups.map((group) => ({
    name: group.name,
    participants: group.total,
    stats: group.journey_energy_stats,
  }))
  if (groupStats.every((group) => !group.stats)) return

  const avgKcal = groupStats.map((group) => {
    const journeyStats = group.stats?.[props.type]
    total.value += journeyStats?.total ?? 0
    return Math.round(journeyStats?.average_energy_per_unique_token ?? 0)
  })
  const aboveWhoCount = groupStats.map((group) => {
    const gains = group.stats?.gains
    return (
      (props.type === 'current' ? gains?.current_above_who_count : gains?.reco_above_who_count) ?? 0
    )
  })

  if (total.value === 0) return

  const metricLabels = [t('stats.energy_journey.yaxis'), t('stats.energy_journey.who_above_count')]

  const series: SeriesOption[] = []
  groupStats.forEach((group, i) => {
    const color = GROUP_COLORS[i % GROUP_COLORS.length] ?? '#ccc'
    series.push({
      name: group.name,
      type: 'bar',
      xAxisIndex: 0,
      yAxisIndex: 0,
      color,
      data: [avgKcal[i] ?? 0, null],
      ...(i === 0
        ? {
            markLine: {
              symbol: ['none', 'none'],
              label: {
                show: true,
                position: 'insideEndTop',
                formatter: `${WHO_RECOMMENDATION}\u00A0kcal`,
                distance: 10,
                fontWeight: 'bold',
              },
              lineStyle: { type: 'dashed', width: 2, opacity: 0.8 },
              data: [{ yAxis: WHO_RECOMMENDATION }],
              z: 1000,
            },
          }
        : {}),
    })
    series.push({
      name: group.name,
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      color,
      data: [null, aboveWhoCount[i] ?? 0],
    })
  })

  option.value = {
    grid: {
      left: '10%',
      right: '10%',
      bottom: '20%',
      top: '80px',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: chartTitle.value,
      subtext: t('stats.total_participants', { count: comparisonTotal(total.value) }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (paramsList: CallbackDataParams | CallbackDataParams[]) => {
        const list = Array.isArray(paramsList) ? paramsList : [paramsList]
        let res = `${list[0]?.name}<br/>`
        list.forEach((item) => {
          if (item.value == null || Number.isNaN(Number(item.value))) return
          res += `${item.marker} ${item.seriesName}: <b>${formatNumber(Number(item.value))}</b><br/>`
        })
        return res
      },
    },
    legend: {
      bottom: 0,
      data: groupStats.map((group) => group.name),
    },
    xAxis: [
      {
        type: 'category',
        data: metricLabels,
        name: props.xaxis || '',
        nameLocation: 'middle',
        nameGap: 30,
        axisLabel: {
          interval: 0,
          width: 150,
          overflow: 'break',
        },
      },
      // Shown nowhere, but keeps the count bars in their own band layout, not
      // squeezed by the kcal series' null slots.
      {
        type: 'category',
        data: metricLabels,
        axisLabel: { show: false },
        axisTick: { show: false },
        axisLine: { show: false },
      },
    ],
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
