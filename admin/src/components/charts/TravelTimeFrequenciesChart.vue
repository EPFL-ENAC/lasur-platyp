<template>
  <chart-panel
    :title="t('stats.travel_time.title')"
    :description="t('stats.travel_time.description')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onTogglePercent">
              <q-item-section side>
                <q-icon :name="stats.travelTimePercent ? 'check_box' : 'check_box_outline_blank'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('stats.percent_employees') }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="onChartDownload">
              <q-item-section side>
                <q-icon name="download" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('download') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </q-toolbar>
    <e-charts-shell
      ref="shellRef"
      :height="height"
      :loading="props.loading"
      :has-data="hasData"
      :show-info="total > 0"
      :show-table="!exportable"
      :no-data-title="t('stats.travel_time.title')"
      :option="option"
      :exportable="!!exportable"
    >
      <p v-if="hasData && medianValue" class="q-mb-xs">
        {{ t('stats.travel_time.texts.specific', { median: medianValue }) }}
      </p>
      <p>{{ t('stats.travel_time.texts.default') }}</p>
    </e-charts-shell>
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Frequencies } from 'src/models'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  frequencies?: Frequencies | null
  loading?: boolean
  xaxis?: string
  yaxis?: string
  rangeStep?: number
  height?: number
  exportable?: boolean
  inline?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

function onChartDownload() {
  shellRef.value?.handleExport()
}

const stats = useStats()

function onTogglePercent() {
  stats.travelTimePercent = !stats.travelTimePercent
}

const option = ref<EChartsOption>({})
const total = ref(0)
const medianValue = ref<number | null>(null)

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

watch([() => stats.travelTimePercent, () => props.height, locale], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.frequencies) {
    return
  }

  initValuesChartOptions(props.frequencies)
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
      return item
        ? stats.travelTimePercent
          ? ((item.count / total.value) * 100).toFixed(2)
          : item.count
        : 0
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
      formatter: `${props.xaxis ? `${props.xaxis}: ` : ''}<b>{b}</b><br/>{c} ${stats.travelTimePercent ? '%' : ''}`,
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
      name:
        props.yaxis ||
        (stats.travelTimePercent ? t('stats.percent_employees') : t('stats.nb_employees')),
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
