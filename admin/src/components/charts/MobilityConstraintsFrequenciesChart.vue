<template>
  <chart-panel
    :title="t('stats.constraints.title')"
    :description="t('stats.constraints.description')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
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
      :show-info="!!hasOther"
      :no-data-title="t('stats.constraints.title')"
      :option="option"
      :exportable="!!exportable"
    >
      <div class="q-mt-md text-italic">
        {{ t('stats.constraints.texts.other') }}
      </div>
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
  xaxis?: string
  yaxis?: string
  rangeStep?: number
  percent?: boolean
  height?: number
  loading?: boolean
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

const option = ref<EChartsOption>({})
const total = ref(0)

const hasData = computed(() => {
  if (!props.frequencies) {
    return false
  }
  return props.frequencies.data.length > 0
})

const hasOther = computed(() => {
  return props.frequencies?.data.some((item) => item.value === 'other')
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
  return t(`stats.constraints.labels.${key}`)
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
      text: t(`stats.constraints.title`),
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
      text: t(`stats.constraints.title`),
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
