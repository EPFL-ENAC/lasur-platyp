<template>
  <e-charts-shell
    ref="shellRef"
    :height="height"
    :loading="props.loading"
    :has-data="total > 0"
    :show-table="!exportable"
    :no-data-title="t(`stats.emissions_${props.chartTranslationName}.title`)"
    :option="option"
    :exportable="!!exportable"
  />
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { CustomChart, BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { MODE_COLORS, SIMPLE_LABELS_COLORS, COMPLEX_LABELS_COLORS, modeSortOrder } from './commons'
import { buildGroupStackedBarOption, type ComparisonGroupDataset } from './comparisonCharts'
import { formatNumber } from 'src/utils/numbers'
import type { ComparisonStats, Emissions } from 'src/models'

const { t, locale } = useI18n()
use([
  SVGRenderer,
  CustomChart,
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
  emissions?: Emissions[] | null
  xaxis?: string
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

function findGroupEmissions(groupStats: ComparisonStats): Emissions[] | undefined {
  switch (props.chartTranslationName) {
    case 'freq_mod_simple':
      return groupStats.mode_emissions_simple_labels ?? undefined
    case 'freq_mod_complex':
      return groupStats.mode_emissions_complex_labels ?? undefined
    case 'freq_mod_pro':
      return groupStats.pro_mode_emissions ?? undefined
    default:
      return undefined
  }
}

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const option = ref<EChartsOption>({})
const total = ref(0)

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

const globalAnswersThreshold = 10
const perModeAnswersThreshold = 3

const emissionItems = computed(() => {
  if (isComparison.value) return null
  if (props.chartTranslationName !== 'freq_mod') {
    return null
  }
  if (!props.emissions) return null
  if (total.value < globalAnswersThreshold) return null

  const carEmissions = props.emissions.find((item) => item.mode === 'car')
  const motoEmissions = props.emissions.find((item) => item.mode === 'moto')
  const allJourneys = props.emissions.reduce((sum, item) => sum + item.journeys, 0)
  const allEmissions = props.emissions.reduce((sum, item) => sum + item.emissions, 0)
  const combinedJourneys = (carEmissions?.journeys || 0) + (motoEmissions?.journeys || 0)
  const combinedEmissions = (carEmissions?.emissions || 0) + (motoEmissions?.emissions || 0)

  if (allJourneys === 0 || allEmissions === 0) {
    return null
  }

  return {
    carMotoJourneysPercentage: (combinedJourneys / allJourneys) * 100,
    carMotoEmissionsPercentage: (combinedEmissions / allEmissions) * 100,
  }
})

const emissionItemsLabels = computed(() => {
  const ei = emissionItems.value
  if (!ei) return null

  return {
    carMotoJourneysPercentage: formatNumber(Math.round(ei.carMotoJourneysPercentage)),
    carMotoEmissionsPercentage: formatNumber(Math.round(ei.carMotoEmissionsPercentage)),
  }
})

const emissionItemsPro = computed(() => {
  if (isComparison.value) return null
  if (!props.chartTranslationName.includes('pro')) {
    return null
  }
  if (!props.emissions) return null
  if (total.value < globalAnswersThreshold) return null

  const emissions = props.emissions || []

  const planeEmissions = emissions.find((item) => item.mode === 'plane')
  const carEmissions = emissions.find((item) => item.mode === 'car')
  if (!planeEmissions || !carEmissions) return null
  if (
    planeEmissions.total < perModeAnswersThreshold ||
    carEmissions.total < perModeAnswersThreshold
  ) {
    return null
  }

  const totalEmissions = emissions.reduce((sum, item) => sum + item.emissions, 0)
  if (totalEmissions === 0) return null

  return {
    first: planeEmissions,
    second: carEmissions,
    total: totalEmissions,
    withoutFirst: emissions.filter((item) => item.mode !== planeEmissions.mode),
  }
})

const emissionItemsProLabels = computed(() => {
  const eip = emissionItemsPro.value
  if (!eip) return null

  const withoutFirstEmissions = eip.withoutFirst.reduce((sum, item) => sum + item.emissions, 0)
  const withoutFirstJourneys = eip.withoutFirst.reduce((sum, item) => sum + item.journeys, 0)

  return {
    firstPercent: formatNumber(Math.round((eip.first.emissions / eip.total) * 100)),
    firstMode: keyLabel(eip.first.mode),
    firstEmissions: formatNumber(Math.round((eip.first.emissions || 0) / eip.first.journeys)),
    secondPercent: formatNumber(Math.round((eip.second.emissions / eip.total) * 100)),
    secondMode: keyLabel(eip.second.mode),
    remainingEmissions: formatNumber(Math.round(withoutFirstEmissions / withoutFirstJourneys)),
  }
})

const chartDescription = computed(() => {
  if (emissionItemsLabels.value) {
    return t(
      `stats.emissions_${props.chartTranslationName}.texts.specific`,
      emissionItemsLabels.value,
    )
  }
  if (emissionItemsProLabels.value) {
    return t(
      `stats.emissions_${props.chartTranslationName}.texts.specific`,
      emissionItemsProLabels.value,
    )
  }
  return ''
})

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    return chartDescription.value
  },
})

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  return t(`stats.emissions_${props.chartTranslationName}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  if (isComparison.value) {
    initComparisonChartOptions()
    return
  }

  option.value = {}
  total.value = 0
  if (!props.emissions) {
    return
  }

  const emissions = props.emissions || []
  if (emissions.length === 0) {
    return
  }

  const colors =
    props.chartTranslationName === 'freq_mod_simple'
      ? SIMPLE_LABELS_COLORS
      : props.chartTranslationName === 'freq_mod_complex'
        ? COMPLEX_LABELS_COLORS
        : MODE_COLORS

  let ubound = 0
  const preparedData = emissions
    .sort((a, b) => {
      const emaA = a.journeys ? a.emissions / a.journeys : 0
      const emaB = b.journeys ? b.emissions / b.journeys : 0
      return emaB - emaA
    })
    .map((item) => {
      const data = {
        name: keyLabel(item.mode),
        color: colors[shortKey(item.mode)] || colors['default'],
        value: [
          ubound, // 0: start x
          ubound + item.journeys, // 1: end x
          item.journeys ? (item.emissions / item.journeys).toFixed(2) : 0, // 2: height
          keyLabel(item.mode), // 3: label
          item.emissions.toFixed(0), // 4
          item.journeys, // 5
          `${item.distances.toFixed(0)} km`, // 6
        ],
      }
      ubound += item.journeys
      return data
    })

  total.value = emissions[0]?.total || 0

  const newOption: EChartsOption = {
    grid: {
      left: '40',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 120,
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
      trigger: 'item',
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: (params: any) => {
        let html = `<div style="font-weight: bold; margin-bottom: 4px;">${params.marker} ${params.name}</div>`

        const indicesToShow = [4, 5, 6]

        indicesToShow.forEach((idx) => {
          const label = params.dimensionNames[idx]
          const value = params.value[idx]

          if (value !== undefined) {
            html += `
              <div style="display: flex; justify-content: space-between; gap: 20px;">
                <span>${label}</span>
                <span style="font-weight: bold;">${value}</span>
              </div>`
          }
        })

        return html
      },
    },
    legend: {
      show: true,
      bottom: 0,
      left: 'center',
      itemGap: 10,
    },
    xAxis: {
      name: props.xaxis || '',
      nameLocation: 'middle',
      nameGap: 20,
      type: 'value',
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'middle',
      nameGap: 40,
      type: 'value',
    },
    series: preparedData.map((item) => ({
      name: item.name, // This makes the item appear in the legend
      color: item.color!,
      type: 'custom',
      renderItem: function (params, api) {
        const val0 = api.value(0) as number
        const val1 = api.value(1) as number
        const yValue = api.value(2) as number
        const start = api.coord([val0, yValue])
        const size = api.size!([val1 - val0, yValue]) as [number, number]
        const style = api.style()

        return {
          type: 'group',
          children: [
            {
              type: 'rect',
              shape: {
                x: start[0]!,
                y: start[1]!,
                width: size[0]!,
                height: size[1]!,
              },
              style: {
                ...style,
                fill: item.color!,
              },
            },
          ],
        }
      },
      data: [item.value],
      dimensions: [
        'from',
        'to',
        'emissions',
        'label',
        keyLabel('emissions'),
        keyLabel('journeys'),
        keyLabel('distances'),
      ],
      encode: {
        x: [0, 1],
        y: 2,
        tooltip: [4, 5, 6],
        itemName: 3,
      },
    })),
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
  const groupEmissions = groups.map((group) => ({
    name: group.name,
    emissions: findGroupEmissions(group) ?? [],
  }))
  if (groupEmissions.every((group) => group.emissions.length === 0)) {
    return
  }

  const colors =
    props.chartTranslationName === 'freq_mod_simple'
      ? SIMPLE_LABELS_COLORS
      : props.chartTranslationName === 'freq_mod_complex'
        ? COMPLEX_LABELS_COLORS
        : MODE_COLORS

  const groupDatasets: ComparisonGroupDataset[] = groupEmissions.map((group) => {
    total.value += group.emissions[0]?.total ?? 0
    return {
      name: group.name,
      items: group.emissions.map((item) => ({
        key: shortKey(item.mode),
        name: keyLabel(item.mode),
        value: item.emissions,
      })),
    }
  })

  const keyOrder = Array.from(
    new Set(groupDatasets.flatMap((group) => group.items.map((item) => item.key))),
  ).sort((a, b) => modeSortOrder(a) - modeSortOrder(b))

  option.value = buildGroupStackedBarOption({
    groupDatasets,
    colors,
    percent: false,
    title: t(`stats.emissions_${props.chartTranslationName}.title`),
    totalLabel: t('stats.total', { count: total.value }),
    height: props.height - 120,
    yAxisName: props.yaxis || 'kgCO₂eq',
    keyOrder,
  })
}
</script>
