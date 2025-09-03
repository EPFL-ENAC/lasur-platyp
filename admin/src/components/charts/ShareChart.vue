<template>
  <div v-if="option.series" :style="`height: ${height}px; width: 100%;`">
    <e-charts
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="stats.loading"
    />
  </div>
</template>

<script setup lang="ts">
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
import type { Frequencies } from 'src/models'
import { MOD_COLORS } from './commons'

const { t } = useI18n()
const stats = useStats()
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})

watch(
  () => stats.loading,
  () => {
    if (stats.loading) {
      initChartOptions()
    }
  },
)

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
  return t(`stats.${props.type}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  if (!stats.frequencies || !stats.frequencies[props.type]) {
    return
  }

  let dataset: { key: string; name: string; value: number }[] = []

  if (Array.isArray(stats.frequencies[props.type])) {
    dataset = (stats.frequencies[props.type] as Frequencies[]).map((item: Frequencies) => ({
      key: shortKey(item.field),
      name: keyLabel(item.field),
      value: item.data
        .map((d) => (d.sum === undefined ? d.count : d.sum))
        .reduce((a, b) => a + b, 0),
    }))
  } else {
    const frequencies = stats.frequencies[props.type] as Frequencies
    dataset = frequencies.data.map((item) => ({
      key: shortKey(item.value),
      name: keyLabel(item.value),
      value: item.sum === undefined ? item.count : item.sum,
    }))
  }

  // Extract category names and values for series
  const categories = dataset.map((item) => item.key).reverse()
  console.log(categories)
  const colors = categories.map((category) => MOD_COLORS[category] || '#ccc')

  if (categories.length === 0) {
    return
  }

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '40',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height,
    title: {
      text: t(`stats.${props.type}.title`),
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
      },
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
        radius: ['30%', '50%'],
        avoidLabelOverlap: true,
        color: colors,
        label: {
          margin: 0,
          fontWeight: 'bold',
        },
        data: dataset,
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
