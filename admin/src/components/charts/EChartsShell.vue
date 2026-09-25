<template>
  <chart-shell
    ref="shellRef"
    :height="height"
    :has-data="hasData"
    :show-info="showInfo"
    :loading="loading"
    :no-data-title="noDataTitle"
    :no-data-text="noDataText ?? t('stats.no_data')"
    :exportable="!!chart && exportable"
    :export-file-name="exportFileName"
    :logo-url="logoUrl"
    :logo-padding="logoPadding"
    :logo-width-ratio="logoWidthRatio"
    :export-background-color="resolvedExportBackgroundColor"
    :capture-raw-image="captureRawImage"
  >
    <e-charts
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="resolvedOption"
      :update-options="updateOptions"
      :loading="!!loading"
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
      @finished="onFinished"
    />

    <template #table>
      <e-charts-table v-if="(showTable || dialogOpen) && !loading" :option="option" />
    </template>
  </chart-shell>
</template>

<script setup lang="ts">
import { computed, onUnmounted, shallowRef } from 'vue'
import type { EChartsType } from 'echarts/core'
import { useQuasar } from 'quasar'
import ECharts from 'vue-echarts'
import ChartShell from './ChartShell.vue'
import EChartsTable from './EChartsTable.vue'
import { chartPanelDialogOpenKey, initOptions, updateOptions } from './commons'
import type { ECBasicOption } from 'echarts/types/dist/shared'

interface Props {
  height?: number | undefined
  hasData: boolean
  showInfo?: boolean
  showTable?: boolean
  loading?: boolean
  noDataTitle: string
  noDataText?: string
  option: ECBasicOption
  exportable?: boolean
  exportFileName?: string
  logoUrl?: string
  logoPadding?: number
  logoWidthRatio?: number
  exportBackgroundColor?: string
  exportPixelRatio?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: 400,
  showInfo: false,
  loading: false,
  exportable: true,
  exportFileName: 'chart.png',
  logoUrl: '/admin/LOGO-VIOLET.svg',
  logoPadding: 12,
  logoWidthRatio: 0.08,
  exportPixelRatio: 8,
})

type ChartShellExposed = {
  handleExport: () => Promise<void>
}

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
})

const $q = useQuasar()
const { t } = useI18n()
const chart = shallowRef<InstanceType<typeof ECharts> | null>(null)
const shellRef = useTemplateRef<ChartShellExposed>('shellRef')
const dialogOpen = inject(chartPanelDialogOpenKey, ref(false))

// Full-screen details: the panel already shows the title, so the in-chart
// title is dropped (its "N: ..." subtext stays).
// The height stays as given: charts derive their grid from it, so a taller
// container would only open a gap above the legend.

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>

// Chart width, from the host element (see the ResizeObserver below) rather
// than the echarts instance: the title clip never measures its own output.
const chartWidth = ref(0)
// Measured from the option render (see onFinished) and fed back into it: the
// room the x axis lacks above a legend that wrapped over several rows, and the
// box pies must fit in between the title and the legend (pies ignore the grid).
const legendRoom = ref(0)
const pieBox = ref<{ top: number; bottom: number } | null>(null)
// Room left for the toolbar menu on each side of a centered title.
const TITLE_MARGIN = 60
// Gap kept between the x axis (labels and name) and the legend.
const LEGEND_GAP = 8
// Fitting takes at most this many render passes per option change (see
// onFinished): a measurement that never settles must not loop for ever.
const ADJUST_PASS_LIMIT = 3

// Whether the rendered chart may still be fitted. Opened by every option or
// size change, closed once the render settles (see onFinished), so repeated
// +finished+ events stay passive instead of feeding back into the option.
let adjustAllowed = true
let adjustPasses = 0

function resetAdjustments() {
  legendRoom.value = 0
  pieBox.value = null
  adjustPasses = 0
  adjustAllowed = true
}

watch(
  () => [props.option, dialogOpen.value, props.height, props.loading],
  () => {
    resetAdjustments()
  },
)

// The host width is clipped from the title (fitTitle); it is measured from the
// DOM rather than the echarts instance, so the fits that depend on it never
// measure their own output.
let resizeObserver: ResizeObserver | undefined

watch(chart, (instance) => {
  resizeObserver?.disconnect()
  if (!instance?.root) {
    resizeObserver = undefined
    return
  }
  resizeObserver = new ResizeObserver((entries) => {
    const entry = entries.at(-1)
    if (!entry) return
    const width = Math.round(entry.contentRect.width)
    if (!width || width === chartWidth.value) return
    chartWidth.value = width
    resetAdjustments()
  })
  resizeObserver.observe(instance.root)
})

onUnmounted(() => resizeObserver?.disconnect())

function fitPie(series: AnyRecord): AnyRecord {
  return series.type === 'pie' && pieBox.value ? { ...series, ...pieBox.value } : series
}

function fitTitle(title: AnyRecord): AnyRecord {
  if (dialogOpen.value) return { ...title, text: '' }
  if (!title.text || !chartWidth.value) return title
  return {
    ...title,
    textStyle: {
      ...title.textStyle,
      width: chartWidth.value - 2 * TITLE_MARGIN,
      overflow: 'truncate',
      ellipsis: '…',
    },
  }
}

function toPx(value: unknown, total: number): number {
  if (typeof value === 'string' && value.endsWith('%')) return (parseFloat(value) / 100) * total
  return Number(value) || 0
}

const resolvedOption = computed<ECBasicOption>(() => {
  const opt: AnyRecord = { ...props.option }
  if (Array.isArray(opt.title)) opt.title = opt.title.map(fitTitle)
  else if (opt.title) opt.title = fitTitle(opt.title)
  if (legendRoom.value && opt.grid && !Array.isArray(opt.grid)) {
    const height = chart.value?.chart?.getHeight() ?? props.height
    opt.grid = { ...opt.grid, bottom: toPx(opt.grid.bottom, height) + legendRoom.value }
  }
  if (pieBox.value && Array.isArray(opt.series)) opt.series = opt.series.map(fitPie)
  return opt as ECBasicOption
})

// Global bounding rect of a component's rendered view.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function viewRect(instance: any, model: any) {
  const group = instance.getViewOfComponentModel(model)?.group
  if (!group) return null
  const rect = group.getBoundingRect().clone()
  const transform = group.getComputedTransform()
  if (transform) rect.applyTransform(transform)
  return rect.height ? rect : null
}

// ponytail: relies on ECharts internals (getModel, getViewOfComponentModel) as
// there is no public API for a component's size; check on ECharts upgrades.
function onFinished() {
  if (!adjustAllowed) return
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const instance = chart.value?.chart as any
  if (!instance) return
  // When the grid cannot take the room (several grids, or none), the resolved
  // option drops the fit: refining it here would only churn re-renders.
  const opt = props.option as AnyRecord
  const canAdjustLegend = !!(opt.grid && !Array.isArray(opt.grid))

  const model = instance.getModel()
  const legendTop = Math.min(
    ...model
      .queryComponents({ mainType: 'legend' })
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .filter((legend: any) => legend.get('bottom') != null)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .map((legend: any) => viewRect(instance, legend)?.y ?? Infinity),
  )
  const axisBottom = Math.max(
    ...model
      .queryComponents({ mainType: 'xAxis' })
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .map((axis: any) => viewRect(instance, axis))
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .map((rect: any) => (rect ? rect.y + rect.height : -Infinity)),
  )
  const overlap =
    legendTop === Infinity || axisBottom === -Infinity
      ? 0
      : Math.ceil(axisBottom + LEGEND_GAP - legendTop)

  let changed = false
  if (overlap > 0 && canAdjustLegend) {
    const next = Math.min(legendRoom.value + overlap, instance.getHeight())
    if (next !== legendRoom.value) {
      legendRoom.value = next
      changed = true
    }
  }

  if (!pieBox.value && legendTop !== Infinity && model.getSeriesByType('pie').length) {
    const titleBottom = Math.max(
      0,
      ...model
        .queryComponents({ mainType: 'title' })
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((title: any) => viewRect(instance, title))
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((rect: any) => (rect ? rect.y + rect.height : 0)),
    )
    // No room between the title and the legend: leave the pie where it is
    // rather than squeezing it into a non-positive band.
    if (legendTop - titleBottom > 2 * LEGEND_GAP) {
      pieBox.value = {
        top: Math.ceil(titleBottom + LEGEND_GAP),
        bottom: Math.ceil(instance.getHeight() - legendTop + LEGEND_GAP),
      }
      changed = true
    }
  }

  adjustPasses += 1
  // Keep fitting only while the axis still collides and a pass actually moved
  // something: a measurement that never settles must not loop for ever.
  if (overlap > 0 && changed && adjustPasses < ADJUST_PASS_LIMIT) return
  adjustAllowed = false
  if (overlap > 0) {
    console.warn(`[EChartsShell] chart fitting gave up after ${adjustPasses} pass(es)`)
  }
}

const resolvedExportBackgroundColor = computed(() => {
  if (props.exportBackgroundColor) {
    return props.exportBackgroundColor
  }

  return $q.dark.isActive ? '#1d1d1d' : '#ffffff'
})

async function captureRawImage(): Promise<string | null> {
  const instance = chart.value?.chart as EChartsType | undefined

  if (!instance) {
    return null
  }

  return instance.getDataURL({
    type: 'png',
    pixelRatio: props.exportPixelRatio,
    backgroundColor: resolvedExportBackgroundColor.value,
  })
}
</script>
