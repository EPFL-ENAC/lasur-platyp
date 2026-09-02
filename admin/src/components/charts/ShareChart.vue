<template>
  <e-charts-shell
    ref="shellRef"
    :height="height"
    :loading="props.loading"
    :has-data="hasData"
    :show-table="!exportable"
    :no-data-title="chartTitle"
    :option="option"
    :exportable="!!exportable"
  />
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { use } from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  MODE_COLORS,
  SIMPLE_LABELS_COLORS,
  aggregateFrequenciesBySimpleLabel,
  modeSortOrder,
  simpleLabelSortOrder,
  computePercentages,
} from './commons'
import {
  buildGroupStackedBarOption,
  findBiggestGroupDifference,
  type ComparisonGroupDataset,
} from './comparisonCharts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatSignedPercent } from '@/utils/numbers'
import type { ComparisonStats, Frequencies } from '@/models'

const { t, te, locale } = useI18n()
use([
  SVGRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const stats = useStats()
const isComparison = computed(() => !!stats.comparisonMode)

interface Props {
  chartTranslationName: string
  // Which vocabulary the frequency values are expressed in: 'simple' for the
  // simple typology labels, transport modes otherwise.
  labelType?: 'simple' | 'mode'
  // Fold recommendation values into simple typology labels before charting,
  // for the data the backend only ships in detailed form.
  foldRecoToSimple?: boolean
  frequencies?: Frequencies | Frequencies[] | null
  height?: number
  loading?: boolean
  exportable?: boolean
  // Overrides the title taken from `chartTranslationName`.
  title?: string
}
const props = withDefaults(defineProps<Props>(), {
  labelType: 'mode',
  height: 400,
  exportable: true,
})

const chartTitle = computed(() => props.title || t(`stats.${props.chartTranslationName}.title`))

// A list of Frequencies is one datum per field, a shape the fold does not apply to.
const frequencies = computed(() => {
  if (!props.frequencies || Array.isArray(props.frequencies) || !props.foldRecoToSimple) {
    return props.frequencies
  }
  return aggregateFrequenciesBySimpleLabel(props.frequencies)
})

const labelColors = computed(() =>
  props.labelType === 'simple' ? SIMPLE_LABELS_COLORS : MODE_COLORS,
)

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    const diff = comparisonDifference.value
    if (!diff) return ''
    return t(`stats.${props.chartTranslationName}.texts.comparison`, {
      lastGroup: diff.lastGroupName,
      prevGroup: diff.prevGroupName,
      mode: diff.name,
      diff: formatSignedPercent(diff.diffPercent),
    })
  },
})

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const option = ref<EChartsOption>({})
const total = ref(0)
const comparisonGroupDatasets = ref<ComparisonGroupDataset[]>([])

const comparisonDifference = computed(() =>
  findBiggestGroupDifference(comparisonGroupDatasets.value, 'prev_minus_last'),
)

function findGroupFrequencies(groupStats: ComparisonStats): Frequencies | undefined {
  const found =
    groupStats.frequencies?.find((freq) => freq.field === props.chartTranslationName) ||
    groupStats.pro_frequencies?.find((freq) => freq.field === props.chartTranslationName)
  if (!found || !props.foldRecoToSimple) {
    return found
  }
  return aggregateFrequenciesBySimpleLabel(found)
}

const hasData = computed(() => {
  if (isComparison.value) {
    return (stats.comparisonResults?.groups ?? []).some(
      (group) => (findGroupFrequencies(group)?.data.length ?? 0) > 0,
    )
  }
  if (!frequencies.value) {
    return false
  }
  return Array.isArray(frequencies.value)
    ? frequencies.value.length > 0
    : frequencies.value.data.length > 0
})

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
    () => props.labelType,
    () => props.foldRecoToSimple,
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

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  if (props.labelType === 'simple') {
    const messageKey = `simple_labels.${shortKey(key)}`
    if (te(messageKey)) {
      return t(messageKey)
    }
  }
  return t(`transportation_modes.${shortKey(key)}`)
}

function labelSortOrder(key: string) {
  return props.labelType === 'simple' ? simpleLabelSortOrder(key) : modeSortOrder(key)
}

function initChartOptions() {
  if (isComparison.value) {
    initComparisonChartOptions()
    return
  }

  comparisonGroupDatasets.value = []
  option.value = {}
  total.value = 0
  if (!frequencies.value) {
    return
  }

  let dataset: { key: string; name: string; value: number }[] = []
  if (Array.isArray(frequencies.value)) {
    dataset = (frequencies.value as Frequencies[]).map((item: Frequencies) => {
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
    const single = frequencies.value as Frequencies
    dataset = single.data.map((item) => ({
      key: shortKey(item.value),
      name: keyLabel(item.value),
      value: item.sum === undefined ? item.count : item.sum,
    }))
    total.value = single.total
  }
  dataset.sort((a, b) => labelSortOrder(a.key) - labelSortOrder(b.key))

  // Add rounded percentages that sum to 100
  const datasetWithPercent = computePercentages(dataset)

  // Extract category names and values for series
  const categories = datasetWithPercent.map((item) => item.key)
  const colors = categories.map((category) => labelColors.value[category] || '#ccc')

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
      text: chartTitle.value,
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: CallbackDataParams | CallbackDataParams[]) => {
        const p = Array.isArray(params) ? params[0] : params
        if (!p) return ''

        return `<b>${p.name}</b><br/>${(p.data as { percent: number }).percent}%`
      },
    },
    legend: {
      show: true,
      bottom: 16,
      type: 'scroll',
      selectedMode: false,
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
          formatter: (params: CallbackDataParams) =>
            `${(params.data as { percent: number }).percent}%`,
        },
        data: datasetWithPercent,
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}

function initComparisonChartOptions() {
  option.value = {}
  total.value = 0

  const groups = stats.comparisonResults?.groups ?? []
  if (groups.length === 0) {
    return
  }

  const groupDatasets: ComparisonGroupDataset[] = groups.map((group) => {
    const frequencies = findGroupFrequencies(group)
    total.value += frequencies?.total ?? 0
    return {
      name: group.name,
      items: (frequencies?.data ?? []).map((item) => ({
        key: shortKey(item.value),
        name: keyLabel(item.value),
        value: item.sum === undefined ? item.count : item.sum,
      })),
    }
  })

  comparisonGroupDatasets.value = groupDatasets

  const keyOrder = Array.from(
    new Set(groupDatasets.flatMap((group) => group.items.map((item) => item.key))),
  ).sort((a, b) => labelSortOrder(a) - labelSortOrder(b))

  option.value = buildGroupStackedBarOption({
    groupDatasets,
    colors: labelColors.value,
    percent: true,
    title: chartTitle.value,
    totalLabel: t('stats.total', { count: total.value }),
    height: props.height,
    yAxisName: '%',
    keyOrder,
  })
}
</script>
