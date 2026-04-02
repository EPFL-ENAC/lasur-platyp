<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="hasData"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="stats.loading"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.equipments.title`) }}</div>
      <div class="text-subtitle1 text-grey-8 text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart, PictorialBarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Frequencies } from 'src/models'

const { t, locale } = useI18n()
const stats = useStats()
use([
  SVGRenderer,
  BarChart,
  PictorialBarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

interface Props {
  xaxis?: string
  yaxis?: string
  percent?: boolean
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)

const hasData = computed(() => {
  if (!stats.frequencies || !stats.frequencies['equipments']) {
    return false
  }
  const frequencies = stats.frequencies['equipments'] as Frequencies
  return frequencies.data.length > 0
})

watch(
  () => stats.loading,
  () => {
    if (stats.loading) {
      initChartOptions()
    }
  },
)

watch([() => props.percent, () => props.height, locale], () => {
  if (!stats.loading) {
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
  return t(`stats.equipments.labels.${key}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!stats.frequencies || !stats.frequencies['equipments']) {
    return
  }

  const frequencies = stats.frequencies['equipments'] as Frequencies
  initLabelsChartOptions(frequencies)
}

const MRMT_VALUES = {
  upt_subs: 26,
  car: 71,
  bike: 54,
  train_subs: 19,
  moto: 20,
  ebike: 15,
  mob_subs: 3,
}

function initLabelsChartOptions(frequencies: Frequencies) {
  total.value = frequencies.total || 0

  const dataset = frequencies.data
    .map((item) => ({
      key: item.value || 'null',
      name: keyLabel(item.value || 'null'),
      value: props.percent ? Number(((item.count / total.value) * 100).toFixed(2)) : item.count,
    }))
    .reverse()

  const categories = dataset.map((item) => item.name)
  const values = dataset.map((item) => item.value)

  const mrmtValues = dataset.map((item) => {
    const mrmt = MRMT_VALUES[item.key as keyof typeof MRMT_VALUES]
    return mrmt ?? null
  })

  if (categories.length === 0) return

  const maxBarValue = values.length ? Math.max(...values) : 0
  const maxMrmtValue = mrmtValues.filter((v): v is number => v !== null).length
    ? Math.max(...mrmtValues.filter((v): v is number => v !== null))
    : 0
  const xAxisMax = Math.max(maxBarValue, maxMrmtValue)

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t(`stats.equipments.title`),
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
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      show: true,
      bottom: 0,
      data: [t('stats.observed'), 'MRMT'],
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'end',
      nameGap: 30,
      type: 'category',
      data: categories,
    },
    xAxis: {
      name: props.xaxis || (props.percent ? t('stats.percent_employees') : t('stats.nb_employees')),
      nameLocation: 'middle',
      nameGap: 25,
      type: 'value',
      max: Math.ceil(xAxisMax * 1.1),
    },
    series: [
      {
        name: t('stats.observed'),
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#008066',
        },
      },
      {
        name: 'MRMT',
        type: 'pictorialBar',
        symbol: 'rect', // This creates the "line" marker
        symbolRepeat: false,
        symbolSize: [4, 32], // [width, height] - height slightly taller than bar
        symbolOffset: [0, 0],
        symbolPosition: 'end',
        itemStyle: {
          color: '#FF5722', // Distinct color for the marker
        },
        data: mrmtValues,
        z: 3, // Ensure it's on top of the bars
      },
    ],
  }

  option.value = newOption
}
</script>
