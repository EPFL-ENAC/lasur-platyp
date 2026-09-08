<template>
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
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption, SeriesOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  aggregateLeversBySimpleLabel,
  aggregateMotivationBySimpleLabel,
  CATEGORY_COLORS,
  MOTIVATION_COLORS,
} from './commons'
import { AXIS_LABEL_GAP, axisLabelsWidth, truncateAxisLabel } from './comparisonCharts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from '@/utils/numbers'
import type { CallbackDataParams, XAXisOption } from 'echarts/types/dist/shared'
import { lowerCaseFirst } from '@/utils/string'
import { moveToStart } from '@/utils/arrays'
import { isSimpleLabel } from '@/utils/modalities'
import type {
  BehaviorChangeByModeLever,
  BehaviorChangeByModeMotivation,
  BehaviorChangeStats,
} from '@/models'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const stats = useStats()
const isComparison = computed(() => !!stats.comparisonMode)

interface Props {
  type: 'levers' | 'motivation'
  behaviorChangeStats: BehaviorChangeStats | null
  height?: number
  loading?: boolean
  percent?: boolean
  exportable?: boolean
  description?: string
  // 'detailed' charts the data as it comes, one row per recommended mode;
  // 'simple' folds those modes into the simple typology labels. Left undefined,
  // the chart has no modal split and its title stays plain.
  modalType?: 'simple' | 'detailed'
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

const chartTitle = computed(() => {
  const base = t(`stats.behavior_change_${props.type}.title`)
  if (!props.modalType) {
    return base
  }
  return `${base} (${t(`stats.freq_mod.modal_split.${props.modalType}`).toLowerCase()})`
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    return props.description || ''
  },
})

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const option = ref<EChartsOption>({})
const total = ref(0)

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale, () => props.percent, () => props.modalType], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  // simple typology labels live in their own namespace, and are case sensitive
  if (isSimpleLabel(key)) {
    return t(`simple_labels.${key}`)
  }
  return t(`stats.behavior_change_${props.type}.labels.${shortKey(key)}`)
}

/** Rows as charted: recommended modes, or the simple labels they fold into. */
function leversByMode(byMode: BehaviorChangeByModeLever[]): BehaviorChangeByModeLever[] {
  return props.modalType === 'simple' ? aggregateLeversBySimpleLabel(byMode) : byMode
}

function motivationByMode(
  byMode: BehaviorChangeByModeMotivation[],
): BehaviorChangeByModeMotivation[] {
  return props.modalType === 'simple' ? aggregateMotivationBySimpleLabel(byMode) : byMode
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  if (isComparison.value) {
    initComparisonChartOptions()
    return
  }

  const opt = props.type === 'levers' ? leversOptions() : motivationOptions()
  if (!opt) {
    return
  }

  total.value = opt.total

  const newOption: EChartsOption = {
    grid: {
      left: '40',
      right: '20',
      top: '60',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height - 140,
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
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      show: true,
      bottom: 16,
    },
    xAxis: {
      type: 'value',
    },
    yAxis: {
      type: 'category',
      data: opt.categories,
    },
    series: opt.series,
  }
  if (props.percent) {
    ;(newOption.xAxis as XAXisOption).max = 100
  }
  option.value = newOption
}

function leversOptions() {
  const behaviorChangeData = props.behaviorChangeStats?.levers
  if (!behaviorChangeData) {
    return null
  }
  const byMode = leversByMode(behaviorChangeData.by_mode_levers)
  const allCategories = new Set<string>(
    byMode.flatMap((item) => item.levers.map((lever) => lever.category)),
  )

  const sorted = getSortedModes(byMode)

  return {
    series: Array.from(allCategories).map((category) => ({
      name: keyLabel(category),
      type: 'bar',
      stack: 'total',
      label: {
        show: true,
        position: 'inside',
        formatter: function (params: CallbackDataParams) {
          if (params.value === 0) {
            return ''
          }
          if (props.percent) {
            return `${formatNumber(params.value as number)}%`
          }
          return formatNumber(params.value as number)
        },
      },
      data: sorted.map((item) => {
        const lever = item.levers.find((l) => l.category === category)
        if (!lever) {
          return 0
        }
        return props.percent ? lever.percentage : lever.count
      }),
      itemStyle: {
        color: CATEGORY_COLORS[category] || '#ccc',
      },
    })) as SeriesOption[],
    categories: sorted.map((item) => keyLabel(item.mode)),
    total: behaviorChangeData.total_responses,
  }
}

function motivationOptions() {
  const behaviorChangeData = props.behaviorChangeStats?.motivation
  if (!behaviorChangeData) {
    return null
  }
  const levels = [1, 2, 3, 4, 5]

  const sorted = getSortedModes(motivationByMode(behaviorChangeData.by_mode_motivation))

  return {
    series: levels.map((level) => ({
      name: keyLabel(`l${level.toString()}`),
      type: 'bar',
      stack: 'total',
      label: {
        show: true,
        position: 'inside',
        formatter: function (params: CallbackDataParams) {
          if (params.value === 0) {
            return ''
          }
          if (props.percent) {
            return `${formatNumber(params.value as number)}%`
          }
          return formatNumber(Math.round(params.value as number))
        },
      },
      data: sorted.map((item) => {
        const lever = item.motivations.find((l) => l.level === level)
        if (!lever) {
          return 0
        }
        return props.percent ? lever.percentage : lever.count
      }),
      itemStyle: {
        color: MOTIVATION_COLORS[level] || '#ccc',
      },
    })) as SeriesOption[],
    categories: sorted.map((item) => keyLabel(item.mode)),
    total: behaviorChangeData.total_responses,
  }
}

function shortKey(key: string) {
  return lowerCaseFirst(key.replace('freq_mod_pro_', '').replace('freq_mod_', ''))
}

function getSortedModes<
  T extends
    | BehaviorChangeStats['levers']['by_mode_levers']
    | BehaviorChangeStats['motivation']['by_mode_motivation'],
>(data: T): T {
  const copy = [...data] as T

  moveToStart(
    copy,
    copy.find((item) => item.mode === 'other'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'Autres'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'allModes'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'Total'),
  )

  return copy
}

function orderModes(modes: string[]): string[] {
  const copy = [...modes]
  moveToStart(
    copy,
    copy.find((mode) => mode === 'other'),
  )
  moveToStart(
    copy,
    copy.find((mode) => mode === 'Autres'),
  )
  moveToStart(
    copy,
    copy.find((mode) => mode === 'allModes'),
  )
  moveToStart(
    copy,
    copy.find((mode) => mode === 'Total'),
  )
  return copy
}

/**
 * A row of a comparison chart: one bar per (mode, comparison group) pair, so
 * that a row is a single stack of categories and the legend is back to plain
 * category names — one entry per lever or motivation level, instead of one per
 * (group, category) pair, which no longer fits under the chart past a couple of
 * groups.
 */
type ComparisonRow = {
  mode: string
  groupName: string
} | null

interface ComparisonChartData {
  rows: ComparisonRow[]
  /** Modes, in charted order: the outer level of the y axis. */
  modes: string[]
  series: SeriesOption[]
  total: number
}

/** Bars are this share of their row, the rest being the gap between two bars. */
const COMPARISON_BAR_CATEGORY_GAP = '10%'

function comparisonRows<G extends { name: string }>(modes: string[], groups: G[]) {
  return modes.flatMap((mode) => [null, ...groups.map((group) => ({ mode, group })), null])
}

function comparisonLeversOptions(): ComparisonChartData | null {
  const groups = (stats.comparisonResults?.groups ?? []).map((group) => ({
    name: group.name,
    byMode: leversByMode(group.behavior_change?.levers?.by_mode_levers ?? []),
    total: group.behavior_change?.levers?.total_responses ?? 0,
  }))
  if (groups.every((group) => group.byMode.length === 0)) {
    return null
  }

  const modes = orderModes(
    Array.from(new Set(groups.flatMap((group) => group.byMode.map((item) => item.mode)))),
  )
  const categories = Array.from(
    new Set(
      groups.flatMap((group) =>
        group.byMode.flatMap((item) => item.levers.map((lever) => lever.category)),
      ),
    ),
  )
  if (modes.length === 0 || categories.length === 0) {
    return null
  }

  const rows = comparisonRows(modes, groups)

  return {
    rows: rows.map((row) => (row ? { mode: row.mode, groupName: row.group.name } : null)),
    modes,
    series: categories.map((category) => ({
      name: keyLabel(category),
      type: 'bar',
      stack: 'total',
      barCategoryGap: COMPARISON_BAR_CATEGORY_GAP,
      emphasis: { focus: 'series' },
      itemStyle: { color: CATEGORY_COLORS[category] || '#ccc' },
      data: rows.map((row) => {
        if (!row) return null
        const lever = row.group.byMode
          .find((item) => item.mode === row.mode)
          ?.levers.find((l) => l.category === category)
        if (!lever) return 0
        return props.percent ? lever.percentage : lever.count
      }),
    })) as SeriesOption[],
    total: groups.reduce((sum, group) => sum + group.total, 0),
  }
}

function comparisonMotivationOptions(): ComparisonChartData | null {
  const groups = (stats.comparisonResults?.groups ?? []).map((group) => ({
    name: group.name,
    byMode: motivationByMode(group.behavior_change?.motivation?.by_mode_motivation ?? []),
    total: group.behavior_change?.motivation?.total_responses ?? 0,
  }))
  if (groups.every((group) => group.byMode.length === 0)) {
    return null
  }

  const modes = orderModes(
    Array.from(new Set(groups.flatMap((group) => group.byMode.map((item) => item.mode)))),
  )
  if (modes.length === 0) {
    return null
  }
  const levels = [1, 2, 3, 4, 5]

  const rows = comparisonRows(modes, groups)

  return {
    rows: rows.map((row) => (row ? { mode: row.mode, groupName: row.group.name } : null)),
    modes,
    series: levels.map((level) => ({
      name: keyLabel(`l${level.toString()}`),
      type: 'bar',
      stack: 'total',
      barCategoryGap: COMPARISON_BAR_CATEGORY_GAP,
      emphasis: { focus: 'series' },
      itemStyle: { color: MOTIVATION_COLORS[level] || '#ccc' },
      data: rows.map((row) => {
        if (!row) return null
        const motivation = row.group.byMode
          .find((item) => item.mode === row.mode)
          ?.motivations.find((m) => m.level === level)
        if (!motivation) return 0
        return props.percent ? motivation.percentage : motivation.count
      }),
    })) as SeriesOption[],
    total: groups.reduce((sum, group) => sum + group.total, 0),
  }
}

function initComparisonChartOptions() {
  const data = props.type === 'levers' ? comparisonLeversOptions() : comparisonMotivationOptions()
  if (!data) {
    return
  }
  total.value = data.total

  const groupLabels = data.rows.map((row) => (row ? truncateAxisLabel(row.groupName) : ''))
  const modeLabels = data.modes.map((mode) => keyLabel(mode))

  // The axis labels sit outside the grid (no containLabel), so the room they
  // need is reserved here: the group names, then the modes on their left.
  const modeAxisOffset = axisLabelsWidth(groupLabels) + AXIS_LABEL_GAP

  option.value = {
    grid: {
      left: modeAxisOffset + axisLabelsWidth(modeLabels) + AXIS_LABEL_GAP,
      right: 20,
      top: 60,
      // Room for the x axis labels, and for the legend below them.
      bottom: 60,
      containLabel: false,
    },
    animation: false,
    // Same as the single-campaign chart, so that two charts sitting side by
    // side keep the same height whether or not campaigns are compared.
    height: props.height - 140,
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
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (paramsList: CallbackDataParams | CallbackDataParams[]) => {
        const items = Array.isArray(paramsList) ? paramsList : [paramsList]
        const row = data.rows[items[0]?.dataIndex ?? 0]
        if (!row) {
          return ''
        }
        const lines = items
          .filter((item) => Number(item.value) > 0)
          .map((item) => {
            const value = formatNumber(Number(item.value))
            return `${item.marker} ${item.seriesName}: <b>${value}${props.percent ? '%' : ''}</b>`
          })
        return [`${keyLabel(row.mode)} — <b>${row.groupName}</b>`, ...lines].join('<br/>')
      },
    },
    legend: { show: true, bottom: 0, left: 'center', type: 'scroll' },
    yAxis: [
      {
        type: 'category',
        data: groupLabels,
        axisLabel: { interval: 0 },
        axisTick: { show: false },
      },
      {
        // Outer level: one band per mode, aligned with its block of group rows
        type: 'category',
        position: 'left',
        offset: modeAxisOffset,
        data: modeLabels,
        axisLabel: { interval: 0, fontWeight: 'bold' },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: true, lineStyle: { color: '#bdbdbd' } },
        splitArea: {
          show: true,
          areaStyle: { color: ['rgba(128, 128, 128, 0.09)', 'transparent'] },
        },
      },
    ],
    xAxis: {
      type: 'value',
      ...(props.percent ? { max: 100 } : {}),
    },
    series: data.series,
  }
}
</script>
