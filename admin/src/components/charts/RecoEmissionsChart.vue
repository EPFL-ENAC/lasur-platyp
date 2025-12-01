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
import { toMaxDecimals } from 'src/utils/numbers'
// import { MODE_COLORS } from './commons'

const { t } = useI18n()
const stats = useStats()
use([SVGRenderer, CustomChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  reco: string
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
    .map((item) => item.field)

  // make dataset for waterfall chart: reference is total of emissions, then for each category, show from previous to current
  const totalEmissions = emissions.map((item) => item.emissions).reduce((a, b) => a + b, 0)
  const categoryEmissions: { [key: string]: number } = {}
  recoEmissions.forEach((item) => {
    categoryEmissions[item.field] = item.emissions
  })
  const savedEmissions =
    totalEmissions - Object.values(categoryEmissions).reduce((a, b) => a + b, 0)

  const categoriesLabels = [keyLabel('total'), ...categories.map((cat) => keyLabel(cat))]
  categoriesLabels.push(keyLabel('saved'))

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
      subtext: t(`stats.total`, { count: emissions[0]?.total }),
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
          tar.name + '<br/>' + tar.seriesName + ' : ' + toMaxDecimals(tar.value, 2) + ' kgCO₂eq'
        )
      },
    },
    legend: {
      show: false,
    },
    xAxis: {
      // name: props.xaxis || '',
      // nameLocation: 'middle',
      // nameGap: 30,
      type: 'category',
      data: categoriesLabels,
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
            return totalEmissions - sum - (categoryEmissions[cat] || 0)
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
        },
        data: [
          toMaxDecimals(totalEmissions, 2),
          ...categories.map((cat) => toMaxDecimals(categoryEmissions[cat] || 0, 2)),
          toMaxDecimals(savedEmissions, 2),
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
