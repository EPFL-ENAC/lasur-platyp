import type { EChartsOption } from 'echarts'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { t } from '@/boot/i18n'
import { formatNumber } from '@/utils/numbers'
import { GROUP_COLORS } from './commons'

export interface ComparisonSeriesItem {
  key: string
  name: string
  value: number
}

export interface ComparisonGroupDataset {
  name: string
  items: ComparisonSeriesItem[]
  /** Denominator used for percentages, defaults to the sum of the item values. */
  total?: number
  /** Series color, defaults to the group color picked from GROUP_COLORS. */
  color?: string
  /** Render the categories missing from `items` as gaps instead of zeros. */
  gapOnMissing?: boolean
  /** Number of participants in the group, displayed along with the group name. */
  participants?: number
}


const AXIS_LABEL_CHAR_WIDTH = 7
const AXIS_LABEL_MAX_CHARS = 24
export const AXIS_LABEL_GAP = 16

export function truncateAxisLabel(label: string) {
  return label.length > AXIS_LABEL_MAX_CHARS
    ? `${label.slice(0, AXIS_LABEL_MAX_CHARS - 1)}…`
    : label
}

export function axisLabelsWidth(labels: string[]) {
  const chars = labels.reduce((max, label) => Math.max(max, truncateAxisLabel(label).length), 0)
  return chars * AXIS_LABEL_CHAR_WIDTH
}

/** Group name followed by its participants count, e.g. "Group A (N: 123)". */
function groupNameWithParticipants(group: ComparisonGroupDataset): string {
  if (group.participants === undefined) return group.name
  return `${group.name} (${t('stats.total', { count: group.participants })})`
}

/**
 * Splits a group name into lines short enough to sit under a bar.
 *
 * Done here rather than with ECharts' own `overflow: 'break'`: its wrapping runs
 * on rich text through `wrapText`, which does not honour the newlines separating
 * the fragments, so the name and the participants count end up on the same line.
 */
function wrapLabel(text: string, maxChars = 20, maxLines = 3): string[] {
  const lines: string[] = []
  let current = ''
  text
    .split(/\s+/)
    .filter(Boolean)
    .forEach((word) => {
      let rest = word
      // A word wider than a line has to be cut: it would overflow on its own.
      while (rest.length > maxChars) {
        if (current) {
          lines.push(current)
          current = ''
        }
        lines.push(rest.slice(0, maxChars))
        rest = rest.slice(maxChars)
      }
      if (!current) {
        current = rest
      } else if (current.length + 1 + rest.length <= maxChars) {
        current += ` ${rest}`
      } else {
        lines.push(current)
        current = rest
      }
    })
  if (current) {
    lines.push(current)
  }
  if (lines.length === 0) {
    return [text]
  }
  if (lines.length > maxLines) {
    const last = lines[maxLines - 1]!
    return [...lines.slice(0, maxLines - 1), `${last.slice(0, maxChars - 1)}\u2026`]
  }
  return lines
}

function groupTotal(group: ComparisonGroupDataset): number {
  return group.items.reduce((sum, item) => sum + item.value, 0)
}

export interface GroupDifference {
  lastGroupName: string
  prevGroupName: string
  key: string
  name: string
  diffPercent: number
}

/**
 * Finds, between the last two comparison groups (chronologically), the item whose
 * percentage share differs the most (in absolute value) between the two groups.
 * `diffDirection` controls the sign of the returned difference: 'last_minus_prev'
 * reports (last% - prev%), 'prev_minus_last' reports (prev% - last%).
 */
export function findBiggestGroupDifference(
  groupDatasets: ComparisonGroupDataset[],
  diffDirection: 'last_minus_prev' | 'prev_minus_last',
): GroupDifference | null {
  if (groupDatasets.length < 2) return null

  const lastGroup = groupDatasets[groupDatasets.length - 1]!
  const prevGroup = groupDatasets[groupDatasets.length - 2]!
  const lastTotal = groupTotal(lastGroup)
  const prevTotal = groupTotal(prevGroup)
  if (lastTotal === 0 || prevTotal === 0) return null

  const keys = new Set([
    ...lastGroup.items.map((item) => item.key),
    ...prevGroup.items.map((item) => item.key),
  ])

  let best: GroupDifference | null = null
  keys.forEach((key) => {
    const lastItem = lastGroup.items.find((item) => item.key === key)
    const prevItem = prevGroup.items.find((item) => item.key === key)
    const lastPercent = ((lastItem?.value ?? 0) / lastTotal) * 100
    const prevPercent = ((prevItem?.value ?? 0) / prevTotal) * 100
    const diffPercent =
      diffDirection === 'last_minus_prev' ? lastPercent - prevPercent : prevPercent - lastPercent

    if (!best || Math.abs(diffPercent) > Math.abs(best.diffPercent)) {
      best = {
        lastGroupName: lastGroup.name,
        prevGroupName: prevGroup.name,
        key,
        name: (lastItem ?? prevItem)!.name,
        diffPercent,
      }
    }
  })

  return best
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
  /** Unit appended to the tooltip values of an absolute-value chart (percent: false). */
  valueUnit?: string
}): EChartsOption {
  const {
    groupDatasets,
    colors,
    percent,
    title,
    totalLabel,
    height,
    yAxisName,
    keyOrder,
    valueUnit,
  } = params

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
    // Bottom fits the legend plus a group name wrapped over a couple of lines;
    // left fits the y axis name, which `containLabel` does not account for.
    grid: { left: '70', right: '20', top: '60', bottom: '90', containLabel: true },
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
          const display = formatNumber(Number(item.value))
          const unit = percent ? '%' : valueUnit ? ` ${valueUnit}` : ''
          res += `${item.marker} ${item.seriesName}: <b>${display}${unit}</b><br/>`
        })
        return res
      },
    },
    legend: { show: true, bottom: 5, left: 'center', type: 'scroll' },
    xAxis: {
      type: 'category',
      data: groupDatasets.map((group) => group.name),
      axisLabel: {
        // Every group must be named: long names wrap instead of being dropped,
        // which is what ECharts does by default when labels collide.
        interval: 0,
        hideOverlap: false,
        // Group name over as many lines as it needs, its participants count on a
        // last, smaller one.
        formatter: (value: string, index: number) => {
          const participants = groupDatasets[index]?.participants
          const lines = wrapLabel(value).map((line) => `{name|${line}}`)
          if (participants !== undefined) {
            lines.push(`{count|${t('stats.total', { count: participants })}}`)
          }
          return lines.join('\n')
        },
        rich: {
          name: { lineHeight: 18 },
          count: { fontSize: 10, opacity: 0.7, lineHeight: 14 },
        },
      },
    },
    yAxis: {
      type: 'value',
      name: yAxisName ?? '',
      nameLocation: 'middle',
      // Clears the widest tick labels, which sit between the axis line and the name.
      nameGap: 55,
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
  const groupTotals = groupDatasets.map((group) => group.total ?? groupTotal(group))

  const series = groupDatasets.map((group, i) => ({
    name: groupNameWithParticipants(group),
    type: 'bar' as const,
    color: group.color ?? GROUP_COLORS[i % GROUP_COLORS.length] ?? '#ccc',
    data: orderedCategories.map((key) => {
      const item = group.items.find((entry) => entry.key === key)
      if (!item && group.gapOnMissing) return null
      const value = item?.value ?? 0
      if (!percent) return value
      const total = groupTotals[i] || 0
      return total > 0 ? Number(((value / total) * 100).toFixed(2)) : 0
    }),
  }))

  return {
    grid: { left: '20', right: '20', top: '60', bottom: '85', containLabel: true },
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
    legend: { show: true, bottom: 5, left: 'center', type: 'scroll' },
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
