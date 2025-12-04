<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="total > 0"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="stats.loading"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.emissions_${props.type}.title`) }}</div>
      <div class="text-subtitle1 text-grey-8 text-center">{{ t('stats.no_data') }}</div>
    </div>
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
const total = ref(0)

watch([() => stats.loading], () => {
  if (stats.loading) {
    initChartOptions()
  }
})

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
  return t(`stats.emissions_${props.type}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
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
        keyLabel(item.mode),
        MODE_COLORS[shortKey(item.mode)] || MODE_COLORS['default'],
        item.emissions.toFixed(0),
        item.journeys,
        `${item.distances.toFixed(0)} km`,
      ]
      ubound += item.journeys
      return data
    })

  total.value = emissions[0]?.total || 0
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
      subtext: t(`stats.total`, { count: total.value }),
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
      nameLocation: 'middle',
      nameGap: 30,
      type: 'value',
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'middle',
      nameGap: 40,
      type: 'value',
    },
    series: [
      {
        type: 'custom',
        renderItem: function (params, api) {
          const val0 = (api.value(0) as number) || 0
          const val1 = (api.value(1) as number) || 0
          const yValue = api.value(2) || 0
          const start = api.coord([api.value(0) || 0, yValue]) || [0, 0]
          const size: [number, number] = api.size
            ? (api.size([val1 - val0, yValue]) as [number, number])
            : [0, 0]
          const style = { fill: api.value(4) as string }
          const rect = {
            type: 'rect' as const,
            shape: {
              x: start[0] as number,
              y: start[1] as number,
              width: size[0],
              height: size[1],
            },
            style: style,
          }

          const pxLeft = api.coord([val0, 0])[0] || 0
          const pxRight = api.coord([val1, 0])[0] || 0
          const pxBaseY = api.coord([0, 0])[1] || 0
          const pxValY = api.coord([0, yValue])[1] || 0
          const label = {
            type: 'text' as const,
            style: {
              text: String(api.value(3)),
              x: (pxLeft + pxRight) / 2,
              y: yValue ? pxValY - 10 : pxBaseY + 14,
              textAlign: 'center',
              textVerticalAlign: 'middle',
            },
            silent: true, // don't intercept mouse events
          }
          return { type: 'group', children: [rect, label] }
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
