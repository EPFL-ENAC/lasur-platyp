import type { EChartsOption } from 'echarts'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { GROUP_COLORS } from './commons'

export interface ComparisonSeriesItem {
  key: string
  name: string
  value: number
}

export interface ComparisonGroupDataset {
  name: string
  items: ComparisonSeriesItem[]
}

function groupTotal(group: ComparisonGroupDataset): number {
  return group.items.reduce((sum, item) => sum + item.value, 0)
}

/**
 * x = comparison groups, stacks = a fixed set of colored categories (modes, labels, ...).
 * Used both for 100%-stacked share charts (percent: true) and absolute-value stacked
 * charts such as CO2 emissions or emission reductions (percent: false).
 */
export function buildGroupStackedBarOption(params: {
  groupDatasets: ComparisonGroupDataset[]
  colors: Record<string, string>
  percent: boolean
  title: string
  totalLabel: string
  height: number
  yAxisName?: string
  keyOrder?: string[]
}): EChartsOption {
  const { groupDatasets, colors, percent, title, totalLabel, height, yAxisName, keyOrder } = params

  const keyNames = new Map<string, string>()
  groupDatasets.forEach((group) => {
    group.items.forEach((item) => {
      if (!keyNames.has(item.key)) {
        keyNames.set(item.key, item.name)
      }
    })
  })
  const keys = keyOrder ? keyOrder.filter((key) => keyNames.has(key)) : Array.from(keyNames.keys())
  const groupTotals = groupDatasets.map(groupTotal)

  const series = keys.map((key) => ({
    name: keyNames.get(key) || key,
    type: 'bar' as const,
    stack: 'total',
    emphasis: { focus: 'series' as const },
    color: colors[key] || colors.default || '#ccc',
    data: groupDatasets.map((group, i) => {
      const value = group.items.find((item) => item.key === key)?.value ?? 0
      if (!percent) return value
      const total = groupTotals[i] || 0
      return total > 0 ? Number(((value / total) * 100).toFixed(2)) : 0
    }),
  }))

  return {
    grid: { left: '20', right: '20', top: '60', bottom: '60', containLabel: true },
    animation: false,
    height,
    title: {
      text: title,
      subtext: totalLabel,
      left: 'center',
      top: 0,
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (paramsList: CallbackDataParams | CallbackDataParams[]) => {
        const list = Array.isArray(paramsList) ? paramsList : [paramsList]
        let res = `${list[0]?.name}<br/>`
        list.forEach((item) => {
          const val = percent ? `${item.value}%` : item.value
          res += `${item.marker} ${item.seriesName}: <b>${val}</b><br/>`
        })
        return res
      },
    },
    legend: { show: true, bottom: 0, left: 'center', type: 'scroll' },
    xAxis: {
      type: 'category',
      data: groupDatasets.map((group) => group.name),
    },
    yAxis: {
      type: 'value',
      name: yAxisName ?? '',
      nameLocation: 'middle',
      nameGap: 40,
      ...(percent ? { max: 100 } : {}),
    },
    series,
  }
}

/**
 * y = a fixed set of categories (equipment, constraints, ...), one bar series per
 * comparison group (GROUP_COLORS), bars placed side by side (not stacked).
 */
export function buildGroupedHorizontalBarOption(params: {
  groupDatasets: ComparisonGroupDataset[]
  categories: string[]
  categoryNames: Map<string, string>
  percent: boolean
  title: string
  totalLabel: string
  height: number
  xAxisName?: string
}): EChartsOption {
  const {
    groupDatasets,
    categories,
    categoryNames,
    percent,
    title,
    totalLabel,
    height,
    xAxisName,
  } = params

  // Reversed so the first category ends up at the top of the (bottom-up) category axis.
  const orderedCategories = [...categories].reverse()
  const groupTotals = groupDatasets.map(groupTotal)

  const series = groupDatasets.map((group, i) => ({
    name: group.name,
    type: 'bar' as const,
    color: GROUP_COLORS[i % GROUP_COLORS.length] ?? '#ccc',
    data: orderedCategories.map((key) => {
      const value = group.items.find((item) => item.key === key)?.value ?? 0
      if (!percent) return value
      const total = groupTotals[i] || 0
      return total > 0 ? Number(((value / total) * 100).toFixed(2)) : 0
    }),
  }))

  return {
    grid: { left: '20', right: '20', top: '60', bottom: '60', containLabel: true },
    animation: false,
    height,
    title: {
      text: title,
      subtext: totalLabel,
      left: 'center',
      top: 0,
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: { show: true, bottom: 0, left: 'center', type: 'scroll' },
    yAxis: {
      type: 'category',
      data: orderedCategories.map((key) => categoryNames.get(key) || key),
    },
    xAxis: {
      type: 'value',
      name: xAxisName ?? '',
      nameLocation: 'middle',
      nameGap: 25,
    },
    series,
  }
}
