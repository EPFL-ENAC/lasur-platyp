<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="total > 0"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="props.loading"
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
      :data-chart-id="chartId"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.emissions_${props.chartTranslationName}.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div class="q-mt-md chart-text" :data-chart-id="chartId">
    <q-markdown
      v-if="emissionItemsLabels"
      :src="t(`stats.emissions_${props.chartTranslationName}.texts.specific`, emissionItemsLabels)"
    />
    <q-markdown
      v-else-if="emissionItemsProLabels"
      :src="t(`stats.emissions_${props.chartTranslationName}.texts.specific`, emissionItemsProLabels)"
    />
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { CustomChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { MODE_COLORS } from './commons'
import { useQuasar } from 'quasar'
import { formatNumber } from 'src/utils/numbers'
import { getRandomId } from 'src/utils/random'
import type { Emissions } from 'src/models'

const { t, locale } = useI18n()
const $q = useQuasar()
use([SVGRenderer, CustomChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  chartTranslationName: string
  emissions?: Emissions[] | null
  xaxis?: string
  yaxis?: string
  rangeStep?: number
  height?: number
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const chartId = getRandomId()
const option = ref<EChartsOption>({})
const total = ref(0)

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale, () => $q.dark.isActive], () => {
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
  if (props.chartTranslationName.includes('pro')) {
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
    carMotoJourneysPercentage: formatNumber(ei.carMotoJourneysPercentage),
    carMotoEmissionsPercentage: formatNumber(ei.carMotoEmissionsPercentage),
  }
})

const emissionItemsPro = computed(() => {
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
    firstPercent: formatNumber((eip.first.emissions / eip.total) * 100),
    firstMode: keyLabel(eip.first.mode),
    firstEmissions: formatNumber((eip.first.emissions || 0) / eip.first.journeys),
    secondPercent: formatNumber((eip.second.emissions / eip.total) * 100),
    secondMode: keyLabel(eip.second.mode),
    remainingEmissions: formatNumber(withoutFirstEmissions / withoutFirstJourneys),
  }
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
  option.value = {}
  total.value = 0
  if (!props.emissions) {
    return
  }

  const emissions = props.emissions || []
  if (emissions.length === 0) {
    return
  }

  const labelColor = $q.dark.isActive ? '#fffcf4' : '#000000'

  let ubound = 0
  const dataset = emissions
    .sort((a, b) => {
      const emaA = a.journeys ? a.emissions / a.journeys : 0
      const emaB = b.journeys ? b.emissions / b.journeys : 0
      return emaB - emaA
    })
    .map((item) => {
      const data = [
        ubound,
        ubound + item.journeys,
        item.journeys ? (item.emissions / item.journeys).toFixed(2) : 0,
        keyLabel(item.mode),
        MODE_COLORS[shortKey(item.mode)] || MODE_COLORS['default'],
        item.emissions.toFixed(0),
        item.journeys,
        `${item.distances.toFixed(0)} km`,
      ]
      ubound += item.journeys
      return data
    })

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
      trigger: 'item',
    },
    legend: {
      show: false,
    },
    xAxis: {
      name: props.xaxis || '',
      nameLocation: 'middle',
      nameGap: 30,
      type: 'value',
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'middle',
      nameGap: 40,
      type: 'value',
    },
    series: [
      {
        type: 'custom',
        renderItem: function (params, api) {
          const val0 = (api.value(0) as number) || 0
          const val1 = (api.value(1) as number) || 0
          const yValue = api.value(2) || 0
          const start = api.coord([api.value(0) || 0, yValue]) || [0, 0]
          const size: [number, number] = api.size
            ? (api.size([val1 - val0, yValue]) as [number, number])
            : [0, 0]
          const style = { fill: api.value(4) as string }
          const rect = {
            type: 'rect' as const,
            shape: {
              x: start[0] as number,
              y: start[1] as number,
              width: size[0],
              height: size[1],
            },
            style: style,
          }

          const pxLeft = api.coord([val0, 0])[0] || 0
          const pxRight = api.coord([val1, 0])[0] || 0
          const pxBaseY = api.coord([0, 0])[1] || 0
          const pxValY = api.coord([0, yValue])[1] || 0
          const label = {
            type: 'text' as const,
            style: {
              text: String(api.value(3)),
              x: (pxLeft + pxRight) / 2,
              y: yValue ? pxValY - 10 : pxBaseY + 14,
              textAlign: 'center',
              textVerticalAlign: 'middle',
              fill: labelColor,
            },
            silent: true, // don't intercept mouse events
          }
          return { type: 'group', children: [rect, label] }
        },
        label: {
          show: true,
          position: 'top',
        },
        dimensions: [
          'from',
          'to',
          'emissions',
          'label',
          'color',
          keyLabel('emissions'),
          keyLabel('journeys'),
          keyLabel('distances'),
        ],
        encode: {
          x: [0, 1],
          y: 2,
          tooltip: [5, 6, 7],
          itemName: 3,
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
