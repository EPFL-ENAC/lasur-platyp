<template>
  <e-charts-shell
    :height="height"
    :loading="props.loading"
    :has-data="total > 0"
    :show-info="true"
    :no-data-title="t(`stats.emissions_${props.chartTranslationName}.title`)"
    :option="option"
    :exportable="!!exportable"
  >
    <q-markdown
      v-if="textLabels"
      :src="t(`stats.emissions_${props.chartTranslationName}.texts.specific`, textLabels)"
    />
  </e-charts-shell>
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { MODE_COLORS, SIMPLE_LABELS_COLORS, COMPLEX_LABELS_COLORS } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from 'src/utils/numbers'
import type { EmissionReduction, Emissions } from 'src/models'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  chartTranslationName: string
  emissions: Emissions[] | null
  reductions: EmissionReduction[] | null
  yaxis?: string
  rangeStep?: number
  height?: number
  loading?: boolean
  exportable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

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
    unit: UNIT_LABEL,
  }
})

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale], () => {
  if (!props.loading) {
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
  // for the simple/complex label variants, categories are v3 typology
  // labels (e.g. 'TIM', 'car+pub'), not plain transport modes
  if (props.chartTranslationName.includes('simple')) {
    return t(`simple_labels.${shortKey(key)}`)
  }
  if (props.chartTranslationName.includes('complex')) {
    return t(`complex_labels.${shortKey(key)}`)
  }
  return t(`transportation_modes.${shortKey(key)}`)
}

const SCALE_FACTOR = 1 / 1000 // convert from kg to tons
const UNIT_LABEL = 'tCO₂eq'

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.emissions || !props.reductions) {
    return
  }

  const emissions = props.emissions || []
  if (emissions.length === 0) {
    return
  }
  const recoEmissions = props.reductions || []
  if (recoEmissions.length === 0) {
    return
  }

  const categories = recoEmissions.sort((a, b) => b.reduced - a.reduced).map((item) => item.mode)

  const colors = props.chartTranslationName.includes('simple')
    ? SIMPLE_LABELS_COLORS
    : props.chartTranslationName.includes('complex')
      ? COMPLEX_LABELS_COLORS
      : MODE_COLORS

  // make dataset for waterfall chart: reference is current total of emissions, then for each category, show from previous to current
  currentEmissions.value = emissions.map((item) => item.emissions).reduce((a, b) => a + b, 0)
  const categoryEmissions: { [key: string]: number } = {}
  recoEmissions.forEach((item) => {
    categoryEmissions[item.mode] = item.reduced
  })
  newEmissions.value =
    currentEmissions.value - Object.values(categoryEmissions).reduce((a, b) => a + b, 0)

  const categoriesLabels = [
    t(`stats.emissions_${props.chartTranslationName}.labels.current`),
    ...categories.map((cat) => keyLabel(cat)),
    t(`stats.emissions_${props.chartTranslationName}.labels.postSaving`),
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
      text: t(`stats.emissions_${props.chartTranslationName}.title`),
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
          tar.name + '<br/>' + tar.seriesName + ' : ' + formatNumber(tar.value) + ' ' + UNIT_LABEL
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
      name: t(`stats.emissions_${props.chartTranslationName}.xaxis`) || '',
      nameLocation: 'middle',
      nameGap: 90,
    },
    yAxis: {
      name: t(`stats.emissions_${props.chartTranslationName}.yaxis`) || '',
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
            return (currentEmissions.value - sum - (categoryEmissions[cat] || 0)) * SCALE_FACTOR
          }),
          0,
        ],
      },
      {
        name: t(`stats.emissions_${props.chartTranslationName}.series`) || '',
        type: 'bar',
        stack: 'Total',
        label: {
          show: true,
          position: 'inside',
          formatter: function (params) {
            if (params.value === 0) {
              return ''
            }
            return formatNumber(params.value as number) + ' ' + UNIT_LABEL
          },
        },
        data: [
          {
            value: currentEmissions.value * SCALE_FACTOR,
            itemStyle: {
              color: '#000',
            },
          },
          ...categories.map((cat) => ({
            value: (categoryEmissions[cat] || 0) * SCALE_FACTOR,
            itemStyle: {
              color: colors[shortKey(cat)] || colors.default || '#ccc',
            },
          })),
          {
            value: newEmissions.value * SCALE_FACTOR,
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
