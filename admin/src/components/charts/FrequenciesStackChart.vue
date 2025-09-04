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
import { type EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Frequencies } from 'src/models'
import { MODE_COLORS } from './commons'

const { t } = useI18n()
const stats = useStats()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  groups: string[]
  xaxis?: string
  yaxis?: string
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

watch([() => props.height], () => {
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
  return t(`stats.${props.type}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  if (!stats.frequencies || !stats.frequencies[props.type]) {
    return
  }

  let dataset: { key: string; name: string; value: number }[] = []
  let total = 0
  if (Array.isArray(stats.frequencies[props.type])) {
    dataset = (stats.frequencies[props.type] as Frequencies[]).map((item: Frequencies) => {
      total = item.total
      return {
        key: shortKey(item.field),
        name: keyLabel(item.field),
        value: item.data
          .map((d) => (d.sum === undefined ? d.count : d.sum))
          .reduce((a, b) => a + b, 0),
      }
    })
  } else {
    const frequencies = stats.frequencies[props.type] as Frequencies
    dataset = frequencies.data.map((item) => ({
      key: shortKey(item.value),
      name: keyLabel(item.value),
      value: item.sum === undefined ? item.count : item.sum,
    }))
    total = frequencies.total
  }

  // Extract category names and values for yAxis and series
  const modes = new Set<string>()
  dataset
    .map((item) => item.key)
    .forEach((key) => {
      props.groups.forEach((grp) => {
        if (key.startsWith(grp)) {
          modes.add(key.replace(`${grp}_`, ''))
        }
      })
    })
  if (modes.size === 0) {
    return
  }
  const modes_order = ['plane', 'car', 'moto', 'pub', 'train', 'bike', 'walking']
  const sorted_modes = Array.from(modes).sort((a, b) => {
    return modes_order.indexOf(a) - modes_order.indexOf(b)
  })

  const series = sorted_modes.map((mode) => {
    return {
      name: t(`stats.${props.type}.labels.${mode}`),
      type: 'bar' as const,
      stack: 'total',
      emphasis: {
        focus: 'series' as const,
      },
      color: MODE_COLORS[mode] || '#ccc',
      data: props.groups.map((grp) => {
        const item = dataset.find((d) => d.key === `${grp}_${mode}`)
        return item ? item.value : 0
      }),
    }
  })

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '40',
      containLabel: true,
    },
    animation: false,
    height: props.height - 120,
    title: {
      text: t(`stats.${props.type}.title`),
      subtext: t(`stats.total`, { count: total }),
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        // Use axis to trigger tooltip
        type: 'shadow', // 'shadow' as default; can also be 'line' or 'shadow'
      },
    },
    legend: {
      show: false,
      bottom: 0, // position at the bottom
      left: 'center', // center horizontally
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'end',
      nameGap: 30,
      type: 'category',
      data: props.groups.map((g) => t(`stats.${props.type}.labels.${g}`)),
    },
    xAxis: {
      name: props.xaxis || t('stats.nb_employees'),
      nameLocation: 'middle',
      nameGap: 30,
      type: 'value',
    },
    series: series,
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
