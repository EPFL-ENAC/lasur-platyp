<template>
  <q-table
    v-if="table"
    flat
    dense
    wrap-cells
    :rows="table.rows"
    :columns="table.columns"
    :row-key="table.rowKey"
    hide-bottom
    :pagination="{ rowsPerPage: 0 }"
    :table-row-class-fn="rowClass"
    class="e-charts-table q-my-lg"
  />
</template>

<script setup lang="ts">
import type { ECBasicOption } from 'echarts/types/dist/shared'
import { formatNumber } from '@/utils/numbers'

interface Props {
  option: ECBasicOption
}

const props = defineProps<Props>()

const { t } = useI18n()

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>

interface Column {
  name: string
  label: string
  field: string
  align: 'left' | 'right'
}

interface Table {
  columns: Column[]
  rows: AnyRecord[]
  rowKey: string
}

function toArray<T>(value: T | T[] | undefined | null): T[] {
  if (value === undefined || value === null) {
    return []
  }
  return Array.isArray(value) ? value : [value]
}

function labelOf(value: unknown): string {
  if (value && typeof value === 'object' && 'value' in (value as AnyRecord)) {
    return String((value as AnyRecord).value)
  }
  return String(value)
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }
  if (typeof value === 'number') {
    return formatNumber(value)
  }
  if (typeof value === 'string') {
    const num = Number(value)
    return value.trim() !== '' && !isNaN(num) ? formatNumber(num) : value
  }
  return String(value)
}

function normalizeSeriesValue(value: unknown): unknown {
  if (
    value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    'value' in (value as AnyRecord)
  ) {
    return (value as AnyRecord).value
  }
  return value
}

function findCategoryAxes(option: AnyRecord, key: 'xAxis' | 'yAxis'): AnyRecord[] {
  return toArray<AnyRecord>(option[key]).filter(
    (axis) => axis?.type === 'category' && Array.isArray(axis.data) && axis.data.length > 0,
  )
}

/**
 * A chart can stack a coarser category axis over the one holding the rows: one
 * band per mode (or per distance scale), each covering the same number of rows.
 * The band a row belongs to is part of its name in the table, which has no
 * second axis to show it: "IMT M1", "IMT M2", ...
 */
function bandLabels(axes: AnyRecord[], rowCount: number): string[] | null {
  const outer = axes.find((axis) => (axis.data as unknown[]).length < rowCount)
  if (!outer) {
    return null
  }
  const bandSize = rowCount / (outer.data as unknown[]).length
  if (!Number.isInteger(bandSize)) {
    return null
  }
  return Array.from({ length: rowCount }, (_, i) =>
    labelOf((outer.data as unknown[])[Math.floor(i / bandSize)]),
  )
}

function seriesLabel(series: AnyRecord, index: number, total: number): string {
  if (series.name) {
    return String(series.name)
  }
  return total > 1 ? `${t('stats.table.value')} ${index + 1}` : t('stats.table.value')
}

function buildMatrixTable(
  xAxis: AnyRecord,
  yAxis: AnyRecord,
  seriesArr: AnyRecord[],
): Table | null {
  const isTriple = (d: unknown): d is [number, number, unknown] => Array.isArray(d) && d.length >= 3

  const triples = seriesArr.flatMap((s) => (Array.isArray(s.data) ? s.data.filter(isTriple) : []))
  if (triples.length === 0) {
    return null
  }

  const columns: Column[] = [
    {
      name: 'category',
      label: yAxis.name || t('stats.table.category'),
      field: 'category',
      align: 'left',
    },
    ...(xAxis.data as unknown[]).map((label, xi) => ({
      name: `col_${xi}`,
      label: labelOf(label),
      field: `col_${xi}`,
      align: 'right' as const,
    })),
  ]

  const rows: AnyRecord[] = (yAxis.data as unknown[]).map((yLabel, yi) => {
    const row: AnyRecord = { category: labelOf(yLabel) }
    ;(xAxis.data as unknown[]).forEach((_xLabel, xi) => {
      const found = triples.find(([x, y]) => x === xi && y === yi)
      row[`col_${xi}`] = formatValue(found ? found[2] : undefined)
    })
    return row
  })

  return { columns, rows, rowKey: 'category' }
}

function buildDimensionsTable(seriesArr: AnyRecord[]): Table | null {
  const dimSeries = seriesArr.filter(
    (s) => Array.isArray(s.dimensions) && s.encode && Array.isArray(s.data) && s.data.length > 0,
  )
  if (dimSeries.length === 0) {
    return null
  }

  const first = dimSeries[0]!
  const dimensions: string[] = first.dimensions
  const itemNameIdx: number | undefined = first.encode.itemName
  const tooltipIdx: number[] = toArray<number>(first.encode.tooltip)

  const columns: Column[] = [
    { name: 'category', label: t('stats.table.category'), field: 'category', align: 'left' },
    ...tooltipIdx.map((idx) => ({
      name: `d${idx}`,
      label: dimensions[idx] ?? `${idx}`,
      field: `d${idx}`,
      align: 'right' as const,
    })),
  ]

  const rows: AnyRecord[] = dimSeries.map((s, i) => {
    const data = (s.data[0] ?? []) as unknown[]
    const category =
      itemNameIdx !== undefined && data[itemNameIdx] !== undefined
        ? String(data[itemNameIdx])
        : seriesLabel(s, i, dimSeries.length)
    const row: AnyRecord = { category }
    tooltipIdx.forEach((idx) => {
      row[`d${idx}`] = formatValue(data[idx])
    })
    return row
  })

  return { columns, rows, rowKey: 'category' }
}

function buildCategoryTable(
  axis: AnyRecord,
  seriesArr: AnyRecord[],
  bands: string[] | null,
  reverse: boolean,
): Table | null {
  const categories = axis.data as unknown[]

  const columns: Column[] = [
    {
      name: 'category',
      label: axis.name || t('stats.table.category'),
      field: 'category',
      align: 'left',
    },
    ...seriesArr.map((s, i) => ({
      name: `s${i}`,
      label: seriesLabel(s, i, seriesArr.length),
      field: `s${i}`,
      align: 'right' as const,
    })),
  ]

  // A category y axis is drawn bottom-up: read it backwards so the table lists
  // the categories in the order the chart shows them, top to bottom.
  const indexes = categories.map((_label, idx) => idx)
  if (reverse) {
    indexes.reverse()
  }

  const totalLabel = t('stats.table.total').toLowerCase()
  const rows: AnyRecord[] = []
  indexes.forEach((idx) => {
    const name = labelOf(categories[idx])
    const values = seriesArr.map((s) =>
      normalizeSeriesValue(Array.isArray(s.data) ? s.data[idx] : undefined),
    )
    // Nameless and valueless: a spacer the chart uses to separate two bands of
    // bars, which the table separates with a rule instead.
    const isSpacer = name === '' && values.every((value) => value === null || value === undefined)
    if (isSpacer) {
      return
    }
    const band = bands?.[idx] ?? ''
    const row: AnyRecord = {
      key: `r${idx}`,
      band,
      category: [band, name].filter((part) => part !== '').join(' '),
      isTotal: (band || name).toLowerCase() === totalLabel,
    }
    values.forEach((value, i) => {
      row[`s${i}`] = formatValue(value)
    })
    rows.push(row)
  })

  // A rule under the last row of each band but the last one, so that bands read
  // as blocks — and no rule above the first one.
  rows.forEach((row, i) => {
    row.bandEnd = !!row.band && i < rows.length - 1 && rows[i + 1]?.band !== row.band
  })

  return { columns, rows, rowKey: 'key' }
}

function buildNameValueTable(seriesArr: AnyRecord[]): Table | null {
  const isNameValueData = (data: unknown): boolean =>
    Array.isArray(data) &&
    data.length > 0 &&
    data.every(
      (d) => d && typeof d === 'object' && !Array.isArray(d) && 'name' in d && 'value' in d,
    )

  const nameValueSeries = seriesArr.filter((s) => isNameValueData(s.data))
  if (nameValueSeries.length === 0) {
    return null
  }

  const names: string[] = []
  nameValueSeries.forEach((s) => {
    ;(s.data as AnyRecord[]).forEach((d) => {
      const name = String(d.name)
      if (!names.includes(name)) {
        names.push(name)
      }
    })
  })

  const columns: Column[] = [
    { name: 'category', label: t('stats.table.category'), field: 'category', align: 'left' },
    ...nameValueSeries.map((s, i) => ({
      name: `s${i}`,
      label: seriesLabel(s, i, nameValueSeries.length),
      field: `s${i}`,
      align: 'right' as const,
    })),
  ]

  const rows: AnyRecord[] = names.map((name) => {
    const row: AnyRecord = { category: name }
    nameValueSeries.forEach((s, i) => {
      const item = (s.data as AnyRecord[]).find((d) => String(d.name) === name)
      row[`s${i}`] = formatValue(item?.value)
    })
    return row
  })

  return { columns, rows, rowKey: 'category' }
}

function buildSankeyTable(seriesArr: AnyRecord[]): Table | null {
  const sankeySeries = seriesArr.filter((s) => Array.isArray(s.links) && s.links.length > 0)
  if (sankeySeries.length === 0) {
    return null
  }

  const columns: Column[] = [
    { name: 'link', label: t('stats.table.link'), field: 'link', align: 'left' },
    { name: 'value', label: t('stats.table.value'), field: 'value', align: 'right' },
  ]

  const rows: AnyRecord[] = sankeySeries.flatMap((s) =>
    (s.links as AnyRecord[]).map((link) => ({
      link: `${labelOf(link.source)} → ${labelOf(link.target)}`,
      value: formatValue(link.value),
    })),
  )

  return { columns, rows, rowKey: 'link' }
}

const table = computed<Table | null>(() => {
  const option = props.option as AnyRecord
  const seriesArr = toArray<AnyRecord>(option?.series)
  if (seriesArr.length === 0) {
    return null
  }

  const xAxes = findCategoryAxes(option, 'xAxis')
  const yAxes = findCategoryAxes(option, 'yAxis')
  const xAxis = xAxes[0]
  const yAxis = yAxes[0]

  if (xAxis && yAxis) {
    const matrix = buildMatrixTable(xAxis, yAxis, seriesArr)
    if (matrix) {
      return matrix
    }
  }

  const axes = xAxis ? xAxes : yAxes
  const categoryAxis = axes[0]
  if (categoryAxis) {
    const rowCount = (categoryAxis.data as unknown[]).length
    return buildCategoryTable(categoryAxis, seriesArr, bandLabels(axes, rowCount), !xAxis)
  }

  return (
    buildDimensionsTable(seriesArr) || buildNameValueTable(seriesArr) || buildSankeyTable(seriesArr)
  )
})

function rowClass(row: AnyRecord) {
  return [row.bandEnd ? 'band-end' : '', row.isTotal ? 'total-row' : ''].filter(Boolean).join(' ')
}
</script>

<style scoped>
.e-charts-table :deep(tbody tr.band-end > td) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.28);
}

.e-charts-table :deep(tbody tr.total-row > td) {
  background-color: rgba(0, 0, 0, 0.04);
  font-weight: 600;
}
</style>
