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
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.${props.type}.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
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
import { useQuasar } from 'quasar'

const { t, locale } = useI18n()
const $q = useQuasar()
const stats = useStats()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  groups: string[]
  percent?: boolean
  xaxis?: string
  yaxis?: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)

watch(
  () => stats.loading,
  () => {
    if (stats.loading) {
      initChartOptions()
    }
  },
)

watch([() => props.height, locale, () => props.percent], () => {
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
  total.value = 0
  if (!stats.frequencies || !stats.frequencies[props.type]) {
    return
  }

  let dataset: { key: string; name: string; value: number }[] = []
  total.value = 0
  if (Array.isArray(stats.frequencies[props.type])) {
    dataset = (stats.frequencies[props.type] as Frequencies[]).map((item: Frequencies) => {
      total.value = item.total
      return {
        key: shortKey(item.field),
        name: keyLabel(item.field),
        value: item.data.map((d) => (d.sum === undefined ? 0 : d.sum)).reduce((a, b) => a + b, 0),
      }
    })
  } else {
    const frequencies = stats.frequencies[props.type] as Frequencies
    dataset = frequencies.data.map((item) => ({
      key: shortKey(item.value),
      name: keyLabel(item.value),
      value: item.sum === undefined ? 0 : item.sum,
    }))
    total.value = frequencies.total
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

  let series: {
    name: string;
    type: "bar";
    stack: string;
    emphasis: {
        focus: "series";
    };
    color: string;
    data: number[];
  }[] = []

  if (props.percent) {
    const sumByGroup: Record<string, number> = {}
    dataset.forEach((item) => {
      const grp = props.groups.find((g) => item.key.startsWith(g))
      if (grp) {
        sumByGroup[grp] = (sumByGroup[grp] || 0) + item.value
      }
    })
    series = sorted_modes.map((mode) => {
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
          return item ? item.value / (sumByGroup[grp] || 1) * 100 : 0
        }),
      }
    })
  } else {
    series = sorted_modes.map((mode) => {
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
  }

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
      subtext: t(`stats.total`, { count: total.value }),
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: (params: any) => {
        let res = `${params[0].name}<br/>`;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        params.forEach((item: any) => {
          // item.value is the data point value
          const val = props.percent 
            ? `${item.value.toFixed(1)}%` 
            : item.value;
          
          res += `${item.marker} ${item.seriesName}: <b>${val}</b><br/>`;
        });
        return res;
      }
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
