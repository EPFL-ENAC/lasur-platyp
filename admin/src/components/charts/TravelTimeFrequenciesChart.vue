<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="hasData"
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
      <div class="text-h6 text-center">{{ t(`stats.travel_time.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div class="q-mt-md chart-text" :data-chart-id="chartId">
    <p class="q-mb-xs">{{ t('stats.travel_time.texts.default') }}</p>
    <p v-if="hasData && medianValue">
      {{ t('stats.travel_time.texts.specific', { median: medianValue }) }}
    </p>
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
import { getRandomId } from 'src/utils/random'

const { t, locale } = useI18n()
const $q = useQuasar()
const stats = useStats()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  xaxis?: string
  yaxis?: string
  rangeStep?: number
  percent?: boolean
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chartId = getRandomId()
const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)
const medianValue = ref<number | null>(null)

const hasData = computed(() => {
  if (!stats.frequencies || !stats.frequencies['travel_time']) {
    return false
  }
  const frequencies = stats.frequencies['travel_time'] as Frequencies
  return frequencies.data.length > 0
})

watch(
  () => stats.loading,
  () => {
    if (stats.loading) {
      initChartOptions()
    }
  },
)

watch([() => props.percent, () => props.height, locale], () => {
  if (!stats.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!stats.frequencies || !stats.frequencies['travel_time']) {
    return
  }

  const frequencies = stats.frequencies['travel_time'] as Frequencies

  initValuesChartOptions(frequencies)
}

function computeMedian(frequencies: Frequencies) {
  const sortedData = frequencies.data.toSorted((a, b) => {
    const valueA = Number(a.value)
    const valueB = Number(b.value)
    if (isNaN(valueA)) return 1
    if (isNaN(valueB)) return -1
    return valueA - valueB
  })

  const totalCount = sortedData.reduce((sum, item) => sum + item.count, 0)
  if (totalCount === 0) return undefined

  const isEven = totalCount % 2 === 0
  const midPoint = totalCount / 2

  let cumulativeCount = 0
  let firstMiddleValue: number | null = null

  for (let i = 0; i < sortedData.length; i++) {
    const element = sortedData[i]!
    cumulativeCount += element.count

    const n = Number(element.value)
    const v = isNaN(n) ? 0 : n

    if (!isEven) {
      if (cumulativeCount > midPoint) {
        return v
      }
    } else {
      if (cumulativeCount === midPoint) {
        firstMiddleValue = v
      } else if (cumulativeCount > midPoint) {
        if (firstMiddleValue !== null) {
          return (firstMiddleValue + v) / 2
        }
        return v
      }
    }
  }

  return undefined // In case something goes wrong
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

  medianValue.value = computeMedian(frequencies) ?? null

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
      text: t(`stats.travel_time.title`),
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

function makeCategories(max: number, step = 5) {
  const arr = []
  for (let i = 0; i <= max; i += step) {
    arr.push(`${i}`)
  }
  return arr
}
</script>
