<template>
  <div :style="`height: ${props.height || 300}px; width: 100%;`">
    <e-charts
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
    />
  </div>
</template>

<script lang="ts" setup>
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
} from 'echarts/components'
import type { CampaignStats } from 'src/models'

interface Props {
  stats: CampaignStats
  height?: number
}
use([
  SVGRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
])

const props = defineProps<Props>()

const { t } = useI18n()

const chart = shallowRef(null)
const option = ref<EChartsOption>({})

onMounted(() => {
  initChartOptions()
})

function initChartOptions() {
  option.value = {}

  const weeks = props.stats.weekly?.map((w) => w.week) || []
  const completedData = props.stats.weekly?.map((w) => w.completed) || []
  const completedDataCumulated = completedData.map(
    (
      (sum) => (value) =>
        (sum += value)
    )(0),
  )
  const inProgressData = props.stats.weekly?.map((w) => w.created - w.completed) || []
  const inProgressDataCumulated = inProgressData.map(
    (
      (sum) => (value) =>
        (sum += value)
    )(0),
  )

  const newOption: EChartsOption = {
    animation: false,
    grid: {
      top: 30,
      right: 0,
      bottom: 50,
      left: 0,
      containLabel: true,
    },
    tooltip: {
      trigger: 'item',
    },
    legend: {
      show: false,
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: weeks,
      },
    ],
    yAxis: [
      {
        type: 'value',
        name: t('stats.records_count'),
        nameTextStyle: {
          align: 'left',
        },
      },
    ],
    dataZoom: [
      {
        show: true,
        realtime: true,
        start: weeks.length > 20 ? 70 : 0,
        end: 100,
      },
      {
        type: 'inside',
        realtime: true,
        start: weeks.length > 20 ? 70 : 0,
        end: 100,
      },
    ],
    series: [
      {
        name: t('stats.completed'),
        type: 'line',
        stack: 'Total',
        areaStyle: {},
        emphasis: {
          focus: 'series',
        },
        data: completedDataCumulated,
        color: '#4caf50',
      },
      {
        name: t('stats.in_progress'),
        type: 'line',
        stack: 'Total',
        areaStyle: {},
        emphasis: {
          focus: 'series',
        },
        data: inProgressDataCumulated,
        color: '#ff9800',
      },
    ],
  }
  option.value = newOption
}
</script>
