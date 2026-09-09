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
// title is dropped (its "N: ..." subtext stays) and paged legends wrap instead.
// The height stays as given: charts derive their grid from it, so a taller
// container would only open a gap above the legend.

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>

function dialogTitle(title: AnyRecord): AnyRecord {
  return { ...title, text: '' }
}

function dialogLegend(legend: AnyRecord): AnyRecord {
  return legend.type === 'scroll' ? { ...legend, type: 'plain' } : legend
}

const resolvedOption = computed<ECBasicOption>(() => {
  if (!dialogOpen.value) return props.option
  const opt: AnyRecord = { ...props.option }
  if (Array.isArray(opt.title)) opt.title = opt.title.map(dialogTitle)
  else if (opt.title) opt.title = dialogTitle(opt.title)
  if (Array.isArray(opt.legend)) opt.legend = opt.legend.map(dialogLegend)
  else if (opt.legend) opt.legend = dialogLegend(opt.legend)
  return opt as ECBasicOption
})

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
