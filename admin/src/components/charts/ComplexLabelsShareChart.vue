<template>
  <e-charts-shell
    ref="shellRef"
    :height="height"
    :loading="props.loading"
    :has-data="hasData"
    :show-info="total > 0"
    :show-table="!exportable"
    :no-data-title="t('stats.freq_mod.title_detailed')"
    :option="option"
    :exportable="!!exportable"
  >
    <p v-if="topModes.length === 3" class="q-mb-xs">
      {{
        t('stats.freq_mod.texts.specific', {
          top_1: topModes[0],
          top_2: topModes[1],
          top_3: topModes[2],
        })
      }}
    </p>
  </e-charts-shell>
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { COMPLEX_LABELS_COLORS, complexLabelSortOrder } from './commons'
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
  frequencies: Frequencies | Frequencies[] | null
  loading?: boolean
  height?: number
  exportable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
})

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const option = ref<EChartsOption>({})
const total = ref(0)
const topModes = ref<string[]>([])

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
  return t(`complex_labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.frequencies) {
    return
  }

  let dataset: { key: string; name: string; value: number; count: number }[] = []
  if (Array.isArray(props.frequencies)) {
    dataset = (props.frequencies as Frequencies[]).map((item: Frequencies) => {
      total.value = item.total
      return {
        key: shortKey(item.field),
        name: keyLabel(item.field),
        count: item.data.reduce((a, b) => a + b.count, 0),
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
      count: item.count,
      value: item.sum === undefined ? item.count : item.sum,
    }))
    total.value = frequencies.total
  }

  dataset.sort((a, b) => complexLabelSortOrder(a.key) - complexLabelSortOrder(b.key))

  const sortedByValue = dataset
    .filter((item) => item.count > 5)
    .toSorted((a, b) => b.value - a.value)
  topModes.value = sortedByValue.slice(0, 3).map((item) => item.name)

  // Extract category names and values for series
  const categories = dataset.map((item) => item.key)
  const colors = categories.map((category) => COMPLEX_LABELS_COLORS[category] || '#ccc')

  if (categories.length === 0) {
    return
  }

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '40',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height,
    title: [
      {
        text: t(`stats.freq_mod.title_detailed`),
        subtext: t(`stats.total`, { count: total.value }),
        left: 'center',
        top: 0,
        textStyle: {
          fontSize: 16,
        },
      },
    ],
    tooltip: {
      trigger: 'item',
      formatter: '<b>{b}</b><br/>{c} ({d}%)',
    },
    legend: {
      show: true,
      bottom: 0,
      left: 'center',
    },
    series: [
      {
        type: 'pie',
        radius: ['30%', '50%'],
        center: ['30%', '50%'],
        avoidLabelOverlap: true,
        color: colors,
        label: {
          margin: 0,
          fontWeight: 'bold',
          formatter: '{d}% ({c})',
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
