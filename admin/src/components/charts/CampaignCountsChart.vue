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
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { CampaignStats } from 'src/models'

interface Props {
  stats: CampaignStats
  height?: number
}
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const props = defineProps<Props>()

const { t } = useI18n()

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = computed(() => props.stats.total_records)
const completed = computed(() => props.stats.completed_records)
const inProgress = computed(() => total.value - completed.value)
const nbEmployees = computed(() => props.stats.nb_employees || 0)

onMounted(() => {
  initChartOptions()
})

function initChartOptions() {
  option.value = {}

  const data = [
    { value: completed.value, name: t('stats.completed') },
    { value: inProgress.value, name: t('stats.in_progress') },
  ]
  if (nbEmployees.value) {
    data.push({ value: nbEmployees.value - total.value, name: t('stats.pending') })
  }

  const newOption: EChartsOption = {
    animation: false,
    grid: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0,
      containLabel: true,
    },
    tooltip: {
      trigger: 'item',
      formatter: '<b>{b}</b><br/>{c} ({d}%)',
    },
    legend: {
      show: false,
    },
    series: [
      {
        type: 'pie',
        //radius: ['30%', '50%'],
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        // adjust the start and end angle
        //startAngle: 180,
        //endAngle: 360,
        avoidLabelOverlap: true,
        color: ['#4caf50', '#ff9800', '#2196f3'],
        label: {
          margin: 0,
          fontWeight: 'bold',
        },
        data: data,
      },
    ],
  }
  option.value = newOption
}
</script>
