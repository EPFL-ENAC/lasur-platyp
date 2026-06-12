<template>
  <e-charts-shell
    :height="height"
    :loading="props.loading"
    :has-data="hasData"
    :no-data-title="t(`stats.${props.chartTranslationName}.title`)"
    :option="option"
    :exportable="!!exportable"
  />
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { MODE_IDEAL_ORDER, MODE_COLORS } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Frequencies } from 'src/models'

const { t, locale } = useI18n()
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  chartTranslationName: string
  frequencies?: Frequencies | Frequencies[] | null
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

const hasData = computed(() => {
  if (!props.frequencies) {
    return false
  }
  return Array.isArray(props.frequencies)
    ? props.frequencies.length > 0
    : props.frequencies.data.length > 0
})

watch(
  () => props.loading,
  () => {
    if (props.loading) {
      initChartOptions()
    }
  },
)

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
  return t(`transportation_modes.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.frequencies) {
    return
  }

  let dataset: { key: string; name: string; value: number }[] = []
  if (Array.isArray(props.frequencies)) {
    dataset = (props.frequencies as Frequencies[]).map((item: Frequencies) => {
      total.value = item.total
      return {
        key: shortKey(item.field),
        name: keyLabel(item.field),
        value: item.data
          .map((d) => (d.sum === undefined ? d.count : d.sum))
          .reduce((a, b) => a + b, 0),
      }
    })
  } else {
    const frequencies = props.frequencies as Frequencies
    dataset = frequencies.data.map((item) => ({
      key: shortKey(item.value),
      name: keyLabel(item.value),
      value: item.sum === undefined ? item.count : item.sum,
    }))
    total.value = frequencies.total
  }
  dataset.sort((a, b) => (MODE_IDEAL_ORDER[a.key] || 0) - (MODE_IDEAL_ORDER[b.key] || 0))

  // Extract category names and values for series
  const categories = dataset.map((item) => item.key)
  const colors = categories.map((category) => MODE_COLORS[category] || '#ccc')

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
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: '<b>{b}</b><br/>{c} ({d}%)',
    },
    legend: {
      show: true,
      bottom: 16,
      type: 'scroll',
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        top: 'middle',
        color: colors,
        label: {
          margin: 0,
          fontWeight: 'bold',
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
