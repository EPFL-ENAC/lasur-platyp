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
      <div class="text-h6 text-center">{{ t(`stats.emissions_${props.reco}.title`) }}</div>
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
import { toMaxDecimals } from 'src/utils/numbers'
// import { MODE_COLORS } from './commons'

const { t } = useI18n()
const stats = useStats()
use([SVGRenderer, CustomChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  reco: string
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
  return t(`stats.emissions_${props.reco}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!stats.emissions || !stats.emissions[props.type] || !stats.emissions[props.reco]) {
    return
  }

  const emissions = stats.emissions[props.type] || []
  if (emissions.length === 0) {
    return
  }
  const recoEmissions = stats.emissions[props.reco] || []
  if (recoEmissions.length === 0) {
    return
  }

  const categories = recoEmissions
    .sort((a, b) => b.emissions - a.emissions)
    .map((item) => item.mode)

  // make dataset for waterfall chart: reference is current total of emissions, then for each category, show from previous to current
  const currentEmissions = emissions.map((item) => item.emissions).reduce((a, b) => a + b, 0)
  const categoryEmissions: { [key: string]: number } = {}
  recoEmissions.forEach((item) => {
    categoryEmissions[item.mode] = item.emissions
  })
  const savedEmissions =
    currentEmissions - Object.values(categoryEmissions).reduce((a, b) => a + b, 0)

  const categoriesLabels = [
    keyLabel('current'),
    ...categories.map((cat) => keyLabel(cat)),
    keyLabel('saved'),
  ]

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
      text: t(`stats.emissions_${props.reco}.title`),
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: function (params: any) {
        const tar = params[1]
        if (!tar) return ''
        return (
          tar.name +
          '<br/>' +
          tar.seriesName +
          ' : ' +
          new Intl.NumberFormat().format(toMaxDecimals(tar.value, 0) || 0) +
          ' kgCO₂eq'
        )
      },
    },
    legend: {
      show: false,
    },
    xAxis: {
      type: 'category',
      data: categoriesLabels,
      axisLabel: {
        rotate: 30,
      },
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'middle',
      nameGap: 50,
      type: 'value',
    },
    series: [
      {
        name: 'Placeholder',
        type: 'bar',
        stack: 'Total',
        itemStyle: {
          borderColor: 'transparent',
          color: 'transparent',
        },
        emphasis: {
          itemStyle: {
            borderColor: 'transparent',
            color: 'transparent',
          },
        },
        data: [
          0,
          ...categories.map((cat) => {
            let sum = 0
            for (const c of categories) {
              if (c === cat) {
                break
              }
              sum += categoryEmissions[c] || 0
            }
            return currentEmissions - sum - (categoryEmissions[cat] || 0)
          }),
          0,
        ],
      },
      {
        name: 'Emissions',
        type: 'bar',
        stack: 'Total',
        label: {
          show: true,
          position: 'inside',
          formatter: function (params) {
            if (params.value === 0) {
              return ''
            }
            return new Intl.NumberFormat().format(toMaxDecimals(params.value as number, 0) || 0)
          },
        },
        data: [
          currentEmissions,
          ...categories.map((cat) => categoryEmissions[cat] || 0),
          savedEmissions,
        ],
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
