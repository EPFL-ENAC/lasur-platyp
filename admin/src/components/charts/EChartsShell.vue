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
      :option="option"
      :update-options="updateOptions"
      :loading="!!loading"
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
    />

    <template #info>
      <slot />
    </template>
  </chart-shell>
</template>

<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import type { EChartsType } from 'echarts/core'
import { useQuasar } from 'quasar'
import ECharts from 'vue-echarts'
import ChartShell from './ChartShell.vue'
import { initOptions, updateOptions } from './commons'
import type { ECBasicOption } from 'echarts/types/dist/shared'

interface Props {
  height?: number | undefined
  hasData: boolean
  showInfo?: boolean
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
