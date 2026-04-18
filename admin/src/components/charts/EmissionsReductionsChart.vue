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
      :data-chart-id="chartId"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.emissions_${props.reductionType}.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div class="q-mt-md chart-text" :data-chart-id="chartId">
    <p class="q-mb-xs">{{ t(`stats.emissions_${props.reductionType}.texts.default`) }}</p>
    <q-markdown
      v-if="textLabels"
      :src="t(`stats.emissions_${props.reductionType}.texts.specific`, textLabels)"
    />
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
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
import { formatNumber } from 'src/utils/numbers'
import { MODE_COLORS } from './commons'
import { useQuasar } from 'quasar'
import { getRandomId } from 'src/utils/random'

const { t, locale } = useI18n()
const $q = useQuasar()
const stats = useStats()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  reductionType: string
  yaxis?: string
  rangeStep?: number
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const chartId = getRandomId()
const option = ref<EChartsOption>({})
const total = ref(0)
const currentEmissions = ref(0)
const newEmissions = ref(0)

const textLabels = computed(() => {
  if (total.value < 5) return null

  return {
    current_emissions: formatNumber(currentEmissions.value / 1000), // convert from kg to tons
    new_emissions: formatNumber(newEmissions.value / 1000),
    cheeseburgers: formatNumber(Math.round((currentEmissions.value - newEmissions.value) / 18.8)),
    vacuum: formatNumber(Math.round((currentEmissions.value - newEmissions.value) / 73.43)),
    shirt: formatNumber(Math.round((currentEmissions.value - newEmissions.value) / 13.23466)),
    laptop: formatNumber(Math.round((currentEmissions.value - newEmissions.value) / 192.62)),
    email_sent: formatNumber(Math.round((currentEmissions.value - newEmissions.value) / 0.002462)),
    visio_hour: formatNumber(Math.round((currentEmissions.value - newEmissions.value) / 0.057063)),
  }
})

watch([() => stats.loading], () => {
  if (stats.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale], () => {
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
  return t(`stats.emissions_${props.reductionType}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (
    !stats.emissions ||
    !stats.emissions[props.type] ||
    !stats.emissionsReductions[props.reductionType]
  ) {
    return
  }

  const emissions = stats.emissions[props.type] || []
  if (emissions.length === 0) {
    return
  }
  const recoEmissions = stats.emissionsReductions[props.reductionType] || []
  if (recoEmissions.length === 0) {
    return
  }

  const categories = recoEmissions.sort((a, b) => b.reduced - a.reduced).map((item) => item.mode)

  // make dataset for waterfall chart: reference is current total of emissions, then for each category, show from previous to current
  currentEmissions.value = emissions.map((item) => item.emissions).reduce((a, b) => a + b, 0)
  const categoryEmissions: { [key: string]: number } = {}
  recoEmissions.forEach((item) => {
    categoryEmissions[item.mode] = item.reduced
  })
  newEmissions.value =
    currentEmissions.value - Object.values(categoryEmissions).reduce((a, b) => a + b, 0)

  const categoriesLabels = [
    keyLabel('current'),
    ...categories.map((cat) => keyLabel(cat)),
    keyLabel('postSaving'),
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
      text: t(`stats.emissions_${props.reductionType}.title`),
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
        return tar.name + '<br/>' + tar.seriesName + ' : ' + formatNumber(tar.value) + ' kgCO₂eq'
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
      name: t(`stats.emissions_${props.reductionType}.xaxis`) || '',
      nameLocation: 'middle',
      nameGap: 90,
    },
    yAxis: {
      name: t(`stats.emissions_${props.reductionType}.yaxis`) || '',
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
            return currentEmissions.value - sum - (categoryEmissions[cat] || 0)
          }),
          0,
        ],
      },
      {
        name: t(`stats.emissions_${props.reductionType}.series`) || '',
        type: 'bar',
        stack: 'Total',
        label: {
          show: true,
          position: 'inside',
          formatter: function (params) {
            if (params.value === 0) {
              return ''
            }
            return formatNumber(params.value as number)
          },
        },
        data: [
          {
            value: currentEmissions.value,
            itemStyle: {
              color: '#000',
            },
          },
          ...categories.map((cat) => ({
            value: categoryEmissions[cat] || 0,
            itemStyle: {
              color: MODE_COLORS[cat] || MODE_COLORS.default || '#ccc',
            },
          })),
          {
            value: newEmissions.value,
            itemStyle: {
              color: '#000',
            },
          },
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
