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
import { CustomChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { MODE_COLORS } from './commons'

const { t } = useI18n()
const stats = useStats()
use([SVGRenderer, CustomChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  xaxis?: string
  yaxis?: string
  rangeStep?: number
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})

watch([() => stats.loading], () => {
  if (stats.loading) {
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
  return t(`stats.emissions_${props.type}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  if (!stats.emissions || !stats.emissions[props.type]) {
    return
  }

  const emissions = stats.emissions[props.type] || []
  if (emissions.length === 0) {
    return
  }

  let ubound = 0
  const dataset = emissions
    .sort((a, b) => {
      const emaA = a.journeys ? a.emissions / a.journeys : 0
      const emaB = b.journeys ? b.emissions / b.journeys : 0
      return emaB - emaA
    })
    .map((item) => {
      const data = [
        ubound,
        ubound + item.journeys,
        item.journeys ? (item.emissions / item.journeys).toFixed(2) : 0,
        keyLabel(item.field),
        MODE_COLORS[shortKey(item.field)] || MODE_COLORS['default'],
        item.emissions.toFixed(0),
        item.journeys,
        `${item.distances.toFixed(0)} km`,
      ]
      ubound += item.journeys
      return data
    })

  const newOption: EChartsOption = {
    grid: {
      left: '40',
      right: '20',
      top: '60',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t(`stats.emissions_${props.type}.title`),
      subtext: t(`stats.total`, { count: emissions[0]?.total }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'item',
    },
    legend: {
      show: false,
    },
    xAxis: {
      name: props.xaxis || '',
      nameLocation: 'end',
      nameGap: 30,
      type: 'value',
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'middle',
      nameGap: 30,
      type: 'value',
    },
    series: [
      {
        type: 'custom',
        renderItem: function (params, api) {
          const val0 = (api.value(0) as number) || 0
          const val1 = (api.value(1) as number) || 0
          const yValue = api.value(2)
          const start = api.coord([api.value(0) || 0, yValue || 0]) || [0, 0]
          const size: [number, number] = api.size
            ? (api.size([val1 - val0, yValue]) as [number, number])
            : [0, 0]
          const style = { fill: api.value(4) as string }
          return {
            type: 'rect',
            shape: {
              x: start[0] as number,
              y: start[1] as number,
              width: size[0],
              height: size[1],
            },
            style: style,
          }
        },
        label: {
          show: true,
          position: 'top',
        },
        dimensions: [
          'from',
          'to',
          'emissions',
          'label',
          'color',
          keyLabel('emissions'),
          keyLabel('journeys'),
          keyLabel('distances'),
        ],
        encode: {
          x: [0, 1],
          y: 2,
          tooltip: [5, 6, 7],
          itemName: 3,
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
