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
import { computed, shallowRef } from 'vue'
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

// Measured after each render (see onFinished), then fed back into the option:
// the chart width, to clip long titles, the room the x axis lacks above a
// legend that wrapped over several rows, and the box pies must fit in between
// the title and the legend (pies ignore the grid).
const chartWidth = ref(0)
const legendRoom = ref(0)
const pieBox = ref<{ top: number; bottom: number } | null>(null)
// Room left for the toolbar menu on each side of a centered title.
const TITLE_MARGIN = 60
// Gap kept between the x axis (labels and name) and the legend.
const LEGEND_GAP = 8

watch(
  () => [props.option, dialogOpen.value],
  () => {
    legendRoom.value = 0
    pieBox.value = null
  },
)

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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const instance = chart.value?.chart as any
  if (!instance) return
  if (instance.getWidth() !== chartWidth.value) {
    chartWidth.value = instance.getWidth()
    legendRoom.value = 0
    pieBox.value = null
    return
  }
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
  const overlap = Math.ceil(axisBottom + LEGEND_GAP - legendTop)
  if (overlap > 0) legendRoom.value += overlap

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
    pieBox.value = {
      top: Math.ceil(titleBottom + LEGEND_GAP),
      bottom: Math.ceil(instance.getHeight() - legendTop + LEGEND_GAP),
    }
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
