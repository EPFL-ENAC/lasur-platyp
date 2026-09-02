<template>
  <e-charts-shell
    ref="shellRef"
    :height="height"
    :loading="props.loading"
    :has-data="total > 0"
    :show-table="!exportable"
    :no-data-title="chartTitle"
    :option="option"
    :exportable="!!exportable"
  />
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import { type EChartsOption, type SeriesOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Frequencies } from '@/models'
import { MODE_COLORS, SIMPLE_LABELS_COLORS, simpleLabelSortOrder } from './commons'
import { getProModalityLabels } from '@/utils/modalities'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const stats = useStats()
const isComparison = computed(() => !!stats.comparisonMode)

interface Props {
  chartTranslationName: string
  frequencies?: Frequencies[] | Frequencies | null
  groups: string[]
  // Fold transport modes into simple typology labels before charting, for the
  // data the backend only ships in detailed form.
  foldModeToSimple?: boolean
  percent?: boolean
  xaxis?: string
  yaxis?: string
  height?: number
  loading?: boolean
  exportable?: boolean
  // Overrides the title taken from `chartTranslationName`.
  title?: string
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

const chartTitle = computed(() => props.title || t(`stats.${props.chartTranslationName}.title`))

const labelColors = computed(() => (props.foldModeToSimple ? SIMPLE_LABELS_COLORS : MODE_COLORS))

// Series keys are '<scale>_<mode>' (e.g. 'local_plane'): only the mode half is
// recategorised, so the distance scales keep their own bars.
function foldedKey(key: string) {
  if (!props.foldModeToSimple) {
    return key
  }
  const group = props.groups.find((grp) => key.startsWith(`${grp}_`))
  if (!group) {
    return key
  }
  const mode = key.slice(group.length + 1)
  return `${group}_${getProModalityLabels(mode)?.simple ?? mode}`
}

// Modes landing in the same bucket add up.
function foldDataset(dataset: { key: string; value: number }[]) {
  if (!props.foldModeToSimple) {
    return dataset
  }
  const merged = new Map<string, number>()
  dataset.forEach((item) => {
    const key = foldedKey(item.key)
    merged.set(key, (merged.get(key) ?? 0) + item.value)
  })
  return Array.from(merged, ([key, value]) => ({ key, value }))
}

const MODES_ORDER = ['plane', 'car', 'moto', 'pub', 'train', 'bike', 'walking']

function modeSortOrder(mode: string) {
  return props.foldModeToSimple ? simpleLabelSortOrder(mode) : MODES_ORDER.indexOf(mode)
}

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
})

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const option = ref<EChartsOption>({})
const total = ref(0)

watch(
  () => props.loading,
  () => {
    if (props.loading) {
      initChartOptions()
    }
  },
)

watch(
  [
    () => props.height,
    locale,
    () => props.percent,
    () => props.foldModeToSimple,
    () => props.title,
  ],
  () => {
    if (!props.loading) {
      initChartOptions()
    }
  },
)

onMounted(() => {
  initChartOptions()
})

function initChartOptions() {
  if (isComparison.value) {
    initComparisonChartOptions()
    return
  }

  option.value = {}
  total.value = 0
  if (!props.frequencies) {
    return
  }

  let dataset: { key: string; value: number }[] = []
  total.value = 0
  if (Array.isArray(props.frequencies)) {
    dataset = (props.frequencies as Frequencies[]).map((item: Frequencies) => {
      total.value = item.total
      return {
        key: shortKey(item.field),
        value: item.data.map((d) => (d.sum === undefined ? 0 : d.sum)).reduce((a, b) => a + b, 0),
      }
    })
  } else {
    const frequencies = props.frequencies as Frequencies
    dataset = frequencies.data.map((item) => ({
      key: shortKey(item.value),
      value: item.sum === undefined ? 0 : item.sum,
    }))
    total.value = frequencies.total
  }
  dataset = foldDataset(dataset)

  // Extract category names and values for yAxis and series
  const modes = new Set<string>()
  dataset
    .map((item) => item.key)
    .forEach((key) => {
      props.groups.forEach((grp) => {
        if (key.startsWith(grp)) {
          modes.add(key.replace(`${grp}_`, ''))
        }
      })
    })
  if (modes.size === 0) {
    return
  }
  const sorted_modes = Array.from(modes).sort((a, b) => modeSortOrder(a) - modeSortOrder(b))

  let series: {
    name: string
    type: 'bar'
    stack: string
    emphasis: {
      focus: 'series'
    }
    color: string
    data: number[]
  }[] = []

  if (props.percent) {
    const sumByGroup: Record<string, number> = {}
    dataset.forEach((item) => {
      const grp = props.groups.find((g) => item.key.startsWith(g))
      if (grp) {
        sumByGroup[grp] = (sumByGroup[grp] || 0) + item.value
      }
    })
    series = sorted_modes.map((mode) => {
      return {
        name: t(`stats.${props.chartTranslationName}.labels.${mode}`),
        type: 'bar' as const,
        stack: 'total',
        emphasis: {
          focus: 'series' as const,
        },
        color: labelColors.value[mode] || '#ccc',
        data: props.groups.map((grp) => {
          const item = dataset.find((d) => d.key === `${grp}_${mode}`)
          return item ? (item.value / (sumByGroup[grp] || 1)) * 100 : 0
        }),
      }
    })
  } else {
    series = sorted_modes.map((mode) => {
      return {
        name: t(`stats.${props.chartTranslationName}.labels.${mode}`),
        type: 'bar' as const,
        stack: 'total',
        emphasis: {
          focus: 'series' as const,
        },
        color: labelColors.value[mode] || '#ccc',
        data: props.groups.map((grp) => {
          const item = dataset.find((d) => d.key === `${grp}_${mode}`)
          return item ? item.value : 0
        }),
      }
    })
  }

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 120,
    title: {
      text: chartTitle.value,
      subtext: t(`stats.total_trips`, { count: total.value }),
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'item',
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: (params: any) => {
        const val = props.percent ? `${Math.round(params.value)}%` : params.value
        return `${params.marker} ${params.seriesName}: <b>${val}</b>`
      },
    },
    legend: {
      show: true,
      bottom: 0, // position at the bottom
      left: 'center', // center horizontally
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'end',
      nameGap: 30,
      type: 'category',
      data: props.groups.map((g) => t(`stats.${props.chartTranslationName}.labels.${g}`)),
    },
    xAxis: {
      name: props.xaxis || t('stats.nb_employees'),
      nameLocation: 'middle',
      nameGap: 20,
      type: 'value',
    },
    series: series,
  }
  option.value = newOption
}

function initComparisonChartOptions() {
  option.value = {}
  total.value = 0

  const comparisonGroups = stats.comparisonResults?.groups ?? []
  const groupFrequencies = comparisonGroups.map((group) => ({
    name: group.name,
    frequencies: group.pro_mode_frequencies || [],
  }))
  if (groupFrequencies.every((group) => group.frequencies.length === 0)) {
    return
  }

  const datasets = groupFrequencies.map((group) => {
    total.value += group.frequencies[0]?.total ?? 0
    const byKey = new Map<string, number>()
    group.frequencies.forEach((item) => {
      const key = foldedKey(shortKey(item.field))
      const value = item.data
        .map((d) => (d.sum === undefined ? 0 : d.sum))
        .reduce((a, b) => a + b, 0)
      byKey.set(key, (byKey.get(key) ?? 0) + value)
    })
    return { name: group.name, byKey }
  })

  const modes = new Set<string>()
  datasets.forEach((dataset) => {
    dataset.byKey.forEach((_, key) => {
      props.groups.forEach((scale) => {
        if (key.startsWith(scale)) {
          modes.add(key.replace(`${scale}_`, ''))
        }
      })
    })
  })
  if (modes.size === 0) {
    return
  }

  const sortedModes = Array.from(modes).sort((a, b) => modeSortOrder(a) - modeSortOrder(b))

  const series: SeriesOption[] = []
  datasets.forEach((dataset, groupIndex) => {
    sortedModes.forEach((mode) => {
      series.push({
        name: `${dataset.name} — ${t(`stats.${props.chartTranslationName}.labels.${mode}`)}`,
        type: 'bar',
        stack: `group_${groupIndex}`,
        emphasis: { focus: 'series' },
        color: labelColors.value[mode] || '#ccc',
        data: props.groups.map((scale) => dataset.byKey.get(`${scale}_${mode}`) ?? 0),
      })
    })
  })

  option.value = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 120,
    title: {
      text: chartTitle.value,
      subtext: t('stats.total', { count: total.value }),
      left: 'center',
      top: 0,
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: { show: true, bottom: 0, left: 'center', type: 'scroll' },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'end',
      nameGap: 30,
      type: 'category',
      data: props.groups.map((g) => t(`stats.${props.chartTranslationName}.labels.${g}`)),
    },
    xAxis: {
      name: props.xaxis || t('stats.nb_employees'),
      nameLocation: 'middle',
      nameGap: 20,
      type: 'value',
    },
    series,
  }
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
