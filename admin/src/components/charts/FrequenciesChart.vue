<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="hasData"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="props.loading"
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.${props.chartTranslationName}.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
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
import type { Frequencies } from 'src/models'
import { useQuasar } from 'quasar'

const { t, locale } = useI18n()
const $q = useQuasar()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  chartTranslationName: string
  frequencies?: Frequencies | null
  xaxis?: string
  yaxis?: string
  rangeStep?: number
  percent?: boolean
  height?: number
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)

const hasData = computed(() => {
  if (!props.frequencies) {
    return false
  }
  return props.frequencies.data.length > 0
})

watch(
  () => props.loading,
  () => {
    if (props.loading) {
      initChartOptions()
    }
  },
)

watch([() => props.percent, () => props.height, locale], () => {
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
  return t(`stats.${props.chartTranslationName}.labels.${key}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.frequencies) {
    return
  }

  const frequencies = props.frequencies as Frequencies

  if (props.rangeStep) {
    initValuesChartOptions(frequencies)
  } else {
    initLabelsChartOptions(frequencies)
  }
}

function initValuesChartOptions(frequencies: Frequencies) {
  total.value = frequencies.total || 0

  // find max value
  const max = Math.max(
    ...frequencies.data.map((item) => {
      const value = Number(item.value)
      return isNaN(value) ? 0 : value
    }),
    0,
  )
  const categories = makeCategories(max, props.rangeStep)

  // foreach category find count in frequencies
  const values =
    categories?.map((category) => {
      const item = frequencies.data.find((item) => item.value === `${category}`)
      return item ? (props.percent ? ((item.count / total.value) * 100).toFixed(2) : item.count) : 0
    }) || []

  const newOption: EChartsOption = {
    grid: {
      left: '40',
      right: '20',
      top: '80',
      bottom: '40',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t(`stats.${props.chartTranslationName}.title`),
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
      formatter: `${props.xaxis ? `${props.xaxis}: ` : ''}<b>{b}</b><br/>{c} ${props.percent ? '%' : ''}`,
    },
    legend: {
      show: false,
    },
    xAxis: {
      type: 'category',
      name: props.xaxis || '',
      nameGap: 30,
      nameLocation: 'middle',
      data: categories,
    },
    yAxis: {
      name: props.yaxis || (props.percent ? t('stats.percent_employees') : t('stats.nb_employees')),
      nameLocation: 'middle',
      nameGap: 30,
      type: 'value',
    },
    series: [
      {
        data: values,
        type: 'bar',
        barCategoryGap: '0',
      },
    ],
  }
  option.value = newOption
}

function initLabelsChartOptions(frequencies: Frequencies) {
  total.value = frequencies.total || 0
  const dataset = frequencies.data.map((item) => ({
    key: item.value || 'null',
    name: keyLabel(item.value || 'null'),
    value: props.percent ? ((item.count / total.value) * 100).toFixed(2) : item.count,
  }))

  // Extract category names and values for yAxis and series
  const categories = dataset.map((item) => item.name).reverse()
  const values = dataset.map((item) => item.value).reverse()

  if (categories.length === 0) {
    return
  }

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t(`stats.${props.chartTranslationName}.title`),
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
      formatter: `<b>{b}</b><br/>{c} ${props.percent ? '%' : ''}`,
    },
    legend: {
      show: false,
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
      nameGap: 30,
      type: 'value',
    },
    series: [
      {
        data: values,
        type: 'bar',
      },
    ],
  }
  option.value = newOption
}

function makeCategories(max: number, step = 5) {
  const arr = []
  for (let i = 0; i <= max; i += step) {
    arr.push(`${i}`)
  }
  return arr
}
</script>
